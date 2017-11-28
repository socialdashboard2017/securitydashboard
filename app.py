import random
from flask import Flask, request, flash, url_for, redirect, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import exists
import telegrambot
import scoring_functions

app = Flask(__name__)

app.config.from_object('config.BaseConfig')

db = SQLAlchemy(app)

from models import vulns, subscriptors

from models_tweet import tweets as Tweets
from models_profiles import profiles, keyword_tags
from spider import save_scraped
from technologies import *

import dashboard

# db.drop_all()
from tweeter import getNegativeTweets, get_cve, get_cvss_rating, get_tweet_score, twitter_user_exist,fetchallprofiles,fetch_and_save_tweets, get_profile
db.create_all()

def ssl_required(fn):
		@wraps(fn)
		def decorated_view(*args, **kwargs):
				#if request.url.startswith("http://"):
				#		return redirect(request.url.replace("http://", "https://"))
				#else:
				#		return fn(*args, **kwargs)
				return fn(*args, **kwargs)
		return decorated_view

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session.get('logged_in'):
			return f(*args, **kwargs)
		else:
			#flash('You need to login first.')
			#return redirect(url_for('do_admin_login'))
			return render_template('login.html')
	return wrap

from spider import allDict, allSource, cve, get_link

import datetime

now = datetime.datetime.now()

from dashboard import *

def check_on_all_tables():
	total_tables_length = len(db.session.query(vulns).all()) + len(db.session.query(Tweets).all())
	
	#if total_tables_length >= 9000:
	#	db.session.query(vulns).delete()
	#	db.session.query(Tweets).delete()
	#	print('Deleting all records since total table length is >= 9000')


#DEBUG JOBS
#MAIN
@app.route('/debugjob/<action>')
def show_debugjob(action=""):
	output = "Done"
	if action=="social":
		output = fetchallprofiles()
	if action=="blogs":
		save_scraped()	
		output = "done"
	if action=="telegram":
		secbot = telegrambot.BotHandler("351082352:AAHLBZW4ObbsMVHh4lrcwZOVHmvKsfyM59E")
		output = secbot.registerHook()
	if action=="technologies-show":
		output=show_technologies()
	if action=="test-bot-vulns":
		vulns=dashboard.fetchBlogVulns(5)
		for vuln in vulns:
			#print (vuln['url'])
			message = "(" + vuln['date'].strftime('%d, %b %Y') + ") " + vuln['name'][0] + " - " + vuln['cve'] + " (Score:" + vuln['score'] +  ") <a href='" +  vuln['name'][1] + "'>View</a>"
			print (message) 
	if action=="technologies-import":
		output="done"
		import_technologies()
	return action + "=" + output;
	
#API Layer
@app.route('/API/<key>/<action>', methods=['GET', 'POST'])
def manage_apis(action="", key=""):
	if key != "EaSKhyGzXU": return "Invalid key!"
	output = "Done"
	if action=="twitter":
		output = fetchallprofiles()
	if action=="telegram-hook":
		request_data = request.data or request.form
		secbot = telegrambot.BotHandler("351082352:AAHLBZW4ObbsMVHh4lrcwZOVHmvKsfyM59E")
		output = secbot.catchHook(request_data,db)
	return output, 200



#MAIN DASHBOARD
@app.route('/')
@ssl_required
@login_required
def show_all():
	#print (fetchallvulns())
	#return render_template('show_dashboard.html', vulns=db.session.query(vulns).limit(5).all())
	return render_template('show_dashboard.html', vulns=fetchallvulns(db))



#BLOGS AND FORUMS	
@app.route('/blogsforum')
@ssl_required
@login_required
def show_blogsforum():
	#save_scraped()
	blogs_vulns = db.session.query(vulns_blogs).order_by(desc(vulns_blogs.id)).limit(100).all()
	all_vulns = []
	for tvuln in blogs_vulns:
		single_vuln = {'name': ast.literal_eval(tvuln.name) ,'score': tvuln.score,'url': tvuln.source,'date': parse(tvuln.date),'cve': tvuln.my_cve,'source': tvuln.source}
		all_vulns.append(single_vuln)
	all_vulns = sorted(all_vulns, key=lambda x: x['date'], reverse=True)
	return render_template('show_blogsforum.html', vulns=all_vulns )


#LOGIN FORM
@app.route('/login', methods=['GET','POST'])
@ssl_required
def do_admin_login():
	if request.form.get('password', None) == '$ocial@dashboard' and request.form.get('username', None) == 'admin':
		session['logged_in'] = True
		#session.permanent = True
		#app.permanent_session_lifetime = timedelta(minutes=30)
		return redirect(url_for('show_all'))

	else:
		session['logged_in'] = False
		#flash('wrong password!')
		#return show_all()
	return render_template('login.html')



def get_num_from_str(x):
		return float(''.join(ele for ele in x if ele in '-.0123456789'))

#TWEETS
@app.route('/tweets/')
@app.route('/tweets/<profile_name>')
@ssl_required
@login_required
def show_all_tweets(profile_name=''):
#def show_all_tweets(profile_name):
	fetch_and_save_tweets(profile_name)
	saved_profiles = db.session.query(profiles).all()
	profile = None
	print (saved_profiles,"saved_profiles")
	print (profile_name, "profile_name")
	if profile_name:
		profile = get_profile(profile_name)
		print (profile, "profile")
	elif saved_profiles:
		profile = random.choice(saved_profiles)
		print (profile, "profile, under saved_profiles")
	if profile:
		saved_tweets = db.session.query(Tweets).filter_by(profile_id=profile.id)
		print (saved_tweets, "saved_tweets", profile.id)
	else:
		saved_tweets = []
	return render_template('show_all_tweets.html', tweets=saved_tweets, profile=profile, profiles=saved_profiles)

#BOT Subscription LIST	
@app.route('/subscribers', methods=['GET', 'POST'])
@ssl_required
@login_required
def show_subscribers():
	return render_template('show_subscriptors.html', subscriptors=db.session.query(subscriptors).all() )	



#PROFILES LIST	
@app.route('/profiles', methods=['GET', 'POST'])
@ssl_required
@login_required
def show_profiles():
	if request.method == 'GET':
		saved_profiles = db.session.query(profiles).all()
		profile_name_invalid = session["profile_name_invalid"] if "profile_name_invalid" in session else False
		return render_template('profiles.html', profiles=saved_profiles, profile_name_invalid=profile_name_invalid)
	
	if request.method == 'POST':
		request_data = request.data or request.form
		profile_name = request_data.get('profile_name')
		session["profile_name_invalid"] = True
		if twitter_user_exist(profile_name):
			session["profile_name_invalid"] = False
			profile = profiles(name=profile_name)
			db.session.add(profile)
			db.session.commit()
		return redirect(url_for('show_profiles'))



#Technology LIST	
@app.route('/technologies', methods=['GET', 'POST'])
@ssl_required
@login_required
def show_technologies():
	if request.method == 'GET':
		saved_technologies = db.session.query(technologies).all()
		#profile_name_invalid = session["profile_name_invalid"] if "profile_name_invalid" in session else False
		return render_template('technologies.html', technologies=saved_technologies)
	
	if request.method == 'POST':
		request_data = request.data or request.form
		technology_name = request_data.get('technology_name')
		technology = technologies(name=technology_name)
		db.session.add(technology)
		db.session.commit()
		return redirect(url_for('show_technologies'))
#SHOW SINGLE TECHNOLOGY
@app.route('/technologies/<int:technology_id>', methods=['PUT', 'DELETE'])
def manage_technology(technology_id):
	if request.method == 'DELETE':
		technology = db.session.query(technologies).filter_by(id=technology_id).first()
		if technology:
			db.session.delete(technology)
			db.session.commit()
			return jsonify({ 'message': 'Technology deleted successfully'}), 204
		
		return jsonify({ 'message': 'Technology deletion was not successful'}), 400
		
	if request.method == 'PUT':
		request_data = request.data or request.form
		technology_name = request_data.get('technology_name')
		print (technology_name)
		if technology_name:
			technology = db.session.query(technologies).filter_by(id=technology_id).first()
			if technology and technology.name != technology_name:
				technology.name = technology_name
				db.session.commit()
			return jsonify({ 'message': 'Technology updated successfully'}), 200
		return jsonify({ 'message': 'Technology update was not successful'}), 400





#SOCIAL DASHBOARD
@app.route('/socials', methods=['GET', 'POST'])
@ssl_required
@login_required
def show_socials():
	if request.method == 'GET':
		twitter_vulns = db.session.query(tweets).order_by(desc(tweets.id)).limit(100).all()
		all_vulns = []
		for tvuln in twitter_vulns:
			profile_array = db.session.query(profiles).filter_by(id=tvuln.profile_id).all()
			profile_name = profile_array[0].name
			final_name = []
			final_name.append(tvuln.tweet)
			final_name.append(tvuln.url)
			
			try:
				d = parse(tvuln.date)
			except ValueError:
				d = datetime.datetime.now()
			single_vuln = {'name': final_name ,'score': tvuln.score,'url': tvuln.url,'date': d,'cve': tvuln.cve,'source': "@" + profile_name}
			all_vulns.append(single_vuln)
		#profile_name_invalid = session["profile_name_invalid"] if "profile_name_invalid" in session else False
		return render_template('show_socials.html', vulns=all_vulns)


#KEYWORDS EDITING
@app.route('/keywords', methods=['GET', 'POST', 'PUT', 'DELETE'])
@ssl_required
@login_required
def show_keywords():
	if request.method == 'GET':
		saved_keywords = db.session.query(keyword_tags).all()
		listt = []
		for each_keyword in saved_keywords:
			listt.append(each_keyword.tag_name)
		print (listt,"check this")
		return render_template('keywords.html', keywords=saved_keywords)
	
	if request.method == 'POST':
		request_data = request.data or request.form
		keyword_name = request_data.get('keyword_name')
		keyword = keyword_tags(tag_name=keyword_name, critical_keyword='', high_keyword='')
		db.session.add(keyword)
		db.session.commit()
		return redirect(url_for('show_keywords'))

	if request.method == 'DELETE':
		request_data = request.data or request.form
		tag_name = request_data.get('tag_name')
		keyword = db.session.query(keyword_tags).filter_by(tag_name=tag_name).first()
		if keyword:
			db.session.delete(keyword)
			db.session.commit()

			return jsonify({ 'message': 'keyword deleted successfully'}), 204
		
		return jsonify({ 'message': 'keyword deletion was not successful'}), 400
		
	if request.method == 'PUT':
		request_data = request.data or request.form
		tag_name = request_data.get('tag_name')
		to_update_tag_text = request_data.get('to_update_tag_text')
		if to_update_tag_text and tag_name:
			keyword = db.session.query(keyword_tags).filter_by(tag_name=tag_name).first()
			if keyword and keyword.tag_name != to_update_tag_text:
				keyword.tag_name = to_update_tag_text
				db.session.commit()

			return jsonify({ 'message': 'keyword updated successfully'}), 200
			
		return jsonify({ 'message': 'keyword update was not successful'}), 400




#SHOW SINGLE PROFILE
@app.route('/profiles/<int:profile_id>', methods=['PUT', 'DELETE'])
def manage_profile(profile_id):
	if request.method == 'DELETE':
		profile = db.session.query(profiles).filter_by(id=profile_id).first()
		if profile:
			db.session.delete(profile)
			db.session.commit()

			return jsonify({ 'message': 'profile deleted successfully'}), 204
		
		return jsonify({ 'message': 'profile deletion was not successful'}), 400
		
	if request.method == 'PUT':
		request_data = request.data or request.form
		profile_name = request_data.get('profile_name')
		if profile_name:
			profile = db.session.query(profiles).filter_by(id=profile_id).first()
			if profile and profile.name != profile_name:
				profile.name = profile_name
				db.session.commit()

			return jsonify({ 'message': 'profile updated successfully'}), 200
			
		return jsonify({ 'message': 'profile update was not successful'}), 400

@app.route('/logout')
@ssl_required
@login_required
def logout():
	session['logged_in'] = False
	return redirect(url_for('show_all'))


if __name__ == '__main__':
	#app.run(debug=True, ssl_context='adhoc',host='0.0.0.0', port=8080)
	app.run(debug=True,host='0.0.0.0', port=8080)
	# app.run(debug=True)
