import time
import argparse
import os
import pandas as pd
from tqdm import tqdm
import requests
from datetime import datetime
from requests import ConnectionError, ReadTimeout
import csv

def is_available(url, cox_check=True):
    try:
        request = requests.get(url, timeout=2)
    except (ConnectionError, ReadTimeout):
        return False
    except:
        return False
    else:
        if 'finder.cox.net' in request.text:
            return False
        return True

def is_url_alive(url):
    if 'http://' in url or 'https://' in url:
        return is_available(url), url

    if is_available('http://' + url):
        return True, 'http://' + url
    return is_available('https://' + url), 'https://' + url

def clean_url(url):
    valid_char = ''
    url = url.lower()
    url = url.replace('...', '').replace('\'', '').replace(',', '').replace('@', '')

    while not ord('a') <= ord(url[0]) <= ord('z') and not ord('0') <= ord(url[0]) <= ord('9'):
        url = url[1:]
    while not ord('a') <= ord(url[-1]) <= ord('z') and not ord('0') <= ord(url[-1]) <= ord('9'):
        url = url[:-1]

    if ('://' in url and len(url.split('://')[0]) != 4) or ('://' in url and len(url.split('://')[0]) != 5):
        url = url.split('://')[1]

    return url

def read_csv(filename, delimiter=','):
    content = []

    with open(filename, 'r', encoding='utf-8') as fin:
        for line in fin.readlines():
            line = line.strip().split(delimiter)
            content.append(line[:2])
        fin.close()
    return content


def check_urls(output_dir, url_filenames):
    filenames = url_filenames

    # load urls
    alive_urls = []
    already_checked = set()

    for filename in filenames:
        urls = read_csv(filename)
        print('Processing %s' %filename)

        for (subm_id, url) in tqdm(urls):
            url = clean_url(url)

            if url == '':
                continue

            if url in already_checked:
                continue
            
            already_checked.add(url)

            is_alive, url = is_url_alive(url)
            if not is_alive:
                continue

            alive_urls.append((subm_id, url))
            
    
    fname = os.path.basename(filenames[0])
    output_filename = 'alive_urls_' + fname.split('_')[1] + '_' + fname.split('_')[2]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # write output
    with open(os.path.join(output_dir, output_filename), 'w', newline='', encoding='utf-8') as f: 
        a = csv.writer(f, delimiter=',')
        #            sub_id   comments
        headers = ["post ID", "url"]
        a.writerow(headers)

        for subm_id, url in alive_urls:
            a.writerow([subm_id, url])
        f.close()
