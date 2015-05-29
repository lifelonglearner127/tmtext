import os
import sys
import datetime
import json

from simmetrica_class import Simmetrica
from additional_sqs_metrics import get_sqs_metrics


s = Simmetrica()
settings = s.get_settings()

SENDMAIL = "/usr/sbin/sendmail"
FROM = "Cache Service"
TO = settings.get('report_mail')
if not TO:
    sys.exit()


END_DATE = datetime.datetime.now()
START_DATE = END_DATE - datetime.timedelta(1)
SUBJECT = " SQS cache service report from %s to %s" % (str(START_DATE), str(END_DATE))

hours = 24

total_cached_items = s.total_resp_in_cache()
total_requests = len(s.get_range_of_received_req(hours))
total_responses = len(s.get_range_of_returned_resp(hours))
if total_requests and total_responses:
    correlation = round((total_responses * 100.0 / total_requests), 2)
else:
    correlation = None
most_recent_resp = s.get_most_recent_resp(hours)
most_recent_resp_str = ''
for item in most_recent_resp:
    pattern = '%s -- %s \n' % (item[0], item[1])
    most_recent_resp_str += pattern
used_memory = s.get_used_memory()

daily_sqs_instances_counter = 0
executed_tasks_during_the_day = 0
waiting_task = 0

try:
    sqs_metrics = get_sqs_metrics(purge=True)
    sqs_metrics = json.loads(sqs_metrics)
    daily_sqs_instances_counter = sqs_metrics['daily_sqs_instances_counter']
    executed_tasks_during_the_day = \
        sqs_metrics['executed_tasks_during_the_day']
    waiting_task = sqs_metrics['waiting_task']
except Exception as e:
    print e

text_draft = """
SQS cache service report for last 24 hours:
Total requests: %s 
Total responses: %s 
Correlation: %s \n
5 Most recent responses:
# response_stamp -- quantity
%s
Total cached items at this moment: %s
Total used memory: %s

SQS metrics:
Daily sqs instances counter: %s # this mean how many instances were rised up
Executed tasks during the day: %s
Still waiting tasks at queue: %s
"""

TEXT = text_draft % (total_requests, total_responses, correlation,
    most_recent_resp_str, total_cached_items, used_memory,
    daily_sqs_instances_counter, executed_tasks_during_the_day, waiting_task)

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, TO, SUBJECT, TEXT)

p = os.popen("%s -t -i" % SENDMAIL, "w")
p.write(message)
status = p.close()
if status:
    print "Sendmail exit status", status