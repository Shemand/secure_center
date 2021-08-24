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
        self.flag_get_from_windows_db = configuration.get("flag_get_from_windows_db")
        self.flag_get_from_linux_db = configuration.get("flag_get_from_linux_db")
        self.dallas_paths = configuration.get("dallas_paths")
        self.database = configuration.get("database")
        self.kaspersky_servers_urls = configuration.get("kaspersky_servers_urls")
        self.active_directory_server_ip = configuration.get("active_directory_server_ip")
        self.active_directory_port = configuration.get("active_directory_port")
        self.kaspersky_login = configuration.get("kaspersky_login")
        self.kaspersky_password = configuration.get("kaspersky_password")
        self.active_directory_login = configuration.get("active_directory_login")
        self.active_directory_password = configuration.get("active_directory_password")
        self.source_crypto_gateways_file = configuration.get("source_crypto_gateways_file")
        self.active_directory_main_container_path = configuration.get('active_directory_main_container_path')
        self.active_directory_begin_node = configuration.get("active_directory_begin_node")
        self.active_directory_end_nodes = configuration.get("active_directory_end_nodes")
        self.kaspersky_win_agent_versions = configuration.get("kaspersky_win_agent_versions")
        self.kaspersky_linux_agent_versions = configuration.get("kaspersky_linux_agent_versions"),
        self.kaspersky_win_security_versions = configuration.get("kaspersky_win_security_versions")
        self.kaspersky_linux_security_versions = configuration.get("kaspersky_linux_security_versions")
        self.kaspersky_right_agent_versions = configuration.get("kaspersky_right_agent_versions")
        self.kaspersky_right_security_versions = configuration.get("kaspersky_right_security_versions")
        self.control_statistics_root_node = configuration.get("control_statistics_root_node")
        self.control_statistics_end_nodes = configuration.get("control_statistics_end_nodes")
        self.time_to_updates_statistics = configuration.get("time_to_updates_statistics")
        self.time_to_uploads_ip_list = configuration.get("time_to_uploads_ip_list")
        locs = configuration.get("locations")
        self.locations = {
            "all": locs,
            "dallas": {a.get("dallas"): {"name": a.get("name"), "ad": a.get("ad")} for a in locs},
            "ad": {a.get("ad"): {"name": a.get("name"), "dallas": a.get("dallas")} for a in locs}
        }


config = Configuration()
