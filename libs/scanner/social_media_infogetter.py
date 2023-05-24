import urllib3, requests, json
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
import time
from datetime import datetime
import re


class InfoGetter:
    def __init__(self):
        self.driver = self.create_driver()

        self.months = {
            'January': '01', 'February': '02', 'March': '03',
            'April': '04', 'May': '05', 'June': '06',
            'July': '07', 'August': '08', 'September': '09',
            'October': '10', 'November': '11', 'December': '12'
        }

    def create_driver(self):
        # return webdriver.Edge()
        return webdriver.Firefox()

    def close_driver(self):
        self.driver.close()

    def get_fb_info(self, url, sleep_time=2):
        # goto the url
        self.driver.get(url)
        time.sleep(sleep_time)
        
        # get page src
        pageSource = self.driver.find_element_by_xpath("//*").get_attribute("outerHTML")    

        if 'This page isn\'t available' in pageSource:
            return {
                'creation_date': -1,
                'likes': -1,
                'followers': -1
            }

        
        # get date
        try:
            ind = pageSource.lower().find('created - ') + 10
            year = pageSource.lower()[ind:ind+30].find(', 20') + 6
            creation_date = pageSource[ind:ind+year]

            raw_date = creation_date.split(' ')
            dt_str = raw_date[1][:-1] + '-' + self.months[raw_date[0]] + '-' + raw_date[2]
            creation_date = datetime.strptime(dt_str, '%d-%m-%Y')

            # get likes
            ind = pageSource.lower().find('people')
            start = pageSource.lower()[ind-15:ind].find('>') + 1
            end = pageSource.lower()[ind-15:ind].find(' ')
            likes = pageSource[ind - 15 + start:ind - 15 + end]
            if '<div>' in likes:
                likes = likes.replace('<div>', '')

            # get followers
            ind = pageSource.lower().find('people follow')
            start = pageSource.lower()[ind-15:ind].find('>') + 1
            end = pageSource.lower()[ind-15:ind].find(' ')
            followers = pageSource[ind - 15 + start:ind - 15 + end]
            if '<div>' in followers:
                followers = followers.replace('<div>', '')
        except:
            return {
                'creation_date': -1,
                'likes': -1,
                'followers': -1,
                'type': 'personal'
            }

        

        return {
            'creation_date': creation_date,
            'likes': likes,
            'followers': followers,
            'type': 'page'
        }

    def get_twitter_info(self, url, sleep_time=2):
        # goto the url
        self.driver.get(url)
        time.sleep(sleep_time)

        # get page src
        pageSource = self.driver.find_element_by_xpath("//*").get_attribute("outerHTML")    

        if 'This account doesn' in pageSource:
            return {
                'creation_date': -1,
                'followers': -1
            }
        
        # get creation date
        ind = pageSource.lower().find('joined ') + 7
        if ind == -1:
            return {
                'creation_date': -1,
                'likes': -1,
                'followers': -1
            }
        
        try:
            year = pageSource.lower()[ind:ind+30].find('20') + 4
            creation_date = pageSource[ind:ind+year]

            # process the date here
            raw_date = creation_date.split(' ')
            dt_str = '01' + '-' + self.months[raw_date[0]] + '-' + raw_date[1]
            creation_date = datetime.strptime(dt_str, '%d-%m-%Y')


            # get followers
            ind = pageSource.find('Followers')
            small_src = pageSource[ind-200:ind+20]
            start = re.search('>\d', small_src).start() + 1
            end = small_src[start:start + 20].find('<')
            followers = small_src[start:start + end]
        except:
            return {
                'creation_date': -1,
                'followers': -1,
                'type': 'sensitive'
            }

        return {
            'creation_date': creation_date,
            'followers': followers,
            'type': 'non-sensitive'
        }

    def get_instagram_info(self, url, sleep_time=5):
        # goto the url
        time.sleep(sleep_time)
        self.driver.get(url)

        # get page src
        pageSource = self.driver.find_element_by_xpath("//*").get_attribute("outerHTML")    

        # get creation date
        if 'this page isn\'t available' in pageSource.lower():
            return {
                'followers': -1
            }

        ind = pageSource.find(' followers')
        if ind == -1:
            return {
                'creation_date': -1,
                'likes': -1,
                'followers': -1
            }
        small_src = pageSource[ind-50:ind+20]
        start = re.search('>\d', small_src).start() + 1
        end = small_src[start:start + 20].find('<')
        followers = small_src[start:start + end]

        return {
            'followers': followers
        }

    def get_info(self, url):
        if 'twitter.com' in url:
            data = self.get_twitter_info(url)
        elif 'facebook.com' in url:
            data = self.get_fb_info(url)    
        elif 'instagram.com' in url:
            data = self.get_instagram_info(url)

        return data
# TEST
if __name__ == '__main__':
    # test the feature getter!
    fb_url = ''
    twitter_url = ''
    instagram_url = ''

    # open driver
    data_getter = InfoGetter()
    print('FACEBOOK TEST:', data_getter.get_info(fb_url))
    # print('TWITTER TEST:', data_getter.get_info(twitter_url))
    # print('INSTAGRAM:', data_getter.get_info(instagram_url))

    data_getter.close_driver()


