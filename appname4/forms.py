from flask.ext.wtf import Form
from appname4 import db
from wtforms import TextField, PasswordField, validators, SelectField, BooleanField, HiddenField, TextAreaField
from wtforms.validators import Required, EqualTo, Length
from appname4.models import User, Company

# Custom validators to check if user or email already exists
def validate_user(form, field):
  if db.session.query(User).filter_by(username=form.username.data).count() > 0:
    raise validators.ValidationError('Username already exists')

def validate_email(form, field):
  if db.session.query(User).filter_by(email=form.email.data).count() > 0:
    raise validators.ValidationError('Email already in use')


# Login, Signup, New movie found forms
class LoginForm(Form):
  username = TextField('username', validators = [Required(message='Please enter username')])
  password = PasswordField('password', validators = [Required(message='Please enter password')])
  remember_me = BooleanField('remember_me', default = False)

class SignupForm(Form):
  username = TextField('username', validators = [Required(), validate_user])
  password = PasswordField('password', [
    Required(message='Password cannot be empty'),
    EqualTo('confirm', message='Passwords did not match'),
    Length(min=8, max=100, message='Password too short')
  ])
  confirm = PasswordField('Repeat password', validators = [Required()])

class ModifyForm(Form):
  id = HiddenField('id')
  name = TextField('name', validators = [Required()])

class PasswordForm(Form):
  password = PasswordField('password', validators = [Required(message='Please enter old password')])
  newpassword = PasswordField('newpassword', [
    Required(message='New password cannot be empty'),
    EqualTo('confirm', message='Passwords did not match'),
    Length(min=8, max=100, message='Password too short')
  ])
  confirm = PasswordField('Repeat password', validators = [Required()])

class CompanyForm(Form):
  company_name = TextField('company_name', validators = [Required(message='Please enter the name of the company')])
  url = TextField('url')
  position = TextField('position', validators = [Required(message='Please enter the position that should be filled')])
  start = TextField('start', validators = [Required(message='Please enter the start date of this position')])
  end = TextField('end', validators = [Required(message='Please enter how long it should last')])
  location = TextField('location', validators = [Required(message='Please enter the location')])
  description = TextAreaField('description', validators = [Required(message='Please describe what the intern will be doing')])
  type_fulltime = TextField('type_fulltime')
  type_part_time = TextField('type_part_time')
  type_contract = TextField('type_contract')

  

  
