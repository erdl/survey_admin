from ubuntuStation import app
from flask import redirect, url_for, session, request, render_template
from . import login_manager
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
import json
from .forms import *
from .models import *
from .database import db_session, data
from requests_oauthlib import OAuth2Session

csrf = CSRFProtect(app)

class Auth:
    CLIENT_ID = data["CLIENT_ID"]
    CLIENT_SECRET = data["CLIENT_SECRET"]
    REDIRECT_URI = data["REDIRECT_URI"]
    AUTH_URI = data["AUTH_URI"]
    TOKEN_URI = data["TOKEN_URI"]
    USER_INFO = data["USER_INFO"]
    SCOPE = data["SCOPE"]

class Config:
    APP_NAME = "Survey Admin "
    SECRET_KEY = "development"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth

@app.route('/', methods=["GET"])
@login_required
def home():
    return render_template('admin_landing.html')

@app.route('/tutorial')
@login_required
def tutorial():
    return render_template('tutorial.html')

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(next or url_for('home'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)

@app.route('/gCallback')
def callback():
    # Redirect user to home page if already logged in.
    #if current_user is not None and current_user.is_authenticated():
        #return redirect(url_for('home'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has
        # successfully authenticated our app.
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                #user = User()
                #user.email = email
                return redirect(url_for('login'))
            user.name = user_data['name']
            print(token)
            user.tokens = json.dumps(token)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        return 'Could not fetch your information.'

@app.route('/logout')
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
        for entries in form.entries.data:
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

    if request.method == 'GET':
        form.url_text.data = deployment.url_text
        form.building_id.data = building.building_id
        form.is_kiosk.data = deployment.is_kioski       #currently not selecting
        form.survey_id.data = kiosksurvey.survey_info_id

    if request.method == 'POST':
        try:
            if request.form['action'] == 'Submit':
                db_session.query(DeployedURL).filter_by(deployed_url_id=deploymentid).update({"url_text": form.url_text.data, "is_kioski": form.is_kiosk.data, "building_id": form.building_id.data})
                db_session.query(KioskSurvey).filter_by(deployed_url_id=deploymentid).update({"url": form.url_text.data, "survey_info_id": form.survey_id.data})
                db_session.commit()
            elif request.form['action'] == 'Disable':
                db_session.query(DeployedURL).filter_by(deployed_url_id=deploymentid).update({"is_deployed": 'f'})
                db_session.commit()
            elif request.form['action'] == 'Enable':
                db_session.query(DeployedURL).filter_by(deployed_url_id=deploymentid).update({"is_deployed": 't'})
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

@app.route('/editquestionform/<int:questionid>', methods=['GET', 'POST'])
@login_required
def edit_question_form(questionid):
    question=Question.query.filter_by(question_id=questionid).one()
    option=Option.query.filter_by(question_id=questionid)
    form=QuestionForm(request.form).new()
    if request.method == 'GET':
        form.questiontext.data = question.question_text
        form.questiondescription.data = question.question_description
        form.questiontype.data = question.question_type
        print(form.entries.data)

    if request.method == 'POST':
        if request.form['action'] == 'Submit':
            try:
                db_session.query(Question).filter_by(question_id=questionid).update({"question_text": form.questiontext.data, "question_description": form.questiondescription.data, "question_type": form.questiontype.data})
                db_session.query(Option).filter_by(question_id=questionid).delete()
                db_session.commit()
            except:
                print("Error inserting into kiosk_survey")
                db_session.rollback()
            finally:
                db_session.close()
            for entries in form.entries.data:
                o=Option(question_id=questionid, text=entries['option'], response_position=entries['responseposition'], option_color=entries['optioncolor'])
                try:
                    db_session.add(o)
                    db_session.commit()
                except:
                    db_session.rollback()
                finally:
                    db_session.close()
            return redirect(url_for('show_questions'))

        if request.form['action'] == 'Delete':
            try:
                db_session.query(Option).filter_by(question_id=questionid).delete()
                db_session.query(Question).filter_by(question_id=questionid).delete()
                db_session.commit()
            except:
                print("Error deleting from kiosk_survey")
                db_session.rollback()
            finally:
                db_session.close()
            return redirect(url_for('show_questions'))

    return render_template("edit_question_form.html", form=form, qid=questionid)

@app.route('/survey/<int:surveyid>', methods=['GET'])
@login_required
def survey_page(surveyid):
    s=SurveyInfo.query.filter_by(survey_info_id=surveyid).one()
    #q=SurveyQuestion.query.filter_by(survey_info_id=surveyid).join(Question, SurveyQuestion.question_id==Question.question_id)
    q=Question.query.join(SurveyQuestion, Question.question_id == SurveyQuestion.question_id).filter_by(survey_info_id=surveyid).order_by(SurveyQuestion.question_position)
    d=KioskSurvey.query.join(SurveyInfo, KioskSurvey.survey_info_id == SurveyInfo.survey_info_id).filter_by(survey_info_id=surveyid)
    if d.count() is 0:
        hasData = False
    else:
        hasData = True
    return render_template("surveypage.html", survey=s, questions=q, deployments=d, hasData=hasData)

@app.route('/editsurveyform/<int:surveyid>', methods=['GET', 'POST'])
@login_required
def edit_survey_form(surveyid):
    survey=SurveyInfo.query.filter_by(survey_info_id=surveyid).one()
    form=SurveyForm(request.form).new()
    if request.method == 'GET':
        form.surveyname.data = survey.survey_name
        form.description.data = survey.description

    if request.method == 'POST':
        if request.form['action'] == 'Submit':
            try:
                db_session.query(SurveyInfo).filter_by(survey_info_id=surveyid).update({"survey_name": form.surveyname.data, "description": form.description.data})
                db_session.query(SurveyQuestion).filter_by(survey_info_id=surveyid).delete()
                db_session.commit()
                survey_id=survey.survey_info_id
            except:
                print("Error inserting into kiosk_survey")
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

        elif request.form['action'] == 'Delete':
            try:
                db_session.query(SurveyQuestion).filter_by(survey_info_id=surveyid).delete()
                db_session.query(SurveyInfo).filter_by(survey_info_id=surveyid).delete()
                db_session.commit()
            except:
                print("Error deleting from kiosk_survey")
                db_session.rollback()
            finally:
                db_session.close()
            return redirect(url_for('show_surveys'))

    return render_template("edit_survey_form.html", form=form, sid=surveyid)

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
    d=DeployedURL.query.order_by(desc('is_deployed')).all()
    return render_template('show_deployments.html', deployments=d)

@app.route('/showsurveys', methods=['GET'])
@login_required
def show_surveys():
    s=SurveyInfo.query.order_by('survey_info_id').all()
    return render_template('show_surveys.html', surveys=s)

@app.route('/showquestions', methods=['GET'])
@login_required
def show_questions():
    question=Question.query.order_by('question_id').all()
    #entries=[dict(questiontext=q.questiontext, questionurl=q.questionurl) for q in question]
    entries=question
    return render_template('show_questions.html', questions=entries)

@app.route('/createuser', methods=['GET', 'POST'])
@login_required
def create_user():
    form=UserForm(request.form).new()
    if request.method == 'POST' and form.validate():
        user=User(name=form.name.data, email=form.email.data)
        try:
            db_session.add(user)
            db_session.commit()
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()
        return redirect(url_for('show_users'))
    else:
        print(form.errors)
    return render_template('user_form.html', form=form)

@app.route('/showusers', methods=['GET'])
@login_required
def show_users():
    u=User.query.all()
    return render_template('show_users.html', users=u)

''' This is disabled as we would like to keep this functionality through the use of database only
@app.route('/edituserform/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user_form(id):
    user=User.query.filter_by(id=id).one()
    form=UserForm(request.form).new()
    if request.method == 'GET':
        form.name.data = user.name
        form.email.data = user.email

    if request.method == 'POST':
        if request.form['action'] == 'Submit':
            try:
                db_session.query(SurveyInfo).filter_by(survey_info_id=surveyid).update({"survey_name": form.surveyname.data, "description": form.description.data})
                db_session.query(SurveyQuestion).filter_by(survey_info_id=surveyid).delete()
                db_session.commit()
                survey_id=survey.survey_info_id
            except:
                print("Error inserting into kiosk_survey")
                db_session.rollback()
                raise
            finally:
                db_session.close()
    return render_template("edit_survey_form.html", form=form, id=id)'''
