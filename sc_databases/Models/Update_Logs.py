from datetime import datetime

from sc_databases.Database import BaseModel
from sqlalchemy import Integer, Text, DateTime, Column


class Update_Logs(BaseModel):
    __tablename__ = "Update_Logs"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    text = Column(Text, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return "<Update_Logs (id: %r, text: %r)>" % (self.id, self.text)