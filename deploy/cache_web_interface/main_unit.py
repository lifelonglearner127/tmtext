import os
import sys
import time
import datetime
import json
import random

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

from flask import Flask, request, send_from_directory, send_file
from flask import render_template
from boto.sqs.message import Message
import boto.sqs

from cache_layer.simmetrica_class import Simmetrica


app = Flask(__name__)


def send_msg_to_sqs(task):
    sqs_conn = boto.sqs.connect_to_region("us-east-1")
    queue = sqs_conn.get_queue('cache_sqs_ranking_spiders_tasks_tests')
    m = Message()
    dumped_task = json.dumps(task)
    m.set_body(dumped_task)
    queue.write(m)
    return dumped_task


@app.route('/cache-stats', methods=['GET', 'POST'])
def cache_stats(hours=1):
    if request.method == 'POST':
        data = request.form
        hours = int(data['required_hours'])
    s = Simmetrica()
    
    try:
        total_cached_items = s.total_resp_in_cache()
        newest_item = float(s.get_time_of_newest_resp())
        age_newest_item = (time.time() - newest_item)/3600
        age_newest_item = round(age_newest_item, 1)
        newest_item_dt = datetime.datetime.fromtimestamp(newest_item)
        oldest_item = float(s.get_time_of_oldest_resp())
        age_oldest_item = (time.time() - oldest_item)/3600
        age_oldest_item = round(age_oldest_item, 1)
        oldest_item_dt = datetime.datetime.fromtimestamp(oldest_item)
    except:
        total_cached_items = age_newest_item = newest_item_dt = None
        age_oldest_item = oldest_item_dt = None

    total_requests = len(s.get_range_of_received_req(hours))
    total_responses = len(s.get_range_of_returned_resp(hours))
    if total_requests and total_responses:
        correlation = round((total_responses * 100.0 / total_requests), 2)
    else:
        correlation = None
    most_recent_resp = s.get_most_recent_resp(hours)

    if hours == 1:
        time_range = '1 hour'
    elif hours == 7*24:
        time_range = '7 days'
    elif hours == 30*24:
        time_range = '30 days'
    else:
        time_range = '%s hours' % hours

    context = {
        'time_range': time_range,
        'total_cached_items': total_cached_items,
        'age_newest_item': age_newest_item,
        'newest_item_dt': newest_item_dt,
        'age_oldest_item': age_oldest_item,
        'oldest_item_dt': oldest_item_dt,
        'total_requests': total_requests,
        'total_responses': total_responses,
        'correlation': correlation,
        'most_recent_resp': most_recent_resp
    }
    return render_template('cache_stats.html', **context)


@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        data = request.form

        task = {}
        task['server_name'] = data['server_name']
        task['site'] = data['site']
        task['task_id'] = data['task_id']

        searchterms_str = data.get('searchterms_str')
        if searchterms_str:
            task['searchterms_str'] = searchterms_str
        quantity = data.get('quantity')
        if quantity:
            task['cmd_args'] = {'quantity': quantity}

        url = data.get('url')
        if url:
            task['url'] = url
        branch_name = data.get('branch_name')
        if branch_name:
            task['branch_name'] = branch_name

        freshness = data.get('freshness')
        if freshness:
            task['freshness'] = freshness

        dumped_task = send_msg_to_sqs(task)
        return render_template('success.html', task=dumped_task)
    else:
        default_id = random.randrange(10000,90000)
        return render_template('add_task.html', default_id=default_id)


@app.route('/send-task-again', methods=['GET', 'POST'])
def send_task_again():
    if request.method == 'POST':
        data = request.form
        task = json.loads(data['task'])
        task['task_id'] = random.randrange(10000,90000)
        dumped_task = send_msg_to_sqs(task)
        return render_template('success.html', task=dumped_task)


@app.route('/all-logs')
def list_all_logs():
    path = '/tmp/cache_logs/'
    l = os.listdir(path)
    l.sort(reverse=True)
    return render_template('all_logs.html', logs=l)


@app.route('/cache-logs/<path:filename>')
def cache_logs(filename):
    log_folder = '/tmp/cache_logs/'
    log_path = os.path.join(log_folder, filename)
    if os.path.exists(log_path):
        lines = open(log_path, 'r').readlines()
        data = '<br>'.join(lines)
        return data
    else:
        return 'Log file not exists'


if __name__ == '__main__':
    app.debug = True
    app.run()