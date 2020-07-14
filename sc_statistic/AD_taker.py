from datetime import datetime

from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, BASE, ALL_ATTRIBUTES, ObjectDef, AttrDef, Reader, \
    Entry, Attribute

from sc_databases.Database import DatabaseClass
from sc_databases.Models.Structures import Structures
from sc_databases.Computers import Computers
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
        self.ignore_list = ['Fakultet MTO', 'Computers', 'computers']
        self.db = DatabaseClass()
        self.__computers = Computers()
        self.__raw_struct = {}
        self.__raw_data = {}
        self.__structures = self.__init_structures()

    def __init_structures(self):
        return { record.name : record for record in self.db.session.query(Structures).all() }

    def update_statistic(self):
        self.__structures = self.__init_structures()
        self.__extract_data()
        self.build_structure(self.__raw_struct)
        for computername in self.__raw_data:
            if not self.__computers.get(computername):
                if not 'root_catalog' in self.__raw_data[computername]:
                    print('ffff')
                self.__computers.add(computername, Structures_name = self.__raw_data[computername]['root_catalog']
                                                 , registred_ad = self.__raw_data[computername]['date_in_domain']
                                                 , last_visible = self.__raw_data[computername]['last_visible'])
            else:
                computer = self.__computers.get(computername)
                if computer.registred_ad != self.__raw_data[computername]['date_in_domain']:
                    computer.registred_ad = self.__raw_data[computername]['date_in_domain']
                if computer.last_visible != self.__raw_data[computername]['last_visible']:
                    computer.update_last_visible(self.__raw_data[computername]['last_visible'])
                structure_id = self.db.session.query(Structures).filter_by(name=self.__raw_data[computername]['root_catalog']).one().id
                if computer.Structures_id != structure_id:
                    computer.Structures_id = structure_id
        self.db.session.commit()

    def build_structure(self, structures, root_name=None):
        for struct_name in structures:
            if isinstance(structures[struct_name], dict) and len(structures[struct_name]) >= 1:
                self.build_structure(structures[struct_name], struct_name)
            self.add_structure(struct_name, prev_node = root_name)

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
                "last_visible": cn['attributes']['lastLogonTimestamp'].replace(tzinfo=None) if 'lastLogonTimestamp' in cn['attributes'] and cn['attributes']['lastLogonTimestamp'].replace(tzinfo=None) <= datetime.now() else None
            })
            index += 1
        return records

    def get_computers_count(self):
        self.__extract_data()
        return len(self.__raw_data)

    def add_structure(self, current_node, prev_node=None):
        if current_node in self.__structures:
            if prev_node and prev_node in self.__structures:
                prev_id = self.__structures[prev_node].id
                if not prev_id:
                    prev_id = self.db.session.query(Structures).filter_by(prev_id).one().id
                if self.__structures[current_node].root_id != prev_id:
                    self.__structures[current_node].root_id = prev_id
            else:
                if prev_node:
                    self.__structures[prev_node] = Structures(name=prev_node)
                    self.db.session.add(self.__structures[prev_node])
                    self.__structures[current_node].root_id = self.db.session.query(Structures)\
                                                                             .filter_by(name=prev_node).one().id
        else:
            self.__structures[current_node] = Structures(name=current_node)
            if prev_node and prev_node in self.__structures:
                prev_id = self.__structures[prev_node].id
                if not prev_id:
                    prev_id = self.db.session.query(Structures).filter_by(name=prev_node).one().id
                self.__structures[current_node].root_id = prev_id
            elif prev_node and not prev_node in self.__structures:
                self.__structures[prev_node] = Structures(name=prev_node)
                self.db.session.add(self.__structures[prev_node])
                self.db.session.commit()
                prev_id = self.db.session.query(Structures).filter_by(name=prev_node).one().id
                self.__structures[current_node].root_id = prev_id
        if self.__structures[current_node]:
            self.db.session.add(self.__structures[current_node])
        self.db.session.commit()

    def __extract_data(self):
        records = self.get_computer_records()
        self.__raw_data = {}
        self.__struct = {}
        for record in records:
            computer_name = record['location'].pop(0)[1]
            length = len(record['location'])
            index = 0
            struct_pointer = self.__raw_struct
            write_flag = False
            end_flag = False
            if computer_name == 'SZO-FMTO1':
                print('fffff')
            while (index < length) and not end_flag:
                loc = record['location'].pop()[1]
                if loc == self.begin_node:
                    write_flag = True
                if loc in self.end_nodes:
                    if not loc in config.locations["ad"]:
                        index += 1
                        continue
                    self.__raw_data[computer_name] = {}
                    self.__raw_data[computer_name]['root_catalog'] = config.locations["ad"][loc]["name"]
                    self.__raw_data[computer_name]['date_in_domain'] = record['created']
                    self.__raw_data[computer_name]['last_visible'] = record['last_visible']
                    self.__raw_data[computer_name]['logon_count'] = record['logon_count']
                    self.__raw_data[computer_name]['ad_user_control'] = record['user_account_control']
                    end_flag = True
                if write_flag:
                    if loc in self.ignore_list:
                        index += 1
                        continue
                    if not loc in struct_pointer:
                        if loc in config.locations["ad"]:
                            struct_pointer[ config.locations["ad"][loc]["name"] ] = {}
                            struct_pointer = struct_pointer[ config.locations["ad"][loc]["name"] ]
                        else:
                            struct_pointer[loc] = {}
                            struct_pointer = struct_pointer[loc]
                    else:
                        struct_pointer = struct_pointer[loc]
                index += 1
