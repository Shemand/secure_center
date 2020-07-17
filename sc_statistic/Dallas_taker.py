import re
from sc_databases.Computers import Computers
from sc_statistic.Config import config


class DallasServer:
    def __init__(self, path_to_file):
        self.computers = Computers()
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

    def taker(self):
        for path in self.paths:
            prev_name = ""
            server_name = ""
            for node in path:
                if prev_name == "":
                    server_name = node["name"][ node["name"].find('(')+1 : node["name"].rfind(')')]
                    prev_name = node["name"]
                    continue
                if node["type"] != 0:
                    computer = self.computers.get(node["name"])
                    if computer:
                        computer.update_dallas_status(self.computers.session, server_name, node["type"])
                prev_name = node["name"]
        self.computers.session.commit()
