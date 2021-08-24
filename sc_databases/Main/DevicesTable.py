from sqlalchemy import select, update, delete


class DevicesTable:
    def __init__(self, db):
        self.db = db
        self.table = self.db.tDevices
        self.id = self.table.c.id
        self.name = self.table.c.name
        self.Addresses_id = self.table.c.Addresses_id
        self.Crypto_Gateways_id = self.table.c.Crypto_Gateways_id
        self.Structures_id = self.table.c.Structures_id
        self.type = self.table.c.type
        self.comment = self.table.c.comment

    # device types
    COMMUTATOR_TYPE = 1
    PRINTER_TYPE = 2
    CAMERA_TYPE = 3
    UPS_TYPE = 4
    ARM_TYPE = 5
    TYPES = [COMMUTATOR_TYPE, PRINTER_TYPE, CAMERA_TYPE, UPS_TYPE, ARM_TYPE]

    def add(self, name, address, type, comment):
        if self.get_one(name) is None:
            address_row = self.db.Addresses.get_one(address)
            if address_row:
                cg_row = self.db.CryptoGateways.get_by_id(address_row['Crypto_Gateways_id'])
                if cg_row:
                    params = {
                        "name" : name,
                        "Addresses_id" : address_row['id'],
                        "Crypto_Gateways_id" : address_row['Crypto_Gateways_id'],
                        "Structures_id" : cg_row['Structures_id'],
                        "type" : type,
                        "comment" : comment,
                    }
                    query = self.db.tDevices.insert().values(params)
                    self.db.engine.execute(query)
                    row = self.get_one(name)
                    if row:
                        self.db.Addresses.attach_device(address, row['id'])
                        return row
                    return None
            else:
                print("DevicesTable.add: ip wasn't found.")
                return None

    def remove(self, devicename):
        if devicename:
            row = self.get_one(devicename)
            if row:
                row = self.db.Addresses.get_by_id(row['Addresses_id'])
                self.db.Addresses.unfasten(row['ip'])
                query = delete(self.table).where(self.Addresses_id == row['id'])
                self.db.engine.execute(query)
                return True
        return False

    def update_comment(self, devicename, text):
        if devicename:
            row = self.get_one(devicename)
            if row:
                query = update(self.table).where(self.id == row['id']).values(comment=text)
                self.db.engine.execute(query)
                return self.get_one(devicename)
        return None

    def get_one(self, _name):
        query = select([self.table]).where(self.name == _name)
        row = self.db.engine.execute(query).fetchone()
        return row

    def get_by_root(self, _root_structures_name):
        if _root_structures_name and _root_structures_name != "":
            root = self.db.Structures.get_one(_root_structures_name)
            if root and root['id']:
                children = self.db.Structures.get_by_root_id(root['id'])
                nodes = []
                nodes.append(root['id'])
                for child in children:
                    nodes.append(child)
                devices = []
                for node in nodes:
                    query = select([self.db.tDevices]).where(self.db.tDevices.c.Structures_id == node)
                    devices_rows = self.db.engine.execute(query)
                    for row in devices_rows:
                        devices.append(row)
                return devices
        return []

    def get_ready_data(self, _name):
        query = select([self.name,
                        self.db.tCryptoGateways.c.name.label("CryptoGateway_name"),
                        self.db.tAddresses.c.ip.label('ip'),
                        self.db.tAddresses.c.isLocked.label('isLocked'),
                        self.db.tAddresses.c.activeToBlock.label('activeToBlock'),
                        self.db.tStructures.c.name.label('unit')]) \
                        .select_from(self.table.join(self.db.tStructures,
                                     self.Structures_id == self.db.tStructures.c.id,
                                     isouter=True)
                             .join(self.db.tCryptoGateways,
                                   self.Crypto_Gateways_id == self.db.tCryptoGateways.c.id,
                                   isouter=True)
                             .join(self.db.tAddresses,
                                   self.Addresses_id == self.db.tAddresses.c.id,
                                   isouter=True)) \
                        .where(self.name == _name)
        row = self.db.engine.execute(query).fetchone()
        if row:
            return {
                "name": row['name'],
                "CG_name": row['CryptoGateway_name'],
                "ip": row['kl_ip'],
                "isLocked": row['isLocked'],
                "activeToBlock" : row['activeToBlock'],
                "unit": row['unit'],
                "type": row['type'],
                "comment": row['comment'],
            }
        return None

    def get_ready_data_for_root(self, _root_structures_name):
        if _root_structures_name and _root_structures_name != "":
            root = self.db.Structures.get_one(_root_structures_name)
            if root and root['id']:
                children = self.db.Structures.get_by_root_id(root['id'])
                nodes = []
                nodes.append(root['id'])
                for child in children:
                    nodes.append(child)
                devices = []
                for node in nodes:
                    query = select([self.name, self.type, self.comment,
                                    self.db.tCryptoGateways.c.name.label("CryptoGateway_name"),
                                    self.db.tAddresses.c.ip.label('ip'),
                                    self.db.tAddresses.c.isLocked.label('isLocked'),
                                    self.db.tAddresses.c.activeToBlock.label('activeToBlock'),
                                    self.db.tStructures.c.name.label('unit')]) \
                                    .select_from(self.table.join(self.db.tStructures,
                                                 self.Structures_id == self.db.tStructures.c.id,
                                                 isouter=True)
                                         .join(self.db.tCryptoGateways,
                                               self.Crypto_Gateways_id == self.db.tCryptoGateways.c.id,
                                               isouter=True)
                                         .join(self.db.tAddresses,
                                               self.Addresses_id == self.db.tAddresses.c.id,
                                               isouter=True)) \
                                    .where(self.Structures_id == node)
                    devices_rows = self.db.engine.execute(query)
                    for row in devices_rows:
                        dic = {
                            "name": row['name'],
                            "CG_name": row['CryptoGateway_name'],
                            "ip": row['ip'],
                            "isLocked": row['isLocked'],
                            "activeToBlock": row['activeToBlock'],
                            "unit": row['unit'],
                            "type": row['type'],
                            "comment": row['comment'],
                        }
                        devices.append(dic)
                return devices
        return []

    def change_type(self, _device_name, _type):
        if _device_name and self.get_one(_device_name):
            if _type in self.TYPES:
                query = update(self.table).where(self.name == _device_name).values(type=_type)
                self.db.engine.execute(query)
                return True
            else:
                print("[ERROR] DevicesTable.change_type: can't update device, because type is wrong!")
        else:
            print("[ERROR] DevicesTable.change_type: Problem with device name. Perhaps, computer with this name wasn't found in database.")
        return False