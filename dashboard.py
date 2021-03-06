from models_blogs import vulns_blogs
from models_tweet import tweets
from models_profiles import profiles, keyword_tags
'''
from spider import save_scraped
from tweeter import getNegativeTweets, get_cve, get_cvss_rating, get_tweet_score, twitter_user_exist,fetchallprofiles,fetch_and_save_tweets, get_profile
'''
from sqlalchemy import desc
from sqlalchemy import cast
import sqlalchemy

import ast
from dateutil.parser import parse
import datetime



def fetchSocialVulns(db, count=5):
    twitter_vulns = db.session.query(tweets).order_by(desc(tweets.id)).limit(count).all()
    all_vulns = []
    for tvuln in twitter_vulns:
        #print (tvuln)
        profile_array = db.session.query(profiles).filter_by(id=tvuln.profile_id).all()
        profile_name = profile_array[0].name
        tweet_url = str(tvuln.url).replace("statuses",profile_name + "/status")
        
        final_name = []
        final_name.append(tvuln.tweet)
        final_name.append(tweet_url)
        
        #TODO
        # - needs to be implemented a TryParse for vulnerability date
        try:
            d = parse(tvuln.date)
        except ValueError:
            d = datetime.datetime.now()
            
        single_vuln = {'name': final_name ,'score': tvuln.score,'url': tweet_url,'date': d,'cve': tvuln.cve,'source': "@" + profile_name}
        all_vulns.append(single_vuln)
    all_vulns = sorted(all_vulns, key=lambda x: x['date'], reverse=True)
    return all_vulns


def fetchBlogVulns(db, count=5):
    blogs_vulns = db.session.query(vulns_blogs).order_by(desc(vulns_blogs.id)).limit(count).all()
    all_vulns = []
    for tvuln in blogs_vulns:
        try:
            d = parse(tvuln.date)
        except ValueError:
            d = datetime.datetime.now()
            
        single_vuln = {'name': ast.literal_eval(tvuln.name) ,'score': tvuln.score,'url': tvuln.source,'date': d,'cve': tvuln.my_cve,'source': tvuln.source}
        all_vulns.append(single_vuln)
    all_vulns = sorted(all_vulns, key=lambda x: x['date'], reverse=True)
    return all_vulns



def fetchallvulns(db):
    twitter_vulns = db.session.query(tweets).order_by(desc(tweets.id)).filter(cast(tweets.score,sqlalchemy.types.Integer ) > 7).limit(5).all()
    blogs_vulns = db.session.query(vulns_blogs).order_by(desc(vulns_blogs.id)).filter(cast(vulns_blogs.score,sqlalchemy.types.Integer ) > 7).limit(5).all()
    all_vulns = []
    for tvuln in twitter_vulns:
        #print (tvuln)
        profile_array = db.session.query(profiles).filter_by(id=tvuln.profile_id).all()
        profile_name = profile_array[0].name
        tweet_url = str(tvuln.url).replace("statuses",profile_name + "/status")
        
        
        final_name = []
        final_name.append(tvuln.tweet)
        final_name.append(tweet_url)
        try:
            d = parse(tvuln.date)
        except ValueError:
            d = datetime.datetime.now()
        
        single_vuln = {'name': final_name ,'score': tvuln.score,'url': tvuln.url,'date': d,'cve': tvuln.cve,'source': "@" + profile_name}
        #single_vuln = {'name': final_name ,'score': tvuln.score,'url': tvuln.url,'date': tvuln.date,'cve': tvuln.cve,'source': "@" + profile_name}
        all_vulns.append(single_vuln)
    for tvuln in blogs_vulns:
        single_vuln = {'name': ast.literal_eval(tvuln.name) ,'score': tvuln.score,'url': tvuln.source,'date': parse(tvuln.date),'cve': tvuln.my_cve,'source': tvuln.source}
        all_vulns.append(single_vuln)
    all_vulns = sorted(all_vulns, key=lambda x: x['date'], reverse=True)
    return all_vulns