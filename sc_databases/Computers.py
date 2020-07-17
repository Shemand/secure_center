from datetime import datetime

from sc_databases.Models.ARMs import ARMs
from sc_databases.Models.ARMs_and_Patches import ARMs_and_Patches
from sc_databases.Models.Adapters import Adapters
from sc_databases.Models.Addresses import Addresses
from sc_databases.Models.Crypto_Gateways import Crypto_Gateways
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
from sc_databases.Database import DatabaseClass
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
            if name in self.__computers:
                return self.__computers[name]
        return None


    # Computers.add params:
    # name - computer name
    # Structures_id or Structures_name - (String) name or (Integer) id of Container ad where was attached computer
    # kwargs params - {
        # registred_ad - (Date) when computer was created in active directory
        # last_visible - (datetime) when computer was detected in anywhere
        # type - (ARMs.TYPES) is type of computer
        # isActive - (Boolean) is computer active or inactive
        # isDeleted - (datetime) is datetime when computer was deleted or None (like a flag)
        # comment - (String) comment of computer
        # kl - (Dictionary) {
            # agent - (String) version of Kaspersky_Info
            # security - (String) version of Kaspersky_Info security
            # ip - (String) ip address in format IPv4 from kaspersky server
            # server - (String) name of KSC
            # hasDuplicate - (Boolean) Flag is True if computer have duplicate
            # os - (String) Operation system name from KSC
        # }
        # dallas = (Dictionary) {
            # type - (Dallas_Statuses.TYPES) status type of dallas
            # server - (String) server name of dallas lock
        # }
    # }

    def add (self, name, Structures_id=None, Structures_name=None, **kwargs):
        name = name.upper()
        if name.find('\\') != -1:
            name = name[0:name.find('\\')]
        if not name in self.__computers:
            if Structures_id or Structures_name:
                if Structures_id:
                    struct = self.session.query(Structures).filter_by(id = Structures_id).one()
                elif Structures_name:
                    struct = self.session.query(Structures).filter_by(name = Structures_name).one()
                if struct is None:
                    print ('Computers.add not found in datebase. Computer wasn\'t added')
                    return None
                kasper = None
                dallas = None
                struct_id = struct.id
                registred_ad = kwargs['registred_ad'] if 'registred_ad' in kwargs else None
                last_visible = kwargs['last_visible'] if 'last_visible' in kwargs else None
                type = kwargs['type'] if 'type' in kwargs and kwargs['type'] in ARMs.TYPES else ARMs.TYPE_ARM
                isActive = kwargs['isActive'] if 'isActive' in kwargs else True
                isDeleted = datetime.now () if 'isDeleted' in kwargs else None
                comment = kwargs['comment'] if 'comment' in kwargs else None
                arm = ARMs (name = name,
                            registred_ad = registred_ad,
                            last_visible = last_visible,
                            type = type,
                            isActive = isActive,
                            isDeleted = isDeleted,
                            comment = comment,
                            Structures_id = struct_id,
                            kaspersky = [],
                            dallas=[])
                self.session.add(arm)
                self.session.commit()
                self.__computers[arm.name] = arm
                if 'kl' in kwargs:
                    kl = kwargs['kl']
                    if kl['server'] is None:
                        print ('dosn\'t set kl[\'server]\'')
                    else:
                        self.update_kaspersky(kl['server'],
                                              ARM=arm,
                                              agent_version = kl['agent'] if "agent" in kl else None,
                                              security_version = kl['security'] if "security" in kl else None,
                                              hasDuplicate = kl['hasDuplicate'] if "hasDuplicate" in kl else None,
                                              os=kl['os'] if "os" in kl else None,
                                              ip=kl['ip'] if "ip" in kl else None)
                if 'dallas' in kwargs:
                    dallas = kwargs['dallas']
                    if dallas['server'] is None or dallas['type'] is None:
                        print ('dosn\'t set dallas[\'server\'] or dallas[\'type\']')
                    else:
                        self.update_dallas_status(arm.name, dallas['server'], dallas['type'])
            else:
                print ('Computers.add must take params of Structures_id or Structures_name')
                return None
        return None

    def update_dallas_status(self, ARMs_name, server, type_code):
        if not ARMs_name in self.__computers:
            print("Can't attach dallas to computer with name: " + ARMs_name + " because ARMs_name didn't found in self.__computers")
            return None
        if str(type_code) not in Dallas_Statuses.TYPES:
            print("unknown dallas code in Dallas_Statuses.TYPES.")
            return None
        check = self.__computers[ARMs_name].actual_dallas()
        dallas = Dallas_Statuses(type=type_code,
                                 server=server,
                                 ARM=self.__computers[ARMs_name])
        if check != dallas:
            self.session.add(dallas)
            self.session.commit()
            return True
        return False


    def get_address_row(self, ip):
        pass
        if not ip in self.__addresses:
            self.session.add()