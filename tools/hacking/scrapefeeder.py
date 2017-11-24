import json
import os
import sqlite3
import datetime
from collections import defaultdict
from pathlib import Path
from bs4 import BeautifulSoup


class Post(object):

    PIAZZA_TABLE = "piazza_posts"
    COL_ID = "post_id"
    COL_UUID = "user_id"
    COL_TIMESTAMP = "timestamp"
    COL_CONTENT = "content"
    COL_CONTENT_LEN = "content_len"
    COL_CID = "cid"
    COL_IS_OP = "is_op"

    def __init__(self, cid, uuid, datestr, content, is_child):
        self.uuid = uuid
        self.timestamp = Post.__make_dt(datestr)
        self.content = Post.__extract_text(content)
        self.content_len = len(content)
        self.cid = cid
        self.is_op = is_child

    def __is_valid(self):
        if self.uuid is None or self.timestamp is None or self.content is None or self.cid is None:
            return False
        if type(self.uuid) is not str:
            return False
        if type(self.content) is not str:
            return False
        if type(self.content_len) is not int:
            return False

        return True

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "cid:{},child:{},timestamp:{},uuid:{},len({})".format(
            self.cid, self.is_op, self.timestamp, self.uuid, self.content_len)

    @staticmethod
    def __make_dt(datestr):
        datestr = str(datestr).replace(' ','')
        astime = datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
        return astime.timestamp()

    @staticmethod
    def __extract_text(data):
        soup = BeautifulSoup(data, 'html.parser')
        return soup.get_text()

class ScrapeFeeder(object):

    def __init__(self, root):
        self.conn = sqlite3.connect('cs6460.db')
        self.root = root
        self.all_data = []

        if not os.path.exists(root):
            raise Exception("{} does not exist. It must contain JSON data".format(self.root))

        files = [str(x) for x in Path(self.root).glob('**/*.json')]
        for f in files:
            with open(f, 'r') as s:
                self.all_data.append(json.load(s))

    def populate_db(self):

        # Batch everything up
        posts = []
        for obj in self.all_data:
            cid = obj['nr']

            # OP is the 1st item in the history list
            op = obj['history']
            if len(op) == 0:
                print("Zero length OP: {}".format(cid))
                continue
            post = op[0]

            if not 'uid' in post:
                print("Coward anon: {}".format(cid))
                uuid = 'anon'
            else:
                uuid = post['uid']

            datestr = post['created']
            content = post['content']

            # We have enough for an object
            posts.append(Post(cid, uuid, datestr, content, False))

            def get_children(obj, bucket):

                if not 'children' in obj:
                    print("Abandoned post: {}".format(cid))
                    return

                for child in obj['children']:
                    if not 'uid' in child:
                        print("Coward anon child: {}".format(cid))
                        uuid = 'anon'
                    else:
                        uuid = child['uid']

                    if not 'subject' in child:
                        continue

                    datestr = child['created']
                    content = child['subject']
                    posts.append(Post(cid, uuid, datestr, content, True))

                    get_children(child, bucket)

            get_children(obj, posts)

        posts.sort(key=lambda x: x.cid, reverse=False)
        groups = defaultdict(list)

        for obj in posts:
            groups[obj.cid].append(obj)

        new_list = groups.values()
        for p in new_list:
            print("CID {}, responses {}".format(p[0].cid, len(p)))

        c = self.conn.cursor()
        for p in posts:
            c.execute("INSERT INTO piazza_posts(user_id, timestamp, content, content_len, cid, is_op) VALUES(?, ?, ?, ?, ?, ?)",
                      (p.uuid, p.timestamp, p.content, p.content_len, p.cid, p.is_op) )
        self.conn.commit()

        print("Total posts: {}".format(len(posts)))

    def remap(self):
        '''Remap source files to properly names CID files'''
        files = [str(x) for x in Path(self.root).glob('**/*.json')]

        if not os.path.exists('cid'):
            os.mkdir('cid')

        for f in files:
            with open(f, 'r') as s:
                obj = json.load(s)
                if 'nr' not in obj:
                    print("Weird, missing CID: {}".format(f))
                    continue
                newout = os.path.join('cid', '{}.json'.format(obj['nr']))
                with open(newout, 'w') as d:
                    json.dump(obj, d)

    def find_cid(self, cid):
        for obj in self.all_data:
            if 'nr' in obj and obj['nr'] == cid:
                return obj
        return None

