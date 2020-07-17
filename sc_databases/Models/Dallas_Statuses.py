from datetime import datetime

from sc_databases.Database import BaseModel
from sqlalchemy import Integer, DateTime, ForeignKey, Column, String
from sqlalchemy.orm import relationship


class Dallas_Statuses(BaseModel):
    __tablename__ = "Dallas_Statuses"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    type = Column(Integer, nullable=False)
    server = Column(String(64), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.now())
    ARMs_id = Column(Integer, ForeignKey('ARMs.id'), nullable=False)

    ARM = relationship("ARMs")

    # Types of status
    TYPE_INSTALLED_ON = 4
    TYPE_INSTALLED_OFF = 5
    TYPE_ERROR = 6
    TYPE_CRITICAL_ERROR = 9
    TYPE_UNKNOWN_ERROR = 37
    TYPES = [TYPE_INSTALLED_ON, TYPE_INSTALLED_OFF, TYPE_ERROR, TYPE_CRITICAL_ERROR, TYPE_UNKNOWN_ERROR]

    def __eq__(self, other):
        if isinstance(other, Dallas_Statuses):
            if self.type == other.type \
                    and self.server == other.server \
                    and (self.ARMs_id == other.ARMs_id or self.ARM == other.ARM):
                return True
        return False

    def __repr__(self):
        return "<Dallas_Statuses (type: %r, ARMs_id: %r)>" % (self.type, self.ARMs_id)
