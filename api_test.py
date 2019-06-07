from instagram import WebAgentAccount, Media
import config
from instagram import Account, Media


agent = WebAgentAccount(config.username)
agent.auth(config.password)

acc = Account(config.username)
agent.update(acc)
pass