import os
from tqdm import trange
import time

from instagram import WebAgentAccount, Account
import pandas as pd

import config


def login():
    user_name, pass_word, cookies = config.username, config.password, config.cookies

    agent = WebAgentAccount(user_name, cookies=cookies)
    if cookies is None:
        agent.auth(config.password)
    return agent


def main():
    count = 12
    target_account_nick_name = 'kosmetichka_com.ua'
    save_path = os.path.abspath(os.path.join(config.username, target_account_nick_name))

    agent = login()

    target_account = Account(target_account_nick_name)
    agent.update(target_account)
    print('Media count = ' + str(target_account.media_count))

    media_pointer = None
    media_stop = True
    media_counter = 0
    users = list()
    while media_stop:
        try:
            medias, media_pointer = agent.get_media(target_account, media_pointer, count=count, limit=count)
        except:
            for i in trange(60):
                time.sleep(1)
            continue
        if media_pointer is None:
            media_stop = False
        for media in medias:
            like_pointer = None
            like_stop = True
            while like_stop:
                try:
                    likes, like_pointer = agent.get_likes(media, like_pointer)
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
    followers_df = pd.DataFrame([list(set(users))])
    followers_df.to_csv(save_path, encoding='utf-8', mode='a', index=False, header=False)


if __name__ == "__main__":
    main()