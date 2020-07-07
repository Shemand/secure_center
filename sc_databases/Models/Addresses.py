from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Column
from sqlalchemy.orm import relationship

class Addresses(BaseModel):
    __tablename__ = "Addresses"

    ip = Column(String(15), primary_key=True, nullable=False)
    isBlocked = Column(Boolean, nullable=False, default=True)
    attempts_count = Column(Integer, nullable=False, default=1)
    expiration_time = Column(DateTime)
    active_to_block = Column(Boolean, nullable=False, default=False)
    Crypto_Gateways_id = Column(Integer, ForeignKey('Crypto_Gateways.id'))

    crypto_gateway = relationship('Crypto_Gateways', backref='addresses')

    def __repr__(self):
        return "<Addresses (ip: %r)>" % (self.ip)