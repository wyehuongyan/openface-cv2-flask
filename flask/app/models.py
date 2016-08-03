from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128))
	first_name = db.Column(db.String(128))
	last_name = db.Column(db.String(128))
 
	def __init__(self, username, first_name, last_name):
		self.username = username
		self.first_name = first_name
		self.last_name = last_name

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id': self.id,
			'username': self.username,
			'first_name': self.first_name,
			'last_name': self.last_name,
			# This is an example how to deal with Many2Many relations
			# 'many2many'  : self.serialize_many2many
		}

	# @property
	# def serialize_many2many(self):
	# 	"""
	# 	Return object's relations in easily serializeable format.
	# 	NB! Calls many2many's serialize property.
	# 	"""
	# 	return [ item.serialize for item in self.many2many]