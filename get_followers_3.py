import InstagramAPI
from InstagramAPI import Checkpoint
import config

i = InstagramAPI.Instagram(config.username, config.password)
i.setUser(config.username, config.password)


page = 'aa_panchenko'
id = i.getUsernameId(page)
inf = i.getUsernameInfo(id)
print(inf)