from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.testing.schema import Column


class Addresses(BaseModel):
    __tablename__ = "Addresses"

    ip = Column(String(15), primary_key=True, nullable=False)
    isBlocked = Column(Boolean, nullable=False)
    attempts_count = Column(Integer, nullable=False)
    expiration_time = Column(DateTime)
    active_to_block = Column(Boolean, nullable=False)
    Crypto_Gateways_id = Column(Integer, ForeignKey('Crypto_Gateways.id'))

    crypto_gateway = relationship('Crypto_Gateways', backref='addresses')

    def __repr__(self):
        return "<Addresses (ip: %r)>" % (self.ip)