from flask import Flask, request
from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.user import current_user, login_required, SQLAlchemyAdapter, UserManager, UserMixin

#app = Flask(__name__)
#app.config.from_object('config')

#Setup Flask and config
app = Flask(__name__)
app.config.from_object('config')

# Load local_settings.py if file exists         # For automated tests
try: app.config.from_object('local_settings')
except: pass

# Load optional test_config                     # For automated tests
#if test_config:
#    app.config.update(test_config)

# Initialize Flask extensions
babel = Babel(app)                              # Initialize Flask-Babel

@babel.localeselector
def get_locale():
    translations = [str(translation) for translation in babel.list_translations()]
    return request.accept_languages.best_match(translations)

from .models import User,Role,db, MemberInfo
# Reset all the database tables
db.drop_all()
db.create_all()

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db,  User)
user_manager = UserManager(db_adapter, app)

# Create 'user007' user with 'secret' and 'agent' roles
if not User.query.filter(User.username=='admin').first():
    user1 = User(username='admin', active=True,
            password=user_manager.hash_password('1'))
    user1.roles.append(Role(name='admin'))
    db.session.add(user1)
    db.session.commit()
if not User.query.filter(User.username=='user').first():
    user2 = User(username='user', active=True,
            password=user_manager.hash_password('1'))
    user2.roles.append(Role(name='user'))
    db.session.add(user2)
    db.session.commit()
if not User.query.filter(User.username=='superAdmin').first():
    user3 = User(username='superAdmin', active=True,
            password=user_manager.hash_password('1'))
    user3.roles.append(Role(name='superAdmin'))
    db.session.add(user3)
    db.session.commit()
if not User.query.filter(User.username=='anon').first():
    user4 = User(username='anon', active=True,
            password=user_manager.hash_password('1'))
    user4.roles.append(Role(name='anon'))
    db.session.add(user4)
    db.session.commit()
    member = MemberInfo(name='Bill Smith',age=23,weight_range='100-140',eye_colour='blue',tattoos='one on back', piercings='4 on ear', hair_colour = 'brown', video_link='www.youtube.com/K3jJ',contact_info='bill@gmail.com', hidden=False,head_shot='bill_smith.png')
    db.session.add(member)
    db.session.commit()
    member = MemberInfo(name='Larry Reed',age=19,weight_range='100-140',eye_colour='green',tattoos='', piercings='', hair_colour = 'black', video_link='www.youtube.com/97JE7j',contact_info='lreed@gmail.com', hidden=False,head_shot='larry_reed.jpg')
    db.session.add(member)
    db.session.commit()
from app import views
