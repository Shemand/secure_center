from sc_databases.Database import DatabaseClass
from sc_databases.Models.ARMs import ARMs
from sc_databases.Models.ARMs_and_Patches import ARMs_and_Patches
from sc_databases.Models.Adapters import Adapters
from sc_databases.Models.Addresses import Addresses
from sc_databases.Models.Crypto_Gateways import Crypto_Gateways
from sc_databases.Models.Dallas_Servers import Dallas_Servers
from sc_databases.Models.Dallas_Statuses import Dallas_Statuses
from sc_databases.Models.Devices import Devices
from sc_databases.Models.Kaspersky_Info import Kaspersky_Info
from sc_databases.Models.Logons import Logons
from sc_databases.Models.Operation_Systems import Operation_System
from sc_databases.Models.Patches import Patches
from sc_databases.Models.Structures import Structures
from sc_databases.Models.System import System
from sc_databases.Models.Update_Logs import Update_Logs
from sc_databases.Models.Users import Users
from sc_databases.Addr import Addr
from sc_databases.OS import OS


class Computers:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Computers, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        db = DatabaseClass()
        self.session = db.session
        self.__computers = {row.name : row for row in db.session.query(ARMs).all()}
        self.__addresses = Addr()
        self.__os = OS()

    def get(self, name=None):
        if not name:
            return self.__computers
        else:
            if self.__computers[name]:
                return self.__computers[name]
        return None

    def update_kaspersky(self, ARMs_name, server, **kwargs):
        if not ARMs_name in self.__computers:
            print("Can't attach kaspersky to computer with name: " + ARMs_name + " because ARMs_name didn't found in self.__computers")
            return None
        ip = None
        if kwargs['ip'] is not None:
            ip = self.__addresses.get(kwargs['ip'])
        if kwargs['os'] is not None:
            os = self.__os.get(kwargs['os'])
        check = self.__computers[ARMs_name].actual_kaspersky()
        kasper = Kaspersky_Info(server=server,
                                agent_version=kwargs["agent_version"] if 'agent_version' in kwargs and kwargs['agent_version'] else None,
                                security_version=kwargs["security_version"] if 'security_version' in kwargs and kwargs['security_version'] else None,
                                hasDuplicate=kwargs["hasDuplicate"] if 'hasDuplicate' in kwargs and kwargs['hasDuplicate'] else False,
                                ARM=self.__computers[ARMs_name],
                                Address=ip,
                                Operation_System_name=os.name)
        if check != kasper:
            self.session.add(kasper)
            self.session.commit()

    def get_address_row(self, ip):
        pass
        if not ip in self.__addresses:
            self.session.add()