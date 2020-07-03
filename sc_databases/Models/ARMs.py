from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, Text, DateTime, ForeignKey, Date
from sqlalchemy.testing.schema import Column


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
    Dallas_Servers_id = Column(Integer, ForeignKey('Dallas_Servers.id'))
    Structures_id = Column(Integer, ForeignKey('Structures.id'), nullable=False)

    def __repr__(self):
        return "<ARMs (name: %r)>" % (self.name)