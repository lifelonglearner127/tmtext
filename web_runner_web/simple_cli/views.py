from django.shortcuts import render
from django.http import HttpResponse
import requests

def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")

def web_runner_status(request):
    """Display the status of Web Runner and Scrapyd"""

    import pdb; pdb.set_trace()
    try:
        req = requests.get('http://localhost:6543/status/')
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
