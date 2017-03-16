from flask_wtf import FlaskForm
from .models import Question, Building
from wtforms import SelectField, StringField, BooleanField, RadioField, TextField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired

class QuestionForm(FlaskForm):
    questiontext = TextAreaField('questiontext', validators=[DataRequired()], description=u'Question')
    questionurl = TextField('questionurl', validators=[DataRequired()], description=u'Question URL')

'''
class ActiveQuestionForm(FlaskForm):
    urls=ActiveQuestion.query.with_entities(ActiveQuestion.activequestionurl)
    print("Hi")
    print(urls)
    activequestionurl = SelectField(u"activequestionurl", choices=[(q.activequestionid, q.activequestionurl) for q in ActiveQuestion.query.order_by('activequestionurl')])  
'''

class SurveyForm(FlaskForm):
    # To insert data into survey_info
    surveyname=TextField('survey_name', description=u'Survey Name', validators=[DataRequired()])
    description=TextAreaField('description', description=u'Description')
    question=SelectMultipleField(u'question', validators=[DataRequired()], description=u'Which questions should be a part of this survey?', coerce=int, choices=[(q.question_id, q.question_description) for q in Question.query.order_by('question_description')])

class DeploymentForm(FlaskForm):
    url_text=TextField('url_text', description=u'What is the URL?', validators=[DataRequired()])
    is_kiosk=RadioField('is_kiosk', choices=[('1', "Yes"), ('0', "No")], description=u'Will this URL be deployed on a kiosk?')
    building_id=SelectField('building_id', description=u'Which building will this kiosk be located in?', coerce=int, choices=[(b.building_id, b.name) for b in Building.query.order_by('name')])

