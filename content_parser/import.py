import os, re, json
from ftplib import FTP
import parser

c = open('config.txt', 'r')
config = json.loads(c.read())
c.close()

if config['import'] == 'FTP':
	ftp = FTP(config['ip']) 
	ftp.login(config['user'], config['passwd'])
	ftp.cwd(config['path'])

	filenames = ftp.nlst()

	# Download all xml files from the given directory
	for filename in filenames:
		if not re.match('.*\.xml', filename):
			continue

		f = open(filename, 'w')
		ftp.retrbinary('RETR ' + filename, f.write)
		print 'downloaded ' + filename
		f.close()

	ftp.quit()

for filename in os.listdir('.'):
	if re.match('.*\.xml', filename):
		if config['parser'] == 'P&G':
			# deletes file after parsing
			parser.parse(filename, config['push'])
