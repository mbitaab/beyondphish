import whois
import json
import sys
import tqdm
from urllib.parse import urlsplit, urlunsplit
import pickle


def get_whois_single(url):
    data = {}

    try:
        w = whois.whois(url)
        data[url] = w
    except:
        pass
    return data

def get_whois(input_file, output_dir):
    # read alive url file
    filename = input_file
    urls = []

    with open(filename, 'r', encoding='utf-8') as fin:
        for line in fin.readlines():
            line = line.strip().split(',')

            urls.append((line[0], line[1]))

    print(len(urls))

    # get whois data
    data = {}
    for ind, d in enumerate(urls):
        print('Step %d/%d\t\t\t\t' %(ind + 1, len(urls)), end='\r', flush=True)
        subm_id, url = d
        page_name = urlsplit(url).netloc
        if url == '':
            continue

        try:
            w = whois.whois(url)
            w['subm_id'] = subm_id
            data[page_name] = w
        except:
            continue

    pickle.dump(data, open(output_dir + '/whois_data.pkl', 'wb'))
