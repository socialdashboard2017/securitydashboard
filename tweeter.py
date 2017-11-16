# # from nltk.corpus import stopwords
import re
import sys
import string
import tweepy
import datetime
import xlsxwriter
import inspect, os
from tweepy import OAuthHandler
from models_tweet import tweets as Tweets
from textblob import TextBlob
from dotenv import load_dotenv, find_dotenv
from spider import *
import urllib.request, json
from models_profiles import profiles


if not os.getenv('HEROKU'):
		load_dotenv(find_dotenv())

class TwitterClient(object):
		'''
		Generic Twitter Class for sentiment analysis.
		'''

		tweetObj = {};

		def __init__(self):
				'''
				Class constructor or initialization method.
				'''
				
				consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
				consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
				access_token = os.getenv('TWITTER_ACCESS_TOKEN')
				access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

				print ("consumer_key = " + str(os.getenv('TWITTER_CONSUMER_KEY')))
				print ("consumer_secret = " + str(os.getenv('TWITTER_CONSUMER_SECRET')))
				print ("access_token = " + str(os.getenv('TWITTER_ACCESS_TOKEN')))
				print ("access_token_secret =" + str(os.getenv('TWITTER_ACCESS_TOKEN_SECRET')))


				# attempt authentication
				try:
						# create OAuthHandler object
						self.auth = OAuthHandler(consumer_key, consumer_secret)
						# set access token and secret
						self.auth.set_access_token(access_token, access_token_secret)
						# create tweepy API object to fetch tweets
						self.api = tweepy.API(self.auth)
				except:
						print("Error: Authentication Failed")

		def cve(tweet):
		
				cve_vuln = ""
				if 'CVE-' in tweet:
						# CVE-2017-7728
						# cve_vuln = name.split('CVE')[1][1:10]
		
						cve_vuln = tweet.split('CVE')[1]
						# print (cve_vuln)
						cve_vuln = 'CVE' + cve_vuln.split(' ')[0]
						print("printing: "+str(get_cvss(cve_vuln)))
		
				else:
						# cve_vuln = ''
						if score <= -0.05:
								print("critical")
						elif score in range(-0.005, -0.1):
								print("High")
		
				return (cve_vuln)
		
		def get_cvss(cve_vuln):
		
				if cve_vuln != '':
		
						link = []
						x = str('https://nvd.nist.gov/vuln/detail/CVE-' + cve_vuln)
						link.append(x)
						page = getpage(link)
						bs4Obj = BeautifulSoup(page[0], 'html.parser')
						vuln_score = bs4Obj.find("a",
																		 {'href': lambda x: x and x.startswith('/vuln-metrics/cvss/v3-calculator?name')})
		
						if vuln_score is None:
								vuln_score = 'Awaiting Analysis'
		
						else:
								vuln_score = vuln_score.get_text()
								vuln_score = vuln_score.replace('\r', '')
								vuln_score = vuln_score.replace('\n', '')
								vuln_score = vuln_score.replace(' ', '')
		
						return vuln_score

		def clean_tweet(self, tweet):
				'''
				Utility function to clean tweet text by removing links, special characters
				using simple regex statements.
				'''
				return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())

		def get_tweet_sentiment(self, tweet):
				'''
				Utility function to classify sentiment of passed tweet
				using textblob's sentiment method
				'''
				# create TextBlob object of passed tweet text
				analysis = TextBlob(self.clean_tweet(tweet))
				# set sentiment
				if analysis.sentiment.polarity > 0:
						# print analysis.sentiment.polarity
						return 'positive'
				elif analysis.sentiment.polarity == 0:
						return 'neutral'
				else:
						return 'negative'

		def get_sentiment_score(self, tweet):
				'''
				Utility function to classify sentiment of passed tweet
				using textblob's sentiment method
				'''
				# create TextBlob object of passed tweet text
				analysis = TextBlob(self.clean_tweet(tweet))
				# set sentiment
				return analysis.sentiment.polarity

		def set_negative_sentiment_score(self, critical_keyword, high_keyword, tweetList):

				for tweet in tweetList:
						if tweet['sentiment'] == 'negative':
								for i in range(len(critical_keyword)):
										keyword = critical_keyword[i]

										tweetText = tweet['text'].split()
										noOfKeywords = tweetText.count(keyword)

										if 'CVE' not in tweet['text'] and noOfKeywords > 0:
												print("Critical Before: " + str(tweet))
												tweet['score'] = str(float(tweet['score']) - 0.2)
												print("Critical: " + str(tweet))
												break


								for i in range(len(high_keyword)):
										keyword = high_keyword[i]

										noOfKeywords = tweetText.count(keyword)

										if 'CVE' not in tweet['text'] and noOfKeywords > 0:
												print("High Before: " + str(tweet))
												tweet['score'] = str(float(tweet['score']) - 0.1)
												print("High: " + str(tweet))
												break

								# if float(tweet['score']) >= -0.05:
								#     tweet['score'] = str(tweet['score']) + " [critical]"
								# elif float(tweet['score']) <= -0.05 or float(tweet['score']) >= -0.1:
								#     tweet['score'] = str(tweet['score']) + " [high]"

				return tweetList

		def get_tweets(self, screen_name, query, count):
				'''
				Main function to fetch tweets and parse them.
				'''
				#print (self.api.rate_limit_status())
				tweets = []  # empty list to store parsed tweets
				dateFilteredTweets = []  # empty list to store date wise filtered tweets
				tagFilteredTweets = []  # empty list to store tag based  tweets

				# Date limit initialization to filter tweets
				startDate = datetime.datetime(2017, 1, 1, 0, 0, 0)
				endDate = datetime.datetime(2017, 7, 16, 0, 0, 0)

				try:
						# call twitter api to fetch tweets
						#fetched_tweets = self.api.user_timeline(screen_name, count=count)
						#fetched_tweets = self.api.user_timeline(screen_name, 10)
						fetched_tweets = self.api.user_timeline(screen_name = screen_name,count=5)
						# fetch tweets between startDate and endDate
						print ("Fetching tweets for " + screen_name)
						for tweet in fetched_tweets:
								if tweet.created_at > startDate:
								#if tweet.created_at < endDate and tweet.created_at > startDate:
										dateFilteredTweets.append(tweet)
						'''
						# fetch more tweets if all retrieved tweets are earlier than endDate limit
						while (fetched_tweets[-1].created_at > startDate):
								print("Last Tweet @", fetched_tweets[-1].created_at, " - fetching some more")
								fetched_tweets = self.api.user_timeline(screen_name, max_id=fetched_tweets[-1].id)
								no_of_date_filtered_tweets = len(dateFilteredTweets)
								for tweet in fetched_tweets:
										if tweet.created_at < endDate and tweet.created_at > startDate and no_of_date_filtered_tweets < count:
												dateFilteredTweets.append(tweet)

                # Break out of loop once tweets reaches or exceed expected number
								if len(dateFilteredTweets) >= count:
									break;
						'''
						# Get all tweets from dateFilteredTweets based on the given tags in query list and store in tagFilteredTweets list
						for tweet in dateFilteredTweets:
								for i in range(len(query)):
										tag = query[i]

										tweetText = tweet.text.split()
										noOfTags = tweetText.count(tag)

										if noOfTags > 0:
												tagFilteredTweets.append(tweet)
												break

						# Get all tweets from tagFilteredTweets and store in tweets dictionay to finally return to main method
						for tweet in tagFilteredTweets:
								# empty dictionary to store required params of a tweet
								parsed_tweet = {}


								# saving text of tweet
								parsed_tweet['text'] = tweet.text
								# saving sentiment of tweet
								parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
								# saving score of tweet
								parsed_tweet['score'] = self.get_sentiment_score(tweet.text)
								# saving created date of tweet
								parsed_tweet['gvndate'] = tweet.created_at
								# saving URL key of tweet
								parsed_tweet['url'] = "https://twitter.com/statuses/"+tweet.id_str

								tweets.append(parsed_tweet)
								# for url in tagFilteredTweets["entities"]["urls"]:
								#   print " - found URL: %s" % url["expanded_url"]
						# return parsed tweets
						return tweets

				except tweepy.TweepError as e:
						# print error (if any)
						print("Error : " + str(e) + " " + str(sys.exc_info()[2]))
						


def get_profile(profile_name):
	return db.session.query(profiles).filter_by(name=profile_name).first()


def fetch_and_save_tweets(profile_name):
	#check_on_all_tables()
	
	negativeDictionary = getNegativeTweets(profile_name, no_of_tweets=70)

	
	#print (negativeDictionary,"negativeDictionary")
	profile = get_profile(profile_name)
	#print (profile)
	if profile:
		for key, value in negativeDictionary.items():
			tweets = value[0]
			scores = value[1]
			urls = value[2]

			for tweet, tweet_score, tweet_url in zip(tweets, scores, urls):
				decoded_tweet = tweet.decode('utf-8')
				tweet_cve = get_cve(decoded_tweet)
				tweet_score = get_tweet_score(decoded_tweet, tweet_score)
				exists = db.session.query(Tweets).filter_by(tweet=decoded_tweet).first() is not None
				print (exists, "exists")
				if exists == False:
					formatted_tweet = {
						'tweet': decoded_tweet ,
						'score': tweet_score,
						'url': tweet_url,
						'date': key,
						'cve': tweet_cve,
						'profile_id': profile.id
					}
					current_tweet = Tweets(**formatted_tweet)
					db.session.add(current_tweet)
		
		db.session.commit()







# # Fetching tweets from all profiles

def fetchallprofiles():
	saved_profiles = db.session.query(profiles).all()
	for profile in saved_profiles:
		fetch_and_save_tweets(profile.name)
	return "done"



# # creating object of TwitterClient Class
api = TwitterClient()

#def fetchtweets(profile_name):
def fetchtweets(profile_name='Inj3ct0r'):	        
		'''
		# # creating and initializing output xlsx file containg all formatted tweets and stored in current directory.
		workbook = xlsxwriter.Workbook(
				os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe()))) + '/trail.xlsx')
		worksheet = workbook.add_worksheet()
		# creating bold formatted text for xlsx cell
		bold = workbook.add_format({'bold': True})
		'''

		# # array of TAGs used to filter tweets
		query = ["#cybersecurity", "cybersecurity", "#infosec", "infosec", "#security", "security", "#cybercrime",
						"cybercrime", "#cyberwar", "cyberwar", "#0dayexploits", "0dayexploits", "#0daytoday", "0daytoday",
						"#vulnerability", "vulnerability", "#struts", "struts", "#struts2", "struts2", "#wordpress", "wordpress", "#Apache", "Apache"]

		# # array of critical words for negative score (-0.2)
		critical_keyword = ["Authenticate", "inject", "vodafone", "remote", "rce"]

		# array of high words for negative score (-0.1)
		high_keyword = ["Xss", "cross site scripting", "cross-site scripting", "encryption", "cypher", "crypto",
										"input validation",
										"traversal", "session", "permission", "privileges", "resource", "ddos", "url redirection",
										"hard-coded", "hard coded"]

		# # calling function to get tweets
		tweets = api.get_tweets(profile_name, query, count=70) or []
		tweets = api.set_negative_sentiment_score(critical_keyword, high_keyword, tweets)




		ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
	

		return {
			'ntweets': ntweets
		}

def get_cve(tweet): 
		cve_tweet = ""
		if 'CVE-' in tweet:
				cve_tweet = tweet.split('CVE')[1]
				cve_tweet = 'CVE' + cve_tweet.split(' ')[0]
		return cve_tweet

def getNegativeTweets(profile_name, no_of_tweets):
		
		ntweets = fetchtweets(profile_name)['ntweets'][:no_of_tweets]
		
		negativeDictionary = {}
		for index, tweet in enumerate(ntweets):
				given_date = tweet['gvndate'].strftime('%b %m %Y')
				tweet_text = tweet['text'].encode('utf-8')
				if index > 0:
						tweet_text_array.append(tweet_text)
						tweet_score_array.append(tweet['score'])
						tweet_url_array.append(tweet['url'])
						negativeDictionary[given_date] = [tweet_text_array, tweet_score_array, tweet_url_array]
				else:
						tweet_text_array = [tweet_text]
						tweet_score_array = [tweet['score']]
						tweet_url_array = [tweet['url']]
						negativeDictionary[given_date] = [tweet_text_array, tweet_score_array, tweet_url_array]
		return negativeDictionary
						

# print(negativeDictionary)
def get_cvss_rating(cve_score):
		cve_rating = ''
		try:
				cve_score = float(cve_score)
				if (0.0 <= cve_score <= 3.9):
						cve_rating = 'low'
				elif (4.0 <= cve_score <= 6.9):
						cve_rating = 'medium'
				elif (7.0 <= cve_score <= 8.9):
						cve_rating = 'high'
				elif (9.0 <= cve_score <= 10.0):
						cve_rating = 'critical'
		except:
				print('An error occured while getting cve rating')
		finally:
				return cve_rating

def get_tweet_score(text, score): 
		cve = get_cve(text)
		print('cve', cve)
		tweet_score = ''
		if cve:
				link = []
				x = str('https://nvd.nist.gov/vuln/detail/' + cve)
				link.append(x)
				page = getpage(link)
				bs4Obj = BeautifulSoup(page[0], 'html.parser')
				tweet_cve_score = bs4Obj.find("a", {'href': lambda x: x and x.startswith('/vuln-metrics/cvss/v3-calculator?name')})

				if tweet_cve_score is None:
						tweet_cve_score = 'Awaiting Analysis'

				else:
						tweet_cve_score = tweet_cve_score.get_text()
						
						tweet_cve_score = tweet_cve_score.replace('\r', '').replace('\n', '').replace(' ', '')
				
				tweet_score = '{} [{}]'.format(tweet_cve_score,  get_cvss_rating(tweet_cve_score))
		
		else:
				if float(score) >= -0.05:
						tweet_score = str(score) + " [critical] "
				elif float(score) <= -0.05 or float(score) >= -0.1:
						tweet_score = str(score) + " [high] "

		return tweet_score.replace('SS', '')


def twitter_user_exist(profile_name):
	try:
		conn = urllib.request.urlopen("https://twitter.com/" + profile_name)
		return True
	except urllib.error.HTTPError as e:
		return False
		# data = json.loads(url.read().decode())
		#return url.getcode() == 200
		# return data["reason"] == "taken" or data["reason"] == "your_name"

		

		
