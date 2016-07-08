import os, flask, requests
from flask import Flask, request

app = Flask(__name__)

MC_API = '/'

@app.route('/parse', methods = ['GET'])
def parse():
    url = request.args.get('url')

    if not url:
        return 'Please specify the url of an xml file to parse<br/><br/>e.g. http://matt-test.contentanalyticsinc.com:8888/parse?url=http://&lt;server&gt;/&lt;path-to-file&gt;/filename.xlsx'

    filename = url.split('/')[-1]

    content = requests.get(url).content

    # Write the content to a local file with the same name
    f = open(filename, 'w')
    f.write(content)
    f.close()

    err = os.system('python parser.py %s %s' % (filename, MC_API))
    if err == 0:
        return filename + ' is being parsed and the result will be sent to ' + MC_API
    else:
        return 'an error occurred'

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=8888)
