'''
wrapper for supporting calls to the crawlera api

credentials are saved at ~/.crawlera_credentials as:
usr=...
pwd=...
make sure theres a new line at the end (eg '\n')

'''

import re
from os.path import expanduser
import requests
import urllib


class CrawleraRequest():
	TOP_LVL = 'paygo.crawlera.com'
	PORT = '8010'
	FETCH = '/fetch?url='
	
	def __init__(self, credentials_path='/.crawlera_credentials'):
		self.usr, self.pwd = self.load_creds(credentials_path)
		if self.usr is None or self.pwd is None:
			raise Exception('Credentials not found at: ', credentials_path)
	
	def get_page(self, url):
		
		""" Returns a URL's response as a string. (Or throws HTTP Error codes (eg 404) """
		
		url = 'http://' + self.TOP_LVL + self.FETCH + urllib.quote(url)
		return requests.get(url, auth=(self.usr, self.pwd)).text
		
		
	def load_creds(self, path):
		'''returns the usr and pwd from a credentials file saved at path'''
		home = expanduser('~')
		creds = open(home+path)
		creds_txt = creds.read()
		creds.close()
		usr = re.findall(r'usr *= *([0-9A-Za-z]+?)\n', creds_txt)[0]
		pwd = re.findall(r'pwd *= *([0-9A-Za-z]+?)\n', creds_txt)[0]
		return usr, pwd

# for testing this class stand-alone
def main():
	print('running "main"...')
	# crawlera info
	url='http://www.example.com/'
	cr = CrawleraRequest()
	page = cr.get_page(url)
	print(page)
	
if __name__ == "__main__":
	main()

