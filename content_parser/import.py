import os, re, json
from ftplib import FTP
from StringIO import StringIO
import pg_parser

c = open('config.txt', 'r')
config = json.loads(c.read())
c.close()

if config['import'] == 'FTP':
    ftp = FTP(config['ip']) 
    ftp.login(config['user'], config['passwd'])
    ftp.cwd(config['path'])

    filenames = ftp.nlst()

    for filename in filenames:
        if not re.match('.*\.xml', filename):
            continue

        r = StringIO() 
        ftp.retrbinary('RETR ' + filename, r.write)

        if config['parser'] == 'P&G':
            pg_parser.setup_parse(r.getvalue(), config['push'])

    ftp.quit()
