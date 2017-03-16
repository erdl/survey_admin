import json, os
basedir = os.path.abspath(os.path.dirname(__file__))

with open('config.json') as json_data_file:
    data=json.load(json_data_file)
    SQLALCHEMY_DATABASE_URI = "postgresql://" + data["user"] + ":" + data["pass"] + "@localhost/" + data["dbname"]
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_ENABLED=True
    SECRET_KEY='something_secret_we_need_to_change'

