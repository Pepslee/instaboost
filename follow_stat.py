import os
import requests
import json
import csv
import pandas as pd
from collections import OrderedDict

import config
from insta_boost import InstaBoost


from instagram import WebAgentAccount, Media
import config
from instagram import Account, Media
import time
from tqdm import trange


URL = 'https://www.instagram.com/'

LIMIT = 50
TIMER = 5


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
    data_base_path = config.data_base_path
    path = os.path.join(data_base_path, 'p.i.n.k.m.a.n/g.r.u.p.p.i.r.o.v.k.a.2.0_active_filtered')
    save_file = os.path.join(data_base_path, 'p.i.n.k.m.a.n/g.r.u.p.p.i.r.o.v.k.a.2.0_active_filtered_stats')
    followers = pd.read_csv(path, header=None)

    agent = WebAgentAccount(config.username)
    agent.auth(config.password)
    sess = agent.session
    time.sleep(TIMER)

    if not os.path.exists(save_file):
        targets_frame = pd.DataFrame(columns=['name', 'id', 'followers', 'follow', 'posts', 'like'])
        targets_frame.to_csv(save_file, encoding='utf-8', index=False)

    length = len(followers)
    j = 0
    for i in range(length):
        print(i)
        if j >= length or j >= LIMIT:
            break
        target_follower_name = followers[i]
        target_url = os.path.join(URL, target_follower_name, '?__a=1')
        try:
            res = sess.get(target_url)
            if res.status_code == 200:
                target_dict = json.loads(res.content)
                user = target_dict['graphql']['user']
                followed_by_me = user['followed_by_viewer']
                if not followed_by_me:
                    j += 1
                    user_id = user['id']
                    count_followers = user['edge_followed_by']['count']
                    count_follow = user['edge_follow']['count']
                    count_post = user['edge_owner_to_timeline_media']['count']
                    like = 0
                    target_account = Account(target_follower_name)
                    print('Try to follow')
                    agent.follow(target_account)
                    time.sleep(TIMER)
                    print('try to get media')
                    med = agent.get_media(target_account)
                    time.sleep(TIMER)
                    if med[0]:
                        print('try to like')
                        agent.like(med[0][0])
                        like = 1
                        time.sleep(TIMER)
                    targets_frame = pd.DataFrame(pd.Series([target_follower_name, user_id, count_followers, count_follow, count_post, like], index=['name', 'id', 'followers', 'follow', 'posts', 'like']), ignore_index=True)
                    targets_frame.to_csv(save_file, encoding='utf-8', mode='a', index=False)
                    print(target_follower_name)
                    time.sleep(TIMER)
        except:
            for i in trange(60):
                time.sleep(1)
            continue




if __name__ == "__main__":
    main()
