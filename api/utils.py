import datetime

from django.db import connection

from main.models import Modules
from utils import git, svn


def custom_sql(sql, format):
    with connection.cursor() as cursor:
        cursor.execute(sql, format)
        rows = [row for row in cursor.fetchall()]
    return rows


def custom_day():
    start = datetime.datetime.now() - datetime.timedelta(days=20)
    end = datetime.datetime.now() + datetime.timedelta(days=1)
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')


def between_days(start, end):
    begin_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    data = []
    while begin_date < end_date:
        data.append(begin_date.strftime('%Y-%m-%d'))
        begin_date += datetime.timedelta(days=1)
    return data


def generate_series(data, zone):
    sumdata = []
    daydata = []
    DateTime = dict((y, x) for x, y in data)
    for i in range(len(zone)):
        if DateTime.get(zone[i]) and DateTime.get(zone[i]) != 0:
            daydata.append(zone[i])
            sumdata.append(DateTime.get(zone[i]))
        else:
            daydata.append(zone[i])
            sumdata.append(0)
    series = {'data': sumdata, 'datetime': daydata}
    return series


def filter_version(project, module):
    m = Modules.objects.get(name=module, project=project)
    data = []
    if m.repo_type == 'git':
        if m.repo_mode == '1':
            data = git.getBranchList(m)
        if m.repo_mode == '2':
            data = git.gitTagList(m)
    if m.repo_type == 'svn':
        if m.repo_mode == '1':
            data = svn.getBranchList(m)
        if m.repo_mode == '2':
            data = svn.getCommitList(m)
        if m.repo_mode == '3':
            data = svn.getCommitList(m)
    return data
