# python flask/db.py db init
# python flask/db.py db migrate
# python flask/db.py db upgrade

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import SQLALCHEMY_DATABASE_URI
from app import app, db
 
migrate = Migrate(app, db)
 
manager = Manager(app)
manager.add_command('db', MigrateCommand)
 
if __name__ == '__main__':
    manager.run()