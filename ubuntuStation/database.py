from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import json

with open('config.json') as json_data_file:
    data=json.load(json_data_file)
url = 'postgresql://' + data["user"] + ":" + data["pass"] + "@localhost" + ":" + data["port"] + "/" + "dbname"

engine=create_engine(url)
db_session=scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
