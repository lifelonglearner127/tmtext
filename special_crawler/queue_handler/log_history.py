import json
import time
import requests

start = None
data = {
    'scraper': 'CH',
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

class LogHistory(object):
    @staticmethod
    def start_log():
        global start
        start = time.time()

    @staticmethod
    def get_log():
        return json.dumps(data)

    @staticmethod
    def add_log(key, value):
        data[key] = value

    @staticmethod
    def send_log():
        end = time.time()

        data['duration'] = round(end-start, 2)
        data['date'] = time.time()

        try:
            data['instance'] = requests.get('http://169.254.169.254/latest/meta-data/instance-id',
                timeout = 10).content
        except Exception as e:
            print 'Failed to get instance metadata:', e

        try:
            requests.post('http://10.0.0.22:49215',
                auth=('chlogstash', 'shijtarkecBekekdetloaxod'),
                headers = {'Content-type': 'application/json'},
                data = LogHistory.get_log(),
                timeout = 10)
        except Exception as e:
            print 'Failed to send logs:', e
        
    @staticmethod
    def add_list_log(key, value):
        if key not in data:
            data[key] = []
        data[key].append(value)
