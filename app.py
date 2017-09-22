import random

from flask import Flask, request, flash, url_for, redirect, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import exists

app = Flask(__name__)

app.config.from_object('config.BaseConfig')

db = SQLAlchemy(app)

from models import *
from models_tweet import tweets as Tweets
from models_profiles import profiles, keyword_tags

# db.drop_all()
from tweeter import getNegativeTweets, get_cve, get_cvss_rating, get_tweet_score, twitter_user_exist
db.create_all()

def ssl_required(fn):
		@wraps(fn)
		def decorated_view(*args, **kwargs):
				if request.url.startswith("http://"):
						return redirect(request.url.replace("http://", "https://"))
				else:
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

from spider import allDict, allSource, cve, scoring, get_link

import datetime

now = datetime.datetime.now()

def get_profile(profile_name):
	return db.session.query(profiles).filter_by(name=profile_name).first()

def check_on_all_tables():
	total_tables_length = len(db.session.query(vulns).all()) + len(db.session.query(Tweets).all())
	if total_tables_length >= 9000:
		db.session.query(vulns).delete()
		db.session.query(Tweets).delete()
		print('Deleting all records since total table length is >= 9000')
				
def fetch_and_save_tweets(profile_name):
	check_on_all_tables()
	negativeDictionary = getNegativeTweets(profile_name, no_of_tweets=70)
	print (negativeDictionary,"negativeDictionary")
	profile = get_profile(profile_name)
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
	
@app.route('/')
@ssl_required
@login_required
def show_all():
	# if not session.get('logged_in'):
	# 	session['logged_in'] = False
	# 	return render_template('login.html')
	# else:
	# db.create_all()
	# db.session.query(vulns).delete()
	check_on_all_tables()
	past = db.session.query(vulns.name)

	mypast = [el.name for el in past]

	#print(mypast)
	#print('MYPAST')

	body = [str(mypast)[1:-1].replace('"', '')]

	#print(body)
	#print('BODY')

	real_past = []
	for el in body:
		if el:
			real_past.append(str(el[0]))

	#print (real_past)
	#print('REAL_PAST')

	i = 0
	for dictionary in allDict:
		for key, value in dictionary.items():
			names = value[0]
			scores = value[1]
			for vname, vscore in zip(names, scores):
				if (vname in real_past) == False:
					ascore = str(scoring(cve(vscore), vname))
					if not ascore.startswith('Low'):
						temp = allSource[i]
						vuln_object = vulns(name = str(get_link(vname, temp)), date = (key + ' ' + str(now.year)), my_cve = cve(vname), score = ascore, source = temp)
						exists = db.session.query(vulns).filter_by(name = str(get_link(vname, temp)), date = (key + ' ' + str(now.year)), my_cve = cve(vname), score = ascore, source = temp).first() is not None
						if exists == False:
							db.session.add(vuln_object)
		i += 1

	db.session.commit()

	return render_template('show_all.html', vulns=db.session.query(vulns).all() )

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


# @app.route('/keywordsedit', methods=['PUT', 'DELETE'])
# def manage_keyword(tag_name):
# 	if request.method == 'DELETE':
# 		keyword = db.session.query(keyword_tags).filter_by(tag_name=tag_name).first()
# 		if keyword:
# 			db.session.delete(keyword)
# 			db.session.commit()

# 			return jsonify({ 'message': 'keyword deleted successfully'}), 204
		
# 		return jsonify({ 'message': 'keyword deletion was not successful'}), 400
		
# 	if request.method == 'PUT':
# 		request_data = request.data or request.form
# 		to_update_tag_text = request_data.get('to_update_tag_text')
# 		if to_update_tag_text:
# 			keyword = db.session.query(keyword_tags).filter_by(tag_name=tag_name).first()
# 			if keyword and keyword.tag_name != to_update_tag_text:
# 				keyword.tag_name = to_update_tag_text
# 				db.session.commit()

# 			return jsonify({ 'message': 'keyword updated successfully'}), 200
			
# 		return jsonify({ 'message': 'keyword update was not successful'}), 400


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
	app.run(debug=True, ssl_context='adhoc')
	# app.run(debug=True)
