import threading
from datetime import datetime
from sqlalchemy import select, and_, update

class LogonsTable:
    def __init__(self, db):
        self.db = db
        self.lock = threading.Lock()

    def add(self, _computername, _username, _os, _domain_server=None):
        computer = self.db.ARMs.get_one(_computername)
        if computer is not None:
            add = self.db.tLogons.insert().values(username=_username.lower(), ARMs_id=computer['id'], os=_os, updated=datetime.now(), domain_server=_domain_server,logon_counter=0, created=datetime.now())
            self.db.engine.execute(add)
        return self.get_one(_computername, _username)["id"]

    def increment_counter(self, _comuptername, _username):
        logon_row = self.get_one(_comuptername, _username)
        if logon_row:
            query = update(self.db.tLogons).where(self.db.tLogons.c.id == logon_row['id']).values(logon_counter=logon_row['logon_counter']+1)
            self.db.engine.execute(query)

    def get_one(self, _computername, _username):
        if _username is not "" and _computername is not "":
            _username = _username.lower()
            computer = self.db.ARMs.get_one(_computername)
            if computer is not None:
                query = select([self.db.tLogons]).where(and_(self.db.tLogons.c.username == _username, self.db.tLogons.c.ARMs_id == computer['id']))
                row = self.db.engine.execute(query).fetchone()
                return row
        return None

    def get_by_id(self, _id):
        if _id:
            query = select([self.db.tLogons]).where(self.db.tLogons.c.id == _id)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def login(self, _computername, _username, _os, adapters, _domain_server=None):
        with self.lock:
            _username = str(_username).lower()
            if _computername and _username:
                logon = self.get_one(_computername, _username)
                if logon is not None:
                    computer = self.db.ARMs.get_one(_computername)
                    if computer is not None:
                        query = update(self.db.tLogons).where(and_(self.db.tLogons.c.username == _username, self.db.tLogons.c.ARMs_id == computer['id'])).values(domain_server=_domain_server, os=_os, updated=datetime.now())
                        self.db.engine.execute(query)
                else:
                    from sc_statistic.Computer import Computer
                    computer = Computer(_computername)
                    if computer:
                        self.db.ARMs.add(computer)
                        self.add(_computername, _username, _os, _domain_server=_domain_server)
                for adapter in adapters:
                    if adapter['ipv4'] is not "127.0.0.1":
                        self.db.Adapters.update_adapter(_computername, adapter['caption'], adapter['mac'], adapter['ipv4'],
                                                        _ipv6=adapter['ipv6'], _dhcp=adapter['dhcp'], _domain=adapter['domain'])
                self.increment_counter(_computername, _username)
                return self.get_one(_computername, _username)