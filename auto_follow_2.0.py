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


def follow(agent, target_list, follows_limit):
    sess = agent.session
    j = 0

    try:
        for target_follower_name in target_list:
            print(target_follower_name)
            if j >= follows_limit:
                break
            target_url = os.path.join(URL, target_follower_name, '?__a=1')
            res = None
            while res is None:
                try:
                    res = sess.get(target_url)
                except:
                    for s in trange(10):
                        time.sleep(1)
                    continue
            if res.status_code == 200 and res.text != '{}':
                target_dict = json.loads(res.content)
                user = target_dict['graphql']['user']
                followed_by_me = user['followed_by_viewer']
                is_private = user['is_private']
                count_followers = user['edge_followed_by']['count']
                count_follow = user['edge_follow']['count']
                count_post = user['edge_owner_to_timeline_media']['count']
                user_id = user['id']
            else:
                print('Something is wrong with ' + target_follower_name)
                continue

            target_account = Account(target_follower_name)

            dif = 0
            if not is_private:

                print('try to get media')
                med = None
                time.sleep(TIMER)
                start_time = time.time()
                while med is None:
                    try:
                        med = agent.get_media(target_account)

                    except:
                        for s in trange(10):
                            time.sleep(1)
                        current_time = time.time()
                        if current_time - start_time > 60:
                            med = 17
                            print('                         17')
                        continue
                if med == 17:
                    continue

                if med[0]:
                    time.sleep(TIMER)
                    post_time = datetime.datetime.fromtimestamp(med[0][0].date)
                    current_time = datetime.datetime.now()
                    dif = (current_time - post_time).days
                    if dif < 500:
                        print('try to like')
                        time.sleep(1)
                        lik = None
                        while lik is None:
                            try:
                                lik = agent.like(med[0][0])
                            except:
                                for s in trange(10):
                                    time.sleep(1)
                                continue
                        # time_dif = start_time - time.time()

                    else:
                        print(target_follower_name, ' too old post = ', dif)
                        black_list_frame = pd.DataFrame([[target_follower_name]])
                        continue
                else:
                    print('no media')
                    black_list_frame = pd.DataFrame([[target_follower_name]])
                    continue
            else:
                print(' Private account')



            follow
            print('try to follow')
            time.sleep(int(TIMER))
            fol = None
            start_time_follow = time.time()
            while fol is None:
                try:
                    fol = agent.follow(target_account)
                    print('pass folow')
                except:
                    for s in trange(10):
                        time.sleep(1)
                    current_time_follow = time.time()
                    time_dif = current_time_follow - start_time_follow
                    if time_dif > 120:
                        fol = 17
                    else:
                        continue
            if fol == 17:
                continue

            # targets_frame = pd.DataFrame(
            #     [[target_follower_name, user_id, count_followers, count_follow, count_post, dif]])
            # targets_frame.to_csv(statistic_frame_path, encoding='utf-8', mode='a', index=False, header=False)
            print(target_follower_name, '                                       ', CRED + str(j) + CEND)

            # write follow name to file
            j += 1

    except KeyboardInterrupt:
        print('Saving already followed users')


def get_target_list(target_list_path, black_list_path, followed_list_path):

    try:
        target_list = list(pd.read_csv(target_list_path, header=None)[0])
    except EmptyDataError:
        raise Exception('Empty target list')

    try:
        black_list = list(pd.read_csv(black_list_path, header=None)[0])
    except EmptyDataError:
        black_list = list()
    except FileNotFoundError:
        black_list = list()

    try:
        followed_list = list(pd.read_csv(followed_list_path, header=None)[0])
    except EmptyDataError:
        followed_list = list()
    except FileNotFoundError:
        black_list = list()

    target_list = list(set(target_list) - set(followed_list) - set(black_list))
    return target_list, followed_list


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


def target_filter(X):
    p = -0.19 * np.log10(X[['followers']].values + EPS) + 0.42 * np.log10(X[['follows']].values + EPS) - 0.18 * np.log10(X[['posts']].values + EPS)

    ind = (p[:, 0] > 0.4) * (X[['posts']].values[:, 0] > 2)
    return list(X['name'][ind])


def main():
    follows_limit = 500
    data_base_path = config.data_base_path
    user_name, pass_word, cookies = config.username, config.password, config.cookies
    path = os.path.join(data_base_path, 'p.i.n.k.m.a.n/g.r.u.p.p.i.r.o.v.k.a.2.0_active_filtered_stats')
    dataframe = pd.read_csv(path)

    target_list = target_filter(dataframe)

    agent = WebAgentAccount(user_name, cookies=cookies)
    if cookies is None:
        agent.auth(config.password)
    follow(agent, target_list, follows_limit)


if __name__ == "__main__":
    main()
