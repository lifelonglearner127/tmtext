# TODO: generate Simmetrica config file by parsing all the spiders, and upload this config to the monitoring host
# (you may run locally)

import os
import re


def find_spiders(path):
    """ Returns the list of spidernames and their domains """
    spiders = []
    for f in os.listdir(path):
        if not re.findall("(.*?).pyc", f):
            if os.path.isdir(os.path.join(path, f)):
                continue
            f = open(os.path.join(path, f), 'r')
            text = f.read()
            allowed_domains = re.findall(
                "allowed_domains\s*=\s*\[([^\]]*)\]", text)
            name = re.findall(r"name\s*=\s*('|\")([\w]+)(\1)", text)
            interm = []
            if name:
                interm.append(name[0][1])
            if allowed_domains:
                interm.append(allowed_domains[0].strip().replace(
                    "\"", "").replace("'", ""))
            if interm:
                spiders.append(interm)
    return spiders


def generate_config_for_spider(spider_name):
    config = """
    # {spider_name}
    - title: {spider_name}
      timespan: 7 day
      colorscheme: cool
      type: area
      interpolation: cardinal
      resolution: 15min
      size: M
      offset: zero
      events:
          - name: monitoring_spider_closed_{spider_name}
            title: Spider finished
          - name: monitoring_spider_working_time_{spider_name}
            title: Working time, seconds
          - name: monitoring_spider_dupefilter_filtered_{spider_name}
            title: Dupefilter/Filtered
          - name: monitoring_spider_downloader_request_count_{spider_name}
            title: Downloader requests - count
          - name: monitoring_spider_downloader_response_bytes_{spider_name}
            title: Megabytes downloaded
    """
    config = config.format(spider_name=spider_name)
    return config


def generate_general_config():
    config = """
    # General
    - title: Overall performance
      timespan: 7 day
      colorscheme: cool
      type: area
      interpolation: cardinal
      resolution: 15min
      size: M
      offset: zero
      events:
          - name: monitoring_spider_closed
            title: Spider finished
          - name: monitoring_spider_working_time
            title: Working time, seconds
    """
    return config


if __name__ == '__main__':
    CWD = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(CWD, '..', 'product_ranking', 'spiders')
    spiders = find_spiders(os.path.realpath(path))
    spiders.sort(key=lambda val: val[0])  # sort by alphabet
    result = generate_general_config() + '\n'
    for spider in spiders:
        result += generate_config_for_spider(spider[0]) + '\n'
    print result