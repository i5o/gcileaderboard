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


task_url = "https://codein.withgoogle.com/dashboard/task-instances/{task_id}"

app = Flask(__name__)

orgs = {
    'apertium': [5149586599444480, "Apertium"],
    'sugarlabs': [5340425418178560, "Sugar Labs"],
    'drupal': [4603782423904256, "Drupal"],
    'fossasia': [4625502878826496, "FOSSAsia"],
    'ubuntu': [4568116747042816, "Ubuntu"],
    'haiku': [6583394590785536, "Haiku"],
    'rtems': [5167877522980864, "RTEMS"],
    'kde': [6015066264567808, "KDE"]
}


@app.route('/')
def start_index():
    return render_template("2015.html")


@app.route('/org/<orgname>/')
def org_data(orgname):
    try:
        data = open("orgs/" + orgname + "_data.json", "r").read()
    except IOError:
        return "<h1>Data for org <i>'%s'</i> not found</h1>" % orgname
    tasks = json.loads(data)["results"]

    last_student_id = 0
    s_id = {}
    final_tasks = []
    student_tasks = []

    code = 0
    user_interface = 0
    doc = 0
    qa = 0
    outreach = 0
    beginner = 0

    for task in tasks:
        student_name = task["claimed_by"]["display_name"]
        student_id = task["claimed_by"]["id"]
        task_name = task["task_definition"]["name"]
        task_link = task_url.format(task_id=task["id"])
        org_id = task["organization_id"]

        if not org_id == orgs[orgname][0]:
            continue

        final_tasks.append(task)
        is_beginner = int(task["task_definition"]["is_beginner"] == True)

        cat = task["task_definition"]['categories']
        code += 1 in cat
        user_interface += 2 in cat
        doc += 3 in cat
        qa += 4 in cat
        outreach += 5 in cat
        beginner += is_beginner

        if student_id in s_id:
            student_id = s_id[student_id]
            student_tasks[student_id][0] += 1
            student_tasks[student_id][2].append([task_name, task_link, cat, is_beginner])
            student_tasks[student_id][3][0] += 1 in cat
            student_tasks[student_id][3][1] += 2 in cat
            student_tasks[student_id][3][2] += 3 in cat
            student_tasks[student_id][3][3] += 4 in cat
            student_tasks[student_id][3][4] += 5 in cat
        else:
            student_code = int(1 in cat)
            student_ui = int(2 in cat)
            student_doc = int(3 in cat)
            student_qa = int(4 in cat)
            student_out = int(5 in cat)
            s_id[student_id] = last_student_id
            student_tasks.append([1, student_name, [[task_name, task_link, cat, is_beginner]],
                                  [student_code, student_ui, student_doc, student_qa, student_out]])
            last_student_id += 1

    student_tasks = sorted(student_tasks, key=lambda x: x[0], reverse=True)

    for key in student_tasks:
        key = student_tasks.index(key)
        tasks_ = student_tasks[key][2]
        sorted_tasks = sorted(tasks_, key=lambda x: x[0], reverse=False)
        student_tasks[key][2] = sorted_tasks

    return render_template(
        'org.html',
        org_name=orgs[orgname][1],
        tasks_count=len(final_tasks),
        students=student_tasks,
        cat_count=[code, user_interface, doc, qa, outreach, beginner],
        year=2015)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
