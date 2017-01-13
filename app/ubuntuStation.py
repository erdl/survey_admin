#!/usr/bin/env python3

import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

#create the application
app = Flask(__name__)
#load configurations from this file
app.config.from_object(__name__)

#load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'ubuntuStation.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('APP_SETTINGS', silent=True)

def connect_db():
    #connects to specific database
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    #initializes DB using command "flask initdb"
    init_db()
    print('Initialized the database.')

def get_db():
    #opens new DB connection if there is none yet
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db=connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    #closes the database at the end of the request
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT * FROM questions limit 100')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db=get_db()
    db.execute('insert into questions (question, answer) values (?, ?)',
        [request.form['question'], request.form['answer']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/display')
def display():
    db=get_db()
    return render_template('survey_mode.html')
    
@app.route('/admin-dashboard')
def admin():
    db=get_db()
    return render_template('admin_dashboard.html')

@app.route('/admin-dashboard', methods=['POST'])
def admin_post():
    db=get_db()
    numOptions=request.form['numOptions']
    question=request.form['question']
    cur=db.execute('insert into question (questiontext) values (?)', [question])
    db.commit()
    questionid=cur.lastrowid
    for i in range(int(numOptions)):
        cur=db.execute('insert into option (optiontext, questionid) values (?, ?)', (request.form['option['+str(i)+']'], questionid))
        db.commit()
    result = db.execute('select question.questiontext, option.optiontext from question join option on question.questionid=option.questionid order by question.questiontext')
    entries=result.fetchall()
    questions=[dict(questiontext=row[0], optiontext=row[1]) for row in entries]
    db.close()
    return render_template('show_questions.html', questions=questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error='Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error='Invalid password'
        else:
            session['logged_in']=True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
