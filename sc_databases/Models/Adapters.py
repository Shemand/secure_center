from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, DateTime, ForeignKey, Column
from sqlalchemy.orm import relationship


class Adapters(BaseModel):
    __tablename__ = "Adapters"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    caption = Column(String(256), nullable=False)
    mac = Column(String(17), nullable=False)
    ip_v6 = Column(String(64))
    dhcp = Column(String(15))
    domain = Column(String(64))
    created = Column(DateTime, nullable=False)
    ARMs_id = Column(Integer, ForeignKey('ARMs.id'), nullable=False)
    Addresses_ip = Column(String(15), ForeignKey('Addresses.ip'), nullable=False)

    arm = relationship('ARMs', backref='adapters')
    address = relationship('Addresses', backref='adapters')

    def __repr__(self):
        return "<Adapters (mac: %r)>" % (self.mac)