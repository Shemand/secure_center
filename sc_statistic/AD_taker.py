from datetime import datetime

from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, BASE, ALL_ATTRIBUTES, ObjectDef, AttrDef, Reader, \
    Entry, Attribute

from sc_statistic.Computer import Computer
from sc_statistic.Config import config


class ActiveDirectory:
    def __init__(self, catalog_path):
        self.conn = Connection(Server('10.3.128.4', port=389, use_ssl=False), auto_bind=AUTO_BIND_NO_TLS,
                               user="rosgvard\\shemakovnd", password='SHema98rg')
        self.catalog_path = catalog_path
        self.begin_node = "SZO"
        self.end_nodes = ['2659', '3526', '3644', '3693', '3705', '3727', '3798', '5134', '5402', '5565', '6716',
                          '6717', '6821', '6832', '6944', 'T210', 'T211', 'T229', 'T235', 'T239', 'T251', 'T253',
                          'T260', 'T278', 'T283', 'upr', 'upr-varshavskaya', 'upr2']
        self.locations = []

    def get_computer_records(self, sizeLimit=0):
        self.conn.search(search_base=self.catalog_path,
                         search_filter='(objectClass=computer)',
                         search_scope=SUBTREE,
                         attributes=["*"],
                          size_limit=sizeLimit)
        index = 0
        records = []
        array = self.conn.response
        for cn in array:
            sub_index = 0
            tmp = []
            for elem in cn['dn'].split(','):
                attr = elem.split('=')
                if len(attr) == 1:
                    tmp[sub_index - 1][1] = tmp[sub_index - 1][1] + "," + attr[0]
                    continue
                tmp.append(attr)
                sub_index += 1
            records.append({
                "location": tmp,
                "created": cn['attributes']['whenCreated'],
                "user_account_control": cn['attributes']['userAccountControl'],
                "logon_count" : cn['attributes']['logonCount'] if 'logonCount' in cn['attributes'] else None,
                #                "logon_count" : cn['attributes']['logonCount'],
                "last_logon": cn['attributes']['lastLogonTimestamp'].replace(tzinfo=None) if 'lastLogonTimestamp' in cn['attributes'] and cn['attributes']['lastLogonTimestamp'].replace(tzinfo=None) <= datetime.now() else None
            })
            index += 1
        return records

    def get_computers_count(self):
        records = self.get_computers()
        if records:
            return len(records)
        return None

    def get_computers(self):
        records = self.get_computer_records()
        computers = []
        for record in records:
            comp = Computer()
            write_flag = 0
            location = []
            comp.set_name(record['location'].pop(0)[1])
            count = len(record['location'])
            i = 0
            while i < count:
                node_name = record['location'].pop()[1]
                if node_name == self.begin_node:
                    write_flag = 1
                if node_name in self.end_nodes:
                    location.append(node_name)
                    comp.root_catalog = config.locations["ad"][node_name]["name"]
                    comp.date_in_domain = record['created']
                    comp.last_logon_ad = record['last_logon']
                    comp.logon_count = record['logon_count']
                    comp.ad_user_control = record['user_account_control']
                    write_flag = 0
                if write_flag:
                    location.append(node_name)
                i += 1
            if write_flag == 0:
                computers.append(comp)
                self.locations.append(location)
        return computers
