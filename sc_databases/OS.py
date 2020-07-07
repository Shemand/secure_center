import ipaddress
import os

from sc_cus import CryptoGateway
from sc_databases.Database import DatabaseClass
from sc_databases.Models.Addresses import Addresses
from sc_databases.Models.Crypto_Gateways import Crypto_Gateways
from sc_databases.Models.Operation_Systems import Operation_System
from sc_databases.Models.Structures import Structures
from sc_databases.Models.Update_Logs import Update_Logs


class OS:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OS, cls).__new__(cls)
            cls.instance.init()
        return cls.instance

    def init(self):
        self.db = DatabaseClass()
        self.session = self.db.session
        self.__os_names = {row.name : row for row in self.session.query(Operation_System).all()}

    def get(self, name=None):
        if not name:
            return self.__os_names
        else:
            if name in self.__os_names:
                return self.__os_names[name]
            else:
                os = Operation_System(name=name, isUnix=True if name.lower().find('win') == -1 else False)
                self.session.add(os)
                self.session.commit()
                self.__os_names[name] = os
                return self.__os_names[name]