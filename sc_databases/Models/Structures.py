from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Column


class Structures(BaseModel):
    __tablename__ = "Structures"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    name = Column(String(64), nullable=False, unique=True)
    root_id = Column(Integer)

    def __repr__(self):
        return "<Structures (name: %r, root_id: %r)>" % (self.name, self.root_id)