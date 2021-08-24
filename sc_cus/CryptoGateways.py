from sc_cus import CryptoGateway
from sc_databases import db as database

class CryptoGateways:

    def __init__(self):
        gateways_data = database.CryptoGateways.get_all()
        self.gateways = {}
        for element in gateways_data:
            struct_name = database.Structures.get_by_id(element['Structures_id'])['name']
            self.gateways[element['name']] = CryptoGateway(name=element['name'],
                                                           address=element['address'],
                                                           mask=element['mask'],
                                                           caption=element['caption'],
                                                           activeToBlock=element['activeToBlock'],
                                                           structure_name=struct_name)

    def get_cryptoGateway_name(self, address):
        for gateway_name in self.gateways:
            if self.gateways[gateway_name].in_network(address):
                return gateway_name
        return None