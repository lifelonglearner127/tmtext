# takes an S3 bucket "list" dump, with lines like
# spyder-bucket,2016/09/23/23-09-2016____zzhba16bx9n95oitv6vrj1ypnhf0____walmart-content--16126555____single-product-url-request____walmart.jl.zip>
#
# creates a report that has the following data: jobs per site, like
#
# ca-test:
#    staples: 100 searchterm jobs, 20 product urls
#    target: 200 searchterm jobs, 10 product urls
# sales2:
#    staples: 150 searchterm jobs, 20 product urls
#    target: 250 searchterm jobs, 15 product urls


import os
import gzip
import sys
import datetime
import time
from collections import OrderedDict


def main(input_file, date, spider_marker=None):
    result = {}

    total_lines_processed = 0
    lines_processed = 0

    date = date.strftime('%d-%m-%Y' + '____')
    with gzip.open(input_file, 'rb') as fh:
        for line in fh:
            total_lines_processed += 1

            if date in line:
                if '.jl.zip' not in line:
                    continue
                try:
                    _, _, server_and_id, _, spider = line.split('____')
                except:
                    continue

                server = server_and_id.split('--')[0].strip()
                spider = spider.replace('.jl.zip', '').replace('>', '').strip()

                if spider_marker:
                    if spider_marker not in spider:
                        continue

                if not server in result:
                    result[server] = {}

                if not spider in result[server]:
                    result[server][spider] = 0

                result[server][spider] += 1

                #print line
                lines_processed += 1

    return result, total_lines_processed, lines_processed


def transform_report_by_spider(report):
    result = {}
    if not isinstance(report, dict):
        report = report[0]
    for server, spider_data in report.items():
        for spider_name, spider_jobs in spider_data.items():
            if spider_name not in result:
                result[spider_name] = {}
            result[spider_name][server] = spider_jobs
    return result


if __name__ == '__main__':
    from dateutil.parser import parse as parse_date
    _date = parse_date(sys.argv[2])
    if len(sys.argv) > 3:
        marker = sys.argv[3]
    else:
        marker = None
    report = main(sys.argv[1], _date, marker)

    from pprint import pprint

    pprint(report)

    pprint(transform_report_by_spider(report))
