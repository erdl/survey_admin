from . import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from passlib.apps import custom_app_context as pwd_context

'''
class User(UserMixin):
    #database of users
    user_database = {"Admin": ("Admin", "pass")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)
'''

class User(UserMixin, db.Model):
    __tablename__="users"
    user_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def __init__(self, username, password=None):
        self.id = username
        self.username = username
        self.password = password

class Question(db.Model):
    __tablename__="question"
    question_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_text=db.Column(db.String(150), nullable=False)
    question_description=db.Column(db.String(50), unique=True, nullable=False)
    question_type=db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Question %r>' % (self.question_text)

class Option(db.Model):
    __tablename__="option"
    option_id=db.Column(db.Integer, primary_key=True, nullable=False)
    text=db.Column(db.String(45), nullable=False)
    value=db.Column(db.String(45), nullable=False)
    question_id=db.Column(db.Integer, db.ForeignKey('question.question_id'), nullable=False)
    
    def __repr__(self):
        return '<option_text %r>' % (self.text)

class Response(db.Model):
    __tablename__="response"
    response_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    survey_info_id=db.Column(db.Integer, db.ForeignKey('survey_info.survey_info_id'))
    question_id=db.Column(db.Integer, db.ForeignKey('question.question_id'), nullable=False)
    option_id=db.Column(db.Integer, db.ForeignKey('option.option_id'), nullable=False)
    deployed_url_id=db.Column(db.Integer, db.ForeignKey('deployed_url.deployed_url_id'), nullable=False)
    timestamp=db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return '<response %r>' % (self.option_id)

class SurveyInfo(db.Model):
    __tablename__="survey_info"
    survey_info_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    description=db.Column(db.String(500), nullable=True)
    survey_name=db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<survey name %r>' % (self.survey_name)

    def __init__(self, description, surveyname):
        self.description=description
        self.survey_name=surveyname
        
class SurveyQuestion(db.Model):
    __tablename__="survey_question"
    __table_args__=(
        PrimaryKeyConstraint('survey_info_id', 'question_id'),
    )
    survey_info_id=db.Column(db.Integer, db.ForeignKey('survey_info.survey_info_id'), nullable=False)
    question_id=db.Column(db.Integer, db.ForeignKey('question.question_id'), nullable=False)
    question_position=db.Column(db.Integer)
    #db.PrimaryKeyConstraint('deploymentid', 'questionid')   

    def __init__(self, survey_id, question_id, question_position):
        self.survey_info_id=survey_id
        self.question_id=question_id
        self.question_position=0

    def __repr__(self):
        return '<survey question id %r>' %(self.question_id)

class DeployedURL(db.Model):
    __tablename__="deployed_url"
    deployed_url_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_text=db.Column(db.String(255))
    is_kioski=db.Column(db.String(45))
    building_id=db.Column(db.Integer, db.ForeignKey('building.building_id'))

    def __init__(self, url, kiosk, building):
        self.url_text = url
        self.is_kioski = kiosk
        self.building_id = building

    def __repr__(self):
        return '<deployment url id %r %r %r>' %(self.url_text, self.is_kioski, self.building_id)

class Building(db.Model):
    __tablename__="building"
    building_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String(45))

class KioskSurvey(db.Model):
    __tablename__="kiosk_survey"
    url=db.Column(db.String(45), nullable=False, primary_key=True)
    survey_info_id=db.Column(db.Integer, nullable=False)
    deployed_url_id=db.Column(db.Integer, nullable=False)
    
    def __init__(self, url, survey_id, deployed_url_id):
        self.url=url
        self.survey_info_id=survey_id
        self.deployed_url_id=deployed_url_id
