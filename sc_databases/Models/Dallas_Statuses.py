from sc_databases.Database import BaseModel
from sqlalchemy import Integer, DateTime, ForeignKey, Column
from sqlalchemy.orm import relationship


class Dallas_Statuses(BaseModel):
    __tablename__ = "Dallas_Statuses"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    type = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)
    ARMs_id = Column(Integer, ForeignKey('ARMs.id'), nullable=False)

    ARM = relationship("ARMs", backref="dallas_statuses")

    def __repr__(self):
        return "<Dallas_Statuses (type: %r, ARMs_id: %r)>" % (self.type, self.ARMs_id)