from sqlalchemy import select, update, and_, or_


class AddressesTable:
    def __init__(self, db):
        self.db = db
        self.table = db.tAddresses
        self.id = self.table.c.id
        self.ip = self.table.c.ip
        self.isLocked = self.table.c.isLocked
        self.attempts_count = self.table.c.attempts_count
        self.activeToBlock = self.table.c.activeToBlock
        self.expiration_time = self.table.c.expiration_time
        self.Crypto_Gateways_id = self.table.c.Crypto_Gateways_id
        self.ARMs_id = self.table.c.ARMs_id
        self.Devices_id = self.table.c.Devices_id
        self.ARMs = db.tARMs
        self.Devices = db.tDevices
        self.CryptoGateways = db.tCryptoGateways

    def add(self, ip, crypto_gateway, attempts_count=1, ARMs_id=None):
        if self.get_one(crypto_gateway.get_name()) is None:
            cg = self.db.CryptoGateways.get_one(crypto_gateway.get_name())
            if cg:
                add = self.table.insert().values(ip = ip,
                                                 isLocked = True,
                                                 attempts_count = attempts_count,
                                                 Crypto_Gateways_id = cg['id'],
                                                 ARMs_id = ARMs_id)
                self.db.engine.execute(add)
                return self.get_one(ip)["id"]
        else:
            return None

    def update(self, address, computername):
        if self.get_one(address):
            computer = self.db.ARMs.get_one(computername)
            if computer:
                query = update(self.table).where(self.ip == address).values(ARMs_id = computer['id'])
                self.db.engine.execute(query)
                return True
        return False

    def get_one(self, _ip):
        if _ip != "":
            query = select([self.table]).where(self.ip == _ip)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_by_id(self, _id):
        if _id:
            query = select([self.table]).where(self.id == _id)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def unlock(self, address, temporarily=False, expiration_time=None):
        row = self.get_one(address)
        if row:
            if temporarily:
                if row['attempts_count'] > 0:
                    if expiration_time:
                        query = update(self.table).where(self.ip == address).values(isLocked=False, attempts_count=row['attempts_count']-1)
                    else:
                        query = update(self.table).where(self.ip == address).values(isLocked=False, attempts_count=row['attempts_count']-1, expiration_time=expiration_time)
                    self.db.engine.execute(query)
                    return True
            else:
                query = update(self.table).where(self.ip == address).values(isLocked=False)
                self.db.engine.execute(query)
                return True
        else:
            print("AddressesTable.unlock: address doesn't exists")
            return False

    def lock(self, address, attempts_count=0):
        row = self.get_one(address)
        if row:
            if attempts_count:
                query = update(self.table).where(self.ip == address).values(isLocked=True, attempts_count=attempts_count)
                self.db.engine.execute(query)
            else:
                query = update(self.table).where(self.ip == address).values(isLocked=True)
                self.db.engine.execute(query)
        else:
            print("AddressesTable.lock: address doesn't exists")

    def get_all(self, locked=None, free=None):
        query = select([self.id, self.ip, self.isLocked, self.attempts_count, self.expiration_time, self.activeToBlock,
                        self.CryptoGateways.c.id.label('Crypto_Gateways_id'),
                        self.CryptoGateways.c.name.label('Crypto_Gateways_name'),
                        self.ARMs.c.id.label('ARMs_id'),
                        self.ARMs.c.name.label('ARMs_name'),
                        self.Devices.c.id.label('Devices_id'),
                        self.Devices.c.name.label('Devices_name')
                        ])\
                      .select_from(self.table.join(self.CryptoGateways,
                                                   self.Crypto_Gateways_id == self.CryptoGateways.c.id,
                                                   isouter=True)
                                             .join(self.ARMs,
                                                   self.ARMs_id == self.ARMs.c.id,
                                                   isouter=True)
                                             .join(self.Devices,
                                                   self.Devices_id == self.Devices.c.id,
                                                   isouter=True)
                                             )
        if locked is not None:
            if locked:
                if free is None: query = query.where(self.isLocked == True)
                elif free is True: query = query.where(and_(self.isLocked == True, and_(self.Devices_id == None, self.ARMs_id == None)))
                else:  query = query.where(and_(self.isLocked == True, or_(self.Device_id != None, self.ARMs_id != None)))
            else:
                if free is None: query = query.where(self.isLocked == False)
                elif free is True: query = query.where(and_(self.isLocked == False, and_(self.Devices_id == None, self.ARMs_id == None)))
                else: query = query.where(and_(self.isLocked == False, or_(self.Device_id != None, self.ARMs_id != None)))
        rows = self.db.engine.execute(query)
        gateways = []
        for row in rows:
            gateways.append({
                "id" : row['id'],
                "ip" : row['ip'],
                "isLocked" : row['isLocked'],
                "attempts_count" : row['attempts_count'],
                "expiration_time " : row['expiration_time'],
                "Crypto_Gateways_id" : row['Crypto_Gateways_id'],
                "Crypto_Gateways_name" : row['Crypto_Gateways_name'],
                "ARMs_id" : row['ARMs_id'],
                "ARMs_name": row['ARMs_name'],
                "Devices_id" : row['Devices_id'],
                "Devices_name" : row['Devices_name'],
                "activeToBlock": row['activeToBlock']
            })
        return gateways

    def update_activeToBlock_by_CG(self, CG_name, activate):
        CG_row = self.db.CryptoGateways.get_one(CG_name)
        if CG_row:
            query = update(self.table).where(self.Crypto_Gateways_id == CG_row['id']).values(activeToBlock=activate)
            self.db.engine.execute(query)
            return True
        print('AddressesTable.update_activateToBlock_by_CG: ' + "unknown CG name.")
        return False

    def get_by_CG(self, crypto_gateway, free=None):
        if crypto_gateway:
            cg = self.db.CryptoGateways.get_one(crypto_gateway)
            if cg:
                if free is None:
                    query = select(self.table).where(self.Crypto_Gateways_id == cg['name'])
                else:
                    if free is True:
                        query = select([self.table]).where(and_(self.Crypto_Gateways_id == cg['id'],
                                                              and_(
                                                              self.ARMs_id == None,
                                                              self.Devices_id == None
                                                                 )
                                                              )
                                                           )
                    else:
                        query = select([self.table]).where(and_(self.Crypto_Gateways_id == cg['id'],
                                                              or_(
                                                                  self.ARMs_id != None,
                                                                  self.Devices_id != None
                                                                 )
                                                              )
                                                        )
            rows = self.db.engine.execute(query)
            ip = []
            for row in rows:
                ip.append(row['ip'])
            return ip
        return None

    def attach_device(self, address, device_id):
        if address and device_id:
            row = self.get_one(address)
            if self.isAttach(address):
                print("AddressesTable.attach_device: Address already attached: " + str(address))
                return False
            query = update(self.table).where(self.ip == address).values(Devices_id=device_id, isLocked=0)
            self.db.engine.execute(query)
            return True
        print("AddressesTable.attach_device: address or device_id doesn't definition")
        return False

    def attach_computer(self, address, computer_id):
        if address and computer_id:
            row = self.get_one(address)
            if row:
                if self.isAttach(address):
                    print("AddressesTable.attach_computer: Address already attached "  + str(address))
                    return False
                query = update(self.table).where(self.ip == address).values(ARMs_id=computer_id)
                self.db.engine.execute(query)
                return True
            return False
        print("AddressesTable.attach_device: address or device_id doesn't definition")
        return False

    def isAttach(self, address):
        if address:
            row = self.get_one(address)
            if row:
                if row['ARMs_id'] or row['Devices_id']:
                    return True
        return False

    def unfasten(self, address):
        if self.isAttach(address):
            query = update(self.table).where(self.ip == address).values(Devices_id=None, ARMs_id=None)
            self.db.engine.execute(query)
            return True
        return False

