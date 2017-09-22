from app import db

class tweet_delta(db.Model):
	id = db.Column('tweets_id', db.Integer, primary_key=True)
	name = db.Column(db.String(500))
	date = db.Column(db.String(500))


	def __init__(self, name, date):
		self.name = name
		self.date = date