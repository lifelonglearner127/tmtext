import os
import sys
import time
import datetime
import json
import random
from collections import OrderedDict

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

from flask import Flask, request, send_from_directory, send_file
from flask import render_template, redirect, url_for, make_response
from boto.sqs.message import Message
import boto.ec2.autoscale
import boto.sqs
import boto
from boto.s3.key import Key

from cache_layer.simmetrica_class import Simmetrica
from cache_layer import additional_sqs_metrics
from cache_layer.cache_service import SqsCache
from cache_layer import CACHE_QUEUES_LIST


app = Flask(__name__)
s = Simmetrica()
cache = SqsCache()

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
    global s
    
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

    used_memory = s.get_used_memory()

    current_settings = s.get_settings()

    daily_sqs_instances_counter = 'Not available'
    executed_tasks_during_the_day = 'Not available'
    waiting_task = 'Not available'
    task_during_last_hour = 'Not available'
    average_tasks = 'Not available'
    try:
        sqs_metrics = additional_sqs_metrics.get_sqs_metrics(hours_limit=hours)
        sqs_metrics = json.loads(sqs_metrics)
        daily_sqs_instances_counter = \
            sqs_metrics['daily_sqs_instances_counter']
        executed_tasks_during_the_day = \
            sqs_metrics['executed_tasks_during_the_day']
        waiting_task = sqs_metrics['waiting_task']
        task_during_last_hour = sqs_metrics['task_during_last_hour']
        average_tasks = sqs_metrics['average_tasks']
    except Exception as e:
        print e

    sqs_instances_quantity = additional_sqs_metrics.check_instance_quantity()

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
        'most_recent_resp': most_recent_resp,
        'used_memory': used_memory,
        'current_settings': current_settings,
        'daily_sqs_instances_counter': daily_sqs_instances_counter,
        'executed_tasks_during_the_day': executed_tasks_during_the_day,
        'waiting_task': waiting_task,
        'sqs_instances_quantity': sqs_instances_quantity,
        'task_during_last_hour': task_during_last_hour,
        'average_tasks': average_tasks,
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


@app.route('/update-settings', methods=['GET', 'POST'])
def update_settings():
    global s
    if request.method == 'POST':
        data = request.form
        result_msg = s.update_settings(data)
        return render_template('update_settings.html', result_msg=result_msg)
    else:
        current_settings = s.get_settings()
        return render_template('update_settings.html',
                               current_settings=current_settings)


@app.route('/remove-old-resp', methods=['POST'])
def remove_old_resp():
    global s
    data = request.form
    try:
        time_limit = int(data['time_limit'])
    except:
        time_limit = 12
    print(time_limit)
    s.delete_old_responses(time_limit)
    return redirect(url_for('cache_stats'))


@app.route('/flash-cache', methods=['POST'])
def flash_cache():
    global s
    s.clear_cache()
    return redirect(url_for('cache_stats'))


@app.route('/get_sqs_instances_quantity')
def get_sqs_instances_quantity():
    data = {'sqs_instances_quantity':
                additional_sqs_metrics.check_instance_quantity()}
    return json.dumps(data)



### This is additional functions for debugging SQS
bucket_list = None
enumerated_list = None
AMAZON_BUCKET_NAME = 'spyder-bucket'

def display_log_file(key):
    filename = '/tmp/tmp_file'
    key.get_contents_to_filename(filename)
    lines = open(filename, 'r').readlines()
    data = '<br>'.join(lines)
    return data

def get_list_of_bucket_items(striped=True):
    global bucket_list
    global enumerated_list
    # bucket_list = None ## comment this to lower s3 load
    if not bucket_list:
        conn = boto.connect_s3()

        bucket = conn.get_bucket(AMAZON_BUCKET_NAME, validate=False)
        bucket_list = list(bucket.list())
        if striped:
            for k in bucket_list:
                if '.zip' in k.name:
                    try:
                        unique_hash = k.name.split('____')[1]
                        bucket_list = [k for k in bucket_list if unique_hash \
                                       not in k.name]
                    except Exception as e:
                        print(e)
        bucket_list.reverse()
        enumerated_list = list(enumerate(bucket_list))
    return enumerated_list

@app.route('/failed_logs')
def get_all_list():
    get_list_of_bucket_items()
    return render_template('all_bucket_items.html',
                           bucket_list=enumerated_list)

@app.route('/get_logs_by_task_by_id', methods=['GET'])
def get_logs_by_task_by_id():
    task_id = request.args.get('task_id')
    get_list_of_bucket_items(striped=False)
    global enumerated_list
    required_list = []
    for item in enumerated_list:
        name = item[1].name
        if task_id in name:
            required_list.append(item)
    enumerated_list = required_list
    return render_template('all_bucket_items.html',
                           bucket_list=enumerated_list)

@app.route('/get_log_body_by_task_id', methods=["GET"])
def get_log_body_by_task_id():
    task_id = request.args.get('task_id')
    print task_id
    get_list_of_bucket_items(striped=False)
    global enumerated_list
    for item in enumerated_list:
        key = item[1]
        if 'remote_instance_starter2' in key.name:
            if task_id in key.get_contents_as_string():
                return display_log_file(key)
                break
    return "Log was not found"


@app.route('/get_content', methods=['GET'])
def get_content():
    item_number = int(request.args.get('item_number'))
    key = enumerated_list[int(item_number)][1]
    data = display_log_file(key)
    return data


@app.route('/get_s3_file', methods=['GET'])
def get_s3_file():
    fname = request.args.get('file')
    if fname:
        conn = boto.connect_s3()
        bucket = conn.get_bucket(AMAZON_BUCKET_NAME, validate=False)
        key = bucket.get_key(fname)
        if not key:
            return render_template(
                's3_file.html', msg='No such file: %r.' % fname)
        file_data = key.get_contents_as_string()
        resp = make_response(file_data)
        resp.headers['Content-Disposition'] = \
            'attachment; filename=%s' % fname.split('/')[-1]
        return resp
    return render_template('s3_file.html')


@app.route('/log_install_error', methods=['GET', 'POST'])
def log_install_error():
    file_to_save_logs = '/tmp/install_errors.log'
    if request.method == 'GET':
        with open(file_to_save_logs, 'r') as f:
            c = f.read()
            return '<pre>%s</pre>' % c
    form = request.form
    item = form['item']
    error = form['error']
    if not error or not item:
        return 'No data'
    with open(file_to_save_logs, 'a') as f:
        f.write('%s - %r\n\n' % (item, error))
    return 'ok'


@app.route('/killer')
def get_killer_logs():
    conn = boto.connect_s3()
    bucket = conn.get_bucket(AMAZON_BUCKET_NAME, validate=False)
    bucket_key = bucket.get_key('instances_killer_logs')
    if bucket_key:
        return '<pre>%s</pre>' % bucket_key.get_contents_as_string()
    else:
        return 'Killer logs not found'


@app.route('/save_cache', methods=['POST'])
def save_cache_item():
    """
    save cached sqs item response
    """
    task = request.form['task']
    message = request.form['message']
    result = cache.put_result(task, message)
    return make_response('', 200 if result else 404)


@app.route('/get_cache', methods=['POST'])
def get_cache_item():
    """
    get item from sqs cache
    """
    task = request.form['task']
    from_cache, result = cache.get_result(task)
    if result:
        return make_response(result, 200)
    elif from_cache:
        return make_response('Item found in cache but it is too old', 404)
    else:
        return make_response('Item not found in cache', 404)


@app.route('/complete_task', methods=['POST'])
def complete_task():
    task = request.form['task']
    cache.complete_task(task)
    return make_response('', 200)

@app.route('/list_s3')
def list_s3():
    marker = request.args.get('marker')
    conn = boto.connect_s3()
    b = conn.get_bucket('spyder-bucket')
    keys = b.get_all_keys(prefix='2015/09/09/', marker=marker, max_keys=1000)
    return '<pre>' + '\n'.join([k.name for k in keys]) + '</pre>'


@app.route('/stats')
def stats():
    try:
        context = dict()
        conn = boto.ec2.autoscale.AutoScaleConnection()
        group = conn.get_all_groups(names=['SCCluster1'])[0]
        context['running_instances'] = len(group.instances)
        #
        context['today_instances'] = cache.get_today_instances()
        #
        context['today_executed_tasks'] = cache.get_executed_tasks_count()
        #
        context['last_hour_executed_tasks'] = cache.get_executed_tasks_count(
            for_last_hour=True)
        #
        sqs_conn = boto.sqs.connect_to_region('us-east-1')
        context['left_tasks'] = [(q, sqs_conn.get_queue(q).count())
                                 for q in CACHE_QUEUES_LIST.itervalues()]
        context['left_tasks_total'] = sum([q[1] for q in context['left_tasks']])
        #
        cur_hour = datetime.datetime.now().hour
        context['avg_hour_task'] = '{0:.2f}'.format(
            context['today_executed_tasks'] / cur_hour)
        #
        hourly_tasks_stats = OrderedDict()
        for i in xrange(0, cur_hour+1, 1):
            key = '%s - %s' % (i, i+1)
            hourly_tasks_stats[key] = cache.get_executed_tasks_count(i, i+1)
        context['hourly_tasks_stats'] = hourly_tasks_stats
        #
        context['used_memory'] = cache.get_used_memory()
        context['items_in_cache'] = cache.get_cached_tasks_count()
        context['cache_most_popular'] = cache.get_most_popular_cached_items(10)
        return render_template('stats.html', **context)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.debug = True
    app.run()