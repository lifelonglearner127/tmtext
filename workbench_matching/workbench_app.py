#!/usr/bin/python
from flask import Flask, jsonify, abort, request, render_template, Response
import random
import urllib2
from lxml import html


app = Flask(__name__)
urls = []
MAX_RETRIES = 3

def import_matches(matches_path = "/home/ana/code/tmtext/data/opd_round3/walmart_amazon_28.08_matches.csv"):
    global urls
    with open(matches_path) as f:
        for line in f:
            try:
                (url1, url2) = line.split(",")
            except:
                # ignore no matches
                continue
            # strip part after ?
            url1 = url1.split("?")[0]
            url2 = url2.split("?")[0]
            urls.append((url1, url2))

import_matches()

@app.route('/workbench', methods = ['GET'])
def display_match():
    matches = urls.pop()
    return render_template('workbench.html', matches=matches)

# use this for loading iframes on sites that don't permit iframes?
@app.route('/page/<path:url>', methods = ['GET'])
def serve_page(url):
    req = urllib2.Request(url)
    req.add_header('User Agent', 'Mozilla')
    
    try:    
        resp = urllib2.urlopen(req)
    except:
        resp = None

    # retry if failed
    retries = 0
    while (not resp or resp.code != 200) and retries < MAX_RETRIES:
        try:
            resp = urllib2.urlopen(req)
        except:
            resp = None
        retries += 1
        print "RETRYING"

    if not resp:
        return "ERROR"

    body = remove_scripts(resp.read())

    response = Response(body)
    return response

def remove_scripts(body):
    root = html.fromstring(body).getroottree()
    for element in root.iter("script"):
        element.drop_tree()
    return html.tostring(root)

if __name__ == '__main__':
    app.run(port = 8080, threaded = True)