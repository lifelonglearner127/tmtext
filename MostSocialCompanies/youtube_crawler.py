#!/usr/bin/python

from apiclient.discovery import build
from optparse import OptionParser
from datetime import datetime, MINYEAR, MAXYEAR, timedelta

from pprint import pprint

class Utils:

	# return a list of dates for all days in a date range
	@staticmethod
	def daterange(start_date, end_date):
		for n in range(int ((end_date - start_date).days)):
			yield start_date + timedelta(n)

class CrawlUploads():
	
	DEVELOPER_KEY = "AIzaSyDOK4_2AvnMXL2vVXAqwtDe0mbVyD39Ndo"
	YOUTUBE_API_SERVICE_NAME = "youtube"
	YOUTUBE_API_VERSION = "v3"

	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

	# search for a channel by username and return its id
	def youtube_search_channel(self, channel_username):

		search_response = self.youtube.search().list(q=channel_username, part="id,snippet").execute()

	  	channels = []

		#TODO: include "channel" option as paramater to search, instead of filtering through them
		for search_result in search_response.get("items", []):
			if search_result["id"]["kind"] == "youtube#channel":
				channels.append(search_result["id"]["channelId"])

		if channels:
			return channels[0]
		else:
			return []

		#print "Channels:\n", "\n".join(channels), "\n"


	# get uploaded videos from a certain channel (given by channel username) published between certain dates
	def get_uploads(self, channel_username, min_date = datetime(MINYEAR, 1, 1), max_date = datetime(MAXYEAR, 12, 31)):
		channel_id = self.youtube_search_channel(channel_username)
		if not channel_id:
			return

		channels_response = self.youtube.channels().list(part = "contentDetails", id = channel_id).execute()

		for channel in channels_response["items"]:
			uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
			#print "Videos in list %s" % uploads_list_id

			# can I rely on chronological order of videos?
			

			ret = {}
			for date in Utils.daterange(min_date, max_date):
				ret[date.strftime("%b %d, %Y")] = 0

			total_videos = 0
			lasttime = min_date

			next_page_token = ""

			#print 'mindate ', min_date, ' maxdate ', max_date, ' lasttime ', lasttime

			# stop if we reached the minimum date (results are given in reverse chronological order)
			while (next_page_token is not None) and (lasttime >= min_date):
			#while next_page_token is not None:
				playlistitems_response = self.youtube.playlistItems().list(playlistId=uploads_list_id, \
					part="snippet", maxResults=50, pageToken=next_page_token).execute()

				print 'length: ', len(playlistitems_response['items'])

				for playlist_item in playlistitems_response["items"]:
					title = playlist_item["snippet"]["title"]
					video_id = playlist_item["snippet"]["resourceId"]["videoId"]
					#views = playlist_item["statistics"]["viewCount"]

					lasttime_iso = playlist_item["snippet"]["publishedAt"]
					lasttime = datetime.strptime(lasttime_iso, "%Y-%m-%dT%H:%M:%S.000Z")

					if (lasttime < min_date):
						break

					# check if the date is also smaller than max date
					if lasttime <= max_date:
						# print "%s (%s)" % (title, video_id)

						# print 'published at:', lasttime

						ret[lasttime.strftime("%b %d, %Y")] += 1
						total_videos += 1


				next_page_token = playlistitems_response.get("tokenPagination", {}).get("nextPageToken")
				#next_page_token = playlistitems_response.get("nextPageToken")


			ret['YT_All_Videos'] = total_videos
    		return ret




if __name__ == "__main__":
  # parser = OptionParser()
  # parser.add_option("--q", dest="q", help="Search term",
  #   default="Google")
  # parser.add_option("--max-results", dest="maxResults",
  #   help="Max results", default=25)
  # (options, args) = parser.parse_args()

  	crawler = CrawlUploads()
  	pprint(crawler.get_uploads("Staples", min_date=datetime(2013, 4, 1), max_date=datetime(2013, 9, 1)))