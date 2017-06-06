from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

user='webuser'
password='3n3rgy'
db='kiosk'
host='localhost'
port=5432
url = 'postgresql://{}:{}@{}:{}/{}'
url=url.format(user, password, host, port, db)

engine=create_engine(url)
db_session=scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
