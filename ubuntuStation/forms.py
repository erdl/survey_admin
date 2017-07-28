from flask_wtf import FlaskForm
from .models import *
from wtforms import SelectField, StringField, BooleanField, RadioField, TextField, TextAreaField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, ValidationError

class UniqueValidator(object):
    def __init__(self, model, field):
        #print(model, field)
        self.model=model
        self.field=field
    def __call__(self, form, field):
        #print("Allie field data", self.model, type(self.model), self.field, type(self.field), field.data, type(field.data))
        check = self.model.query.filter(self.field==field.data).first()
        #check = self.model.query.all()
        #filter_by(survey_name=='allietest1').first()
        '''
        if 'id' in form:
            id=int(form.id.data)
        else:
            id=None
        '''
        #print("Allie check", check)
        #if check and (id is None or id != check.id):
        if check:
            #print("Error")
            raise ValidationError('Entry with this value already exists in the database')

class QuestionForm(FlaskForm):
    questiontext = TextAreaField('questiontext', validators=[DataRequired()], description=u'Question')


class SurveyForm(FlaskForm):
    # To insert data into survey_info
    surveyname=TextField('survey_name', description=u'Survey Name', validators=[DataRequired(), UniqueValidator(SurveyInfo, SurveyInfo.survey_name)])
    description=TextAreaField('description', description=u'Description')
    question=SelectMultipleField(u'question', validators=[DataRequired()], description=u'Which questions should be a part of this survey?', coerce=int, choices=[(q.question_id, q.question_description) for q in Question.query.order_by('question_description')])

    @classmethod
    def new(cls):
        form=cls()
        form.question.choices=[(q.question_id, q.question_description) for q in Question.query.order_by('question_description')]
        return form

class DeploymentForm(FlaskForm):
    #print("Creating deployment form")
    url_text=TextField('url_text', description=u'URL (e.g. "frog1kiosk")', validators=[DataRequired(), UniqueValidator(DeployedURL, DeployedURL.url_text)])
    is_kiosk=RadioField('is_kiosk', choices=[('1', "Yes"), ('0', "No")], description=u'Will this URL be deployed on a kiosk?')
    building_id=SelectField('building_id', description=u'Which building will this kiosk be located in?', coerce=int, choices=[(b.building_id, b.name) for b in Building.query.order_by('name')])
    survey_id=SelectField('survey_id', description=u'Which survey should be shown on this kiosk?', coerce=int, choices=[(s.survey_info_id, s.survey_name) for s in SurveyInfo.query.order_by("survey_name")])
    
    @classmethod
    def new(cls):
        form=cls()
        form.survey_id.choices=[(s.survey_info_id, s.survey_name) for s in SurveyInfo.query.order_by("survey_name")]
        form.building_id.choices=[(b.building_id, b.name) for b in Building.query.order_by('name')]
        return form

class EditDeploymentForm(FlaskForm):
    survey_id=SelectField('survey_id', description=u'Which survey should be shown on this kiosk?', coerce=int, choices=[(s.survey_info_id, s.survey_name) for s in SurveyInfo.query.order_by("survey_name")])

    @classmethod
    def new(cls):
        form=cls()
        form.survey_id.choices=[(s.survey_info_id, s.survey_name) for s in SurveyInfo.query.order_by("survey_name")]
        return form
        
class LoginForm(FlaskForm):
    username=TextField('username', description=u'Username', validators=[DataRequired()])
    password=PasswordField('password', description=u'Password', validators=[DataRequired()])

