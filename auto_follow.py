import os
import requests
import json
import csv
import datetime
import numpy as np
import pandas as pd
from collections import OrderedDict

import config
from joblib import dump, load


from instagram import WebAgentAccount, Media
import config
from instagram import Account, Media
import time
from tqdm import trange

EPS = 0.0001

URL = 'https://www.instagram.com/'

LIMIT = 1000
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
    # load sklearn model
    model_path = 'p.i.n.k.m.a.n/filename_2.joblib'
    model = load(model_path)

    target_account_nick_name = 'g.r.u.p.p.i.r.o.v.k.a.2.0'
    target_followers_list_path = os.path.join(os.path.join('/home/serg/PycharmProjects/instaboost/', config.username), target_account_nick_name)
    save_file = os.path.join('/home/serg/PycharmProjects/instaboost/', config.username, 'followed_stats')
    black_file = os.path.join('/home/serg/PycharmProjects/instaboost/', config.username, 'black_list')

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
    cookies = config.cookies
    agent = WebAgentAccount(config.username, cookies=cookies)
    # agent.auth(config.password)
    sess = agent.session
    time.sleep(3)

    followers = list(set(followers) - set(followed_names) - set(black_list))

    stats_path = 'g.r.u.p.p.i.r.o.v.k.a.2.0_stats_6_2'
    stat_df = pd.read_csv(stats_path)
    mask = stat_df['name'].isin(followers)
    stat_df = stat_df[mask].copy()
    stat_df['fb_factor'] = stat_df['follow'] / (stat_df['followers'] + 1)
    feature_names = ['id', 'followers', 'follow', 'fb_factor', 'posts']
    target_names = stat_df['name']
    X = stat_df[feature_names]

    p = -0.19 * np.log10(X[['followers']].values + EPS) + 0.42 * np.log10(X[['follow']].values + EPS) - 0.18 * np.log10(X[['posts']].values + EPS)

    ind = (p[:, 0] > 0.4) * (X[['posts']].values[:, 0] > 2)
    # ind = model.predict_proba(X[['id', 'followers', 'follow', 'fb_factor', 'posts']].values)[:, 1] > 0.5

    followers = target_names[ind].values









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
            user_id = user['id']
        else:
            continue
        # prob = -0.19 * np.log10(count_followers + EPS) + 0.42 * np.log10(count_follow + EPS) - 0.18 * np.log10(count_post + EPS)
        # ['id', 'followers', 'follow', 'fb_factor', 'posts']
        # prob = model.predict_proba(np.array([user['id'], count_followers, count_follow, count_follow/float(count_followers+1), count_post]).reshape(1, -1))[0][1]
        # prob1 = -0.19 * np.log10(count_followers + EPS) + 0.42 * np.log10(count_follow + EPS) - 0.18 * np.log10(count_post + EPS)
        # if followed_by_me:
        #     user_id = user['id']
        #     targets_frame = pd.DataFrame([[target_follower_name, user_id, count_followers, count_follow, count_post, 1, t]])
        #     targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False, header=False)
        #     continue
        # if not followed_by_me and not is_private and prob > 0.5:


        target_account = Account(target_follower_name)

        if followed_by_me:
            targets_frame = pd.DataFrame(
                [[target_follower_name, user_id, count_followers, count_follow, count_post, 'None', t]])
            targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False, header=False)
            continue


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
                    continue
            if med == 17:
                continue



            if med[0]:
                time.sleep(TIMER)
                post_time = datetime.datetime.fromtimestamp(med[0][0].date)
                current_time = datetime.datetime.now()
                dif = (current_time - post_time).days
                if dif < 500:
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
                    # time_dif = start_time - time.time()

                else:
                    print(target_follower_name, ' too old post = ', dif)
                    black_list_frame = pd.DataFrame([[target_follower_name]])
                    black_list_frame.to_csv(black_file, encoding='utf-8', mode='a', index=False, header=False)
                    continue
            else:
                print('no media')
                black_list_frame = pd.DataFrame([[target_follower_name]])
                black_list_frame.to_csv(black_file, encoding='utf-8', mode='a', index=False, header=False)
                continue
        else:
            print(' Private account')

        print('try to follow')
        time.sleep(int(TIMER))
        fol = None
        start_time_follow = time.time()
        while fol is None:
            try:
                fol = agent.follow(target_account)
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
        # wr.writerow([target_follower_name, user_id, count_followers, count_follow, count_post, like, t])
        targets_frame = pd.DataFrame(
            [[target_follower_name, user_id, count_followers, count_follow, count_post, dif, t]])
        targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False, header=False)
        print(target_follower_name, '                                       ', CRED + str(j) + CEND)


if __name__ == "__main__":
    main()
