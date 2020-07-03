from sc_databases.Database import BaseModel
from sqlalchemy import String, Boolean
from sqlalchemy.testing.schema import Column


class Operation_System(BaseModel):
    __tablename__ = "Operation_System"

    name = Column(String(64), primary_key=True, nullable=False, unique=True)
    isUnix = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<Operation_System (name: %r)>" % (self.name)