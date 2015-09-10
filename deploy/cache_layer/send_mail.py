import os
import json
from datetime import date
from flask import render_template
from .cache_service import SqsCache


def collect_data(cache):
    # executed_tasks, total_instances, used_memory
    # total_cached_items, cache_most_popular
    context = dict()
    context['executed_tasks'] = cache.get_executed_tasks_count()
    context['total_instances'] = cache.get_today_instances()
    context['total_cached_items'] = cache.get_cached_tasks_count()
    context['cached_most_popular'] = cache.get_most_popular_cached_items(5)
    return context


def generate_mail_message(data):
    return render_template('mail_template', **data)


def send_mail(sender, receivers, subject, text):
    message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (
        sender, receivers, subject, text)
    p = os.popen('/usr/sbin/sendmail -t -i', 'w')
    p.write(message)
    p.close()


def delete_old_cache_data(cache):
    # delete cached responses, older then 7 days
    days = 7
    freshness = 24 * 60 * days
    res = cache.delete_old_tasks(freshness)
    removed_cache, removed_resp = cache.clear_stats()
    res = sum([res, removed_cache, removed_resp])
    return res


def main():
    cache = SqsCache()
    with open('settings') as f:
        s = f.read()
    s_data = json.loads(s)
    sender = 'Cache Service'
    receivers = s_data['report_mail']
    today = date.today()
    subject = 'SQS cache daily report for %s' % today.strftime('%A, %Y-%m-%d')
    content = generate_mail_message(collect_data(cache))
    send_mail(sender, receivers, subject, content)
    res = delete_old_cache_data(cache)
    print 'Deleted %s total records from cache.' % res