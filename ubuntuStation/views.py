from ubuntuStation import app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from . import login_manager
from . import limiter
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import urllib.parse as urlparse
from .forms import *
from .models import *
from .database import db_session

'''
@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username,password = token.split(":")
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0], user_entry[1])
            if (user.password == password):
                return user
    return None
'''
class UserManager(UserMixin):
    user_database = {}
    users = User.query.all()
    for u in users:
        user_database[u.username] = (u.username, u.password_hash)

    def __init__(self, username):
        self.id = username
        self.username = username

    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)

@login_manager.user_loader
def load_user(user_id):
    username = user_id
    user_entry = UserManager.get(username)
    if (user_entry is not None):
        user = User(user_entry[0], user_entry[1])
        return user
    return None

@app.route('/', methods=["GET"])
@login_required
def home():
    return render_template('admin_landing.html')

@app.route('/tutorial')
@login_required
def tutorial():
    return render_template('tutorial.html')

@app.route('/login', methods=["GET", "POST"])
@limiter.limit("50 per hour")
def login():
    #print(request.method)
    form = LoginForm(request.form)
    #print("Next: ", request.args.get('next'))
    if form.validate_on_submit(): #and request.method=="POST":
        #print("Form is valid")
        '''
        if form.username.data=="Admin" and form.password.data=="pass":
        '''
        user = User.query.filter_by(username = form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(UserManager(form.username.data))
            #login_user(UserManager(form.username.data))
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('home'))
    return render_template('login.html', form=form)

def is_safe_url(target):
    ref_url = urlparse.urlparse(request.host_url)
    test_url = urlparse.urlparse(urlparse.urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/logoout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/questionform', methods=['GET', 'POST'])
@login_required
def question_form():
    form = QuestionForm(request.form).new()
    if request.method == 'POST' and form.validate():
        question=Question(question_text=form.questiontext.data, \
            question_description=form.questiondescription.data, question_type=form.questiontype.data)
        try:
            db_session.add(question)
            db_session.commit()
            question_id=question.question_id
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()
        print(form.entries.data)
        for entries in form.entries.data:
            print(entries)
            o=Option(question_id=question_id, text=entries['option'], response_position=entries['responseposition'], option_color=entries['optioncolor'])
            try:
                db_session.add(o)
                db_session.commit()
            except:
                db_session.rollback()
            finally:
                db_session.close()
        return redirect(url_for('show_questions'))
    else:
        print(form.errors)
    return render_template('question_form.html', form=form)

@app.route('/surveyform', methods=['GET', 'POST'])
@login_required
def survey_form():
    form=SurveyForm(request.form).new()
    if request.method == 'POST' and form.validate():
        survey=SurveyInfo(form.description.data, form.surveyname.data)
        try:
            db_session.add(survey)
            db_session.commit()
            survey_id=survey.survey_info_id
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()
        for question_id in form.question.data:
            q=SurveyQuestion(survey_id, question_id, 1) 
            try:
                db_session.add(q)
                db_session.commit()
            except:
                db_session.rollback()
            finally:
                db_session.close()
        return redirect(url_for('show_surveys'))
    else:
        print(form.errors)
    return render_template('survey_form.html', form=form)

@app.route('/deploymentform', methods=['GET', 'POST'])
@login_required
def deployment_form():
    form=DeploymentForm(request.form).new()
    if request.method == 'POST' and form.validate():
        deployment=DeployedURL(form.url_text.data, form.is_kiosk.data, form.building_id.data)
        try:
            db_session.add(deployment)
            #print(deployment)
            db_session.commit()
        except:
            db_session.rollback()
            raise
        finally:
            #print(deployment.deployed_url_id)
            ks=KioskSurvey(form.url_text.data, form.survey_id.data, deployment.deployed_url_id)    
            try:
                db_session.add(ks)
                db_session.commit()
            except:
                db_session.rollback()
                raise
            finally:
                db_session.close()
        return redirect(url_for('show_deployments'))
    else:
        print(form.errors)
    return render_template('deployment_form.html', form=form)
    '''
    else:
        #try:
        form=DeploymentForm(request.form)
        deployment=DeployedURL.query.filter_by(deployed_url_id=deploymentid).one()
        kiosksurvey=KioskSurvey.query.filter_by(deployed_url_id=deploymentid).one()
        del form.url_text
        del form.is_kiosk
        del form.building_id
        if request.method == 'POST':
            kiosksurvey.deployed_url_id=form.survey_id.data
            try:
                db_session.commit()
            except:
                db_session.rollback()
                raise
            finally:
                db_session.close()
            return redirect(url_for('deployment_page', deployedurlid=deploymentid))
        return render_template('deployment_form.html', form=form)
        else:
            print(form.errors)
        #except:
        return render_template('error_deployment.html')
    '''

@app.route('/editdeploymentform/<int:deploymentid>', methods=['GET', 'POST'])
@login_required
def edit_deployment_form(deploymentid):
    deployment=DeployedURL.query.filter_by(deployed_url_id=deploymentid).one()
    building=Building.query.filter_by(building_id=deployment.building_id).one()
    kiosksurvey=KioskSurvey.query.filter_by(deployed_url_id=deploymentid).one()
    form=DeploymentForm(request.form).new()
    del form.url_text
    del form.is_kiosk
    del form.building_id
    if request.method == 'POST':
        #kiosksurvey.survey_info_id=form.survey_id.data
        #TODO: debug this, kiosk_survey table isn't getting updated
        try:
            db_session.query(KioskSurvey).filter_by(deployed_url_id=deploymentid).update({"survey_info_id": form.survey_id.data})
            #print(kiosksurvey.survey_info_id)
            db_session.commit()
        except:
            print("Error inserting into kiosk_survey")
            db_session.rollback()
        finally:
            db_session.close()
        return redirect(url_for('show_deployments'))
    return render_template("edit_deployment_form.html", form=form, ks=kiosksurvey, d=deployment, did=deploymentid, b=building)
    '''
    deployment=DeployedURL.query.filter_by(deployed_url_id=deploymentid).one()
    kiosksurvey=KioskSurvey.query.filter_by(deployed_url_id=deploymentid).one()
    form=DeploymentForm(request.form)
    opt_param = request.args.get("deploymentid")
    print(opt_param)
    del form.url_text
    del form.is_kiosk
    del form.building_id
    if request.method == 'POST':
        kiosksurvey.deployed_url_id=form.survey_id.data
        try:
            db_session.commit()
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()
    return render_template('deployment_form.html', form=form, ks=kiosksurvey, d=deployment)
'''

@app.route('/question/<int:questionid>', methods=['GET', 'POST'])
@login_required
def question_page(questionid):
    q=Question.query.filter_by(question_id=questionid).one()
    #question=[dict(questiontext=q.questiontext, questionurl=q.questionurl)]
    o=Option.query.filter_by(question_id=q.question_id).order_by('response_position')
    #print(o[0])
    #form=ActiveQuestionForm(request.form)
    #if request.method == 'POST':
    #    db_session.commit()
    #    return redirect(url_for('show_questions'))
    return render_template("questionpage.html", question=q, option=o)

@app.route('/survey/<int:surveyid>', methods=['GET'])
@login_required
def survey_page(surveyid):
    s=SurveyInfo.query.filter_by(survey_info_id=surveyid).one()
    #q=SurveyQuestion.query.filter_by(survey_info_id=surveyid).join(Question, SurveyQuestion.question_id==Question.question_id)
    q=Question.query.join(SurveyQuestion, Question.question_id == SurveyQuestion.question_id).filter_by(survey_info_id=surveyid)
    d=KioskSurvey.query.join(SurveyInfo, KioskSurvey.survey_info_id == SurveyInfo.survey_info_id).filter_by(survey_info_id=surveyid)
    if d.count() is 0:
        hasData = False
    else:
        hasData = True
    return render_template("surveypage.html", survey=s, questions=q, deployments=d, hasData=hasData)

@app.route('/deployment/<int:deployedurlid>', methods=['GET'])
@login_required
def deployment_page(deployedurlid):
    d=DeployedURL.query.filter_by(deployed_url_id=deployedurlid).one()
    b=Building.query.filter_by(building_id=d.building_id).one()
    ks=KioskSurvey.query.filter_by(deployed_url_id=d.deployed_url_id).one()
    #print(ks.survey_info_id)
    s=SurveyInfo.query.filter_by(survey_info_id=ks.survey_info_id).one()
    return render_template("deploymentpage.html", deployment=d, building=b, survey=s) 

@app.route('/showdeployments', methods=['GET'])
@login_required
def show_deployments():
    d=DeployedURL.query.all()
    return render_template('show_deployments.html', deployments=d)

@app.route('/showsurveys', methods=['GET'])
@login_required
def show_surveys():
    s=SurveyInfo.query.all()
    return render_template('show_surveys.html', surveys=s)

@app.route('/showquestions', methods=['GET'])
@login_required
def show_questions():
    question=Question.query.all()
    #entries=[dict(questiontext=q.questiontext, questionurl=q.questionurl) for q in question]
    entries=question
    return render_template('show_questions.html', questions=entries)
