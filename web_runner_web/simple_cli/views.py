from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import requests

def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")

def web_runner_status(request):
    """Display the status of Web Runner and Scrapyd"""

    try:
        base_url = settings.WEB_RUNNER_BASE_URL
        url = '%sstatus/' % base_url
        req = requests.get(url)
        web_runner_error = False
    except requests.exceptions.RequestException as e:
        web_runner_error = True

    
    error = {"webRunner": False, 
          "scrapyd_operational": "Don't know", 
          "spiders": "Don't know", 
          "scrapyd_projects": None, 
          "scrapyd_alive": "Don't know",
        }

    if web_runner_error:
        status = error
    else:
        if req.status_code == 200:
            status = req.json()
        else:
            status = error
    return render(request, 'simple_cli/web_runner_status.html', status)

# vim: set expandtab ts=4 sw=2:
