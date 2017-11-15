from app import db
from models_blogs import vulns_blogs
from models_tweet import tweets
from models_profiles import profiles, keyword_tags
from spider import save_scraped
from sqlalchemy import desc

from tweeter import getNegativeTweets, get_cve, get_cvss_rating, get_tweet_score, twitter_user_exist,fetchallprofiles,fetch_and_save_tweets, get_profile



def fetchallvulns():
    twitter_vulns = db.session.query(tweets).order_by(desc(tweets.date)).limit(5).all()
    blogs_vulns = db.session.query(vulns_blogs).order_by(desc(vulns_blogs.date)).limit(5).all()
    all_vulns = []
    for tvuln in twitter_vulns:
        profile_array = db.session.query(profiles).filter_by(id=tvuln.profile_id).all()
        profile_name = profile_array[0].name
        single_vuln = {'name': tvuln.tweet ,'score': tvuln.score,'url': tvuln.url,'date': tvuln.date,'cve': tvuln.cve,'source': "@" + profile_name}
        all_vulns.append(single_vuln)
    for tvuln in blogs_vulns:
        single_vuln = {'name': tvuln.name ,'score': tvuln.score,'url': tvuln.source,'date': tvuln.date,'cve': tvuln.my_cve,'source': tvuln.source}
        all_vulns.append(single_vuln)
    all_vulns = sorted(all_vulns, key=lambda x: x['date'])
    #print (all_vulns)
    return all_vulns