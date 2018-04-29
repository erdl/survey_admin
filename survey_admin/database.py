from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import json
import os

file_path= os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'config.json')

with open(file_path) as json_data_file:
    data=json.load(json_data_file)
url = 'postgresql://' + data["user"] + ":" + data["pass"] + "@localhost" + ":" + data["port"] + "/" + data["dbname"]

engine=create_engine(url)
db_session=scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
