from datetime import datetime
from sqlalchemy import select, update, and_

class ARMsTable:
    def __init__(self, db):
        self.db = db

    # computer types
    ARM_TYPE = 1
    SERVER_TYPE = 2
    COMMUTATOR_TYPE = 3
    PRINTER_TYPE = 4
    CAMERA_TYPE = 5
    UPS_TYPE = 6
    TYPES = [ARM_TYPE, SERVER_TYPE, COMMUTATOR_TYPE, PRINTER_TYPE, CAMERA_TYPE, UPS_TYPE]

    def add(self, _computer):
        if self.get_one(_computer.name) is None:
            params = {
                "name": _computer.name,
                "dateAdded": datetime.now().date(),
                "dateADRegistred": _computer.date_in_domain if _computer.isAD() else None,
                "dateDallasRegistred": datetime.now().date() if _computer.isDallas() else None,
                "last_logon": _computer.get_last_logon(),
                "operationSystem": _computer.get_os() if _computer.get_os() else 'unkw',
                "KSC_info_id" : None,
                "Crypto_Gateways_id" : self.db.CryptoGateways.get_one(_computer.crypto_gateway_name)["id"] if _computer.isCG()
                                                                                                          else None,
                "DallasServers_id": self.db.DallasServers.get_one(_computer.dallas_server)["id"] if _computer.isDallas()
                                                                                                 else None,
                "Structures_id": self.db.Structures.get_one(_computer.root_catalog)["id"] if _computer.isCataloged()
                                                                                          else None
            }
            query = self.db.tARMs.insert().values(params)
            self.db.engine.execute(query)
        instance = self.get_one(_computer.name)
        if _computer.isKaspersky():
            self.change_kl_info(instance, _computer.get_kl_info())
        self.change_dallas_status(instance, _computer.dallas_status)
        self.db.Addresses.attach_computer(_computer.kl_ip, instance['id'])
        if instance is None:
            return None
        return instance["id"]

    def update_comment(self, computername, text):
        ARMs = self.db.tARMs
        if computername:
            row = self.get_one(computername)
            if row:
                query = update(ARMs).where(ARMs.c.id == row['id']).values(comment=text)
                self.db.engine.execute(query)
                return self.get_one(computername)
        return None

    def get_all_ad_names(self):
        query = select([self.db.tARMs.c.name]).where(self.db.tARMs.c.dateADRegistred.isnot(None))
        rows = self.db.engine.execute(query)
        computers = []
        for row in rows:
            computers.append(row['name'])
        return computers

    def get_one(self, _name):
        query = select([self.db.tARMs]).where(self.db.tARMs.c.name == _name)
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
                computers = []
                for node in nodes:
                    query = select([self.db.tARMs]).where(self.db.tARMs.c.Structures_id == node)
                    comps = self.db.engine.execute(query)
                    for comp in comps:
                        computers.append(comp)
                return computers
        return []

    def get_with_AD(self, _root_structure_name):
        if _root_structure_name:
            computers = self.get_by_root(_root_structure_name)
            comp_with_AD = []
            for comp in computers:
                if comp['dateADRegistred']:
                    comp_with_AD.append(comp)
            return comp_with_AD
        return []

    def get_ready_data(self, _name):
        ARM = self.db.tARMs
        query = select([ARM.c.name, ARM.c.dateAdded, ARM.c.dateADRegistred, ARM.c.type, ARM.c.comment,
                        ARM.c.dateDallasRegistred, ARM.c.last_logon, ARM.c.operationSystem.label('os'),
                        self.db.tCryptoGateways.c.name.label("CryptoGateway_name"),
                        self.db.tDallasServers.c.name.label('DallasServers_name'),
                        self.db.tDallasStatus.c.type.label('DallasStatus_type'),
                        self.db.tKSC_info.c.hasDuplicate.label('hasDuplicate'),
                        self.db.tKSC_info.c.agent_version.label('kl_agent_version'),
                        self.db.tKSC_info.c.security_version.label('kl_security_version'),
                        self.db.tKSC_info.c.ip.label('kl_ip'),
                        self.db.tAddresses.c.isLocked.label('isLocked'),
                        self.db.tAddresses.c.activeToBlock.label('activeToBlock'),
                        self.db.tStructures.c.name.label('unit')]) \
                        .select_from(ARM.join(self.db.tStructures,
                                      ARM.c.Structures_id == self.db.tStructures.c.id,
                                      isouter=True)
                             .join(self.db.tDallasServers,
                                   ARM.c.DallasServers_id == self.db.tDallasServers.c.id,
                                   isouter=True)
                             .join(self.db.tDallasStatus,
                                   ARM.c.DallasStatus_id == self.db.tDallasStatus.c.id,
                                   isouter=True)
                             .join(self.db.tKSC_info,
                                   ARM.c.KSC_info_id == self.db.tKSC_info.c.id,
                                   isouter=True)
                             .join(self.db.tCryptoGateways,
                                   ARM.c.Crypto_Gateways_id == self.db.tCryptoGateways.c.id,
                                   isouter=True)
                             .join(self.db.tAddresses,
                                   self.db.tKSC_info.c.ip == self.db.tAddresses.c.ip,
                                   isouter=True)) \
            .where(and_(ARM.c.name == _name))
        row = self.db.engine.execute(query).fetchone()
        if row:
            return {
                "name": row['name'],
                "CG_name": row['CryptoGateway_name'],
                "ad_added": row['dateADRegistred'],
                "dallas": row['DallasStatus_type'],
                "kl_agent": row['kl_agent_version'],
                "kl_security": row['kl_security_version'],
                "kl_ip": row['kl_ip'],
                "isLocked": row['isLocked'],
                "activeToBlock" : row['activeToBlock'],
                "hasDuplicate": row['hasDuplicate'],
                "last_logon": row['last_logon'],
                "os": row['os'],
                "dallas_server": row['DallasServers_name'],
                "unit": row['unit'],
                "type": row['type'],
                "comment": row['comment'],
            }
        return None

    def get_ready_data_for_root(self, _root_structures_name):
        ARM = self.db.tARMs
        if _root_structures_name and _root_structures_name != "":
            root = self.db.Structures.get_one(_root_structures_name)
            if root and root['id']:
                children = self.db.Structures.get_by_root_id(root['id'])
                nodes = []
                nodes.append(root['id'])
                for child in children:
                    nodes.append(child)
                computers = []
                for node in nodes:
                    query = select([ARM.c.name, ARM.c.dateAdded, ARM.c.dateADRegistred, ARM.c.type, ARM.c.comment, ARM.c.isActive,
                                    ARM.c.dateDallasRegistred, ARM.c.last_logon, ARM.c.operationSystem.label('os'),
                                    self.db.tCryptoGateways.c.name.label("CryptoGateway_name"),
                                    self.db.tDallasServers.c.name.label('DallasServers_name'),
                                    self.db.tDallasStatus.c.type.label('DallasStatus_type'),
                                    self.db.tKSC_info.c.hasDuplicate.label('hasDuplicate'),
                                    self.db.tKSC_info.c.agent_version.label('kl_agent_version'),
                                    self.db.tKSC_info.c.security_version.label('kl_security_version'),
                                    self.db.tKSC_info.c.ip.label('kl_ip'),
                                    self.db.tAddresses.c.isLocked.label('isLocked'),
                                    self.db.tAddresses.c.activeToBlock.label('activeToBlock'),
                                    self.db.tStructures.c.name.label('unit')])\
                                    .select_from(ARM.join(self.db.tStructures,
                                                          ARM.c.Structures_id == self.db.tStructures.c.id,
                                                          isouter=True)
                                                    .join(self.db.tDallasServers,
                                                          ARM.c.DallasServers_id == self.db.tDallasServers.c.id,
                                                          isouter=True)
                                                    .join(self.db.tDallasStatus,
                                                          ARM.c.DallasStatus_id == self.db.tDallasStatus.c.id,
                                                          isouter=True)
                                                    .join(self.db.tKSC_info,
                                                          ARM.c.KSC_info_id == self.db.tKSC_info.c.id,
                                                          isouter=True)
                                                    .join(self.db.tCryptoGateways,
                                                          ARM.c.Crypto_Gateways_id == self.db.tCryptoGateways.c.id,
                                                          isouter=True)
                                                    .join(self.db.tAddresses,
                                                          self.db.tKSC_info.c.ip == self.db.tAddresses.c.ip,
                                                          isouter=True)) \
                        .where(and_(ARM.c.Structures_id == node, ARM.c.isDeleted == None))
                    comps = self.db.engine.execute(query)
                    for comp in comps:
                        dic = {
                            "name" : comp['name'],
                            "CG_name" : comp['CryptoGateway_name'],
                            "ad_added" : comp['dateADRegistred'],
                            "dallas" : comp['DallasStatus_type'],
                            "kl_agent" : comp['kl_agent_version'],
                            "kl_security" : comp['kl_security_version'],
                            "kl_ip" : comp['kl_ip'],
                            "isLocked" : comp['isLocked'],
                            "isActive" : comp['isActive'],
                            "activeToBlock": comp['activeToBlock'],
                            "hasDuplicate" : comp['hasDuplicate'],
                            "last_logon" : comp['last_logon'],
                            "os" : comp['os'],
                            "dallas_server" : comp['DallasServers_name'],
                            "unit" : comp['unit'],
                            "type" : comp['type'],
                            "comment" : comp['comment'],
                        }
                        computers.append(dic)
                return computers
        return []

    def change_dallas_status(self, _computer_row, type):
        if _computer_row:
            last_row = self.db.DallasStatus.get_last(_computer_row['name'])
            if not last_row or int(last_row['type']) != int(type):
                if type is not None:
                    dallas_status_id = self.db.DallasStatus.add(_computer_row['id'], type)
                else:
                    dallas_status_id = None
                query = update(self.db.tARMs).where(self.db.tARMs.c.id == _computer_row['id']).values(
                    DallasStatus_id=dallas_status_id)
                self.db.engine.execute(query)
        else:
            print("Computer without dallas server")

    def change_kl_info(self, _computer_row, _data_kl):
        if _computer_row:
            info_id = self.db.KSC_info.add(_computer_row['name'], _data_kl)['id'] if _data_kl else None,
            if info_id:
                query = update(self.db.tARMs).where(self.db.tARMs.c.id == _computer_row['id']).values(KSC_info_id=info_id)
                self.db.engine.execute(query)
        else:
            print("Computer without kl info id")

    def change_type(self, _computer_name, _type):
        if _computer_name and self.get_one(_computer_name):
            if _type in self.TYPES:
                query = update(self.db.tARMs).where(self.db.tARMs.c.name == _computer_name).values(type=_type)
                self.db.engine.execute(query)
                return True
            else:
                print("[ERROR] ARMsTable.change_type: can't update computer, because type is wrong!")
        else:
            print("[ERROR] ARMsTable.change_type: Problem with computer name. Perhaps, computer with this name wasn't found in database.")
        return False

    # Initialization functions
    def disactivate_computers(self, _computers):
        names_db = self.get_all_ad_names()
        names_current = []
        to_delete = []
        ARMs = self.db.tARMs
        for computer in _computers:
            names_current.append(computer.name.upper())
        for name in names_db:
            if name not in names_current:
                to_delete.append(name)
        query = update(ARMs).where(self.db.tARMs.c.name.in_(to_delete)).values(isDeleted=datetime.now())
        self.db.engine.execute(query)


