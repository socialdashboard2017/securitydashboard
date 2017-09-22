from app import db
from models_profiles import profiles

class tweets(db.Model):
  id = db.Column('tweets_id', db.Integer, primary_key=True)
  tweet = db.Column(db.String(500))
  date = db.Column(db.String(500))
  cve = db.Column(db.String(50))
  score = db.Column(db.String(500))
  url = db.Column(db.String(500))
  profile_id = db.Column(db.Integer, db.ForeignKey(profiles.id))
  
  def __init__(self, tweet, date, cve, score, url, profile_id):
    self.tweet = tweet
    self.date = date
    self.cve = self.update_cve(cve)
    self.score = score
    self.url = url
    self.profile_id = profile_id

