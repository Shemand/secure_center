from datetime import datetime

from sqlalchemy import select, update

from sc_cus import cryptoGateways as CG, load_crypto_gateways
from sc_databases import db as database


def __attach_AD(_computer, _row):
    if _computer.isActive != _row['isActive']:
        if not _computer.isActive:
            _computer.isActive = False
        query = update(database.tARMs).where(database.tARMs.c.name == _computer.name).values(
            isActive=_computer.isActive)
        database.engine.execute(query)
    if _computer.isAD():
        if _row['dateADRegistred'] is None:
            query = update(database.tARMs).where(database.tARMs.c.name == _computer.name).values(
                dateADRegistred=_computer.date_in_domain)
            database.engine.execute(query)
        if _row['isDeleted'] is not None:
            query = update(database.tARMs).where(database.tARMs.c.name == _computer.name).values(
                isDeleted=None)
            database.engine.execute(query)


def __attach_os(_computer, _row):
    if _row is not None:
        if _computer.get_os() != 'unkw':
            if _computer.get_os() != _row['operationSystem']:
                if _computer.get_os():
                    query = update(database.tARMs).where(database.tARMs.c.name == _computer.name).values(
                        operationSystem=_computer.get_os())
                    database.engine.execute(query)


# def __attach_logon(_computer, _row):
#     if _row is not None:
#         if not _row['last_logon'] or _computer.get_last_logon() > _row['last_logon']:
#             query = update(database.tARMs).where(database.tARMs.c.name == _computer.name).values(
#                 last_logon=_computer.get_last_logon())
#             database.engine.execute(query)
def __attach_logon(_computer, _row):
    if _computer.isKaspersky and _computer.isKaspersky_updated():
        last_logon = _computer.get_last_logon()
        if last_logon != _row['last_logon']:
            query = update(database.tARMs).where(database.tARMs.c.name == _row['name']).values(last_logon=last_logon)
            database.engine.execute(query)

def __attach_structure(_computer, _row):
    if _row is not None:
        if _row['Structures_id'] is None:
            if _computer.root_catalog != "":
                structures_id = database.engine.execute(select([database.tStructures]).where(
                    database.tStructures.c.name == _computer.root_catalog)).fetchone()["id"]
                query = update(database.tARMs).where(database.tARMs.c.name == _computer.name).values(
                    Structures_id=structures_id)
                database.engine.execute(query)


def __attach_dallas(_computer, _row):
    if _computer.isDallas():
        if _row is not None:
            if _row['DallasServers_id'] is None:
                if _computer.dallas_server is not None:
                    _dallas_servers_id = database.engine.execute(select([database.tDallasServers]).where(
                        database.tDallasServers.c.name == _computer.dallas_server)).fetchone()["id"]
                    query = update(database.tARMs).where(database.tARMs.c.name == _computer.name).values(
                        DallasServers_id=_dallas_servers_id, dateDallasRegistred=datetime.now().date())
                    database.engine.execute(query)
                    database.ARMs.change_dallas_status(_row, _computer.dallas_status)
            else:
                last = database.DallasStatus.get_last(_computer.name)
                if _computer.dallas_status != last['type']:
                    database.ARMs.change_dallas_status(_row, _computer.dallas_status)

    else:
        if _row is not None:
            if _row['DallasServers_id'] is not None:
                database.ARMs.change_dallas_status(_row, None)

def __attach_kl(_computer, _row):
    if _computer.isKaspersky():
        database.ARMs.change_kl_info(_row, _computer.get_kl_info())
    else:
        last_record = database.KSC_info.get_last(_computer.get_name())
        if _computer.kl_info_is_not_found and last_record and (last_record['agent_version'] or last_record['security_version']):
            _computer.kl_ksc_server = last_record['server']
            _computer.kl_ip = last_record['ip']
            _computer.kl_os = last_record['os']
            database.ARMs.change_kl_info(_row, _computer.get_kl_info())


def __attach_cryptoGateway(_computer, _row):
    if _computer.isKaspersky() or _row['KSC_info_id']:
        ip = None
        if _computer.isKaspersky():
            ip = _computer.kl_ip
        else:
            KSC_info_record = database.KSC_info.get_last(_row['name'])
            ip = KSC_info_record['ip']
        if _row['Crypto_Gateways_id'] is None:
            if _computer.crypto_gateway_name:
                query = select([database.tCryptoGateways]).where(
                    database.tCryptoGateways.c.name == CG.get_cryptoGateway_name(ip))
                row = database.engine.execute(query).fetchone()
                if row:
                    query = update(database.tARMs).where(database.tARMs.c.id == _row['id']).values(
                        Crypto_Gateways_id=row['id'])
                    database.engine.execute(query)
                else:
                    print("__attache_cryptoGateway: crypto gateway with this name wasn't found")
        else:
            current_gateway = database.CryptoGateways.get_by_id(_row['Crypto_Gateways_id'])
            if 'name' in current_gateway:
                if _computer.crypto_gateway_name != current_gateway['name']:
                    query = update(database.tARMs).where(database.tARMs.c.id == _row['id']).values(
                        Crypto_Gateways_id=current_gateway['id'])
                    database.engine.execute(query)

def __attach_addresses(_computer, _row):
    if _computer.kl_ip:
        address_object = database.Addresses.get_one(_computer.kl_ip)
        if address_object:
            if not database.Addresses.isAttach(_computer.kl_ip):
                database.Addresses.attach_computer(_computer.kl_ip, _row['id'])

def update_database(_computer):
    row = database.ARMs.get_one(_computer.name)
    if row is None:
        database.ARMs.add(_computer)
    else:
        __attach_AD(_computer, row)
        __attach_dallas(_computer, row)
        __attach_kl(_computer, row)
        __attach_cryptoGateway(_computer, row)
        __attach_logon(_computer, row)
        __attach_addresses(_computer, row)
        __attach_structure(_computer, row)
        __attach_os(_computer, row)
