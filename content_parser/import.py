import os, re, xml, json, requests
from ftplib import FTP
from StringIO import StringIO
import pg_parser
from api_lib import *

c = open('config.txt', 'r')
config = json.loads(c.read())
c.close()

if config['import'] == 'FTP':
    ftp = FTP(config['ip']) 
    ftp.login(config['user'], config['passwd'])
    ftp.cwd(config['path'])

    filenames = ftp.nlst()

    # Only parse the most recent xml file (the last one in the list)
    #filename = filter(lambda f: re.match('.*\.xml', f), filenames)[-1]
    filenames = filter(lambda f: re.match('.*\.xml', f), filenames)

    for filename in filenames:
        r = StringIO()
        ftp.retrbinary('RETR ' + filename, r.write)

        token = request_token(filename)
        print token

        if config['parser'] == 'P&G':
            try:
                pg_parser.setup_parse(r.getvalue(), config['push'], token)

            except (ValueError, xml.etree.ElementTree.ParseError) as e:
                print 'Error parsing %s with %s template parser: %s' % (filename, config['parser'], e.message)
                report_status(token, 4)

            except Exception as e:
                print e
                report_status(token, 4)

    ftp.quit()
