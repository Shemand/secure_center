import json


class Configuration:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Configuration, cls).__new__(cls)
            cls.instance.reload()
        return cls.instance

    def reload(self):
        file = open("config.json", 'r')
        configuration = json.loads(file.read())
        self.root = configuration.get("root")
        locs = configuration.get("locations")
        self.locations = {
            "all": locs,
            "dallas": {a.get("dallas"): {"name": a.get("name"), "ad": a.get("ad")} for a in locs},
            "ad": {a.get("ad"): {"name": a.get("name"), "dallas": a.get("dallas")} for a in locs}
        }
        self.ignore_containers = configuration.get("ignore_containers")


config = Configuration()
