import re
# import requests


def get_data(request_arguments):
    url = request_arguments['url']
    return re.findall(r'http://www\.(.*)\.com.*', url)[0]
    