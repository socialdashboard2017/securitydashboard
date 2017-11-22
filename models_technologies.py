from app import db

class technologies(db.Model):
	id = db.Column('technology_id', db.Integer, primary_key=True)
	name = db.Column(db.String(500))
	
	def __init__(self, name):
		self.name = name
	