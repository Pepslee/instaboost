import os

from instagram import WebAgentAccount, Media
import config
from instagram import Account
import time
from tqdm import trange

import pandas as pd

# cookies = {'sessionid': '13503104221%3AQ5kmSUAFXvHBJB%3A11'}
agent = WebAgentAccount(config.username)
agent.auth(config.password)
time.sleep(2)

user_name = config.username
pages = [user_name]


mode = 'follows'


# pages = ['koreann_ua',
#          'pocket_bunny_ua',
#          'beautystore_cosmetics',
#          'your_korea_shop',
#          'beautyskin_ua',
#          'beauty.smart.ua',
#          '_just__enjoy_',
#          'glanc.ua',
#          'kiev_beauty_bar']
data_base_path = config.data_base_path

for page in pages:
    pointer = None
    stop = None

    followers = []
    while stop is None:
        try:
            if mode == 'followers':
                medias, pointer = agent.get_followers(Account(page), pointer)
            elif mode == 'follows':
                medias, pointer = agent.get_follows(Account(page), pointer)
            else:
                print('Error mode')
                exit(0)
            # time.sleep(3)
            followers += medias
            print(len(followers), pointer)
            for fol in medias:
                followers_df = pd.DataFrame([[fol]])
                followers_df.to_csv(os.path.join(data_base_path, user_name, page + '_' + mode), encoding='utf-8', mode='a', index=False, header=False)
            if pointer is None:
                stop = 1
        except:
            for i in trange(60):
                time.sleep(1)
            continue


