from apscheduler.schedulers.blocking import BlockingScheduler
from app import show_all, fetch_and_save_tweets
from mail import *
from spider import save_scraped;



sched = BlockingScheduler()

# interval for checking if a mail has to be sent

@sched.scheduled_job('interval', hours=2)
def timed_job():
	mail()
	
	

@sched.scheduled_job('interval', minutes=30)
def timed_fetch_data():
	#fetch_and_save_tweets()
	save_scraped()


sched.start()

# in order to have timed_job() running constantly the app needs to receive multiple pings
# going to https://uptimerobot.com we can set these pings