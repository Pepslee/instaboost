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

# proxy = [{'http': '80.92.224.43:80'},
#          {'http': '94.244.191.219:3128'},
#          {'http': '94.131.198.60:8080'},
#          {'http': '91.205.218.32:80'},
#          {'http': '37.229.122.18:8080'},
#          {'http': '80.92.224.43:80	'},
#          {'https': '195.234.215.81:33932'},
#          {'https': '93.171.242.179:31717'},
#          {'https': '188.239.90.130:53281'},
#          {'https': '82.207.41.135:48608'},
#          {'https': '193.105.62.116:47477'},
#          {'https': '178.150.100.39:35216'},
#          {'https': '94.179.130.34:57201'},
#          {'https': '46.151.252.157:53281'},
#          {'https': '212.90.191.41:30928'},
#          {'https': '46.33.253.29:41261'},
#          {'https': '109.251.185.20:43620'},
#          {'https': '91.240.97.133:60771'},
#          ]

proxy = [{'https': '127.0.0.1:80'},
         {'https': '91.205.218.32:80'},
         {'https': '195.230.115.241:8080'},
         {'https': '87.244.181.136:8080'},
         {'https': '91.205.218.33:80'},
         {'https': '46.35.233.176:8080'},
         {'https': '80.92.224.43:80'},
         {'https': '195.138.93.34:3128'},
         {'https': '91.194.239.122:8080'},
         {'https': '213.5.194.226:9090'},
         ]


p_len = len(proxy)


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
    target_account_nick_name = 'g.r.u.p.p.i.r.o.v.k.a'
    target_followers_list_path = os.path.join('/home/serg/PycharmProjects/instaboost/p.i.n.k.m.a.n/', target_account_nick_name)
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
    # res = sess.get("https://www.instagram.com/accounts/login/",
    #                data={'username': config.username, 'password': config.password},
    #                allow_redirects=True)


    if 200 == 200:
        f = open(target_followers_list_path, "r")
        followers = f.read().split('\n')[:-1]

        # if not os.path.exists(save_file):
        #     targets_frame = pd.DataFrame(columns=['name', 'id', 'followers', 'follow', 'posts', 'like'])
        #     targets_frame.to_csv(save_file, encoding='utf-8', index=False)



        length = len(followers)
        j = 0
        pp = 0
        for i in trange(length):
            if j >= length or j >= LIMIT:
                break
            target_follower_name = followers[i]
            target_url = os.path.join(URL, target_follower_name, '?__a=1')
            res = None

            while res is None:
                settings = proxy[pp % p_len]
                try:
                    res = sess.get(target_url, proxies=settings, timeout=2)
                    if res.status_code == 429:
                        res = None
                        pp += 1
                        continue
                except:
                    pp += 1
                    continue
            if res.status_code == 200:
                target_dict = json.loads(res.content)
                user = target_dict['graphql']['user']
                j += 1
                user_id = user['id']
                is_private = user['is_private']
                count_followers = user['edge_followed_by']['count']
                count_follow = user['edge_follow']['count']
                count_post = user['edge_owner_to_timeline_media']['count']
                like = 0
                if not is_private:
                    if count_post > 0:
                        post_list = user['edge_owner_to_timeline_media']['edges']
                        if len(post_list) > 0:
                            post_data = post_list[0]['node']['taken_at_timestamp']
                            post_time = datetime.datetime.fromtimestamp(post_data)
                            current_time = datetime.datetime.now()
                            dif = (current_time - post_time).days
                            if dif < 5:
                                # wr.writerow([target_follower_name, user_id, count_followers, count_follow, count_post, like])
                                targets_frame = pd.DataFrame([[target_follower_name, user_id, count_followers, count_follow, count_post, like]])
                                targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False, header=False)


if __name__ == "__main__":
    main()
