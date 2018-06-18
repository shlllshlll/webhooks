# -*- coding: utf-8 -*-
# @Author: SHLLL
# @Email: shlll7347@gmail.com
# @Date:   2018-06-17 15:07:16
# @Last Modified by:   SHLLL
# @Last Modified time: 2018-06-18 13:58:50
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
render = web.template.render("templates/")

with open('config.json', 'r') as config_j:
    config = json.load(config_j)


def git_pull_in_thread(repo_path, stat):
    stat['stat'] = 1
    repo = Repo(repo_path)
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
        git_thread = threading.Thread(target=git_pull_in_thread, args=(
            config['blog']['path'], blog.thread_stat,), name="BlogGitThread")
        git_thread.setDaemon(True)
        git_thread.start()
        return 'Done.'


if __name__ == "__main__":
    app.run()
