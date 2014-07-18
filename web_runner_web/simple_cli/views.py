from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings

import requests

def index(request):
#    return HttpResponse("Here will be the main page")
    return render(request, 'simple_cli/index.html')


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

def web_runner_logs(request):
    """Display web runner logs"""

    context = {'logfiles': settings.WEB_RUNNER_LOG_FILES}
    return render(request, 'simple_cli/show_logs.html', context)


def web_runner_logs_view(request, logfile_id):
    """Return the log files as files"""
    
    logfiles = settings.WEB_RUNNER_LOG_FILES
    try:
        filename = logfiles[int(logfile_id)]
    except IndexError:
        raise Http404("File does not exists")
        
    try:
        fh = open(filename, 'r')
    except:
        raise Http404("Issues open the log file")

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    response.write(fh.read())

    return response


def web_runner_lastrequests(request, n=None):
    """Display a table with the last n requests"""
 
    # TODO: Method with a lot of things to improve:
    # * manage max lines
    # * max lines should be in simple_cli
    # * handle errors calling the REST API
    # * None fields should be displayed empty
    # * Creation date format
    # * TZ in creation date
    try:
        base_url = settings.WEB_RUNNER_BASE_URL
        url = '%slast_requests' % base_url
        req = requests.get(url)
        error = False
    except requests.exceptions.RequestException as e:
        error = True

    context = {'last_requests': req.json()}
    return render(request, 'simple_cli/last_requests.html', context)
    
    return HttpResponse("Hola")
    

# vim: set expandtab ts=4 sw=2:
