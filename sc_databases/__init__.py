from sc_databases.Main.AddressesTable import AddressesTable
from sc_databases.Main.CryptoGatewaysTable import CryptoGatewaysTable
from sc_databases.Main.LogTables import LogTables
from sc_databases.Main.LogonsTable import LogonsTable
from sc_databases.Main.AdaptersTable import AdaptersTable
from sc_databases.Main.DallasStatusTable import DallasStatusTable
from sc_databases.Main.KSC_InfoTable import KSC_InfoTable
from sc_databases.Main.PatchesTable import PatchesTable

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine.url import URL

import sc_databases.Main.DatabasesModels as Models
from sc_databases.Main.ARMsTable import ARMsTable
from sc_databases.Main.DallasServersTables import DallasServersTable
from sc_databases.Main.StructuresTable import StructuresTable
from sc_databases.Main.SystemTable import SystemTable
from sc_databases.Main.UsersTable import UsersTable
from sc_databases.Main.DevicesTable import DevicesTable

class Database(object):

    isUpdating = False

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
            cls.instance.init()
        return cls.instance

    def init(self):
        self.metadata = MetaData()
        db_url = {
            'database': "secure_center",
            'drivername': "mysql",
            'username': "root",
            'password': "qwerty",
            'host': "localhost",
            'query': {'charset': 'utf8'}
        }
        self.engine = create_engine(URL(**db_url), echo=False, encoding="utf8", pool_size=10)
        self.tStructures = Models.init_table_Structures(self.metadata)
        self.tDallasServers = Models.init_table_DallasServers(self.metadata)
        self.tARMs = Models.init_table_ARMs(self.metadata)
        self.tDallasStatus = Models.init_table_DallasStatus(self.metadata)
        self.tKSC_info = Models.init_table_KSC_info(self.metadata)
        self.tUsers = Models.init_table_Users(self.metadata)
        self.tAdapters = Models.init_table_Adapters(self.metadata)
        self.tLogons = Models.init_table_Logons(self.metadata)
        self.tPatches = Models.init_table_Patches(self.metadata)
        self.tARMs_and_Patches = Models.init_table_ARMs_and_Patches(self.metadata)
        self.tCryptoGateways = Models.init_table_Crypto_Gateways(self.metadata)
        self.tDevices = Models.init_table_Devices(self.metadata)
        self.tAddresses = Models.init_table_Addresses(self.metadata)
        self.tSystem = Models.init_table_System(self.metadata)
        self.tUpdate_logs = Models.init_table_Update_Logs(self.metadata)
        self.metadata.create_all(self.engine)
        self.ARMs = ARMsTable(self)
        self.DallasServers = DallasServersTable(self)
        self.DallasStatus = DallasStatusTable(self)
        self.Structures = StructuresTable(self)
        self.Users = UsersTable(self)
        self.Adapters = AdaptersTable(self)
        self.Logons = LogonsTable(self)
        self.Patches = PatchesTable(self)
        self.KSC_info = KSC_InfoTable(self)
        self.CryptoGateways = CryptoGatewaysTable(self)
        self.Devices = DevicesTable(self)
        self.Addresses = AddressesTable(self)
        self.System = SystemTable(self)
        self.Logs = LogTables(self)
        self.inUpdating = False

db = Database()
