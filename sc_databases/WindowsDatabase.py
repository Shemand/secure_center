from sqlalchemy import MetaData, create_engine, select, func, cast, String
from sqlalchemy import Integer, Column, Table, DateTime, Text
from sqlalchemy.engine.url import URL

def init_table_szodata(metadata):
    return Table('szodata', metadata,
                 Column('id', Integer, nullable=False),
                 Column('time', DateTime),
                 Column('login', Text),
                 Column('fullname', Text),
                 Column('ipaddr', Text),
                 Column('pcname', Text),
                 Column('logonserver', Text)
                 )

class WindowsDB:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WindowsDB, cls).__new__(cls)
            cls.instance.init()
        return cls.instance

    def init(self):
        self.metadata = MetaData()
        db_url = {
            'database': "nmonitor",
            'drivername': "mssql+pymssql",
            'username': "shemakov",
            'password': "qwerty",
            'host': "10.3.128.25",
            'query': {'charset': 'utf8'}
        }
        self.engine = create_engine(URL(**db_url), encoding="utf8")
        self.table = init_table_szodata(self.metadata)

    def getComputerNames(self):
        query = select([cast(self.table.c.pcname, String(128)).label("pcname"), func.max(self.table.c.time).label("date")]).where(self.table.c.time > '2019-06-01 00:00:00').group_by(cast(self.table.c.pcname, String(128)))
        rows = self.engine.execute(query)
        dic = {row["pcname"].split(".")[0].split('"')[0].upper() : row.date for row in rows}
        return dic


WindowsComputers = WindowsDB()
