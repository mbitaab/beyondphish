import numpy as np
import torch
import json
import pickle
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from dataset import Dataset
from model import Model
from tqdm import tqdm
from sklearn.preprocessing import MultiLabelBinarizer
from torch import nn
import wandb


def test(model, loader):
    model.eval()
    y_pred, y_true, y_prob, urls = [], [], [], []
    corrects = 0
    all_data = 0
    for batch_ind, batch in enumerate(loader):

        x = batch[0].float()
        y = batch[1]
        
        # pass to model
        preds = model(x)
        
        for i, pred_prob in enumerate(preds.cpu().detach().numpy()):
            y_prob.append(pred_prob)
        
        preds = torch.argmax(preds, dim=-1)

        # calc acc
        for i, pred_label in enumerate(preds.cpu().detach().numpy()):
            if y[i] == pred_label:
                corrects += 1
            y_true.append(y[i].item())
            y_pred.append(pred_label)
            urls.append(batch[2][i])
            all_data += 1

    # calculate metrics
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return corrects / all_data, fp / (fp + tn), y_pred, y_true, y_prob, urls


def main():
    # load the dataset
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    X, Y, src_addr_bot = pickle.load(open('./cache/dataset.pkl', 'rb'))
    X = np.array(X).squeeze(1)
    BATCH_SIZE = 32 

    # # convert to pyt dataloader
    dataset = Dataset(
        X, 
        Y, 
        {}, # url_categories 
        [], # exclusions
        src_addr_bot, 
        device, 
        whitelist_path='./data/whitelist.txt',
        manual_labels_files=[], 
        debug=False, 
    )

    # split into train/test
    train_len = int(len(dataset) * 0.8)
    test_len = len(dataset) - train_len

    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_len, test_len])
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=True)

    print('Train len = %d | Test len = %d' %(len(train_dataset), len(test_dataset)))
    labels_count = {'train': {0: 0, 1: 0}, 'test': {0: 0, 1: 0}}

    for _, y, _ in train_dataset:
        labels_count['train'][y.cpu().item()] += 1
    for _, y, _ in test_dataset:
        labels_count['test'][y.cpu().item()] += 1

    print('Labels Dist:', labels_count)

    # initialize wandb for logging
    wandb.init(project="scam-detection-pipeline")

    # define the model and train
    # train
    MAX_ITERS = 300
    model = Model(dataset[0][0].shape[0], 2, [512, 256, 128]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_values = []
    loss_func = nn.BCEWithLogitsLoss()

    for iteration in tqdm(range(MAX_ITERS)):
        model.train()
        iter_loss = []
        for batch_ind, batch in enumerate(train_loader):
            x = batch[0].float()
            y = batch[1]
            y_logits = torch.zeros((y.shape[0], 2)).to(device)
            for i in range(y.shape[0]):
                y_logits[i, y[i]] = 1

            # pass to model
            optimizer.zero_grad()
            preds = model(x)

            # calc loss
            loss = loss_func(preds.squeeze(-1), y_logits)
            loss.backward()
            optimizer.step()

            iter_loss.append(loss.item())
        
        loss_values.append(np.mean(iter_loss))


        # test on validation
        if (iteration + 1) % 5 == 0:
            # returns ACC, FPR, y_pred, y_true, y_prob
            rb = test(model, test_loader)

            # print test results only
            tn, fp, fn, tp = confusion_matrix(rb[-3], rb[-4]).ravel()
            wandb.log({
                'train_loss': np.mean(iter_loss), 
                'FPR': fp / (fp + tn), 
                'FNR': fn / (tp + fn), 
                'Accuracy': (tp + tn) / (tp + tn + fp + fn)
            })
        else:
            wandb.log({'train_loss': np.mean(iter_loss)})
            
        # save latest checkpoint
        if (iteration + 1) % 50 == 0:
            torch.save(model.state_dict(), './cache/model_at_%d.pt' %(iteration + 1))
    torch.save(model.state_dict(), './cache/model_final.pt')


if __name__ == '__main__':
    main()
