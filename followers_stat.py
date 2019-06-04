import os
import requests
import json
import csv
import datetime
import pandas as pd
import time


import config
from tqdm import trange


URL = 'https://www.instagram.com/'

LIMIT = 50000000


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
    target_followers_list_path = os.path.join('/home/serg/PycharmProjects/instaboost/pinkman/', target_account_nick_name)
    day = datetime.datetime.now().day
    month = datetime.datetime.now().month
    save_file = os.path.join('/home/serg/PycharmProjects/instaboost/', target_account_nick_name + '_stats_' + str(month) + '_' + str(day))

    if not os.path.exists(save_file):
        targets_frame = pd.DataFrame([['name', 'id', 'followers', 'follow', 'posts', 'like']])
        targets_frame.to_csv(save_file, encoding='utf-8', mode='w', index=False, header=False)
        followed_names = []
    else:
        already_followed = pd.read_csv(save_file)
        followed_names = list(already_followed['name'])

    sess = requests.Session()
    res = sess.get("https://www.instagram.com/accounts/login/",
                   data={'username': config.username, 'password': config.password},
                   allow_redirects=True)


    if res.status_code == 200:
        f = open(target_followers_list_path, "r")
        followers = f.read().split('\n')[:-1]

        # if not os.path.exists(save_file):
        #     targets_frame = pd.DataFrame(columns=['name', 'id', 'followers', 'follow', 'posts', 'like'])
        #     targets_frame.to_csv(save_file, encoding='utf-8', index=False)



        length = len(followers)
        j = 0
        for i in trange(length):
            if j >= length or j >= LIMIT:
                break
            target_follower_name = followers[i]
            if target_follower_name not in followed_names:

                target_url = os.path.join(URL, target_follower_name, '?__a=1')
                res = None
                while res is None:
                    try:
                        res = sess.get(target_url)
                        if res.status_code == 429:
                            res = None
                            for s in trange(10):
                                time.sleep(1)
                            continue
                    except:
                        for s in trange(10):
                            time.sleep(1)
                        continue
                if res.status_code == 200:
                    target_dict = json.loads(res.content)
                    user = target_dict['graphql']['user']
                    j += 1
                    user_id = user['id']
                    count_followers = user['edge_followed_by']['count']
                    count_follow = user['edge_follow']['count']
                    count_post = user['edge_owner_to_timeline_media']['count']
                    like = 0
                    # wr.writerow([target_follower_name, user_id, count_followers, count_follow, count_post, like])
                    targets_frame = pd.DataFrame([[target_follower_name, user_id, count_followers, count_follow, count_post, like]])
                    targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False, header=False)


if __name__ == "__main__":
    main()
