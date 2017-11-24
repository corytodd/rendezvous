import json
import os
import time
import random

try:
    from types import SimpleNamespace as Namespace
except ImportError:
    # Python 2.x fallback
    pass #from types import SimpleNamespace

from piazza_api.piazza import Piazza as pz
from piazza_api.piazza import PiazzaRPC as rpc

class Piazza(object):
    def __init__(self, network, creds):
        self.nid = network
        self.creds = creds
        self.rpc = rpc(self.nid)
        self.rpc.user_login(self.creds['email'], self.creds['pwd'])
        self.course = pz(self.rpc)
        self.network = self.course.network(self.nid)

    def get_user_profile(self):
        prof = self.course.get_user_profile()
        return prof

    def get_user_profiles(self):
        users = self.rpc.get_all_users()
        profs = self.rpc.get_users(users)
        return profs

    def get_stats(self):
        data = self.rpc.get_stats(self.nid)
        return data

    def iter_all_posts(self):
        it = self.network.iter_all_posts(limit=10)
        return it

    def get_post(self, cid):
        p = self.network.get_post(cid)
        return p

    def get_all(self, out):
        it = self.network.iter_all_posts()
        c = 0

        if not os.path.exists(out):
            os.mkdir(out)

        for post in it:
            fname = os.path.join(out, 'cid_{}.json'.format(c))
            with open(fname, 'w') as d:
                json.dump(post, d, indent=4, sort_keys=True)
            c += 1
            time.sleep(2 + random.uniform(1.1, 5.1))