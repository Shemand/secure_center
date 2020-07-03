from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.testing.schema import Column


class Devices(BaseModel):
    __tablename__ = "Devices"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    name = Column(String(64), nullable=False, unique=False)
    type = Column(Integer, nullable=False)
    comment = Column(Text)
    Crypto_Gateways_id = Column(Integer, ForeignKey("Crypto_Gateway.id"), nullable=False)
    Addresses_id = Column(String(15), ForeignKey("Addresses.ip"), nullable=False)

    Crypto_Gateway = relationship("CryptoGateways", backref="devices")
    Addresses = relationship("Addresses", backref="devices")

    def __repr__(self):
        return "<Devices (name: %r,)>" % (self.name)