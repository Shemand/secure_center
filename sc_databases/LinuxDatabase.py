from sqlalchemy import MetaData, create_engine, select, func
from sqlalchemy import Integer, Column, Table, DateTime, Text
from sqlalchemy.engine.url import URL

def init_table_puppetlist(metadata):
    return Table('puppetlist', metadata,
                 Column('id', Integer),
                 Column('date', DateTime),
                 Column('name', Text)
                 )

class LinuxDB:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LinuxDB, cls).__new__(cls)
            cls.instance.init()
        return cls.instance

    def init(self):
        self.metadata = MetaData()
        db_url = {
            'database': "logs",
            'drivername': "mysql",
            'username': "show",
            'password': "show",
            'host': "10.3.128.124",
            'query': {'charset': 'utf8'}
        }
        self.engine = create_engine(URL(**db_url), encoding="utf8")
        self.table = init_table_puppetlist(self.metadata)

    def getComputerNames(self):
        query = select([self.table.c.name, func.max(self.table.c.date).label("date")]).where(self.table.c.date > '2019-06-01 00:00:00').group_by(self.table.c.name)
        rows = self.engine.execute(query)
        dic = {row["name"].split(".")[0].split('"')[1].upper() : row.date for row in rows}
        print(dic)
        return dic


LinuxComputers = LinuxDB()
