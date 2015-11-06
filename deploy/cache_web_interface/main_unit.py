import os
import sys
import datetime
import json
from collections import OrderedDict
from flask import Flask, request, flash
from flask import render_template, make_response
import boto.ec2.autoscale
import boto.sqs
import boto

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

from cache_layer.cache_service import SqsCache
from cache_layer import CACHE_QUEUES_LIST


AMAZON_BUCKET_NAME = 'spyder-bucket'
app = Flask(__name__)
cache = SqsCache()


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


@app.route('/settings', methods=['GET', 'POST'])
def update_settings():
    data = dict()
    if request.method == 'POST':
        data = {k: v for k, v in request.form.items()}
        cache.save_cache_settings(data)
        data['result_msg'] = 'Changes saved'
    data['form_fields'] = cache.get_cache_settings()
    return render_template('update_settings.html', **data)


@app.route('/clear_cache', methods=['GET', 'POST'])
def clear_cache():
    # dict: key is the form input name,
    #  value is tuple with description and redis keys to remove
    params = {
        'cache_data': ('S3 keys to the cached data', [
            cache.REDIS_CACHE_TIMESTAMP, cache.REDIS_CACHE_KEY]),
        'cache_stats': ('Stats of most used cached items', [
            cache.REDIS_CACHE_STATS_URL, cache.REDIS_CACHE_STATS_TERM,
            cache.REDIS_COMPLETED_COUNTER]),
        'sqs_stats': ('Stats of the sqs: count of tasks and instances', [
            cache.REDIS_COMPLETED_TASKS, cache.REDIS_INSTANCES_COUNTER]),
        'urgent_stats': ('Stats of the urgent queue', [
            cache.REDIS_URGENT_STATS])
    }
    if request.method == 'POST':
        keys_to_clear = []
        for k, v in request.form.iteritems():
            if k in params:
                keys_to_clear += params[k][1]
        cache.del_redis_keys(*keys_to_clear)
        flash('Selected items were cleared, keys removed: %s' % keys_to_clear)

    return render_template('clear_cache.html', fields=params)


@app.route('/killer')
def get_killer_logs():
    """
    list content of s3 file with killer logs
    """
    conn = boto.connect_s3()
    bucket = conn.get_bucket(AMAZON_BUCKET_NAME, validate=False)
    bucket_key = bucket.get_key('instances_killer_logs')
    if bucket_key:
        return '<pre>%s</pre>' % bucket_key.get_contents_as_string()
    else:
        return 'Killer logs not found'


@app.route('/get_s3_file', methods=['GET'])
def get_s3_file():
    """
    allows downloading selected files from s3 storage
    """
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


@app.route('/list_s3')
def list_s3():
    """
    lists files (limited to 1000) with the given prefix, supports marker
    to move between result pages
    """
    marker = request.args.get('marker')
    prefix = request.args.get('prefix')
    if not prefix:
        prefix = datetime.date.today().strftime('%Y/%m/%d')
    conn = boto.connect_s3()
    b = conn.get_bucket('spyder-bucket')
    keys = b.get_all_keys(prefix=prefix, marker=marker, max_keys=1000)
    return render_template('list_s3_files.html',
                           list_files=[_.name for _ in keys],
                           last_file=keys[-1].name if keys else '')


@app.route('/stats')
def stats():
    """
    show cache and sqs stats
    """
    try:
        context = dict()
        conn = boto.ec2.autoscale.AutoScaleConnection()
        groups = conn.get_all_groups(
            names=['SCCluster1', 'SCCluster2', 'SCCluster3'])
        instances = {group.name: len(group.instances) for group in groups}
        context['running_instances'] = sum(instances.itervalues())
        context['running_instances_info'] = instances
        context['today_instances'] = cache.get_today_instances()
        context['today_executed_tasks'] = cache.get_executed_tasks_count()
        context['last_hour_executed_tasks'] = cache.get_executed_tasks_count(
            for_last_hour=True)
        context['responses_from_cache_url'] = \
            cache.get_total_cached_responses(False)
        context['responses_from_cache_term'] = \
            cache.get_total_cached_responses(True)
        sqs_conn = boto.sqs.connect_to_region('us-east-1')
        context['left_tasks'] = [
            (q.split('_')[-1], sqs_conn.get_queue(q).count())
            for q in CACHE_QUEUES_LIST.itervalues()]
        context['left_tasks_total'] = sum([q[1] for q in context['left_tasks']])
        cur_hour = datetime.datetime.now().hour
        context['avg_hour_task'] = '{0:.2f}'.format(
            context['today_executed_tasks'] / (cur_hour + 1))
        hourly_tasks_stats = OrderedDict()
        for i in xrange(0, cur_hour+1, 1):
            key = '%s - %s' % (i, i+1)
            hourly_tasks_stats[key] = cache.get_executed_tasks_count(i, i+1)
        context['hourly_tasks_stats'] = hourly_tasks_stats
        context['used_memory'] = cache.get_used_memory()
        context['items_in_cache'] = cache.get_cached_tasks_count()
        context['cache_most_popular_url'] = \
            cache.get_most_popular_cached_items(10, False)
        context['cache_most_popular_term'] = \
            cache.get_most_popular_cached_items(10, True)
        context['urgent_stats'] = cache.get_urgent_stats()
        context['completed_stats'] = cache.get_completed_stats()
        context['failed_tasks'] = cache.get_all_failed_results()
        return render_template('stats.html', **context)
    except Exception as e:
        return str(e)


@app.route('/autoscale_history', methods=['GET', 'POST'])
def autoscale_history():
    if request.method == 'GET':
        return render_template('autoscale_history.html')
    days = int(request.form.get('days', '0'))
    data = cache.get_instances_history(days)
    resp = make_response(json.dumps(data))
    resp.headers['Content-Type'] = 'application/json'
    return resp


# ###################################
# ####### CACHE METHODS START #######
# ###################################
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
    try:
        queue = request.form['queue']
        if not queue:
            raise Exception
    except:
        queue = ''
    from_cache, result = cache.get_result(task, queue)
    if result:
        return make_response(result, 200)
    elif from_cache:
        return make_response('Item found in cache but it is too old', 404)
    else:
        return make_response('Item not found in cache', 404)


@app.route('/complete_task', methods=['POST'])
def complete_task():
    """
    log taken task
    (when it was acquired from sqs, not when it was actually completed)
    """
    task = request.form['task']
    is_from_cache_str = request.form['is_from_cache']
    cache.complete_task(task, is_from_cache_str)
    return make_response('', 200)


@app.route('/fail_task', methods=['POST'])
def fail_task():
    task = request.form['task']
    res = cache.fail_result(task)
    return '1' if res else '0'
# ###################################
# ######### CACHE METHODS END #######
# ###################################


if __name__ == '__main__':
    app.secret_key = '$%6^78967804^46#$%^$fdG'
    app.debug = False
    app.run()
