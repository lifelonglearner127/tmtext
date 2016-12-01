import json
import time
import requests
import logging

# initialize the logger
logger = logging.getLogger('basic_logger')
logger.setLevel(logging.DEBUG)
fh = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

class LogHistory(object):
    start = None
    data = {
        'scraper': None,
        'scraper_type': None,
        'server_hostname': None,
        'pl_name': None,
        'url': None,
        'response_time': None,
        'failure_type': None,
        'date': None,
        'duration': None,
        'page_size': None,
        'instance': None,
        'errors': []
    }

    @staticmethod
    def start_log():
        global start
        start = time.time()

    @staticmethod
    def get_log():
        return json.dumps(LogHistory.data)

    @staticmethod
    def add_log(key, value):
        LogHistory.data[key] = value

    @staticmethod
    def send_log():
        end = time.time()

        LogHistory.data['duration'] = round(end-start, 2)
        LogHistory.data['date'] = time.time()

        try:
            LogHistory.data['instance'] = requests.get('http://169.254.169.254/latest/meta-LogHistory.data/instance-id',
                timeout = 10).content
        except Exception as e:
            LogHistory.data['instance'] = 'Failed to get instance metadata: %s' % str(e)

        try:
            requests.post('http://10.0.0.22:49215',
                auth=('chlogstash', 'shijtarkecBekekdetloaxod'),
                headers = {'Content-type': 'application/json'},
                data = LogHistory.get_log(),
                timeout = 10)
        except Exception as e:
            logger.warn('Failed to send logs: %s' % str(e))
        
    @staticmethod
    def add_list_log(key, value):
        if key not in LogHistory.data:
            LogHistory.data[key] = []
        LogHistory.data[key].append(value)
