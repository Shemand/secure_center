import re
from sc_statistic.Computer import Computer
from sc_statistic.Config import config

from sc_databases import db


class DallasServer:
    def __init__(self, path_to_file):
        file = open(path_to_file, 'r')
        self.paths = []
        for line in file:
            path = []
            for elem in line.split('|'):
                end = elem.strip().split('<=>')
                end[0] = re.sub('\[\d{0,}\]', "", end[0]).strip()
                if len(end) == 2:
                    path.append({"name": end[0], "type": end[1]})
                else:
                    path.append({"name": end[0], "type": 0})
            self.paths.append(path)

    @staticmethod
    def add_arm(computers, name, type, parent_name, server_name):
        exists_flag = False
        for computer in computers:
            name = name.split(" ")[0]
            if computer.get_name() == name:
                computer.set_dallas_server(server_name)
                computer.root_catalog = config.locations["dallas"][parent_name]["name"]
                computer.dallas_status = type
                exists_flag = True
                break
        # if exists_flag is False and not parent_name in config.ignore_containers:
        #     computers.append(Computer(_name=name, _dallas_server=server_name,
        #                               _root_catalog=config.locations["dallas"][parent_name]["name"],
        #                               _dallas_status=type, _isActive=False))

    @staticmethod
    def add_server(name):
        db.DallasServers.add(name)
        # make some actions

    @staticmethod
    def add_node(name, parent_name):
        pass
        # make some actions

    def taker(self, computers):
        for path in self.paths:
            prev_name = ""
            server_name = ""
            for node in path:
                if node['name'] == 'Default':
                    break
                if prev_name == "":
                    server_name = node["name"][ node["name"].find('(')+1 : node["name"].rfind(')')]
                    DallasServer.add_server(server_name)
                    prev_name = node["name"]
                    continue
                if node["type"] != 0:
                    DallasServer.add_arm(computers, node["name"], node["type"], prev_name, server_name)
                else:
                    DallasServer.add_node(node["name"], prev_name)
                prev_name = node["name"]
