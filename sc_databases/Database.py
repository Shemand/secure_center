from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

BaseModel = declarative_base()

class Database(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        db_url = {
            'database': "secure_center_v2",
            'drivername': "mysql",
            'username': "root",
            'password': "qwerty",
            'host': "localhost",
            'query': {'charset': 'utf8'}
        }
        self.__engine = create_engine(URL(**db_url), echo=False, encoding="utf8", pool_size=10)
        self.BaseModel = BaseModel
        self.BaseModel.metadata.create_all(self.__engine)
        self.session = Session(bind=self.__engine)