# -*- coding: utf-8 -*-
# @Author: SHLLL
# @Email: shlll7347@gmail.com
# @Date:   2018-06-17 15:07:16
# @Last Modified by:   SHLLL
# @Last Modified time: 2018-06-19 11:45:32
# @License: MIT LICENSE

import json
import threading
import time
import web
from git import Repo


urls = (
    '/', 'index',
    '/blog', 'blog'
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


class blog(object):
    data = ''
    thread_stat = {'stat': 0, 'time': None}

    def GET(self):
        return render.index('博客系统Webhook服务器运行中', self.thread_stat, self.data)

    def POST(self):
        blog.data = web.data().decode()
        data_dict = json.loads(blog.data)
        if data_dict['ref'] == config['blog']['ref']:
            git_thread = threading.Thread(
                target=git_pull_in_thread,
                args=(config['blog'], blog.thread_stat,),
                name="BlogGitThread")
            git_thread.setDaemon(True)
            git_thread.start()
        return 'Done.'


if __name__ == "__main__":
    app.run()
