from datetime import datetime

from sqlalchemy import update, select, insert


class SystemTable:
    Types = {
        "integer": 1,
        "string": 2,
        "datetime": 3
    }

    ParameterType = {
        "dallas_updated" : "datetime",
        "kaspersky_updated" : "datetime",
        "ad_updated" : "datetime",
        "full_updated" : "datetime",
        "started_updated" : "datetime",
        "save_statistic_count" : "integer"
    }

    ParameterDefaultValue = {
        "dallas_updated" : 0,
        "kaspersky_updated": 0,
        "ad_updated": 0,
        "full_updated": 0,
        "started_updated": 0,
        "save_statistic_count" : 0
    }

    def __init__(self, db):
        self.db = db

    def get(self, parameter_name):
        if self.ParameterType[parameter_name] == "datetime":
            toReturn = { "type" : "datetime", "value" : self.get_datetime(parameter_name) }
        elif self.ParameterType[parameter_name] == "string":
            toReturn = { "type" : "string", "value" : self.get_string(parameter_name) }
        elif self.ParameterType[parameter_name] == "integer":
            toReturn = { "type" : "integer", "value" : self.get_integer(parameter_name) }
        else:
            toReturn = { "type" : "error", "value" : None}

        if toReturn['value'] is None:
            return { "type" : "error", "value" : None}
        return toReturn

    def set(self, parameter_name, value):
        if parameter_name in self.ParameterType:
            if isinstance(value, datetime):
                self.set_datetime(parameter_name, value)
            elif isinstance(value, int):
                self.set_interger(parameter_name, value)
            elif isinstance(value, str):
                self.set_interger(parameter_name, value)
            else:
                print("Unknown type of parameter [" + parameter_name + "] in SystemTable.set")

    def dallas_updated(self):
        self.set('dallas_updated', datetime.now())

    def kaspersky_updated(self):
        self.set('kaspersky_updated', datetime.now())

    def ad_updated(self):
        self.set('ad_updated', datetime.now())

    def full_updated(self):
        self.set('full_updated', datetime.now())

    def started_updated(self):
        self.set('started_updated', datetime.now())

    def system_initialization(self):
        tSystem = self.db.tSystem
        for param in self.ParameterType:
            if not self.check_exists(param):
                try:
                    query = tSystem.insert().values(parameter=param, type=self.Types[self.ParameterType[param]],
                                                    value=self.ParameterDefaultValue[param])
                    self.db.engine.execute(query)
                except Exception:
                    print("[ERROR] system_initialization ended with error!")
                    return None

    def check_exists(self, parameter_name):
        tSystem = self.db.tSystem
        query = select([tSystem]).where(tSystem.c.parameter == parameter_name)
        data = self.db.engine.execute(query).fetchone()
        if data:
            return True
        return False

    def get_datetime(self, parameter_name):
        tSystem = self.db.tSystem
        query = select([tSystem]).where(tSystem.c.parameter == parameter_name).limit(1)
        try:
            data = self.db.engine.execute(query)
            data = data.fetchone()
            data = data['value']
            data = int(data) / 1000
            dt = datetime.fromtimestamp(data)
            return dt
        except Exception:
            print("[ERROR] SystemTable.get_datetime - can't get a value")
            return None

    def set_datetime(self, parameter_name, dt):
        tSystem = self.db.tSystem
        query = update(tSystem).where(tSystem.c.parameter == parameter_name).values(value=int(dt.timestamp() * 1000))
        self.db.engine.execute(query)
        return dt

    def get_integer(self, parameter_name):
        tSystem = self.db.tSystem
        query = select([tSystem]).where(tSystem.c.parameter == parameter_name).limit(1)
        try:
            data = self.db.engine.execute(query)
            data = data.fetchone()
            data = int(data['value'])
            return data
        except Exception:
            return None

    def set_interger(self, parameter_name, _value):
        tSystem = self.db.tSystem
        try:
            query = update(tSystem).where(tSystem.c.parameter == parameter_name).values(value=int(_value))
            self.db.engine.execute(query)
            return int(_value)
        except Exception:
            return None

    def get_string(self, parameter_name):
        tSystem = self.db.tSystem
        query = select([tSystem]).where(tSystem.c.parameter == parameter_name).limit(1)
        data = self.db.engine.execute(query).fetchone()['value']
        return data

    def set_string(self, parameter_name, str):
        tSystem = self.db.tSystem
        query = update(tSystem).where(tSystem.c.parameter == parameter_name).update(value=str)
        self.db.engine.execute(query)
        return str
