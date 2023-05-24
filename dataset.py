import torch
from sklearn.metrics import confusion_matrix
import pickle
import numpy as np
import os


class Dataset(torch.utils.data.Dataset):
    def __init__(self, X, Y, categories, accepted_categories, urls, device, whitelist_path, manual_labels_files=None, debug=False, rm_features=[], rebuild_email=False):
        self.features_list()
        self.device = device
        self.rebuild_email = rebuild_email
        self.x = []
        self.y = [] # 0 = not scam | 1: scam
        self.urls = []

        # get the whitelist data -> remove them!
        whitelist = []
        with open(whitelist_path, 'r', encoding='utf-8') as fin:
            for line in fin.readlines():
                whitelist.append(line.strip())
            fin.close()

        # get manual labeling correction!
        manual_labels = {} # url -> url
        if manual_labels_files != None:
            for manual_labels_file in manual_labels_files:
                with open(manual_labels_file, 'r', encoding='utf-8') as fin:
                    for line in fin.readlines():
                        if len(line.strip().split(', ')) != 4:
                            continue
                        url, true_label, pred_label, manual_label = line.strip().split(', ')
                        if int(manual_label) in [0, 1]:
                            manual_labels[url] = int(manual_label)
                    fin.close()
            print('Manual Labels:', len(manual_labels))
        
        # preprocess the data -> quantizing social media features
        self.removed_features = [self.features_list[i] for i in rm_features]
        
        for data_ind, x in enumerate(X):
            if categories != {} and (accepted_categories != [] and (urls[data_ind] in categories and categories[urls[data_ind]] not in accepted_categories) or (urls[data_ind] not in categories)):
                continue

            # check if whitelist:
            is_white = False
            for wurl in whitelist:
                if wurl in urls[data_ind]:
                    is_white = True
                    break
            if is_white:
                Y[data_ind] = 0

            # check manual labeling filter
            if urls[data_ind] in manual_labels and manual_labels[urls[data_ind]] == -1:
                continue

            # count the sm features
            x_tmp = []
            for i, v in enumerate(x):
                # remove features
                if i in self.removed_features:
                    x_tmp.append(0)
                    continue
                if i != 18:
                    x_tmp.append(v)

            self.x.append(x_tmp) 
            if urls[data_ind] not in manual_labels:
                self.y.append(Y[data_ind]) 
            else:
                self.y.append(manual_labels[urls[data_ind]])
            self.urls.append(urls[data_ind])  

        # assert features len
        l = len(self.x[0])
        for x in self.x:
            assert len(x) == l
        
        # print some stats
        print('# features: %d' %(l))
        counts = {0: 0, 1: 0}
        for y in self.y:
            counts[y] += 1
            
        print(counts)

        # get min max of each feature!
        if debug:
            X = np.array(self.x)
            for feature_ind in range(X.shape[1]):
                if 19 < feature_ind < 500:
                    continue
                print('Feature #%d: Min = %0.2f, Max = %0.2f, Avg = %0.3f' %(feature_ind + 1, np.min(X[:, feature_ind]), np.max(X[:, feature_ind]), np.mean(X[:, feature_ind])))
        
        # fix feature bugs
        top_cheap_domains = ['club', 'buzz', 'xyz', 'ua', 'icu', 'space', 'agency', 'monster', 'pw', 'click', 'website', 'site', 'club', 'online', 'link', 'shop', 'feedback', 'uno', 'press', 'best', 'fun', 'host', 'store', 'tech', 'top', 'it']

        for ind in range(len(self.urls)):
            for cheap_domain in top_cheap_domains:
                if cheap_domain in self.urls[ind]:
                    self.x[ind][13] = 1

    def __getitem__(self, ind):
        return torch.tensor(self.x[ind], device=self.device), torch.tensor(self.y[ind], device=self.device), self.urls[ind]

    def __len__(self):
        return len(self.x)

    def get_src(self, url):
        page_content = ''
        if os.path.exists(os.path.join('dataset', 'saved_pages', url.replace('/', '').replace('?', '').replace('!', '').replace('@', '').replace(':', '')) + '.html'):
            fin = open(os.path.join('dataset', 'saved_pages', url.replace('/', '').replace('?', '').replace('!', '').replace('@', '').replace(':', '') + '.html'), 'r', encoding='utf-8')
            page_content = fin.read()
            fin.close()
        elif os.path.exists(os.path.join('dataset', 'saved_pages', 'http' + url.replace('/', '').replace('?', '').replace('!', '').replace('@', '').replace(':', '')) + '.html'):
            fin = open(os.path.join('dataset', 'saved_pages', 'http' + url.replace('/', '').replace('?', '').replace('!', '').replace('@', '').replace(':', '') + '.html'), 'r', encoding='utf-8')
            page_content = fin.read()
            fin.close()
        elif os.path.exists(os.path.join('dataset', 'saved_pages', 'https' + url.replace('/', '').replace('?', '').replace('!', '').replace('@', '').replace(':', '')) + '.html'):
            fin = open(os.path.join('dataset', 'saved_pages', 'https' + url.replace('/', '').replace('?', '').replace('!', '').replace('@', '').replace(':', '') + '.html'), 'r', encoding='utf-8')
            page_content = fin.read()
            fin.close()
        else:
            return None
        return page_content
           
    def features_list(self):
        self.features_list = {
            'Domain Age': 0,
            'Has Guard': 1,
            'Instagram': 2,
            'Facebook': 3,
            'Twitter': 4,
            'Num Ext Links': 5,
            'Top 1M': 6,
            'Host == Domain': 7,
            'Num Script Tags': 8,
            'Hypen': 9,
            'Dots Count': 10,
            'Has Digit': 11,
            'Is Cheap in WHOIS': 12,
            'Cheap Domain': 13,
            'Num Domain in Text': 14,
            'Zero': 15,
            'Common Domains': 16,
            'Total Age': 17,
            'Missing Data': 528,
            'Instagram Followers': 529,
            'Twitter Followers': 530,
            'Twitter Age': 531,
            'Facebook Followers': 532,
            'Facebook Age': 533,
            'Facebook Likes': 534,
            'SSL': 536,
            'URLLEN': 537
        }

