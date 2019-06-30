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
from joblib import dump, load


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


def follow(agent, target_list, follows_limit, statistic_frame_path, black_list_path, followed_list_path, followed_list):
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
                        black_list_frame.to_csv(black_list_path, encoding='utf-8', mode='a', index=False, header=False)
                        continue
                else:
                    print('no media')
                    black_list_frame = pd.DataFrame([[target_follower_name]])
                    black_list_frame.to_csv(black_list_path, encoding='utf-8', mode='a', index=False, header=False)
                    continue
            else:
                print(' Private account')

            # unfollow
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

            # follow
            # print('try to follow')
            # time.sleep(int(TIMER))
            # fol = None
            # start_time_follow = time.time()
            # while fol is None:
            #     try:
            #         fol = agent.follow(target_account)
            #         print('pass folow')
            #     except:
            #         for s in trange(10):
            #             time.sleep(1)
            #         current_time_follow = time.time()
            #         time_dif = current_time_follow - start_time_follow
            #         if time_dif > 120:
            #             fol = 17
            #         else:
            #             continue
            # if fol == 17:
            #     continue

            # targets_frame = pd.DataFrame(
            #     [[target_follower_name, user_id, count_followers, count_follow, count_post, dif]])
            # targets_frame.to_csv(statistic_frame_path, encoding='utf-8', mode='a', index=False, header=False)
            print(target_follower_name, '                                       ', CRED + str(j) + CEND)

            # write follow name to file
            followed_list.append(target_follower_name)
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


def get_target_list(target_list_path, black_list_path, followed_list_path):

    try:
        target_list = list(pd.read_csv(target_list_path, header=None)[0])
    except EmptyDataError:
        raise Exception('Empty target list')

    try:
        black_list = list(pd.read_csv(black_list_path, header=None)[0])
    except EmptyDataError:
        black_list = list()

    try:
        followed_list = list(pd.read_csv(followed_list_path, header=None)[0])
    except EmptyDataError:
        followed_list = list()

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


def main():
    follows_limit = 500
    target_account_nick_name = 'kosmetichka_com.ua'
    user_name, pass_word, cookies = config.username, config.password, config.cookies

    statistic_frame_path = os.path.abspath(os.path.join(user_name, 'target_account_nick_name'))
    statistic_frame_path = None
    target_list_path = os.path.abspath(os.path.join(user_name, target_account_nick_name))
    black_list_path = os.path.abspath(os.path.join(user_name, 'black_list'))
    followed_list_path = os.path.abspath(os.path.join(user_name, user_name + '_follows'))

    if statistic_frame_path is None:
        target_list, followed_list = get_target_list(target_list_path, black_list_path, followed_list_path)
    else:
        stat_frame, target_list, followed_list = get_target_frame(statistic_frame_path, black_list_path, followed_list_path)

        model_path = None
        model = None
        if model_path is not None:
            model = load_model(model_path)
        target_list = targets_filter(stat_frame, target_list, model)

    agent = WebAgentAccount(user_name, cookies=cookies)
    if cookies is None:
        agent.auth(config.password)
    follow(agent, target_list, follows_limit, statistic_frame_path, black_list_path, followed_list_path, followed_list)


if __name__ == "__main__":
    main()
