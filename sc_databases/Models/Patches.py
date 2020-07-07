from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Column


class Patches(BaseModel):
    __tablename__ = "Patches"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    name = Column(String(32), nullable=False, unique=True)

    def __repr__(self):
        return "<Patches (name: %r)>" % (self.name)