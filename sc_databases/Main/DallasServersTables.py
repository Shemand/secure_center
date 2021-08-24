from sqlalchemy import select

class DallasServersTable:
    def __init__(self, db):
        self.db = db

    def add(self, _name, **kwargs):
        if self.get_one(_name) is None:
            add = self.db.tDallasServers.insert().values(name = _name, **kwargs)
            self.db.engine.execute(add)
        return self.get_one(_name)["id"]

    def get_one(self, _name):
        if _name is not "":
            query = select([self.db.tDallasServers]).where(self.db.tDallasServers.c.name == _name)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_by_id(self, _id):
        if _id:
            query = select([self.db.tDallasServers]).where(self.db.tDallasServers.c.id == _id)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_with_dallas(self, _structure_name):
        if _structure_name:
            computers = self.db.ARMs.get_by_root(_structure_name)
            with_dallas = []
            for computer in computers:
                if computer['dateDallasRegistred']:
                    with_dallas.append(computer)
            return with_dallas
        return []
