from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.testing.schema import Column


class Dallas_Servers(BaseModel):
    __tablename__ = "Dallas_Servers"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    name = Column(String(64), nullable=False, unique=True)

    def __repr__(self):
        return "<Dallas_Servers (name: %r>" % (self.name)