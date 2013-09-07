#!/usr/bin/python

import twitter

#api = twitter.Api()

api = twitter.Api(consumer_key='r5w2kkRf41hqVLhkDyZOQ', consumer_secret='ikmZYINui6evYZZkkyqHbVQa3LKJIaaSy6LJm2cVUk', access_token_key='1786251122-Nmr09nFArsRKRKUdvKyyyA3RCtVTvNz0eLdYLLc', access_token_secret='0AQ3rA19GQBMdmxTasRBxOTtuYPgNB7KtnGextKQ')

api.VerifyCredentials()

# doesn't work:
username = "@Amazon"
statuses = api.GetUserTimeline(username)
print [s.text for s in statuses]