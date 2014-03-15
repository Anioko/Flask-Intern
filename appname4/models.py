from appname4 import app, db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

# Roles
ROLE_USER = 0
ROLE_MOD = 1
ROLE_ADMIN = 2
ROLE_COMPANY = 3

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    password = db.Column(db.String)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    companies = db.relationship('Company', backref = 'author', lazy = 'dynamic')


  
    def is_authenticated(self):
        return True
  
    def is_active(self):
        return True
  
    def get_id(self):
        return unicode(self.id)
  
    def is_anonymous(self):
        return False

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.id}>'.format(self=self)
    
class Company(db.Model):
    

    id = db.Column(db.Integer, primary_key = True)
    company_name = db.Column(db.String(55))
    url = db.Column(db.String(55))
    position = db.Column(db.String(55))
    location = db.Column(db.String(55))
    start = db.Column(db.String(55))
    end = db.Column(db.String(55))
    description = db.Column(db.Text)
    type_fulltime = db.Column(db.String(55))
    type_part_time = db.Column(db.String(55))
    type_contract = db.Column(db.String(55))
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    

    
class Intern(db.Model):
    __tablename__ = 'interns'
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(255), index = True, unique = True)
    last_name = db.Column(db.String(255), index = True, unique = True)
    languages = db.Column(db.String(255))
    major = db.Column(db.String(255))
    year_of_study = db.Column(db.String(255))
    school = db.Column(db.String(255))
    nationality = db.Column(db.String(255))
    describe_self = db.Column(db.String(255))
    skills_one = db.Column(db.String(255))
    skills_two = db.Column(db.String(255))
    skills_three = db.Column(db.String(255))
    skills_four = db.Column(db.String(255))
    skills_five = db.Column(db.String(255))
    skills_six = db.Column(db.String(255))
    skills_seven = db.Column(db.String(255))
    skills_eight = db.Column(db.String(255))
    skills_nine = db.Column(db.String(255))
    skills_ten = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))


db.create_all()
