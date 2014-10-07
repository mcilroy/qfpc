from app import app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.user import current_user, login_required, SQLAlchemyAdapter, UserManager, UserMixin

db = SQLAlchemy(app)                            # Initialize Flask-SQLAlchemy

# Define the User-Roles pivot table
user_roles = db.Table('user_roles',
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE')))

# Define Role model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define User model. Make sure to add flask.ext.user UserMixin!!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, default='')
    reset_password_token = db.Column(db.String(100), nullable=False, default='')
    # Relationships
    roles = db.relationship('Role', secondary=user_roles,
            backref=db.backref('users', lazy='dynamic'))
    member_info = db.relationship('MemberInfo', uselist=False,backref='user')

class MemberInfo(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False, default=False)
  age = db.Column(db.Integer, nullable=True, default=False)
  weight_range = db.Column(db.String(25), nullable=True, default=False)
  eye_colour = db.Column(db.String(50), nullable=True, default=False)
  tattoos = db.Column(db.String(255), nullable=True, default=False)
  piercings = db.Column(db.String(255), nullable=True, default=False)
  hair_colour = db.Column(db.String(255), nullable=True, default=False)
  video_link = db.Column(db.String(500), nullable=True, default=False)
  contact_info = db.Column(db.String(255), nullable=False, unique=True)
  hidden = db.Column(db.Boolean(), nullable=False, default=False)
  head_shot = db.Column(db.String(255), nullable=True, default=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
