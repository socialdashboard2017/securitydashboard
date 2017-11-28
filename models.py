from dbclass import db

class vulns(db.Model):
	id = db.Column('vuln_id', db.Integer, primary_key=True)
	name = db.Column(db.String(500))
	date = db.Column(db.String(500))
	my_cve = db.Column(db.String(50))
	score = db.Column(db.String(500))
	source = db.Column(db.String(500))
	
	def __init__(self, name, date, my_cve, score, source):
		self.name = name
		self.date = date
		self.my_cve = my_cve
		self.score = score
		self.source = source

class subscriptors(db.Model):
	id = db.Column('subscription_id', db.Integer, primary_key=True)
	name = db.Column(db.String(500))
	chat_id = db.Column(db.String(500))
	push = db.Column(db.Boolean)
	
	def __init__(self, name, chat_id, push):
		self.name = name
		self.chat_id = chat_id
		self.push = push