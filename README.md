# BEYOND PHISH: Toward Detecting Fraudulent e-Commerce Websites at Scale

Despite recent advancements in malicious website detection and phishing mitigation, the ecosystem has paid little attention to Fraudulent e-Commerce websites (FCWs), such as Fraudulent shopping websites, fake charities, and malicious cryptocurrency websites. Even worse, there are no active mitigation systems or publicly available dataset for FCWs.

In this paper, we first propose an efficient and automated approach to gather FCWs through crowdsourcing.  We identify eight different types of non-phishing FCWs and derive key defining characteristics. Then, we find that anti-phishing mitigation systems, such as Google Safe Browsing, have a detection rate of just 0.46% on our dataset. We create a classifier, Beyond Phish, to identify FCWs using manually defined features based on our analysis. Validating Beyond Phish on never-before-seen (untrained and untested data) through a user study indicates that our system has a high detection rate and a low false positive score of 98.34% and 1.34%, respectively. Lastly, we collaborated with a major Internet security company, Palo Alto Networks, to evaluate our classifier on manually labeled real-world data. The model achieves a false positive rate of 2.46% and a 94.88% detection rate, showing potential for real-world defense against FCWs.


## How to use
The pipeline has two parts. The build_data-reddit.ipynb notebook can be used to convert URLs to features. Then, it will create a pickle file that can be used to train the neural network model. You can use the pickle file to train any type of classifier.

To convert the shared jsonl dataset, you can use the same notebook to create features based on the provided content/whois information.

## Data
The dataset consisting of follected FCWs can be downloaded from here:

[FCWs Dataset](https://www.dropbox.com/s/pdnkje0q9m5sp1u/dataset.jsonl?dl=0)


### Citation:
Bitaab, Marzieh, et al. "BEYOND PHISH: Toward Detecting Fraudulent e-Commerce Websites at Scale." 2023 IEEE Symposium on Security and Privacy (SP). IEEE, 2023.
