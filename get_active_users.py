import os
from tqdm import trange
import time
import requests

from instagram import WebAgentAccount, Account
import pandas as pd


import config


def login(account):
    user_name = account['username']
    pass_word = account['password']
    cookies = account.get('cookies')

    agent = WebAgentAccount(user_name, cookies=cookies)
    if cookies is None:
        agent.auth(pass_word)
        account['cookies'] = agent.session.cookies.get_dict()['sessionid']
    return agent


def ping_proxies(accounts):
    status = []
    for account in accounts:
        proxy = account['settings']['proxies']
        try:
            _ = requests.get(url='http://www.instagram.com/', timeout=5, proxies=proxy)
            status.append(True)
        except requests.ConnectionError:
            print("proxy " + str(proxy) + ' have no connection')
            status.append(False)
    if all(status):
        return True
    else:
        exit(0)


def main():
    count = 12
    target_account_nick_name = 'g.r.u.p.p.i.r.o.v.k.a.2.0'
    accounts_origin = config.accounts
    accounts = iter(accounts_origin)
    ping_proxies(accounts_origin)
    data_base_path = config.data_base_path
    save_path = os.path.abspath(os.path.join(data_base_path, config.username, target_account_nick_name + '_active'))

    account = next(accounts)
    agent = login(account)

    target_account = Account(target_account_nick_name)
    agent.update(target_account, account['settings'])
    time.sleep(1)
    print('Media count = ' + str(target_account.media_count))

    media_pointer = None
    media_stop = True
    media_counter = 0
    users = list()
    second_round_proxy = False
    while media_stop:
        try:
            medias, media_pointer = agent.get_media(target_account, media_pointer, count=count, limit=count, settings=account['settings'])
        except:
            if second_round_proxy:
                for i in trange(60):
                    time.sleep(1)
                second_round_proxy = False
            try:
                account = next(accounts)
            except StopIteration:
                accounts = iter(accounts_origin)
                second_round_proxy = True

            agent = login(account)

        if media_pointer is None:
            media_stop = False
        for media in medias:
            like_pointer = None
            like_stop = True
            while like_stop:
                try:
                    likes, like_pointer = agent.get_likes(media, like_pointer, settings=account['settings'])
                except:
                    for i in trange(60):
                        time.sleep(1)
                    continue
                if like_pointer is None:
                    like_stop = False
                for like in likes:
                    users.append(like.username)
            media_counter += 1
            print(media_counter, ' from ', target_account.media_count)
    followers_df = pd.DataFrame(pd.Series(users))
    followers_df.to_csv(save_path, encoding='utf-8', mode='a', index=False, header=False)


if __name__ == "__main__":
    main()
