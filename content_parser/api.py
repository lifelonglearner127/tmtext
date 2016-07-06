import os, flask, requests
from flask import Flask, request
import parser

app = Flask(__name__)

MC_API = '/'

@app.route('/parse', methods = ['GET'])
def parse():
    url = request.args.get('url')

    if not url:
	return 'Please specify the url of an xml file to parse<br/><br/>e.g. http://matt-test.contentanalyticsinc.com:8888/parse?url=http://&lt;server&gt;/&lt;path-to-file&gt;/filename.xlsx'

    filename = url.split('/')[-1]

    content = requests.get(url).content

    response = parser.parse(content)

    #requests.post(MC_API, data=response, headers={'Content-Type': 'application/json'})
    return flask.jsonify(response)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=8888)
