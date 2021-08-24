from datetime import datetime

from sqlalchemy import select, and_, desc, update


class KSC_InfoTable:
    def __init__(self, db):
        self.db = db

    def add(self, _computer_name, _data):
        computer = self.db.ARMs.get_one(_computer_name)
        def add_record(_data):
            query = self.db.tKSC_info.insert()\
                    .values(ARMs_id=computer['id'],
                            server=_data['server'],
                            hasDuplicate=_data['hasDuplicate'],
                            ip=_data['ip'],
                            os=_data['os'],
                            agent_version=_data['products']['agent'],
                            security_version=_data['products']['security'],
                            created=datetime.now())
            self.db.engine.execute(query)

        if computer:
            last_record = self.get_last(_computer_name)
            if not last_record\
               or last_record['os'] != _data['os']\
               or last_record['ip'] != _data['ip']\
               or last_record['server'] != _data['server']\
               or last_record['security_version'] != _data['products']['security']\
               or last_record['agent_version'] != _data['products']['agent']\
               or last_record['hasDuplicate'] != _data['hasDuplicate']:
                add_record(_data)
                return self.get_last_by_id(computer['id'])
            return last_record
        return None

    def get_last(self, _computer_name):
        if _computer_name is not "":
            KSC = self.db.tKSC_info
            ARM = self.db.tARMs
            query = select([KSC]).where(KSC.c.ARMs_id == select([ARM.c.id]).where(ARM.c.name == _computer_name))\
                                 .order_by(desc(KSC.c.created)).limit(1)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_last_by_id(self, _id):
        if _id:
            KSC = self.db.tKSC_info
            ARM = self.db.tARMs
            query = select([KSC]).where(KSC.c.ARMs_id == _id).order_by(desc(KSC.c.created)).limit(1)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None