from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, DateTime, Boolean, Text


def init_table_Structures(metadata):
    return Table('Structures', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String(64), index=True),
                 Column('root_id', Integer, default=0)
                 )


def init_table_DallasServers(metadata):
    return Table('DallasServers', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String(64), unique=True, index=True)
                 )


def init_table_ARMs(metadata):
    return Table('ARMs', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String(64), unique=True, nullable=False, index=True),
                 Column('dateAdded', Date, nullable=False),
                 Column('dateADRegistred', Date, nullable=True),
                 Column('dateDallasRegistred', Date, nullable=True),
                 Column('last_logon', Date, nullable=True),
                 Column('operationSystem', String(4), nullable=False, default='unkw'),
                 Column('type', Integer, nullable=False, default=1),
                 Column('isActive', Boolean, nullable=False, default=True),
                 Column('isDeleted', DateTime, nullable=True),
                 Column('comment', Text),
                 Column('KSC_info_id', Integer, ForeignKey('KSC_info.id'), nullable=True),
                 Column('DallasServers_id', Integer, ForeignKey('DallasServers.id'), nullable=True),
                 Column('DallasStatus_id', Integer, ForeignKey('DallasStatus.id'), nullable=True),
                 Column('Crypto_Gateways_id', Integer, ForeignKey('Crypto_Gateways.id'), nullable=True),
                 Column('Structures_id', Integer, ForeignKey('Structures.id'), nullable=True)
                 )

def init_table_DallasStatus(metadata):
    return Table('DallasStatus', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('type', Integer, nullable=False),
                 Column('created', DateTime, nullable=False),
                 Column('ARMs_id', Integer, ForeignKey('ARMs.id'), nullable=False)
                 )

def init_table_KSC_info(metadata):
    return Table('KSC_info', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('server', String(32), nullable=False),
                 Column('ip', String(15), nullable=True),
                 Column('os', String(4), nullable=True),
                 Column('agent_version', String(16), nullable=True),
                 Column('security_version', String(16), nullable=True),
                 Column('hasDuplicate', Boolean, nullable=False),
                 Column('created', DateTime, nullable=False, default=datetime.now()),
                 Column('ARMs_id', Integer, ForeignKey('ARMs.id'), nullable=False)
                 )

def init_table_Users(metadata):
    return Table('Users', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String(256), nullable=False),
                 Column('Structures_id_access', Integer, ForeignKey('Structures.id')),
                 Column('login', String(64), nullable=False),
                 Column('password', String(256), nullable=False),
                 Column('email', String(128)),
                 Column('isAdmin', Boolean, nullable=False, default=False),
                 Column('activated', Integer, nullable=False, default=0)
                 )

def init_table_Adapters(metadata):
    return Table('Adapters', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('caption', String(256), nullable=False),
                 Column('ARMs_id', Integer, ForeignKey('ARMs.id')),
                 Column('mac', String(17), nullable=False),
                 Column('ipv4', String(15), nullable=False),
                 Column('ipv6', String(64)),
                 Column('dhcp', String(15)),
                 Column('domain', String(64)),
                 Column('created', DateTime, nullable=False)
                 )

def init_table_Logons(metadata):
    return Table('Logons', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('domain_server', String(64)),
                 Column('username', String(128), nullable=False),
                 Column('os', String(4), nullable=False),
                 Column('ARMs_id', Integer, ForeignKey('ARMs.id')),
                 Column('logon_counter', Integer, default=0),
                 Column('updated', DateTime, nullable=False, default=datetime.now()),
                 Column('created', DateTime, nullable=False, default=datetime.now())
                 )

def init_table_Patches(metadata):
    return Table('Patches', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String(32), unique=True, nullable=False)
                 )

def init_table_ARMs_and_Patches(metadata):
    return Table('ARMs_and_Patches', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('ARMs_id', Integer, ForeignKey('ARMs.id'), nullable=False),
                 Column('Patches_id', Integer, ForeignKey('Patches.id'), nullable=False)
                 )

def init_table_Crypto_Gateways(metadata):
    return Table('Crypto_Gateways', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String(16), nullable=False, unique=True),
                 Column('address', String(15), nullable=False),
                 Column('mask', Integer, nullable=False),
                 Column('caption', Text, nullable=False),
                 Column('activeToBlock', Boolean, nullable=False, default=False),
                 Column('Structures_id', Integer, ForeignKey('Structures.id'))
                 )

def init_table_Addresses(metadata):
    return Table('Addresses', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('ip', String(15), nullable=False),
                 Column('isLocked', Boolean, nullable=False, default=True),
                 Column('attempts_count', Integer, nullable=False, default=1),
                 Column('expiration_time', DateTime),
                 Column('activeToBlock', Boolean, nullable=False, default=False),
                 Column('Crypto_Gateways_id', Integer, ForeignKey('Crypto_Gateways.id'), nullable=False),
                 Column('ARMs_id', Integer, ForeignKey('ARMs.id')),
                 Column('Devices_id', Integer, ForeignKey('Devices.id'))
                 )

def init_table_Devices(metadata):
    return Table('Devices', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('name', String(64), unique=True, nullable=False),
                 Column('Addresses_id', Integer, ForeignKey('Addresses.id'), unique=True, nullable=False),
                 Column('Crypto_Gateways_id', Integer, ForeignKey('Crypto_Gateways.id'), nullable=False),
                 Column('Structures_id', Integer, ForeignKey('Structures.zid'), nullable=False),
                 Column('type', Integer, nullable=False),
                 Column('comment', Text)
                 )

def init_table_System(metadata):
    return Table('System', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('parameter', String(32), nullable=False, unique=True),
                 Column('type', Integer, nullable=False),
                 Column('value', Text, nullable=True)
                 )

def init_table_Update_Logs(metadata):
    return Table('Update_logs', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('text', Text),
                 Column('created', DateTime)
                 )