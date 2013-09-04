#!/usr/bin/python

from apiclient.discovery import build
from optparse import OptionParser
from datetime import datetime, MINYEAR, MAXYEAR, timedelta

from pprint import pprint
import csv

class Utils:

	# return a list of dates for all days in a date range
	@staticmethod
	def daterange(start_date, end_date):
		for n in range(int ((end_date - start_date).days)):
			yield start_date + timedelta(n)

	# read site youtube usernames from csv input file
	@staticmethod
	def input_sites(filename):
		csvfile = open(filename, "rw")

		sites = []

		sitesreader = csv.reader(csvfile, delimiter=',')
		for row in sitesreader:
			site = {}

			#TODO: maybe work with name indexes (insted of number)
			site["site"] = row[1]
			site["yt_username"] = row[3]
			sites.append(site)

		return sites

	# output results to csv file
	@staticmethod
	def output_all(filename):
		pass

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


	# get uploaded videos from a certain channel (given by channel username) published between certain dates
	def get_uploads(self, channel_username, min_date = datetime(MINYEAR, 1, 1), max_date = datetime(MAXYEAR, 12, 31)):
		channel_id = self.youtube_search_channel(channel_username)
		if not channel_id:
			return

		channels_response = self.youtube.channels().list(part = "contentDetails", id = channel_id).execute()

		for channel in channels_response["items"]:
			uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

			ret = {}
			for date in Utils.daterange(min_date, max_date):
				ret[date.strftime("%b %d, %Y")] = 0

			total_videos = 0
			total_views = 0
			lasttime = min_date

			next_page_token = ""


			# stop if we reached the minimum date (assuming results are given in reverse chronological order)
			while (next_page_token is not None) and (lasttime >= min_date):
				playlistitems_response = self.youtube.playlistItems().list(playlistId=uploads_list_id, \
					part="snippet", maxResults=50, pageToken=next_page_token).execute()

				for playlist_item in playlistitems_response["items"]:
					title = playlist_item["snippet"]["title"]
					video_id = playlist_item["snippet"]["resourceId"]["videoId"]
					#video = self.get_video(video_id)
					video_response = self.youtube.videos().list(part="snippet,statistics", id = video_id).execute()
					video = video_response["items"][0]

					title = video["snippet"]["title"]
					views = int(video["statistics"]["viewCount"])

					lasttime_iso = playlist_item["snippet"]["publishedAt"]
					lasttime = datetime.strptime(lasttime_iso, "%Y-%m-%dT%H:%M:%S.000Z")

					if (lasttime < min_date):
						break

					# check if the date is also smaller than max date
					if lasttime <= max_date:

						date = lasttime.strftime("%b %d, %Y")
						# if date not in ret:
						# 	ret[date] = 1
						# else:
						# 	ret[date] += 1
						ret[date] += 1
						total_videos += 1

						ret[title] = views
						total_views += views


				next_page_token = playlistitems_response.get("tokenPagination", {}).get("nextPageToken")

			ret['YT_All_Videos'] = total_videos
			ret['YT_All_Views'] = total_views
    		return ret




if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("--date1", dest="date1", help="Minimum publish date")
	parser.add_option("--date2", dest="date2", help="Maximum publish date")
	(options, args) = parser.parse_args()

	date1 = datetime.strptime(options.date1, "%Y-%m-%d")
	date2 = datetime.strptime(options.date2, "%Y-%m-%d")

  	crawler = CrawlUploads()

  	sites = Utils.input_sites("Brand Retail Import Data.csv")

  	results = []
  	for site in sites:
  		res_site = crawler.get_uploads(site["yt_username"], min_date=date1, max_date=date2)
  		#res_site["Brand"] = site["site"]
  		results.append(res_site)

  	Utils.output_all(results)