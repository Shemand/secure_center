from sc_statistic.http import db
from sc_statistic.http.users import constants as USER

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    Structures_id_access = db.Column(db.Integer, db.ForeignKey('Structures.id'))
    login = db.Column(db.String(64), nullable=False)
    password = db.Column(nullable=False)
    email = db.Column(db.String(128))
    isAdmin = db.Column(db.Integer, nullable=False)
    activated = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, name=None,email=None,password=None):
        self.name = name
        self.email = email
        self.password = password

    def getStatus(self):
        return USER.STATUS[self.status]

    def __repr__(self):
        return '<User %r>' % self.login

