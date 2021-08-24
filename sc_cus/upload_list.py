
from sc_databases import db as database

def upload_list():
    addresses_object = database.Addresses.get_all(locked=True)
    records = []
    for address_object in addresses_object:
        if address_object['activeToBlock'] == True:
            cg = database.CryptoGateways.get_by_id(int(address_object['Crypto_Gateways_id']))
            if cg:
                records.append({
                    "cg_name" : cg['name'],
                    "cg_ip" : address_object['ip'],
                    "mask" : 32,
                    "next_node" : cg['address']
                })
    hFile = open('block.txt', 'w')
    for record in records:
        hFile.write(record['cg_name'] + "/" + record['cg_ip'] + "/" + str(record['mask']) + "/" + record['next_node'] + "\n")
    hFile.close()