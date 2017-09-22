# from flask import Flask, request, session, render_template
# from functools import wraps
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)

# app.config.from_object('config.BaseConfig')

# db = SQLAlchemy(app)

# from models import *
# from models_tweet import tweets as Tweets

# # from tweeter import *
# db.create_all()

# def ssl_required(fn):
#     @wraps(fn)
#     def decorated_view(*args, **kwargs):
#         if request.url.startswith("http://"):
#             return redirect(request.url.replace("http://", "https://"))
#         else:
#             return fn(*args, **kwargs)

#     return decorated_view

# def login_required(f):
# 	@wraps(f)
# 	def wrap(*args, **kwargs):
# 		if session.get('logged_in'):
# 			return f(*args, **kwargs)
# 		else:
# 			#flash('You need to login first.')
# 			#return redirect(url_for('do_admin_login'))
# 			return render_template('login.html')
# 	return wrap

# @app.route('/')
# @ssl_required
# @login_required
# def hello():
# 	return 'Hello world'

# app.run(debug=True, ssl_context='adhoc', threaded=True)

from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import exists

app = Flask(__name__)
app.config.from_object('config.BaseConfig')
db = SQLAlchemy(app)

from models import *
from models_tweet import tweets as Tweets

from tweeter import *
# from spider import allDict, allSource, cve, scoring, get_link

import datetime

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

now = datetime.datetime.now()

def check_on_all_tables():
	total_tables_length = len(db.session.query(vulns).all()) + len(db.session.query(Tweets).all())
	if total_tables_length >= 9000:
		db.session.query(vulns).delete()
		db.session.query(Tweets).delete()
		print('Deleting all records since total table length is >= 9000')

def fetch_and_save_tweets():
	print('fetching and saving tweets')
	check_on_all_tables()
	negativeDictionary = getNegativeTweets(70)
	formatted_tweets = []
	for key, value in negativeDictionary.items():
		tweets = value[0]
		scores = value[1]
		urls = value[2]

		for tweet, tweet_score, tweet_url in zip(tweets, scores, urls):
			decoded_tweet = tweet.decode('utf-8')
			tweet_cve = get_cve(decoded_tweet)
			tweet_score = get_tweet_score(decoded_tweet, tweet_score)
			exists = db.session.query(Tweets).filter_by(tweet=decoded_tweet).first() is not None
			if exists == False:
				formatted_tweet = {
					'tweet': decoded_tweet ,
					'score': tweet_score,
					'url': tweet_url,
					'date': key,
					'cve': tweet_cve
				}
				current_tweet = Tweets(**formatted_tweet)
				db.session.add(current_tweet)
	db.session.commit()
	
@app.route('/')
@ssl_required
@login_required
def show_all():
	check_on_all_tables()
	past = db.session.query(vulns.name)
	mypast = []
	for el in past:
		mypast.append(el.name)
	print(mypast)
	print('MYPAST')

	body = [str(mypast)[1:-1].replace('"', '')]

	print(body)
	print('BODY')

	real_past = []

	for el in body:
		if el:
			real_past.append(str(el[0]))

	print (real_past)
	print('REAL_PAST')

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
						vuln = vulns(name = str(get_link(vname, temp)), date = (key + ' ' + str(now.year)), my_cve = cve(vname), score = ascore, source = temp)
						db.session.add(vuln)
		i += 1
	db.session.commit()

	return render_template('show_all.html', vulns=db.session.query(vulns).all() )


@app.route('/login', methods=['GET','POST'])
@ssl_required
def do_admin_login():
	if request.form.get('password', None) == 'pass' and request.form.get('username', None) == 'admin':
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

@app.route('/tweets', methods=['GET', 'POST'])
@ssl_required
@login_required
def show_all_tweets():
	fetch_and_save_tweets()
	saved_tweets = db.session.query(Tweets).all()
	
	return render_template('show_all_tweets.html', tweets=saved_tweets)


@app.route('/logout')
@ssl_required
@login_required
def logout():
	session['logged_in'] = False
	#session.pop('logged_in', None)
	#flash('wrong password!')

	#return show_all()
	return redirect(url_for('show_all'))


if __name__ == '__main__':
	#db.create_all()
	app.run(debug=True, ssl_context='adhoc', threaded=True)
	# app.run(debug=True)
