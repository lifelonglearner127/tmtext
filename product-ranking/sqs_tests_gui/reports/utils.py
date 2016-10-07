import os
import sys
import json
import threading
import copy


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', 's3_reports'))

from jobs_per_server_per_site import dump_reports


SCRIPT_DIR = REPORTS_DIR = os.path.join(CWD, '..', '..', 's3_reports')
LIST_FILE = os.path.join(CWD, '..', 'gui', 'management', 'commands', "_amazon_listing.txt")


def get_report_fname(date):
    return os.path.join(REPORTS_DIR, 'sqs_jobs_%s.json.txt' % date.strftime('%Y-%m-%d'))


def run_report_generation(date):
    thread = threading.Thread(target=dump_reports, args=(LIST_FILE, date, self._get_report_fname(date)))
    thread.daemon = True
    thread.run()


def dicts_to_ordered_lists(dikt):
    if isinstance(dikt, (list, tuple)):
        dikt = dikt[0]
    result = copy.copy({})
    for key, value in dikt.items():
        value_list = copy.copy([])
        result[key] = value_list
        for val_key, val_val in value.items():
            result[key].append((val_key, val_val))
        result[key].sort(reverse=True, key=lambda i: i[1])
    return result
