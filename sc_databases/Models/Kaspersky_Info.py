from datetime import datetime

from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Column
from sqlalchemy.orm import relationship


class Kaspersky_Info(BaseModel):
    __tablename__ = "Kaspersky_Info"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    server = Column(String(32), nullable=False)
    agent_version = Column(String(16))
    security_version = Column(String(16))
    hasDuplicate = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, nullable=False, default=datetime.now())
    ARMs_id = Column(Integer, ForeignKey('ARMs.id'), nullable=False)
    Addresses_ip = Column(String(15), ForeignKey('Addresses.ip'))
    Operation_System_name = Column(String(64), ForeignKey('Operation_System.name'))

    ARM = relationship("ARMs")
    Address = relationship("Addresses", backref="kaspersky")

    def __eq__(self, other):
        if self.ARMs_id == 1475:
            print('ff')
        if isinstance(other, Kaspersky_Info):
            if self.server == other.server \
                    and self.agent_version == other.agent_version \
                    and self.security_version == other.security_version \
                    and self.hasDuplicate == other.hasDuplicate \
                    and (self.ARMs_id == other.ARMs_id or self.ARM.name == other.ARM.name) \
                    and (self.Addresses_ip == other.Addresses_ip or self.Address.ip == other.Address.ip if self.Address is not None else False) \
                    and self.Operation_System_name == other.Operation_System_name:
                return True
        return False

    def __repr__(self):
        return "<Kaspersky_Info (agent: %r, security: %r, ARMs_id: %r)>" % (
        self.agent_version, self.security_version, self.ARMs_id)
