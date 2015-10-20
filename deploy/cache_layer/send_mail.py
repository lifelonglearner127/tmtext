import os
import sys
import json
from datetime import date
from jinja2 import Environment, FileSystemLoader
CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))
from cache_service import SqsCache


def collect_data(cache):
    context = dict()
    context['executed_tasks'] = cache.get_executed_tasks_count()
    context['total_instances'] = cache.get_today_instances()
    context['total_cached_items'] = cache.get_cached_tasks_count()
    context['cache_most_popular_url'] = \
        cache.get_most_popular_cached_items(5, False)
    context['cache_most_popular_term'] = \
        cache.get_most_popular_cached_items(5, True)
    context['used_memory'] = cache.get_used_memory()
    context['responses_from_cache_url'] = \
        cache.get_total_cached_responses(False)
    context['responses_from_cache_term'] = \
        cache.get_total_cached_responses(True)
    context['urgent_stats'] = cache.get_urgent_stats()
    context['completed_stats'] = cache.get_completed_stats()
    context['failed_tasks'] = cache.get_all_failed_results()
    return context


def generate_mail_message(data):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('mail_template')
    return template.render(**data)


def send_mail(sender, receivers, subject, text):
    message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (
        sender, receivers, subject, text)
    p = os.popen('/usr/sbin/sendmail -t -i', 'w')
    p.write(message)
    p.close()


def delete_old_cache_data(cache):
    # delete cached responses, older then 7 days (default value)
    freshness = int(cache.get_cache_settings().get('hours_limit', '168'))
    freshness *= 60  # convert into minutes
    res = cache.delete_old_tasks(freshness)
    removed_cache_url, removed_cache_term, removed_resp, removed_urgent = \
        cache.clear_stats()
    res = sum([res, removed_cache_url, removed_cache_term,
               removed_resp, removed_urgent])
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

if __name__ == '__main__':
    main()