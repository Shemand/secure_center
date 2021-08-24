from datetime import datetime
from datetime import date

from sqlalchemy import select, distinct, and_
from sqlalchemy.sql.functions import count

from sc_statistic.Config import config

from sc_databases import db as database
class ControlStatistics(object):
    def __init__(self):
        self.table = database.tStatistics
        # self.all = database.tStatistics.c.all
        # self.kaspersky_right = database.tStatistics.c.kaspersky_right
        # self.kaspersky_wrong = database.tStatistics.c.kaspersky_wrong
        # self.kaspersky_percent_right = database.tStatistics.c.kaspersky_percent_right
        # self.disabled_computers = database.tStatistics.c.quantity_of_disabled_computers
        # self.on_windows = database.tStatistics.c.ARMs_on_windows
        # self.on_linux = database.tStatistics.c.ARMs_on_linux
        # self.on_unknown_os = database.tStatistics.c.ARMs_unknown_os
        # self.ARMs_on_puppet = database.tStatistics.c.ARMs_on_puppet
        # self.with_dallas = database.tStatistics.c.ARMs_with_dallas
        # self.with_dallas = database.tStatistics.c.ARMs_with_dallas
        # self.created = database.tStatistics.c.created
        # self.Structures_id = database.tStatistics.c.Structures_id
        self.root_node = config.control_statistics_root_node
        self.end_nodes = config.control_statistics_end_nodes
        self.right_agent_versions = config.kaspersky_right_agent_versions
        self.right_security_versions = config.kaspersky_right_security_versions


    def add(self, all=None, kaspersky_right=None, disabled_computers=None,
                  computers_on_windows=None, computers_on_linux=None, dallas_right=None,
                  puppet_ARMs=None, structure_name=None, number_of_update=None,
                  servers_on_windows=None, servers_on_linux=None):
        if not (all is not None
                and kaspersky_right is not None
                and disabled_computers is not None
                and computers_on_windows is not None
                and computers_on_linux is not None
                and dallas_right is not None
                and puppet_ARMs is not None
                and structure_name is not None
                and number_of_update is not None
                and servers_on_windows is not None
                and servers_on_linux is not None):
            print("ControlStatistics.add: not all argument not None")
            return
        if all == 0:
            return
        all = all - disabled_computers
        kaspersky_wrong = all - kaspersky_right
        kaspersky_percent_right = int( (kaspersky_right / all) * 100 )
        dallas_percent_right = int( (dallas_right / all) * 100 )
        unknown_os = all - computers_on_windows - computers_on_linux
        ARMs_on_windows = computers_on_windows - servers_on_windows
        puppet_ARMs = 0
        dallas_wrong=computers_on_windows - servers_on_windows - dallas_right
        structure_id = select([database.tStructures.c.id]).where(database.tStructures.c.name == structure_name)
        structure_id = database.engine.execute(structure_id).fetchone()
        if not (structure_id and 'id' in structure_id):
            print("ControlStatistics.add: structures with this name not found!")
            return
        structure_id = structure_id['id']
        query = self.table.insert().values(
            Structures_id=structure_id,
            all=all,
            quantity_of_disabled_computers=disabled_computers,
            quantity_ARMs=all-servers_on_windows-servers_on_linux,
            quantity_servers=servers_on_windows+servers_on_linux,
            kaspersky_right=kaspersky_right,
            kaspersky_wrong=kaspersky_wrong,
            kaspersky_percent_right=kaspersky_percent_right,
            computers_on_windows=computers_on_windows,
            ARMs_on_windows=ARMs_on_windows,
            servers_on_windows=servers_on_windows,
            ARMs_with_dallas=dallas_right,
            ARMs_without_dallas=dallas_wrong,
            dallas_percent_right=dallas_percent_right,
            computers_on_linux=computers_on_linux,
            ARMs_on_linux=computers_on_linux-servers_on_linux,
            servers_on_linux=servers_on_linux,
            computers_on_puppet=0,
            puppet_percent_right=0,
            ARMs_unknown_os=unknown_os,
            created=datetime.now(),
            number_of_update=number_of_update
        )
        database.engine.execute(query)

    def create_upload(self):
        def inner_upload(struct, counter):
            default_part_of_without_structure = select([count()]).select_from(database.tARMs) \
                                                                 .where(database.tARMs.c.dateADRegistred.isnot(None)) \
                                                                 .where(database.tARMs.c.isDeleted.is_(None))
            if struct['name'] != self.root_node:
                default_part_of_select = default_part_of_without_structure.where(struct['id'] == database.tARMs.c.Structures_id)
                all = default_part_of_select.where(struct['id'] == database.tARMs.c.Structures_id)
            else:
                default_part_of_select = default_part_of_without_structure
                all = default_part_of_select
            all = database.engine.execute(all).fetchone()[0]
            kaspersky_right = select([count()]).select_from(database.tARMs.join(database.tKSC_info, database.tARMs.c.KSC_info_id == database.tKSC_info.c.id, isouter=True)) \
                .where(database.tARMs.c.dateADRegistred.isnot(None)) \
                .where(database.tARMs.c.isActive == True)\
                .where(database.tARMs.c.isDeleted.is_(None)) \
                .where(database.tKSC_info.c.agent_version.in_(self.right_agent_versions)) \
                .where(database.tKSC_info.c.security_version.in_(self.right_security_versions))
            if self.root_node != struct['name']:
                kaspersky_right = kaspersky_right.where(struct['id'] == database.tARMs.c.Structures_id)
            kaspersky_right = database.engine.execute(kaspersky_right).fetchone()[0]
            computers_on_windows = default_part_of_select.where(database.tARMs.c.operationSystem == 'wind').where(database.tARMs.c.isActive == True)
            computers_on_windows = database.engine.execute(computers_on_windows).fetchone()[0]
            servers_on_windows = default_part_of_select.where(and_(database.tARMs.c.operationSystem == 'wind', database.tARMs.c.type == 2)).where(database.tARMs.c.isActive == True)
            servers_on_windows = database.engine.execute(servers_on_windows).fetchone()[0]
            servers_on_linux = default_part_of_select.where(and_(database.tARMs.c.operationSystem == 'linx', database.tARMs.c.type == 2)).where(database.tARMs.c.isActive == True)
            servers_on_linux = database.engine.execute(servers_on_linux).fetchone()[0]
            computers_on_linux = default_part_of_select.where(database.tARMs.c.operationSystem == 'linx').where(database.tARMs.c.isActive == True)
            computers_on_linux = database.engine.execute(computers_on_linux).fetchone()[0]
            disabled_computers = default_part_of_select.where(database.tARMs.c.isActive == False)
            disabled_computers = database.engine.execute(disabled_computers).fetchone()[0]
            dallas_right = default_part_of_select.where(database.tARMs.c.dateDallasRegistred.isnot(None)).where(database.tARMs.c.isActive == True)
            dallas_right = database.engine.execute(dallas_right).fetchone()[0]
            self.add(all=all,
                     kaspersky_right=kaspersky_right,
                     disabled_computers=disabled_computers,
                     computers_on_windows=computers_on_windows, computers_on_linux=computers_on_linux,
                     servers_on_windows=servers_on_windows,
                     servers_on_linux=servers_on_linux,
                     dallas_right=dallas_right,
                     puppet_ARMs=0,
                     structure_name=struct['name'] if struct['name'] != self.root_node else self.root_node,
                     number_of_update=counter)
        today = date.today()
        today = datetime(today.year, today.month, today.day, 0 , 0, 0)
        today_records = select([database.tStatistics]).where(database.tStatistics.c.created > today)
        today_records = database.engine.execute(today_records).fetchall()
        for tr in today_records:
            object_to_delete = database.tStatistics.delete().where(database.tStatistics.c.id == tr[ 'id' ])
            database.engine.execute(object_to_delete)
        structures = select([distinct(database.tStructures.c.name), database.tStructures.c.id])
        structures = database.engine.execute(structures)
        counter = database.System.get('save_statistic_count')['value']
        if counter:
            database.System.set('save_statistic_count', int(counter) + 1)
        else:
            counter = 0
            database.System.set('save_statistic_count', 1)
        counter += 1
        for struct in structures:
            inner_upload(struct, counter)

    def get(self, last_only=None, id=None):
        if last_only or id:
            counter = database.System.get('save_statistic_count')['value']
            counter = int(counter)
            if counter == 0:
                return None
            query = select([database.tStatistics])
            if id is None:
                query = query.where(database.tStatistics.c.number_of_update == counter)
            else:
                query = query.where(database.tStatistics.c.number_of_update == id)
            statistics = database.engine.execute(query)
            if statistics is None:
                return None
            data = []
            for statistic in statistics:
                data.append({
                    "structure_name": database.Structures.get_by_id(statistic['Structures_id'])['name'],
                    "all": statistic['all'],
                    "quantity_of_disabled_computers": statistic['quantity_of_disabled_computers'],
                    "quantity_ARMs" : statistic['quantity_ARMs'],
                    "quantity_servers" : statistic['quantity_servers'],
                    "kaspersky_right" : statistic['kaspersky_right'],
                    "kaspersky_wrong" : statistic['kaspersky_wrong'],
                    "kaspersky_percent_right" : statistic['kaspersky_percent_right'],
                    "computers_on_windows" : statistic['computers_on_windows'],
                    "ARMs_on_windows" : statistic['ARMs_on_windows'],
                    "servers_on_windows": statistic['servers_on_windows'],
                    "ARMs_with_dallas": statistic['ARMs_with_dallas'],
                    "ARMs_without_dallas": statistic['ARMs_without_dallas'],
                    "dallas_percent_right": statistic['dallas_percent_right'],
                    "computers_on_linux" : statistic['computers_on_linux'],
                    "ARMs_on_linux" : statistic['ARMs_on_linux'],
                    "servers_on_linux" : statistic['servers_on_linux'],
                    "computers_on_puppet": statistic['computers_on_puppet'],
                    "puppet_percent_right": statistic['puppet_percent_right'],
                    "ARMs_unknown_os" : statistic['ARMs_unknown_os'],
                    "created" : statistic['created'].timestamp() * 1000,
                    "number_of_update" : statistic['number_of_update'],
                })
            return data
        query = select([database.tStatistics]).order_by(database.tStatistics.c.number_of_update)
        statistics = database.engine.execute(query)
        data = {}
        for statistic in statistics:
            counter = statistic['number_of_update']
            struct_name = database.Structures.get_by_id(statistic['Structures_id'])['name']
            if not counter in data:
                data[counter] = {}
            if not struct_name in data[counter]:
                data[counter][struct_name] = {
                    "structure_name": database.Structures.get_by_id(statistic['Structures_id'])['name'],
                    "all": statistic['all'],
                    "quantity_of_disabled_computers": statistic['quantity_of_disabled_computers'],
                    "quantity_ARMs" : statistic['quantity_ARMs'],
                    "quantity_servers" : statistic['quantity_servers'],
                    "kaspersky_right" : statistic['kaspersky_right'],
                    "kaspersky_wrong" : statistic['kaspersky_wrong'],
                    "kaspersky_percent_right" : statistic['kaspersky_percent_right'],
                    "computers_on_windows" : statistic['computers_on_windows'],
                    "ARMs_on_windows" : statistic['ARMs_on_windows'],
                    "servers_on_windows": statistic['servers_on_windows'],
                    "ARMs_with_dallas": statistic['ARMs_with_dallas'],
                    "ARMs_without_dallas": statistic['ARMs_without_dallas'],
                    "dallas_percent_right": statistic['dallas_percent_right'],
                    "computers_on_linux" : statistic['computers_on_linux'],
                    "ARMs_on_linux" : statistic['ARMs_on_linux'],
                    "servers_on_linux" : statistic['servers_on_linux'],
                    "computers_on_puppet": statistic['computers_on_puppet'],
                    "puppet_percent_right": statistic['puppet_percent_right'],
                    "ARMs_unknown_os" : statistic['ARMs_unknown_os'],
                    "created" : statistic['created'].timestamp() * 1000,
                    "number_of_update" : statistic['number_of_update'],
                }
        return data