# -*- coding: utf-8 -*-
# @Author: SHLLL
# @Email: shlll7347@gmail.com
# @Date:   2018-06-17 15:07:16
# @Last Modified by:   Mr.Shi
# @Last Modified time: 2019-09-08 02:15:48
# @License: MIT LICENSE

import json
import threading
import time
import web
from git import Repo


urls = [
    '/', 'index'
]

with open('config.json', 'r') as config_j:
    config = json.load(config_j)


def git_pull_in_thread(config, stat):
    stat['stat'] = 1

    if config['test_mode']:
        print('Start to fetch git.')
    else:
        repo = Repo(config['path'])
        repo.heads[config['branch']].checkout()

        if config['force']:
            git = repo.git
            git.fetch('--all')
            git.reset('--hard', config["remote"])
            git.pull()
        else:
            origin = repo.remote()
            origin.pull()
    stat['time'] = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    stat['stat'] = 2


class index(object):
    def GET(self):
        return render.index('', '', '')


class WebhookBase(object):
    data = ''
    thread_stat = {'stat': 0, 'time': None}

    @classmethod
    def GET(cls):
        return render.index(cls.conf['message'], cls.thread_stat, cls.data)

    @classmethod
    def POST(cls):
        cls.data = web.data().decode()
        data_dict = json.loads(cls.data)
        if data_dict['ref'] == cls.conf['ref']:
            git_thread = threading.Thread(
                target=git_pull_in_thread,
                args=(cls.conf, cls.thread_stat,),
                name="BlogGitThread")
            git_thread.setDaemon(True)
            git_thread.start()
        return 'Done.'


for key in config.keys():
    urls.extend([f'/{key}', key])
    locals()[key] = type(key, (WebhookBase,), {'conf': config[key]})

app = web.application(urls, globals())
application = app.wsgifunc()
render = web.template.render("templates/")

if __name__ == "__main__":
    app.run()
