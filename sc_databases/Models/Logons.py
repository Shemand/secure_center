from datetime import datetime

from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, DateTime, ForeignKey, Column
from sqlalchemy.orm import relationship


class Logons(BaseModel):
    __tablename__ = "Logons"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    domain_server = Column(String(64))
    username = Column(String(128), nullable=False)
    logon_counter = Column(Integer, default=0)
    updated = Column(DateTime, nullable=False, default=datetime.now())
    created = Column(DateTime, nullable=False, default=datetime.now())
    ARMs_id = Column(Integer, ForeignKey('ARMs.id'))
    Operation_System_name = Column(String(64), ForeignKey('Operation_System.name'), nullable=False)

    ARM = relationship("ARMs", backref="logons")

    def __repr__(self):
        return "<Logons (username: %r, ARMs_id: %r)>" % (self.username, self.ARMs_id)