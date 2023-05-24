from torch import nn


class Model(nn.Module):
    def __init__(self, num_features, num_classes, hidden_sizes):
        super(Model, self).__init__()

        # define network
        self.manual_features = nn.Sequential(
            nn.Linear(num_features, hidden_sizes[0]),
            nn.LeakyReLU(),

            nn.Linear(hidden_sizes[0], hidden_sizes[1]),
            nn.LeakyReLU(),

            nn.Linear(hidden_sizes[1], hidden_sizes[2]),
            nn.Dropout(0.2),
            nn.LeakyReLU(),
        )

        self.clf = nn.Sequential(
            nn.Linear(hidden_sizes[2], 64),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.clf(self.manual_features(x))
