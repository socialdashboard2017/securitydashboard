import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime
import pytz

from flask import session
from app import db

from models import *
from models_delta import *
from models_tweet_delta import *
from models_tweet import tweets as Tweets

db.create_all()
import sys


tz = pytz.timezone('Europe/Rome')

now = datetime.now(tz)

now = now.strftime("%Y-%m-%d %H:%M")


def check_vulns_mail():

	db.create_all()

	mail_text = []
	
	record = vulns.query.filter(vulns.score.startswith('Critic'))

	past = db.session.query(delta)

	mypast = []

	for el in past:

		mypast.append(el.name)


	
	for el in record:
	

		if (el.name) not in mypast:


			mail_text.append(el.name)
			
	
	for el in record:

		row = delta(name = el.name, date = el.date)	

		db.session.add(row)

	db.session.query(delta).delete()

	db.session.commit()


	return mail_text
	
def check_tweets_mail():
	
	db.create_all()
	mail_text = []
	record = Tweets.query.filter(Tweets.score.contains('critical'))

	past = db.session.query(tweet_delta)
	mypast = [ el.name for el in past]
	
	for el in record:	
		if (el.name) not in mypast:
			mail_text.append(el.name)

	for el in record:
		row = tweet_delta(name = el.name, date = el.date)
		db.session.add(row)
	db.session.query(tweet_delta).delete()
	db.session.commit()
	
	return mail_text

def mail():
	mail_text = check_vulns_mail()[:5] + check_tweets_mail()[:5]
	if mail_text != []:

		fromaddr = "socialdashboard2017@gmail.com"
		toaddr = "socialdashboard@tutanota.com"
		msg = MIMEMultipart()
		msg['From'] = fromaddr
		msg['To'] = toaddr
		msg['Subject'] = "Security update " + str ( now )

		body = [str(mail_text)[1:-1].replace('"', '')]
		body = eval(body[0])
		intro = str('Ciao,' + '\n' + '\n' + 'di seguito trovi gli ultimi updates su vulnerabilities ed exploits presenti sul web.'  + '\n') + str('Saluti' + '\n'  + '\n' + 'Paolo Pietro Pavlu')


		new_list = [intro]
		for el in body:
			if isinstance(el, list):
				new_list.append(str(el[0]) + ': ' + str(el[1]) + '\n') 
			else:
				new_list.append(el + '\n')
			
		body = ('\n'.join((new_list)))

		msg.attach(MIMEText(body, 'plain'))

		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

		server.login('socialdashboard2017@gmail.com', "Progettoformativo")
		text = msg.as_string()
		server.sendmail(fromaddr, toaddr, text)
		server.quit()

		print ('mail sent')
