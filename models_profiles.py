from app import db

class profiles(db.Model):
	id = db.Column('profiles_id', db.Integer, primary_key=True)
	name = db.Column(db.String(500), unique=True)

	def __init__(self, name):
		self.name = name

class keyword_tags(db.Model):
	__tablename__ = 'keyword_tags'

	tag_name = db.Column(db.String(500), primary_key=True)
	critical_keyword = db.Column(db.String(500))
	high_keyword = db.Column(db.String(50))

	def __init__(self, tag_name, critical_keyword, high_keyword):
		self.tag_name = tag_name
		self.critical_keyword = critical_keyword
		self.high_keyword = high_keyword
