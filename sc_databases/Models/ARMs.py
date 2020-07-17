from datetime import datetime, date
import datetime as datetimeClass

from sqlalchemy.orm import relationship

from sc_databases.Addr import Addr
from sc_databases.Database import BaseModel
from sqlalchemy import Integer, String, Boolean, Text, DateTime, ForeignKey, Date, Column, desc

from sc_databases.Models.Addresses import Addresses
from sc_databases.Models.Crypto_Gateways import Crypto_Gateways
from sc_databases.Models.Dallas_Statuses import Dallas_Statuses
from sc_databases.Models.Kaspersky_Info import Kaspersky_Info
from sc_databases.Models.Structures import Structures
from sc_databases.OS import OS


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

    @staticmethod
    def get_all_ready_data(session):
        print('begin')
        stmt_crypto_gateway = session.query(Crypto_Gateways.id.label('CG_id')
                                           ,Crypto_Gateways.name.label('CG_name')
                                           ,Crypto_Gateways.caption.label('CG_caption'))\
                                     .subquery()
        stmt_addresses = session.query(Addresses.ip.label('ip')
                                      ,stmt_crypto_gateway.c.CG_name.label('CG_name')
                                      ,stmt_crypto_gateway.c.CG_caption.label('CG_caption'))\
                                .outerjoin(stmt_crypto_gateway,
                                           stmt_crypto_gateway.c.CG_id == Addresses.Crypto_Gateways_id)\
                                .subquery()
        stmt_kaspersky = session.query(Kaspersky_Info.agent_version.label('agent_version')
                                      ,Kaspersky_Info.security_version.label('security_version')
                                      ,Kaspersky_Info.ARMs_id.label('ARMs_id')
                                      ,Kaspersky_Info.hasDuplicate.label('hasDuplicate')
                                      ,Kaspersky_Info.Operation_System_name.label('os')
                                      ,stmt_addresses.c.ip.label('ip')
                                      ,stmt_addresses.c.CG_name.label('CG_name'))\
                                .outerjoin(stmt_addresses,
                                           stmt_addresses.c.ip == Kaspersky_Info.Addresses_ip)\
                                .order_by(desc(Kaspersky_Info.created))\
                                .limit(1)\
                                .subquery()
        data = session.query(ARMs.name.label('computername')
                            ,ARMs.registred_ad.label('registred_ad')
                            ,ARMs.last_visible.label('last_visible')
                            ,ARMs.comment.label('comment')
                            ,ARMs.isActive.label('isActive')
                            ,Structures.name.label('unit')
                            ,stmt_kaspersky.c.agent_version.label('agent_version')
                            ,stmt_kaspersky.c.security_version.label('security_version')
                            ,stmt_kaspersky.c.ARMs_id.label('ARMs_id')
                            ,stmt_kaspersky.c.hasDuplicate.label('hasDuplicate')
                            ,stmt_kaspersky.c.os.label('os')
                            ,stmt_kaspersky.c.ip.label('ip')
                            ,stmt_kaspersky.c.CG_name.label('CG_name'))\
                      .outerjoin(stmt_kaspersky, ARMs.id == stmt_kaspersky.c.ARMs_id)\
                      .outerjoin(Structures, ARMs.Structures_id == Structures.id) \
                      .filter(ARMs.isDeleted == None)\
                      .all()
        return data

    def actual_kaspersky(self):
        return self.kaspersky.order_by(Kaspersky_Info.created.desc()).first()

    def actual_dallas(self):
        return self.dallas.order_by(Dallas_Statuses.created.desc()).first()

    def update_kaspersky(self, session, server=None, agent_version=None,
                         security_version=None, hasDuplicate=None,
                         ip=None, os=None):
        kasper = self.actual_kaspersky()
        if ip is not None:
            ip = Addr().GET(ip)
        if os is not None:
            os = OS().GET(os)
        if kasper is not None:
            if not (kasper.server == server \
                and kasper.agent_version == agent_version\
                and kasper.security_version == security_version\
                and kasper.hasDuplicate == hasDuplicate\
                and kasper.Operation_System_name == os.name\
                and kasper.Addresses_ip == ip.ip) or not kasper:
                kasper = Kaspersky_Info(server=server,
                                        agent_version=agent_version,
                                        security_version=security_version,
                                        hasDuplicate=hasDuplicate,
                                        ARM=self,
                                        Addresses_ip=ip.ip,
                                        Operation_System_name=os.name)
                session.add(kasper)
        else:
            kasper = Kaspersky_Info(server = server,
                                    agent_version = agent_version,
                                    security_version = security_version,
                                    hasDuplicate = hasDuplicate,
                                    ARM = self,
                                    Addresses_ip = ip.ip,
                                    Operation_System_name = os.name)
            session.add(kasper)

    def update_dallas_status(self, session, server, type_code):
        if int(type_code) not in Dallas_Statuses.TYPES:
            print("unknown dallas code in Dallas_Statuses.TYPES.")
            return None
        check = self.actual_dallas()
        if check:
            if not (server == check.server
                and int(type_code) == check.type):
                    dallas = Dallas_Statuses(type=int(type_code),
                                             server=server,
                                             ARM=self)
                    session.add(dallas)
        else:
            dallas = Dallas_Statuses(type = int(type_code),
                                     server = server,
                                     ARM = self)
            session.add(dallas)

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