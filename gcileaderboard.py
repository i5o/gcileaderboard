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
import time
import os.path
from flask import request
from flask import Flask
from flask import render_template
from flask import redirect

from utils_old import *

GCI = GCIUtils()

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


@app.route("/")
def test():
    return render_template("/index.html")


@app.route('/<year>/')
@app.route('/<year>')
def start_index(year):
    if year not in ['2010', '2011', '2012', '2013', '2014', '2015', '2016']:
        return redirect("/")

    return render_template("/%s.html" % year)


@app.route('/<year>/org/<orgname>/')
def org_year_data(year, orgname):
    if year not in ['2010', '2011', '2012', '2013', '2014']:
        return render_template("/index.html")

    org_title = GCI.get_org_name(int(year), orgname)
    tags = GCI.get_tasks_count(int(year), orgname)
    tasks = GCI.get_tasks(int(year), orgname)

    model_tags = [
        tags['Code'],
        tags['User Interface'],
        tags['Documentation/Training'],
        tags['Quality Assurance'],
        tags['Outreach/Research']
    ]

    student_total_tasks = []
    pos = -1
    last_student = None

    for student in tasks['userTasks']:
        student_name = student[0]

        if last_student != student_name:
            last_student = student_name
            student_total_tasks.append([0, student_name, []])
            pos += 1

        student = GCI.get_student_tasks(student_name, int(year), orgname)
        student_tasks = student['tasks']

        for task in student_tasks:
            task = student_tasks[task]
            task_name = task['title']
            task_link = task['link']

            student_total_tasks[pos][0] += 1
            student_total_tasks[pos][2].append(
                [task_name, task_link])

    student_total_tasks = sorted(
        student_total_tasks,
        key=lambda x: x[0],
        reverse=True)
    for key in student_total_tasks:
        key = student_total_tasks.index(key)
        tasks_ = student_total_tasks[key][2]
        sorted_tasks = sorted(tasks_, key=lambda x: x[0], reverse=False)
        student_total_tasks[key][2] = sorted_tasks

    return render_template(
        'org_old.html',
        org_name=org_title,
        tasks_count=tasks["totalTasks"],
        students=student_total_tasks,
        cat_count=model_tags,
        year=year)

    return org_title


@app.route('/2015/org/<orgname>/')
def org_2015_data(orgname):
    year = "2015"
    try:
        file_path = "orgs/" + year + "/" + orgname + "_data.json"
        data = open(file_path).read()
        last_update_time = time.ctime(os.path.getmtime(file_path))
    except IOError:
        return redirect("/" + year)
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
        is_beginner = int(task["task_definition"]["is_beginner"])

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
            student_tasks[student_id][2].append(
                [task_name, task_link, cat, is_beginner])
            student_tasks[student_id][3][0] += 1 in cat
            student_tasks[student_id][3][1] += 2 in cat
            student_tasks[student_id][3][2] += 3 in cat
            student_tasks[student_id][3][3] += 4 in cat
            student_tasks[student_id][3][4] += 5 in cat
        else:
            s_code = int(1 in cat)
            s_ui = int(2 in cat)
            s_doc = int(3 in cat)
            s_qa = int(4 in cat)
            s_out = int(5 in cat)
            s_id[student_id] = last_student_id
            student_tasks.append([1, student_name,
                                  [[task_name, task_link, cat, is_beginner]],
                                  [s_code, s_ui, s_doc, s_qa, s_out]])
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
        year=2015,
        last_update_time=last_update_time)


@app.route('/2016/org/<orgname>/')
def org_2016_data(orgname):
    year = "2016"
    try:
        file_path = "orgs/" + year + "/" + orgname + "_data.json"
        data = open(file_path).read()
        last_update_time = time.ctime(os.path.getmtime(file_path))
    except IOError:
        return redirect("/" + year)
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

        # if not org_id == orgs[orgname][0]:
        #    continue
        orgs[org_id] = "Sugar Labs"

        final_tasks.append(task)
        is_beginner = int(task["task_definition"]["is_beginner"])

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
            student_tasks[student_id][2].append(
                [task_name, task_link, cat, is_beginner])
            student_tasks[student_id][3][0] += 1 in cat
            student_tasks[student_id][3][1] += 2 in cat
            student_tasks[student_id][3][2] += 3 in cat
            student_tasks[student_id][3][3] += 4 in cat
            student_tasks[student_id][3][4] += 5 in cat
        else:
            s_code = int(1 in cat)
            s_ui = int(2 in cat)
            s_doc = int(3 in cat)
            s_qa = int(4 in cat)
            s_out = int(5 in cat)
            s_id[student_id] = last_student_id
            student_tasks.append([1, student_name,
                                  [[task_name, task_link, cat, is_beginner]],
                                  [s_code, s_ui, s_doc, s_qa, s_out]])
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
        year=2016,
        last_update_time=last_update_time)


@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
