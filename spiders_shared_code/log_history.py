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
    def __init__(self, scraper):
        self.start = None
        self.data = {
            'scraper': scraper,
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

    def start_log(self):
        self.start = time.time()

    def get_log(self):
        return json.dumps(self.data)

    def add_log(self, key, value):
        self.data[key] = value

    def add_list_log(self, key, value):
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(value)

    def send_log(self):
        end = time.time()

        self.data['duration'] = round(end-self.start, 2)
        self.data['date'] = time.time()

        try:
            self.data['instance'] = requests.get('http://169.254.169.254/latest/meta-self.data/instance-id',
                timeout = 10).content
        except Exception as e:
            self.data['instance'] = 'Failed to get instance metadata: %s %s' % (type(e), e)

        try:
            requests.post('http://10.0.0.22:49215',
                auth=('chlogstash', 'shijtarkecBekekdetloaxod'),
                headers = {'Content-type': 'application/json'},
                data = self.get_log(),
                timeout = 10)
        except Exception as e:
            logger.warn('Failed to send logs: %s %s' % (type(e), e))
