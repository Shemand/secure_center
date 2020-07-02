from datetime import datetime

from sqlalchemy import select, desc


class LogTables:
    def __init__(self, db):
        self.db = db

    def add_update_logs(self, _text):
        if _text is not None and _text != "":
            query = self.db.tUpdate_logs.insert().values(text=_text, created=datetime.now())
            self.db.engine.execute(query)
            print("[UPD LOGS]: " + _text)

    def get_last_100_update_logs(self):
        logs = []
        query = select([self.db.tUpdate_logs]).order_by(desc(self.db.tUpdate_logs.c.created)).limit(100)
        rows = self.db.engine.execute(query)
        for row in rows:
            logs.append({ "text" : row['text'], "date" : row['created']})
        return logs
