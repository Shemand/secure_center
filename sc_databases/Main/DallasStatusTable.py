from datetime import datetime

from sqlalchemy import select, and_, desc


class DallasStatusTable:
    def __init__(self, db):
        self.db = db

    def add(self, _computer_id, _type, **kwargs):
        if _type:
            add = self.db.tDallasStatus.insert().values(type=_type, created=datetime.now(), ARMs_id=_computer_id, **kwargs)
            self.db.engine.execute(add)
            return self.get_last_by_id(_computer_id)["id"]
        return None

    def get_last(self, _computer_name):
        if _computer_name is not "":
            query = select([self.db.tDallasStatus]).where(self.db.tDallasStatus.c.ARMs_id == select([self.db.tARMs.c.id]).where(self.db.tARMs.c.name == _computer_name)).order_by(desc(self.db.tDallasStatus.c.created)).limit(1)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_last_by_id(self, _id):
        if _id:
            query = select([self.db.tDallasStatus]).where(self.db.tDallasStatus.c.ARMs_id == _id).order_by(desc(self.db.tDallasStatus.c.created)).limit(1)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None