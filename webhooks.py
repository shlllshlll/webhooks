# -*- coding: utf-8 -*-
# @Author: SHLLL
# @Email: shlll7347@gmail.com
# @Date:   2018-06-17 15:07:16
# @Last Modified by:   SHLLL
# @Last Modified time: 2018-06-20 01:59:54
# @License: MIT LICENSE

import json
import threading
import time
import web
from git import Repo


urls = (
    '/', 'index',
    '/blog', 'blog',
    '/keyvisual', 'keyvisual'
)

app = web.application(urls, globals())
application = app.wsgifunc()
render = web.template.render("templates/")

with open('config.json', 'r') as config_j:
    config = json.load(config_j)


def git_pull_in_thread(config, stat):
    stat['stat'] = 1
    repo = Repo(config['path'])
    repo.heads[config['branch']].checkout()
    if config['force']:
        git = repo.git
        git.fetch('--all')
        git.reset('--hard', 'origin/master')
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
    @classmethod
    def GET(cls):
        return render.index(cls.message, cls.thread_stat, cls.data)

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


class blog(WebhookBase):
    data = ''
    thread_stat = {'stat': 0, 'time': None}
    message = '博客系统Webhook服务器运行中'
    conf = config['blog']


class keyvisual(WebhookBase):
    data = ''
    thread_stat = {'stat': 0, 'time': None}
    message = '基于垂直搜索引擎的关联关键词可视化系统Webhook服务器运行中'
    conf = config['keyvisual']


if __name__ == "__main__":
    app.run()
