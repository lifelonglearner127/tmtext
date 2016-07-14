import re, xml, requests, threading
from flask import Flask, request, jsonify, abort
import parser

app = Flask(__name__)

MC_API = '/'

ERR_MESSAGE = 'Please specify the url of an xml file to parse<br/><br/>e.g. http://matt-test.con    tentanalyticsinc.com:8888/parse?url=http://&lt;server&gt;/&lt;path-to-file&gt;/filename.xml'

@app.route('/parse', methods = ['GET'])
def parse():
    url = request.args.get('url')

    if not url:
        return ERR_MESSAGE, 400

    filename = url.split('/')[-1]

    if not re.search('\.xml$', filename):
        return ERR_MESSAGE, 400

    r = requests.get(url)

    if not r.status_code == 200:
        return 'not found: ' + url, 404

    content = r.content

    try:
        parser.setup_parse(content, MC_API)
    except (ValueError, xml.etree.ElementTree.ParseError) as e:
        return 'error parsing %s: %s' % (filename, e.message), 400
    except:
        return 'an error occurred', 400

    return filename + ' is being parsed and the result will be sent to ' + MC_API

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=8888)
