import ipaddress

from sc_databases import db as database

class CryptoGateway:
    def __init__(self, name=None, address=None, mask=None, caption=None, structure_name=None, activeToBlock=False):
        try:
            if name is None or address is None or mask is None or caption is None or structure_name is None:
                raise Exception("Constructor of class 'CryptoGateway' took incorrect parameters.")
            self.name = name
            self.address = address
            self.mask = mask
            self.caption = caption
            self.activeToBlock = activeToBlock
            self.network = ipaddress.ip_network(self.address + "/" + str(self.mask))
            struct = database.Structures.get_one(structure_name)
            if struct is not None:
                self.structure_name = struct['name']
                self.structure_id = struct['id']
            else:
                raise Exception("Constructor of class 'CryptoGateway' took incorrect parameters. (Structure name dosn't found in database)")
        except Exception:
            print("Constructor of class 'CryptoGateway' took incorrect parameters.")

    def set_mask(self, value):
        if int(value) < 0 and int(value) > 32:
            print("CryptoGateway[" + self.name + "].set_mask value must be more than 0, and less than 33")
            return False
        else:
            self.mask = value
            return True

    def set_address(self, address):
        self.address = address

    def set_caption(self, text):
        self.caption = text

    def set_structure_by_id(self, id):
        self.structure_id = id

    def set_structure(self, struct_name):
        struct = database.Structures.get_one(struct_name)
        if struct:
            self.structure_id = struct['id']
            return True
        else:
            print("CryptoGateway[" + self.name + "].set_structure. Can't set structure, because structure with this name doesn't exists.")
            return False

    def get_name(self):
        return self.name

    def get_address(self):
        return self.address

    def get_mask(self):
        return self.mask

    def get_caption(self):
        return self.caption

    def get_structure_id(self):
        return self.structure_id

    def get_structure_name(self):
        return self.structure_name

    def get_addresses(self):
        addresses = []
        for address in self.network.hosts():
            addresses.append(str(address))
        return addresses

    def in_network(self, address):
        if address and ipaddress.ip_address(address) in self.network:
            return True
        return False

    def isActiveToBlock(self):
        if self.activeToBlock:
            return True
        return False
