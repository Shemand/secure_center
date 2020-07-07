import ipaddress
import os

from sc_cus import CryptoGateway
from sc_databases.Database import DatabaseClass
from sc_databases.Models.Addresses import Addresses
from sc_databases.Models.Crypto_Gateways import Crypto_Gateways
from sc_databases.Models.Structures import Structures
from sc_databases.Models.Update_Logs import Update_Logs


class Addr:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Addr, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.db = DatabaseClass()
        self.session = self.db.session
        self.__crypto_gateways = self.__load_crypto_gateways()
        self.__addresses = {row.ip : row for row in self.db.session.query(Addresses).all()}
        self.__active_addrs = {}
        self.__deactive_addrs = {}
        self.__update_addresses_by_crypto_gateways()
        self.upload_list()
        print('ff')

    def __load_crypto_gateways(self):
        self.__crypto_gateways = {row.name: row for row in self.session.query(Crypto_Gateways).all()}
        file_name = 'crypto_gateways.txt'
        if os.path.exists(file_name):
            hFile = open(file_name, 'r')
            for line in hFile:
                data = line.split('/')
                structure = self.session.query(Structures).filter_by(name=data[2]).first()
                if structure is None:
                    continue
                structure_name = structure.name
                address = data[0]
                mask = data[1]
                caption = data[3]
                name = data[4]
                active_to_block = True if data[5] == '+' else False
                if name in self.__crypto_gateways:
                    self.__crypto_gateways[name].name = name
                    self.__crypto_gateways[name].address = address
                    self.__crypto_gateways[name].mask = mask
                    self.__crypto_gateways[name].caption = caption
                    self.__crypto_gateways[name].active_to_block =  active_to_block
                    self.__crypto_gateways[name].structure = structure
                else:
                    self.session.add(Crypto_Gateways(name=name,
                                                         address=address,
                                                         mask=mask,
                                                         caption=caption,
                                                         active_to_block=active_to_block,
                                                         structure=structure))
                self.session.commit()
            return { row.name: row for row in self.session.query(Crypto_Gateways).all() }
        else:
            Update_Logs.insert().values(text='file with name "' + file_name + '" doesn\'t exists. Data abount CG taked from databases')
            raise Exception('file with name "' + file_name + '" doesn\'t exists. Data abount CG taked from databases')
            return None

    def __update_addresses_by_crypto_gateways(self):
        for cg_name in self.__crypto_gateways:
            network = ipaddress.ip_network(self.__crypto_gateways[cg_name].address + "/" + str(self.__crypto_gateways[cg_name].mask))
            for ip in network:
                row = self.session.query(Addresses).filter_by(ip=ip).first()
                if row:
                    if row.active_to_block != self.__crypto_gateways[cg_name].active_to_block:
                        row.active_to_block = self.__crypto_gateways[cg_name].active_to_block
                    if row.active_to_block is True:
                        self.__active_addrs[ip] = row
                    else:
                        self.__deactive_addrs[ip] = row
                    self.__addresses[ip] = row
                else:
                    address_obj = Addresses(ip=ip,
                                            active_to_block=self.__crypto_gateways[cg_name].active_to_block,
                                            crypto_gateway = self.__crypto_gateways[cg_name]
                                            )
                    self.session.add(address_obj)
                    if address_obj.active_to_block:
                        self.__active_addrs[address_obj.ip] = address_obj
                    else:
                        self.__deactive_addrs[address_obj.ip] = address_obj
                    self.__addresses[address_obj.ip] = address_obj
        self.session.commit()

    def upload_list(self):
        addresses_object = self.session.query(Addresses).filter(Addresses.active_to_block == True)\
                                                        .filter(Addresses.isBlocked == True)\
                                                        .filter(Addresses.Crypto_Gateways_id != None)\
                                                        .all()
        records = []
        for address_object in addresses_object:
            if address_object.active_to_block == True:
                cg = self.session.query(Crypto_Gateways).filter_by(id=int(address_object.Crypto_Gateways_id)).one()
                if cg:
                    records.append({
                        "cg_name": cg.name,
                        "cg_ip": address_object.ip,
                        "mask": 32,
                        "next_node": cg.address
                    })
        hFile = open('block.txt', 'w')
        for record in records:
            hFile.write(record['cg_name'] + "/" + record['cg_ip'] + "/" + str(record['mask']) + "/" + record[
                'next_node'] + "\n")
        hFile.close()

    def get(self, ip=None):
        if not ip:
            return self.__addresses
        else:
            if ip in self.__addresses:
                return self.__addresses[ip]
            else:
                addr = Addresses(ip=ip)
                self.session.add(addr)
                self.session.commit()
                self.__addresses[ip] = addr
                return self.__addresses[ip]
        return None