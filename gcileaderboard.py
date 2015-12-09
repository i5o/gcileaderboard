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

import data
import requests
import json
from bs4 import BeautifulSoup

from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import make_response

url = "https://codein.withgoogle.com/api/program/2015/taskinstance/?status=7"
task_url = "https://codein.withgoogle.com/tasks/{task_id}/"
url_login = "https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https%3A%2F%2Fappengine.google.com%2F_ah%2Fconflogin%3Fcontinue%3Dhttps%3A%2F%2Fcodein.withgoogle.com%2F&ltmpl#identifier"
url_auth = "https://accounts.google.com/ServiceLoginAuth?service=ah&passive=true&continue=https%3A%2F%2Fappengine.google.com%2F_ah%2Fconflogin%3Fcontinue%3Dhttps%3A%2F%2Fcodein.withgoogle.com%2F&ltmpl#identifier"
student_model = """<div class="panel panel-primary">
  <div class="panel-heading">{student_name} <span class="badge">{tasks}</span></div>
  <table class="table">
    {tasks_table}
  </table>
</div>"""


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

app = Flask(__name__)
session = SessionGoogle(url_login, url_auth, data.user, data.password)


@app.route('/')
def start_index():
    return redirect('/org/sugarlabs')


@app.route('/org/<orgname>/')
def org_data(orgname):
    html = """

    <style>
    .content {
    margin-top: 1%;
    margin-left: 2%;
    margin-right: 2%;
    }
    .badge {
        float: right;
    }
    </style>
        <link rel="stylesheet" type="text/css" href="/static/css/bootstrap.min.css"/>
        <link rel="stylesheet" type="text/css" href="/static/css/bootstrap-theme.min.css"/>

<div class="content">
        """

    header = """

    <h1>Sugar Labs<br>
    <h2> {tasks_count} tasks have been completed by {students_count} students.</h2><br></h1>
    """

    d = session.get(url)
    tasks = json.loads(d.text)["results"]

    students = {}
    tasks_by_student = {}
    tasks_names_by_student = {}
    total_tasks = 0

    for task in tasks:
        student_id = task["claimed_by"]["id"]
        students[student_id] = task["claimed_by"]["display_name"]
        task_name = task["task_definition"]["name"]
        task_link = task_url.format(task_id=task["task_definition_id"])

        if student_id in tasks_by_student:
            tasks_by_student[student_id] += 1
        else:
            tasks_by_student[student_id] = 1

        if student_id in tasks_names_by_student:
            tasks_names_by_student[student_id].append([task_name, task_link])
        else:
            tasks_names_by_student[student_id] = [[task_name, task_link]]

        total_tasks += 1

    html += header.format(tasks_count=total_tasks,
                          students_count=len(tasks_by_student.keys()))
    for student in students:
        prefix = "task"
        if tasks_by_student[student] > 1:
            prefix = "tasks"

        tasks_html = ""

        for task in tasks_names_by_student[student]:
            tasks_html += "\n<tr><td><a href='%s'>%s</a></td></tr>" % (task[
                                                                       1], task[0])

        student_html = student_model.format(
            student_name=students[student], tasks="%d %s" %
            (tasks_by_student[student], prefix), tasks_table=tasks_html)
        html += student_html
    return html


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
