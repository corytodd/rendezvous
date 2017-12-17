#!/bin/python
from __future__ import print_function

import argparse
import json
import sys
import os
import shutil
import subprocess

from tools.hacking import piazza
from private import creds


def handle_iconify(src):
    command = ['convert', '-strip', '-resize', '3', src, '5']

    params = [
        ('16x16', 'icons/icon16.png'),
        ('19x19', 'icons/icon19.png'),
        ('30x30', 'icons/icon30.png'),
        ('48x48', 'icons/icon48.png'),
        ('128x128', 'icons/icon128.png'),
    ]

    if os.path.exists('icons'):
        shutil.rmtree('icons', ignore_errors=True)
    os.mkdir('icons')

    for p in params:
        command[3] = p[0]
        command[5] = p[1]
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        if len(result) > 0:
            print(result)

def handle_json_post():
    import requests, json
    with open(r'C:\temp\a.ir', 'r') as src:
        raw = src.f.read()
    resp = requests.post("http://***REMOVED***/api/v1/ir",
                      data= json.dumps({'content':raw}, indent=4),  # Need pretty print because ir requires newline
                      headers={'Content-Type': 'application/json'})
    if 'content' in resp.content:
        print(json.loads(resp.content)['content'])
    else:
        print("Invalid response")

class CS6460(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Do stuff with CS6460 package',
            usage='''cs6460 <command> [<args>]

            Commands are:
               user     get user info
               stats    get course post stats
            ''')
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command: {}'.format(parser.print_help()))
            exit(1)
        getattr(self, args.command)()

    def getuser(self):
        parser = argparse.ArgumentParser(
            description='Get user info')
        parser.add_argument('network', help='Network ID for target Piazza class')
        args = parser.parse_args(sys.argv[2:])
        pz = piazza.Piazza(args.network, creds.auth)
        profs = pz.get_user_profiles()
        print(profs)

    def stats(self):
        parser = argparse.ArgumentParser(
            description='Get course post stats')
        parser.add_argument('network', help='Network ID for target Piazza class')
        args = parser.parse_args(sys.argv[2:])
        pz = piazza.Piazza(args.network, creds.auth)
        print(pz.get_stats())

    def posts(self):
        parser = argparse.ArgumentParser(
            description='Get all posts visible to current user')
        parser.add_argument('network', help='Network ID for target Piazza class')
        args = parser.parse_args(sys.argv[2:])
        pz = piazza.Piazza(args.network, creds.auth)
        for i in pz.iter_all_posts():
            print(i)

    def post(self):
        parser = argparse.ArgumentParser(
            description='Get all posts visible to current user')
        parser.add_argument('network', help='Network ID for target Piazza class')
        parser.add_argument('cid', help='Piazza post ID (cid)')
        args = parser.parse_args(sys.argv[2:])
        pz = piazza.Piazza(args.network, creds.auth)
        post = pz.get_post(args.cid)
        print(json.dumps(post))

    def scrape(self):
        parser = argparse.ArgumentParser(
            description='Starting from post 1, capture each post until no more are found')
        parser.add_argument('network', help='Network ID for target Piazza class')
        parser.add_argument('out', help='Directory to write JSON')
        args = parser.parse_args(sys.argv[2:])
        pz = piazza.Piazza(args.network, creds.auth)
        post = pz.get_all(args.out)
        print(post)

    def explore(self):
        parser = argparse.ArgumentParser(
            description='Play with Piazza data')
        parser.add_argument('root', help='Directory containing JSON')
        args = parser.parse_args(sys.argv[2:])
        #feeder = scrapefeeder.ScrapeFeeder(args.root)
        # print(feeder.find_cid(688))
        # feeder.remap()
        handle_json_post()
        #feeder.populate_db()

    def iconify(self):
        parser = argparse.ArgumentParser(
            description='Generate Chrome extension icon set')
        parser.add_argument('src', help='Path to source image')
        args = parser.parse_args(sys.argv[2:])
        handle_iconify(args.src)

    def serve(self):
        parser = argparse.ArgumentParser(
            description='Start local development server')
        pz = piazza.Piazza()

    def play(self):
        parser = argparse.ArgumentParser(
            description='Play')
        nlp.run_quickstart()


if __name__ == '__main__':
    CS6460()
