from sqlalchemy import select, update


class CryptoGatewaysTable:
    def __init__(self, db):
        self.db = db
        self.table = db.tCryptoGateways
        self.address = self.table.c.address
        self.mask = self.table.c.mask
        self.name = self.table.c.name
        self.caption = self.table.c.caption
        self.id = self.table.c.id
        self.Structures_id = self.table.c.Structures_id

    def add(self, crypto_gateway):
        if self.get_one(crypto_gateway.get_name()) is None:
            add = self.table.insert().values(name = crypto_gateway.get_name(),
                                             address = crypto_gateway.get_address(),
                                             mask = crypto_gateway.get_mask(),
                                             caption = crypto_gateway.get_caption(),
                                             activeToBlock=crypto_gateway.isActiveToBlock(),
                                             Structures_id = crypto_gateway.get_structure_id())
            self.db.engine.execute(add)
        else:
            query = update(self.table).where(self.name == crypto_gateway.get_name()).values(name = crypto_gateway.get_name(),
                                                                                            address = crypto_gateway.get_address(),
                                                                                            mask = crypto_gateway.get_mask(),
                                                                                            caption = crypto_gateway.get_caption(),
                                                                                            activeToBlock = crypto_gateway.isActiveToBlock(),
                                                                                            Structures_id = crypto_gateway.get_structure_id())
            self.db.engine.execute(query)
        return self.get_one(crypto_gateway.get_name())["id"]

    def get_one(self, _name):
        if _name is not "":
            query = select([self.table]).where(self.name == _name)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_by_id(self, _id):
        if _id:
            query = select([self.table]).where(self.id == _id)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_by_structure_id(self, id):
        if id:
            structures = []
            query = select([self.table]).where(self.Structures_id == id)
            rows = self.db.engine.execute(query)
            for row in rows:
                structures.append(row)
            return structures
        return []

    def get_by_structure(self, name):
        if name:
            struct = self.db.Structures.get_one(name)
            if not struct:
                return []
            structures = []
            query = select(self.table).where(self.Structures_id == struct['id'])
            rows = self.db.engine.execure(query)
            for row in rows:
                structures.append(row)
            return structures
        return []

    def get_all(self):
        query = select([self.table])
        rows = self.db.engine.execute(query)
        gateways = []
        for row in rows:
            gateways.append({
                "name" : row['name'],
                "caption" : row['caption'],
                "address" : row['address'],
                "mask" : row['mask'],
                "activeToBlock" : row['activeToBlock'],
                "Structures_id" : row['Structures_id']
            })
        return gateways

    def isAccess_by_structure(self, CG_name, structure_id):
        structs_id = self.db.Structures.get_by_root_id(structure_id)
        if self.db.Structures.get_by_id(structure_id):
            structs_id.append(structure_id)
        query = select([self.table]).where(self.Structures_id.in_(structs_id))
        rows = self.db.engine.execute(query)
        for row in rows:
            if row['name'] == CG_name:
                return True
        return False
