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

import json

from flask import Flask
from flask import render_template
from flask import redirect


task_url = "https://codein.withgoogle.com/tasks/{task_id}/"

app = Flask(__name__)

orgs = {
    'apertium': "Apertium",
    'sugarlabs': "SugarLabs"
}


@app.route('/')
def start_index():
    return redirect('/org/sugarlabs')


@app.route('/org/<orgname>/')
def org_data(orgname):
    try:
        data = open(orgname + "_data.json", "r").read()
    except IOError:
        return "<h1>Data for org <i>'%s'</i> not found</h1>" % orgname
    tasks = json.loads(data)["results"]

    last_student_id = 0
    s_id = {}
    student_tasks = []

    for task in tasks:
        student_name = task["claimed_by"]["display_name"]
        task_name = task["task_definition"]["name"]
        task_link = task_url.format(task_id=task["task_definition_id"])

        if student_name in s_id:
            student_id = s_id[student_name]
            student_tasks[student_id][0] += 1
            student_tasks[student_id][2].append([task_name, task_link])
        else:
            s_id[student_name] = last_student_id
            student_tasks.append([1, student_name, [[task_name, task_link]]])
            last_student_id += 1

    student_tasks = sorted(student_tasks, key=lambda x: x[0], reverse=True)

    for key in student_tasks:
        key = student_tasks.index(key)
        tasks_ = student_tasks[key][2]
        sorted_tasks = sorted(tasks_, key=lambda x: x[0], reverse=False)
        student_tasks[key][2] = sorted_tasks

    return render_template(
        'org.html',
        org_name=orgs[orgname],
        tasks_count=len(tasks),
        students=student_tasks)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
