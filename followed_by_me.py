from instagram import WebAgentAccount, Media
import config
from instagram import Account
import time
from tqdm import trange

agent = WebAgentAccount(config.username)
agent.auth(config.password)

pages = ['p.i.n.k.m.a.n']


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
            # medias, pointer = agent.get_followers(Account(page), pointer)
            medias, pointer = agent.get_follows(Account(page), pointer)
            # time.sleep(3)
            followers += medias
            print(len(followers), pointer)
            if pointer is None:
                stop = 1
        except:
            for i in trange(60):
                time.sleep(1)
            continue

    with open(page, 'w') as file:
        for follower in followers:
            file.write('%s\n' % follower)
