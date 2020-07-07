from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, Text, Column, ForeignKey
from sqlalchemy.orm import relationship


class Crypto_Gateways(BaseModel):
    __tablename__ = "Crypto_Gateways"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    name = Column(String(16), nullable=False, unique=True)
    address = Column(String(15), nullable=False)
    mask = Column(Integer, nullable=False)
    caption = Column(Text, nullable=False)
    active_to_block = Column(Boolean, nullable=False)
    Structures_id = Column(Integer, ForeignKey('Structures.id'), nullable=False)

    structure = relationship("Structures", backref="crypto_gateways")

    def __repr__(self):
        return "<Crypto_Gateways (name: %r, network: %r/%r)>" % (self.name, self.address, self.mask)