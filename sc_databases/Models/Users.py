from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, Column


class Users(BaseModel):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    name = Column(String(256), nullable=False)
    login = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)
    email = Column(String(128))
    isAdmin = Column(Boolean, nullable=False)
    activated = Column(Integer, nullable=False)
    Structures_id_access = Column(Integer)

    def __repr__(self):
        return "<Users (login: %r)>" % (self.login)