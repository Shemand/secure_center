from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash


class UsersTable:
    def __init__(self, db):
        self.db = db

    def add(self, _login, _password, _name=None, _structures_name=None, _email=None, _activated=0):
        if self.get_one(_login) is None:
            if _structures_name is not None:
                _root_id = self.db.Structures.get_one(_structures_name)["id"]
            else:
                _root_id = None
            _structures_id = None
            if _structures_name is not None and _structures_name != "":
                query = select([self.db.tStructures]).where(self.db.tStructures.c.name == _structures_name)
                _structures_id = self.db.engine.execute(query).fetchone()["id"]
            params = {
                "name" : _name,
                "login" : _login,
                "password" : generate_password_hash(_password),
                "Structures_id_access" : _structures_id,
                "email" : _email,
                "activated" : 0
            }
            query = self.db.tUsers.insert().values(params)
            try:
                self.db.engine.execute(query)
                return self.get_one(_login)["id"]
            except IntegrityError:
                return None
        return None

    def get_one(self, _login):
        if _login and _login is not "":
            query = select([self.db.tUsers]).where(self.db.tUsers.c.login == _login)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_by_id(self, _id):
        if _id:
            query = select([self.db.tUsers]).where(self.db.tUsers.c.id == _id)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def available_computers(self, _id):
        if _id is not None:
            user = self.get_by_id(_id)
            if user and user['Structures_id_access'] is not None:
                computers = self.db.ARMs.get_by_root(self.db.Structures.get_by_id(user['Structures_id_access'])["name"])
                c_names = []
                for computer in computers:
                    c_names.append(computer['name'])
                return c_names
        return []

    def check_password(self, _login, _password):
        user = self.get_one(_login)
        if user is not None:
            return check_password_hash(user['password'], _password)
        return False
