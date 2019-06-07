from instagram import WebAgentAccount, Media
import config
from instagram import Account
import time
from tqdm import trange

import pandas as pd
agent = WebAgentAccount(config.username)
agent.auth(config.password)
time.sleep(2)

pages = ['g.r.u.p.p.i.r.o.v.k.a']


# pages = ['koreann_ua',
#          'pocket_bunny_ua',
#          'beautystore_cosmetics',
#          'your_korea_shop',
#          'beautyskin_ua',
#          'beauty.smart.ua',
#          '_just__enjoy_',
#          'glanc.ua',
#          'kiev_beauty_bar']


for page in pages:
    pointer = None
    stop = None

    followers = []
    while stop is None:
        try:
            medias, pointer = agent.get_followers(Account(page), pointer)
            # time.sleep(3)
            followers += medias
            print(len(followers), pointer)
            for fol in medias:
                followers_df = pd.DataFrame([[fol]])
                followers_df.to_csv(page, encoding='utf-8', mode='a', index=False, header=False)
            if pointer is None:
                stop = 1
        except:
            for i in trange(60):
                time.sleep(1)
            continue


