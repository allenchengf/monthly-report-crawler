from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

HOST = 'localhost'
PORT = '3306'
DATABASE = 'monthly_report'
USERNAME = 'root'
PASSWORD = 'root'
CHARSET = 'utf8mb4'

Base = declarative_base()

engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset={}'.format(USERNAME, PASSWORD, HOST, DATABASE, CHARSET))

def loadSession():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
