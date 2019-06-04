import os
import requests
import json
import csv
import datetime
import numpy as np
import pandas as pd
from collections import OrderedDict

import config


from instagram import WebAgentAccount, Media
import config
from instagram import Account, Media
import time
from tqdm import trange

EPS = 0.0001

URL = 'https://www.instagram.com/'

LIMIT = 500
TIMER = 60

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


def main():
    target_account_nick_name = 'g.r.u.p.p.i.r.o.v.k.a.2.0'
    target_followers_list_path = os.path.join('/home/serg/PycharmProjects/instaboost/', target_account_nick_name)
    save_file = os.path.join('/home/serg/PycharmProjects/instaboost/', target_account_nick_name + '_followed_stats_merged')
    black_file = os.path.join('/home/serg/PycharmProjects/instaboost/', target_account_nick_name + '_black_list')

    f = open(target_followers_list_path, "r")
    followers = f.read().split('\n')[:-1]

    if not os.path.exists(save_file):
        targets_frame = pd.DataFrame(columns=['name', 'id', 'followers', 'follow', 'posts', 'like'])
        targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False)
        followed_names = []
    else:
        already_followed = pd.read_csv(save_file)
        followed_names = already_followed['name']

    if not os.path.exists(black_file):
        targets_frame = pd.DataFrame(columns=['name'])
        targets_frame.to_csv(black_file, encoding='utf-8', mode='a', index=False)
        black_list = []
    else:
        black_list = pd.read_csv(black_file)
        black_list = black_list['name']

    t = datetime.datetime.now().hour
    agent = WebAgentAccount(config.username)
    agent.auth(config.password)
    sess = agent.session
    time.sleep(3)

    followers = list(set(followers) - set(followed_names) - set(black_list))
    length = len(followers)
    j = 0
    start_time = time.time()
    for i in range(length):
        print(i)
        if j >= length or j >= LIMIT:
            break
        target_follower_name = followers[i]
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
            prob = -0.19 * np.log10(count_followers + EPS) + 0.42 * np.log10(count_follow + EPS) - 0.18 * np.log10(count_post + EPS)
            if followed_by_me:
                user_id = user['id']
                targets_frame = pd.DataFrame([[target_follower_name, user_id, count_followers, count_follow, count_post, 1, t]])
                targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False, header=False)
                continue
            if not followed_by_me and not is_private and prob > 0.5:
                user_id = user['id']

                target_account = Account(target_follower_name)
                time.sleep(1)
                print('try to get media')
                med = None
                while med is None:
                    try:
                        med = agent.get_media(target_account)
                    except:
                        for s in trange(10):
                            time.sleep(1)
                        continue

                if med[0]:
                    post_time = datetime.datetime.fromtimestamp(med[0][0].date)
                    current_time = datetime.datetime.now()
                    dif = (current_time - post_time).days
                    if dif < 5:
                        j += 1
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
                        time_dif = start_time - time.time()
                        if time_dif < TIMER:
                            time.sleep(int(TIMER - time_dif))
                        print('try to follow')
                        fol = None
                        while fol is None:
                            try:
                                fol = agent.follow(target_account)
                            except:
                                for s in trange(10):
                                    time.sleep(1)
                                continue
                        # wr.writerow([target_follower_name, user_id, count_followers, count_follow, count_post, like, t])
                        targets_frame = pd.DataFrame([[target_follower_name, user_id, count_followers, count_follow, count_post, 1, t]])
                        targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False, header=False)
                        print(target_follower_name, '                                       ', CRED + str(j) + CEND)
                        start_time = time.time()
                    else:
                        print(target_follower_name, ' too old post = ', dif)
                        black_list_frame = pd.DataFrame([[target_follower_name]])
                        black_list_frame.to_csv(black_file, encoding='utf-8', mode='a', index=False, header=False)
                else:
                    print('no media')
                    black_list_frame = pd.DataFrame([[target_follower_name]])
                    black_list_frame.to_csv(black_file, encoding='utf-8', mode='a', index=False, header=False)


if __name__ == "__main__":
    main()
