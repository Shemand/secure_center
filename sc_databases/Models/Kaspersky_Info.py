from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.testing.schema import Column


class Kaspersky_Info(BaseModel):
    __tablename__ = "Kaspersky_Info"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    server = Column(String(32), nullable=False)
    agent_version = Column(String(16))
    security_version = Column(String(16))
    hasDuplicate = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, nullable=False)
    ARMs_id = Column(Integer, ForeignKey('ARMs.id'), nullable=False)
    Addresses_ip = Column(String(15), ForeignKey('Addresses.ip'))
    Operation_System_name = Column(String(64), ForeignKey('Operation_System.name'))

    ARM = relationship("ARMs", backref="kaspersky")
    Addresses = relationship("Addresses", backref="kaspersky")

    def __repr__(self):
        return "<Kaspersky_Info (agent: %r, security: %r, ARMs_id: %r)>" % (self.agent_version, self.security_version, self.ARMs_id)