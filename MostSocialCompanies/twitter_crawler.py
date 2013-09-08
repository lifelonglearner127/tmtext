#!/usr/bin/python

import twitter
from datetime import datetime
from pprint import pprint

class CrawlTweets():

	def __init__(self):
		self.api = twitter.Api(consumer_key='r5w2kkRf41hqVLhkDyZOQ', consumer_secret='ikmZYINui6evYZZkkyqHbVQa3LKJIaaSy6LJm2cVUk', \
			access_token_key='1786251122-Nmr09nFArsRKRKUdvKyyyA3RCtVTvNz0eLdYLLc', access_token_secret='0AQ3rA19GQBMdmxTasRBxOTtuYPgNB7KtnGextKQ')
		self.api.VerifyCredentials()


	# convert unicode date (as returned by twitter api) to datetime object
	@staticmethod
	def toDate(unicode_date):
		return datetime.strptime(unicode_date, "%a %b %d %H:%M:%S +0000 %Y")

	def getTweets(self, username, min_date, max_date):
		statuses = self.api.GetUserTimeline(screen_name=username, count=100)

		while CrawlTweets.toDate(statuses[-1].created_at) > min_date:
			statuses += self.api.GetUserTimeline(screen_name=username, count=100)
		return filter(lambda x : (CrawlTweets.toDate(x.created_at) <= max_date) \
			and (CrawlTweets.toDate(x.created_at) >= min_date), statuses)


ct = CrawlTweets()
tweets = ct.getTweets("@amazon", datetime(2013, 04, 15), datetime(2013, 05, 15))
pprint([(tweet.text, tweet.created_at) for tweet in tweets])
