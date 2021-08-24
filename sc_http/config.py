import os

from sqlalchemy.engine.url import URL

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['email@email.ru'])
SECRET_KEY = 'somekey'

db_url = {
    'database': "login",
    'drivername': "mysql",
    'username': "username",
    'password': "password",
    'host': "localhost",
    'query': {'charset': 'utf8'}
}

SQLALCHEMY_DATABASE_URI = URL(**db_url)
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 4

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "csrfsecritkey"
