from datetime import datetime

from sqlalchemy import select, and_, desc, update, func


class AdaptersTable:
    def __init__(self, db):
        self.db = db

    def add(self, _computername, _caption, _mac, _ipv4, _ipv6=None, _dhcp=None, _domain=None):
        computer = self.db.ARMs.get_one(_computername)
        if computer is not None:
            add = self.db.tAdapters.insert().values(caption=_caption, ARMs_id=computer['id'], dhcp=_dhcp, mac=_mac, ipv4=_ipv4, ipv6=_ipv6, domain=_domain, created=datetime.now())
            self.db.engine.execute(add)
            return self.get_last_by_mac(_mac)["id"]
        return None

    def get_computer_actual_adapters(self, _computername):
        adapters = []
        computer = self.db.ARMs.get_one(_computername)
        if computer is not None:
            a = self.db.tAdapters.alias('a')
            s = select([self.db.tAdapters.c.mac, func.max(self.db.tAdapters.c.created).label("created")]).group_by(self.db.tAdapters.c.mac).alias('s')
            query = select([a, s]).where(and_(a.c.mac == s.c.mac, a.c.created == s.c.created, a.c.ARMs_id == computer['id']))
            rows = self.db.engine.execute(query)
            for adapter in rows:
                adapters.append(adapter)
        return adapters

    def get_last_by_mac(self, _mac):
        if _mac:
            query = select([self.db.tAdapters]).where(self.db.tAdapters.c.mac == _mac).order_by(desc(self.db.tAdapters.c.created)).limit(1)
            row = self.db.engine.execute(query).fetchone()
            if row:
                return row
        return None

    def get_by_id(self, _id):
        if _id:
            query = select([self.db.tAdapters]).where(self.db.tAdapters.c.id == _id)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def update_adapter(self, _computername, _caption, _mac, _ipv4, _ipv6=None, _dhcp=None, _domain=None):
        adapter = self.get_last_by_mac(_mac)
        if adapter:
            if _ipv4 != adapter['ipv4'] or _ipv6 and _ipv6 != adapter['ipv6']:
                self.add(_computername, _caption, _mac, _ipv4, _ipv6=_ipv6, _dhcp=_dhcp, _domain=_domain)
        else:
            self.add(_computername, _caption, _mac, _ipv4, _ipv6=_ipv6, _dhcp=_dhcp, _domain=_domain)