from datetime import datetime, date
import datetime as datetimeClass

from sqlalchemy.orm import relationship

from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, Text, DateTime, ForeignKey, Date, Column

from sc_databases.Models.Dallas_Statuses import Dallas_Statuses
from sc_databases.Models.Kaspersky_Info import Kaspersky_Info


class ARMs(BaseModel):
    __tablename__ = "ARMs"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    name = Column(String(64), nullable=False, unique=True)
    created = Column(DateTime, nullable=False, default=datetime.now())
    registred_ad = Column(Date)
    last_visible = Column(Date)
    type = Column(Integer, nullable=False, default=1)
    isActive = Column(Boolean, nullable=False, default=1)
    isDeleted = Column(DateTime)
    comment = Column(Text)
    Structures_id = Column(Integer, ForeignKey('Structures.id'), nullable=False)

    kaspersky = relationship(Kaspersky_Info, lazy='dynamic')
    dallas = relationship(Dallas_Statuses, lazy="dynamic")

    TYPE_ARM = 1
    TYPE_SERVER = 2
    TYPES = [TYPE_ARM, TYPE_SERVER]

    def actual_kaspersky(self):
        return self.kaspersky.order_by(Kaspersky_Info.created.desc()).first()

    def actual_dallas(self):
        return self.dallas.order_by(Dallas_Statuses.created.desc()).first()

    def update_last_visible(self, dt):
        if type(dt) == datetimeClass.date:
            dt = datetime.combine(dt, datetime.min.time())
        if type (self.last_visible) == datetimeClass.date:
            self.last_visible = datetime.combine (self.last_visible, datetime.min.time ())
        if isinstance(dt, datetime):
            lv = self.last_visible
            if lv is not None:
                if lv < dt:
                    self.last_visible = dt
                    return True
            else:
                self.last_visible = dt
        return False

    def __repr__(self):
        return "<ARMs (name: %r)>" % (self.name)