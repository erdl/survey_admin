from app import app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from .forms import *
from .models import *
from .database import db_session


@app.route('/')
def home():
    return render_template('admin_landing.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/questionform', methods=['GET', 'POST'])
def questionform():
    form = QuestionForm(request.form)
    if request.method == 'POST':
        question=Question(form.questiontext.data, form.questionurl.data)
        db_session.add(question)
        db_session.commit()
        return redirect(url_for('show_questions'))
    return render_template('question_form.html', form=form)

@app.route('/surveyform', methods=['GET', 'POST'])
def survey_form():
    form=SurveyForm(request.form)
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
def deployment_form():
    form=DeploymentForm(request.form)
    if request.method == 'POST' and form.validate():
        deployment=DeployedURL(form.url_text.data, form.is_kiosk.data, form.building_id.data)
        try:
            db_session.add(deployment)
            db_session.commit()
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()
    else:
        print(form.errors)
    return render_template('deployment_form.html', form=form)
    
@app.route('/question/<int:questionid>', methods=['GET', 'POST'])
def question_page(questionid):
    q=Question.query.filter_by(question_id=questionid).one()
    #question=[dict(questiontext=q.questiontext, questionurl=q.questionurl)]
    o=Option.query.filter_by(question_id=q.question_id)
    print(o[0])
    #form=ActiveQuestionForm(request.form)
    #if request.method == 'POST':
    #    db_session.commit()
    #    return redirect(url_for('show_questions'))
    return render_template("questionpage.html", question=q, option=o)

@app.route('/survey/<int:surveyid>', methods=['GET'])
def survey_page(surveyid):
    s=SurveyInfo.query.filter_by(survey_info_id=surveyid).one()
    #q=SurveyQuestion.query.filter_by(survey_info_id=surveyid).join(Question, SurveyQuestion.question_id==Question.question_id)
    q=Question.query.join(SurveyQuestion, Question.question_id == SurveyQuestion.question_id).filter_by(survey_info_id=surveyid)
    return render_template("surveypage.html", survey=s, questions=q)

@app.route('/showdevices', methods=['GET'])
def show_devices():
    a=ActiveQuestion.query.all()
    aq=[dict(activequestionid=active.activequestionid, activequestionurl=active.activequestionurl, questiontext=(Question.query.filter_by(questionid=active.questionid)).first().questiontext) for active in a] 
    return render_template('show_devices.html', activequestions=aq)

@app.route('/showdeployments', methods=['GET'])
def show_deployments():
    d=DeployedURL.query.all()
    return render_template('show_deployments.html', deployments=d)

@app.route('/showsurveys', methods=['GET'])
def show_surveys():
    s=SurveyInfo.query.all()
    return render_template('show_surveys.html', surveys=s)

@app.route('/showquestions', methods=['GET'])
def show_questions():
    question=Question.query.all()
    #entries=[dict(questiontext=q.questiontext, questionurl=q.questionurl) for q in question]
    entries=question
    return render_template('show_questions.html', questions=entries)
