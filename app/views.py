from flask import Flask, render_template_string, request, render_template, flash, redirect, url_for
from app import app
from .forms import MemberSearchForm, ApproveUserForm, AddMemberForm
from flask.ext.user import roles_required
from .models import User,Role,db,MemberInfo
import re
import os
from flask.ext.login import current_user
from werkzeug import secure_filename

def allowed_file(filename):
  return '.' in filename and \
      filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# The Home page is accessible to anyone
@app.route('/')
@app.route('/index')
def home_page():
  isUser,isAdmin,isSuperAdmin = False,False,False
  if 'user' in [role.name for role in current_user.roles]:
    isUser = True
  if 'admin' in [role.name for role in current_user.roles]:
    isAdmin = True
  if 'superAdmin' in [role.name for role in current_user.roles]:
    isSuperAdmin = True
  return render_template('index.html',isUser=isUser,isAdmin=isAdmin,isSuperAdmin=isSuperAdmin)

# Member directory page
@app.route('/member_directory',methods=['GET','POST'])
@roles_required(['user','admin','superAdmin'])   # Use of @roles_required decorator
def member_directory_page():
  members = MemberInfo.query.all()
#  for member in members:
#    head_shot = re.sub(' ','_',member.name.lower())
#    member.head_shot=head_shot+'_'+str(member.age)
  columns=[]
  for column in MemberInfo.__table__.columns:
    if column.name != 'hidden' and column.name != 'id' and column.name != 'user_id':
      columns.append(column.name)
  columns_dict = [(i, c) for i,c in enumerate(columns)]
  member_directory = MemberSearchForm()
  member_directory.user_list.choices = columns_dict
  isAdmin = False
  if 'admin' in [role.name for role in current_user.roles] or 'superAdmin' in [role.name for role in current_user.roles]:
    isAdmin = True
  if member_directory.validate_on_submit():
    sort_column_name = member_directory.user_list.data
    sort_column_value = member_directory.search_value.data
    the_name = columns_dict[sort_column_name][1]
    members = db.session.query(MemberInfo).filter(getattr(MemberInfo,the_name).like("%" + sort_column_value+ "%"))
    return render_template('member_directory.html',isAdmin=isAdmin,form = member_directory,columns=columns,members=members)
  return render_template('member_directory.html',isAdmin=isAdmin,form = member_directory,columns=columns,members=members)
      
# add member page
@app.route('/add_member',methods=['GET','POST'])
@roles_required(['admin','superAdmin'])   # Use of @roles_required decorator
def add_member_page():
  f = AddMemberForm()
  if f.validate_on_submit():
    if f.head_shot.data:
      image_data = request.files[f.head_shot.name]
      if image_data and allowed_file(image_data.filename):
        filename = secure_filename(image_data.filename)
        image_data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        member = MemberInfo(name=f.name.data,age=f.age.data,weight_range=f.weight_range.data,eye_colour=f.eye_colour.data,tattoos=f.tattoos.data,piercings=f.piercings.data,hair_colour=f.hair_colour.data,video_link=f.video_link.data,contact_info=f.contact_info.data,hidden=False,head_shot=filename)
        db.session.add(member)
        db.session.commit()
        flash("Successfully added a new member","success")
        return redirect(url_for('add_member_page'))
  return render_template('add_member.html',form = f)

# remove member page
@app.route('/remove_member',methods=['GET','POST'])
@roles_required(['admin','superAdmin'])   # Use of @roles_required decorator
def remove_member_page():
    user_list_dict = [(c.id, c.name) for c in MemberInfo.query.all()]
    user_Approve = ApproveUserForm()
    user_Approve.user_list.choices = user_list_dict
    if user_Approve.validate_on_submit():
      flash('Successfully removed member.','success')
      a_user = MemberInfo.query.filter_by(id=user_Approve.user_list.data).first()
      db.session.delete(a_user)
      db.session.commit()
      user_list_dict = [(c.id, c.name) for c in MemberInfo.query.all()]
      user_Approve = ApproveUserForm()
      user_Approve.user_list.choices = user_list_dict
    return render_template('remove_member.html', form = user_Approve)

# The Profile page requires a logged-in user
@app.route('/profile')
@roles_required(['user','admin','superAdmin'])   # Use of @roles_required decorator
def profile_page():
  return render_template_string("""
      {% extends "base.html" %}
      {% block content %}
      <h2>{%trans%}Profile Page{%endtrans%}</h2>
      <p> {%trans%}Hello{%endtrans%}
          {{ current_user.username or current_user.email }},</p>
      <p> <a href="{{ url_for('user.change_username') }}">
          {%trans%}Change username{%endtrans%}</a></p>
      <p> <a href="{{ url_for('user.change_password') }}">
          {%trans%}Change password{%endtrans%}</a></p>
      {% endblock %}
      """)
#where admin can approve users
@app.route('/user_approve', methods=['GET', 'POST'])
@roles_required(['admin','superAdmin'])   # Use of @roles_required decorator
def user_approve_page():
  users = User.query.all()
  filtered_users = []
  for user in users:
    isNotAdmin = True
    if 'admin' in [role.name for role in user.roles] or 'superAdmin' in [role.name for role in user.roles]:
      isNotAdmin = False
    if isNotAdmin == True:
      filtered_users.append(user)

  user_list_dict = [(c.id, c.username) for c in filtered_users]
  user_Approve = ApproveUserForm()
  user_Approve.user_list.choices = user_list_dict
  if user_Approve.validate_on_submit():
    a_user = User.query.filter_by(id=user_Approve.user_list.data).first()
    found = False
    for role in a_user.roles:
      if role.name == 'user':
        found = True
    if found == False:
      flash('Successfully approved user','success')
      a_role = Role.query.filter_by(name='user').first()
      a_user.roles.append(a_role)
    db.session.commit()
  return render_template('user_approve.html',form = user_Approve,users=users, modifier_type='user')

#where superadmin approve admin
@app.route('/admin_approve', methods=['GET', 'POST'])
@roles_required('superAdmin')   # Use of @roles_required decorator
def admin_approve_page():
    users = User.query.all()
    filtered_users = []
    for user in users:
      isNotAdmin = True
      if 'superAdmin' in [role.name for role in user.roles]:
        isNotAdmin = False
      if isNotAdmin == True:
        filtered_users.append(user)

    user_list_dict = [(c.id, c.username) for c in filtered_users]
    user_Approve = ApproveUserForm()
    user_Approve.user_list.choices = user_list_dict
    if user_Approve.validate_on_submit():
      a_user = User.query.filter_by(id=user_Approve.user_list.data).first()
      found = False
      for role in a_user.roles:
        if role.name == 'admin':
          found = True
      if found == False:
        flash('Successfully approved admin','success')
        a_role = Role.query.filter_by(name='admin').first()
        a_user.roles.append(a_role)
      db.session.commit()
    return render_template('user_approve.html', form = user_Approve,users=users, modifier_type='admin')

# remove user page
@app.route('/remove_user',methods=['GET','POST'])
@roles_required(['admin','superAdmin'])   # Use of @roles_required decorator
def remove_user_page():
    user_list_dict = [(c.id, c.username) for c in User.query.all()]
    user_Approve = ApproveUserForm()
    user_Approve.user_list.choices = user_list_dict
    if user_Approve.validate_on_submit():
      flash('Successfully removed user.','success')
      a_user = User.query.filter_by(id=user_Approve.user_list.data).first()
      db.session.delete(a_user)
      db.session.commit()
      user_list_dict = [(c.id, c.username) for c in User.query.all()]
      user_Approve = ApproveUserForm()
      user_Approve.user_list.choices = user_list_dict
    return render_template('remove_user.html', form = user_Approve)
