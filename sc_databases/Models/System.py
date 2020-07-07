from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Text, Column


class System(BaseModel):
    __tablename__ = "System"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    parameter = Column(String(32), nullable=False, unique=True)
    type = Column(Integer, nullable=False)
    value = Column(Text)

    def __repr__(self):
        return "<System (parameter: %r, value: %r)>" % (self.parameter, self.value)