#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Ignacio Rodríguez <ignacio@sugarlabs.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import time
import data
import requests
from bs4 import BeautifulSoup


url = "https://codein.withgoogle.com/api/program/2015/taskinstance/?status=7&page_size=1000"
url_login = "https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https%3A%2F%2Fappengine.google.com%2F_ah%2Fconflogin%3Fcontinue%3Dhttps%3A%2F%2Fcodein.withgoogle.com%2F&ltmpl#identifier"
url_auth = "https://accounts.google.com/ServiceLoginAuth?service=ah&passive=true&continue=https%3A%2F%2Fappengine.google.com%2F_ah%2Fconflogin%3Fcontinue%3Dhttps%3A%2F%2Fcodein.withgoogle.com%2F&ltmpl#identifier"


class SessionGoogle:

    def __init__(self, url_login, url_auth, login, pwd):
        self.ses = requests.session()
        login_html = self.ses.get(url_login)
        soup_login = BeautifulSoup(
            login_html.content).find('form').find_all('input')
        dico = {}
        for u in soup_login:
            if u.has_attr('value'):
                dico[u['name']] = u['value']
        dico['Email'] = login
        dico['Passwd'] = pwd
        self.ses.post(url_auth, data=dico)

    def get(self, url):
        return self.ses.get(url)

session = SessionGoogle(url_login, url_auth, data.user, data.password)
while True:
    try:
        d = session.get(url)
        open(
            "sugarlabs_data.json",
            "w").write(
            u''.join(
                d.text).encode("utf-8"))
        print "Data updated, sleeping 3m"
        time.sleep(180)
    except:
        session = SessionGoogle(url_login, url_auth, data.user, data.password)
