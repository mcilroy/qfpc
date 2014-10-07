from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField, TextField, FileField, validators
from wtforms.validators import DataRequired

class ApproveUserForm(Form):
  user_list = SelectField('user_list', choices=[], coerce=int)

class MemberSearchForm(Form):
  user_list = SelectField('user_list', choices=[], coerce=int)
  search_value = TextField('search_value')

class AddMemberForm(Form):
  name = TextField('name', [validators.Required()])
  age = TextField('age', [validators.Required()])
  weight_range = TextField('weight_range')
  eye_colour = TextField('eye_colour')
  tattoos = TextField('tattoos')
  piercings = TextField('piercings')
  hair_colour = TextField('hair_colour')
  video_link = TextField('video_link')
  head_shot = FileField('head_shot')
  contact_info = TextField('contact_info', [validators.Required()])

  
