from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Boolean, Text, ForeignKey
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

BaseModel = declarative_base()

class DatabaseClass(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DatabaseClass, cls).__new__(cls)
            cls.instance.init()
        return cls.instance

    def init(self):
        db_url = {
            'database': "secure_center_v2",
            'drivername': "mysql",
            'username': "root",
            'password': "qwerty",
            'host': "localhost",
            'query': {'charset': 'utf8'}
        }
        self.BaseModel = BaseModel
        self.__engine = create_engine(URL(**db_url), echo=False, encoding="utf8", pool_size=10)
        self.BaseModel.metadata.create_all(self.__engine)
        self.session = Session(bind=self.__engine)
        self.session.commit()

    def get_local_session(self):
        return Session(bind=self.__engine)

    def update(self):
        self.session.commit()

    def cancel_changes(self):
        self.session.rollback()