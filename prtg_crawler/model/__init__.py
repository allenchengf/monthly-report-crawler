from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

HOST = 'localhost'
PORT = '3306'
DATABASE = 'monthly_report'
USERNAME = 'root'
PASSWORD = 'root'
CHARSET = 'utf8mb4'

Base = declarative_base()

# engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset={}'.format(USERNAME, PASSWORD, HOST, DATABASE, CHARSET))
engine = create_engine('mysql+pymysql://root:root@localhost:3306/monthly_report?charset=utf8', pool_size=100)

def loadSession():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
