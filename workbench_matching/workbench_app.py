#!/usr/bin/python
from flask import Flask, jsonify, abort, request, render_template, Response, g
import random
import urllib2
from lxml import html

import sqlite3

app = Flask(__name__)
urls = []
MAX_RETRIES = 3

# TODO: do this better
current_urls = []
# TODO: do this better
conn = None


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
def init():
    # global g
    with app.app_context(): 
        global conn
        conn = sqlite3.connect('matching_feedback.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (id integer primary key, url1 text, url2 text, product_matches boolean, name_matches boolean, image_matches boolean, 
                    manufacturer_matches boolean, category_matches boolean, seen boolean)''')
        conn.commit()
        import_matches()

init()


@app.route('/workbench', methods = ['GET', 'POST'])
def display_match():
    # store form data
    if request.form:
        store_feedback()

    global current_urls
    with app.app_context():
        matches = urls.pop()
        g.urls = matches
        current_urls = matches
        print current_urls
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


def insert_feedback(urls, features_dict):
    '''
    :param urls: list of the 2 urls
    :param features_dict: *immutable* dict of features and yes/no (matches or not) for each
    '''

    url1 = urls[0]
    url2 = urls[0]
    keys2cols = {
    'product': 'product_matches',
    'name' : 'name_matches', 
    'image' : 'image_matches',
    'manufacturer' : 'manufacturer_matches',
    'category' : 'category_matches'
    }
    global conn
    c = conn.cursor()
    columns = []
    values = []
    for key in keys2cols:
        columns.append(keys2cols[key])
        if key not in features_dict:
            values.append(None)
        else:
            values.append(True if features_dict[key]=='yes' else False)
    c.execute('''INSERT INTO TABLE matches
             (url1, url2, %s, %s, %s, %s, %s, seen)
             values %s, %s, %s, %s, %s, %s, %s)''', (columns + current_urls[0] + current_urls[1] + values))
    conn.commit()


def store_feedback():
    print request.form
    global current_urls
    with app.app_context():
        for key in request.form:
            print current_urls
            # insert_feedback(current_urls, request.form)
    print request

if __name__ == '__main__':
    app.run(port = 8080, threaded = True, debug=True)