import os
import requests
import json
import csv
import datetime
import numpy as np
import pandas as pd
from collections import OrderedDict

from pandas.errors import EmptyDataError

import config

from instagram import WebAgentAccount, Media
import config
from instagram import Account, Media
import time
from tqdm import trange

EPS = 0.0001

URL = 'https://www.instagram.com/'

LIMIT = 5000
TIMER = 80

CRED = '\033[91m'
CEND = '\033[0m'


def media_id_to_code(media_id):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    short_code = ''
    while media_id > 0:
        remainder = media_id % 64
        media_id = (media_id-remainder)/64
        short_code = alphabet[remainder] + short_code
    return short_code


def get_media_id(media_url):
    url = 'https://api.instagram.com/oembed/?callback=&url=' + media_url
    response = requests.get(url).json()
    return response['media_id']


def unfollow(agent, followed_list_path, followed_list):
    j = 0
    try:
        while len(followed_list) > 0:

            # unfollow
            print(j)
            print('try to unfollow')
            time.sleep(int(TIMER))
            unfol = None
            start_time_follow = time.time()
            unfollow_account = Account(followed_list[0])
            while unfol is None:
                try:
                    unfol = agent.unfollow(unfollow_account)
                    followed_list.remove(followed_list[0])
                except:
                    for s in trange(10):
                        time.sleep(1)
                    current_time_follow = time.time()
                    time_dif = current_time_follow - start_time_follow
                    if time_dif > 120:
                        unfol = 17
                    else:
                        continue
            if unfol == 17:
                continue

            j += 1

    except KeyboardInterrupt:
        print('Saving already followed users')
        mode = 'w'
        for followed in followed_list:
            followed_frame = pd.DataFrame([[followed]])
            followed_frame.to_csv(followed_list_path, encoding='utf-8', mode=mode, index=False, header=False)
            mode = 'a'

    mode = 'w'
    for followed in followed_list:
        followed_frame = pd.DataFrame([[followed]])
        followed_frame.to_csv(followed_list_path, encoding='utf-8', mode=mode, index=False, header=False)
        mode = 'a'


def get_followed_list(followed_list_path):

    try:
        followed_list = list(pd.read_csv(followed_list_path, header=None)[0])
    except EmptyDataError:
        followed_list = list()

    return followed_list


def get_target_frame(statistic_frame_path, black_list_path, followed_list_path):

    try:
        stat_frame = pd.read_csv(statistic_frame_path, header=None)
    except EmptyDataError:
        raise Exception('Empty target frame')

    try:
        black_list = list(pd.read_csv(black_list_path, header=None)[0])
    except EmptyDataError:
        black_list = list()

    try:
        followed_list = list(pd.read_csv(followed_list_path, header=None)[0])
    except EmptyDataError:
        followed_list = list()

    target_list = stat_frame['name']
    target_list = list(set(target_list) - set(followed_list) - set(black_list))

    mask = stat_frame['name'].isin(target_list)
    stat_frame = stat_frame[mask].copy()
    return stat_frame, target_list, followed_list


def load_model(path):
    return path


def targets_filter(statistic_frame, target_list, model):
    return target_list


def main():
    data_base_path = config.data_base_path
    user_name, pass_word, cookies = config.username, config.password, config.cookies
    followed_list_path = os.path.abspath(os.path.join(data_base_path, user_name, user_name + '_follows'))

    followed_list = get_followed_list(followed_list_path)

    agent = WebAgentAccount(user_name, cookies=cookies)
    if cookies is None:
        agent.auth(config.password)
    unfollow(agent, followed_list)


if __name__ == "__main__":
    main()
