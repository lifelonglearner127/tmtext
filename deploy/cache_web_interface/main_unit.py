import os
import sys
import time
import datetime
import json

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

from flask import Flask, request
from flask import render_template
from boto.sqs.message import Message
import boto.sqs

from cache_layer.simmetrica_class import Simmetrica


app = Flask(__name__)


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
        quantity = data['quantity']
        if quantity:
            task['cmd_args'] = {'quantity': quantity}

        url = data.get('url')
        if url:
            task['url'] = url
        branch_name = data.get('branch_name')
        if branch_name:
            task['branch_name'] = branch_name

        sqs_conn = boto.sqs.connect_to_region("us-east-1")
        queue = sqs_conn.get_queue('cache_sqs_ranking_spiders_tasks_tests')
        m = Message()
        dumped_task = json.dumps(task)
        m.set_body(dumped_task)

        return render_template('success.html', task=dumped_task)
    else:
        return render_template('add_task.html')


if __name__ == '__main__':
    app.debug = True
    app.run()