import os

from sc_cus.CryptoGateway import CryptoGateway
from sc_cus.CryptoGateways import CryptoGateways
from sc_databases import db as database

def load_crypto_gateways():
    file_name = 'crypto_gateways.txt'
    if os.path.exists(file_name):
        hFile = open(file_name, 'r')
        for line in hFile:
            data = line.split('/')
            structure = database.Structures.get_one(data[2])
            if structure is None:
                continue
            structure_name = structure['name']
            address = data[0]
            mask = data[1]
            caption = data[3]
            name = data[4]
            activeToBlock = data[5]
            cGateway = CryptoGateway(name = name,
                                     address = address,
                                     mask = mask,
                                     caption = caption,
                                     structure_name = structure_name,
                                     activeToBlock = True if activeToBlock == '+' else False)
            database.CryptoGateways.add(cGateway)
        return True
    else:
        database.Logs.add_update_logs('file with name "' + file_name + '" doesn\'t exists. Data abount CG taked from databases')
        return False

cryptoGateways = CryptoGateways()
