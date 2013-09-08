#!/usr/bin/python

import twitter
from datetime import datetime, MINYEAR, MAXYEAR
from pprint import pprint

class CrawlTweets():

	def __init__(self):
		self.api = twitter.Api(consumer_key='r5w2kkRf41hqVLhkDyZOQ', consumer_secret='ikmZYINui6evYZZkkyqHbVQa3LKJIaaSy6LJm2cVUk', \
			access_token_key='1786251122-Nmr09nFArsRKRKUdvKyyyA3RCtVTvNz0eLdYLLc', access_token_secret='0AQ3rA19GQBMdmxTasRBxOTtuYPgNB7KtnGextKQ')
		self.api.VerifyCredentials()


	# convert unicode date (as returned by twitter api) to datetime object
	@staticmethod
	def stringToDate(unicode_date):
		return datetime.strptime(unicode_date, "%a %b %d %H:%M:%S +0000 %Y")

	@staticmethod
	def dateToString(date):
		return date.strftime("%b %d, %Y")

	# get tweets for user with screen name username, that were published between min_date and max_date
	# return list of dictionaries containing number of tweets for each day in the time interval and total number of tweets in the interval

	# note: username without the "@" prefix
	def getTweets(self, brand, username, min_date = datetime(MINYEAR, 1, 1), max_date = datetime(MAXYEAR, 12, 31)):

		results = []

		statuses = self.api.GetUserTimeline(screen_name=username, count=100)
		day_views = {}

		while CrawlTweets.stringToDate(statuses[-1].created_at) > min_date:
			statuses += self.api.GetUserTimeline(screen_name=username, count=100)

		all_tweets = filter(lambda x : (CrawlTweets.stringToDate(x.created_at) <= max_date) \
			and (CrawlTweets.stringToDate(x.created_at) >= min_date), statuses)
		all_tweets_count = len(all_tweets)

		# count tweets for each day
		date_count = {}
		for tweet in statuses:
			if tweet.created_at not in date_count:
				date_count[tweet.created_at] = 0
			else:
				date_count[tweet.created_at] += 1

		# get additional info about this user
		data = self.getDataForUser(username)
		followers = data['followers']
		following = data['following']
		total_tweets = data['tweets']

		for tweet in statuses:
			ret_elem = {}
			ret_elem['brand'] = brand
			ret_elem['date'] = self.dateToString(self.stringToDate(tweet.created_at))
			ret_elem['all_tweets_count'] = all_tweets_count
			ret_elem['tweets_count'] = date_count[tweet.created_at]
			ret_elem['followers'] = followers
			ret_elem['following'] = following
			ret_elem['total_tweets'] = total_tweets
			results.append(ret_elem)

		return results


	# get additional data for a user: nr of followers, nr of following, total nr of tweets
	# return dictionary containing this data
	# all in one function to minimize nr of requests

	# note: username without the "@" prefix
	def getDataForUser(self, username):
		users = self.api.UsersLookup(screen_name = ["amazon"])
		if users:
			user = users[0]
		else:
			return {'followers': None, 'following': None, 'tweets': None}

		followers = user.GetFollowersCount()
		following = user.GetFriendsCount()
		tweets = user.GetStatusesCount()

		ret = {}
		ret['followers'] = followers
		ret['following'] = following
		ret['tweets'] = tweets

		return ret


ct = CrawlTweets()
tweets = ct.getTweets("Amazon", "amazon", datetime(2013, 04, 15), datetime(2013, 05, 15))
pprint(tweets)