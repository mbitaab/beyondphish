import datetime
from progressbar import progressbar
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urlsplit, urlunsplit
import urllib
import socket
import libs.scanner.IP2Location as IP2Location

def get_html(subm_id, base_dir):
    content = 0
    
    try:
        with open(os.path.join(base_dir, 'saved_pages', '%s.html') %(subm_id), 'r', encoding='utf-8') as fin:
            content = ''.join(fin.readlines())
        return content
    except:
        return ''

def create_features_single(icann_data, countries, html_string, url, sm_info_gettter, data_file="IP2LOCATION-LITE-DB1.BIN"):
    ip_location = IP2Location.IP2Location(data_file)
    u = urlsplit(url)
    if 'http' not in url:
        u = u.path
    else:
        u = u.netloc
    X = []

    ## get domain age
    if 'creation_date' in icann_data[url] and (type(icann_data[url]['creation_date']) is datetime.datetime or type(icann_data[url]['creation_date']) is list):
        try:
            if type(icann_data[url]['creation_date'][0]) != list:
                age = 2000
            else:
                created = icann_data[url]['creation_date'][0]
                age = (datetime.datetime.now() - icann_data[url]['creation_date'][0]).days
        except:
            age = (datetime.datetime.now() - icann_data[url]['creation_date']).days
            created = icann_data[url]['creation_date']
            
        age /= 365.0
    else:
        age = -1.0

    # range
    try:
        total_age = (icann_data[url]['expiration_date'] - icann_data[url]['creation_date']).days / 365.0
    except:
        total_age = -1

    ## set country
    country_feature = [0 for i in range(255)]
    if 'country' in icann_data[url] and icann_data[url]['country'] in countries:
        country = countries.index(icann_data[url]['country'])
        country_feature[country] = 1
    else:
        country = -1

    ## whois guard is used or not
    names = icann_data[url]['name'] if 'name' in icann_data[url] else None
    if type(names) is list:
        names = names[0]

    whois_guard_keywords = ['WhoisGuard'.lower(), 'REDACTED FOR PRIVACY'.lower(), 'Private Whois'.lower(), 'DOMAIN PRIVACY'.lower()]

    for kw in whois_guard_keywords:
        if names != None and (kw in names.lower() or 'priva' in names.lower()):
            guard = 1
            break
        elif names == None:
            guard = -1
        else:
            guard = 0

    ### get features from a single page
    # parse DOM tree
    parsed_tree = BeautifulSoup(html_string, 'html.parser')
    script_tags = parsed_tree.find_all('script', src=True)
    
    link_tags = parsed_tree.find_all('a', href=True)
    num_external_links = 0

    if link_tags != None:
        for link_tag in link_tags:
            link = link_tag['href'] # if 'href' in link_tag else ''
            # check if it's external link
            if link.find('http') == 0 and u not in link:
                num_external_links += 1
    
    ## Shopping sites only filter: filter sites with payment
    # if 'payment' not in html_string.lower() and 'cart' not in html_string.lower():
    #     continue
    
    # check social media links
    total_social_medias = [-1, -1, -1]
    social_media_regex = [
        r'instagram\.com\/[a-zA-Z0-9_\-]+',
        r'facebook\.com\/[a-zA-Z0-9_\-]+',
        r'twitter\.com\/[a-zA-Z0-9_\-]+',
    ]

    sm_info = {}
    
    for i, r in enumerate(social_media_regex):
        found = re.findall(r, html_string)
        if len(found) > 0 and 'login' not in found[0]:
            if found[0].split('/')[-1] in url:
                total_social_medias[i] = 1
            else:
                total_social_medias[i] = 0
                
            if 'twitter.com' in found[0] or 'instagram.com' in found[0] or 'facebook.com' in found[0]:
                if 'https://' not in found[0]:
                    found[0] = 'https://' + found[0]
                if sm_info_gettter != None:
                    sm_info[found[0]] = sm_info_gettter.get_info(found[0])
                else:
                    sm_info[found[0]] = {
                        'creation_date': -1,
                        'likes': -1,
                        'followers': -1,
                        'type': 'personal'
                    }

    # alexa
    try:
        top_1m = int(BeautifulSoup(urllib.request.urlopen('http://data.alexa.com/data?cli=10&dat=s&url={}'.format(url)).read(), features='lxml').find('popularity')['text'])
        top_1m = 1 if top_1m <= 100000 else 0
    except:
        top_1m = -1
        pass


    ## Host country
    host_country_feature = [0 for i in range(255)]
    try:
        host_ip = socket.gethostbyname(u)
        response = ip_location.get_all(host_ip)
        host_country = response.country_short.decode()
        host_domain_same = 1 if countries.index(host_country) == country else 0
        host_country = countries.index(host_country)
        host_country_feature[host_country] = 1
    except:
        host_domain_same = -1
        host_country = -1

    has_digit = False
    for i in url:
        if i.isdigit():
            has_digit = True
            break

    is_cheap = 0
    if 'whois_server' in i and i['whois_server'].lower() is not None and 'cheap' in i['whois_server'].lower():
        is_cheap = 1
    
    top_cheap_domains = ['club', 'buzz', 'xyz', 'ua', 'icu', 'space', 'agency', 'monster', 'pw', 'click', 'website', 'site', 'club', 'online', 'link', 'shop', 'feedback', 'uno', 'press', 'best', 'fun', 'host', 'store', 'tech', 'top', 'it']
    uses_cheap_domain = 0
    for tld in top_cheap_domains:
        if tld in url:
            uses_cheap_domain = 1
            
    # domain in text
    if parsed_tree.find('body') is not None:
        domain_in_text = parsed_tree.find('body').text.count(u)
    else:
        domain_in_text = -1
        
    # append feature vector to dataset
    domain_name = '.'.join(u.split('.')[:-1])
    
    X.append([
        age, 
        guard, 
        total_social_medias[0], 
        total_social_medias[1], 
        total_social_medias[2], 
        num_external_links, 
        top_1m, 
        host_domain_same,
        len(script_tags),
        1 if '-' in url else 0,
        domain_name.count('.'),
        1 if has_digit else 0,
        is_cheap,
        uses_cheap_domain,
        domain_in_text,
        0,
        1 if u.split('.')[-1] not in ['com', 'net', 'org', 'uk', 'gov', 'au'] else 0,
        total_age,
        sm_info
    ])

    X[-1].extend(country_feature)
    X[-1].extend(host_country_feature)

    # count missing features
    missings = 0

    for i in X[-1]:
        if i == -1:
            missings += 1
    if country == -1:
        missings += 1
    if host_country == -1:
        missings += 1

    X[-1].append(missings)

    return X
