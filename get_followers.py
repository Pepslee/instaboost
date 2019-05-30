import instaloader
import config
# Get instance
L = instaloader.Instaloader()

# Login or load session
from getpass import getpass

L.login(config.username, config.password)        # (login)
# L.interactive_login(config.username)      # (ask password on terminal)
# L.load_session_from_file(config.username) # (load session created w/
                               #  `instaloader -l USERNAME`)

# Obtain profile metadata
page = 'g.r.u.p.p.i.r.o.v.k.a.0'
profile = instaloader.Profile.from_username(L.context, page)

with open(page, 'w') as file:

    for followee in profile.get_followers():
        file.write('%s\n' % followee.username)
