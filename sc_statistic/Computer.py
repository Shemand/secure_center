from datetime import date, datetime
from sc_statistic.Config import config

class Computer:

    KASPERKSY_VERSIONS = {
        'WIN_AGENT' : config.kaspersky_win_agent_versions,
        'LIN_AGENT': config.kaspersky_linux_agent_versions,
        'WIN_SECURITY': config.kaspersky_win_security_versions,
        'LIN_SECURITY': config.kaspersky_linux_security_versions
    }

    def __init__(self, _name="", _dallas_server=None, _root_catalog="",
                 _date_in_domain=None, _last_logon_puppet=None, _isActive=False,
                 _last_logon_windows=None, _type=0, _ad_user_control=None, _crypto_gateway_name=None,
                 _last_logon_ad=None, _last_logon_kaspersky=None, _last_logon_local=None,
                 _logon_count=None, _dallas_status=None, _local_os=None,
                 _kl_ksc_server=None, _kl_last_visible=None, _kl_ip=None, _kl_os=None, _kl_status=None, _kl_hasDuplicate=False,
                 _kl_agent_version=None, _kl_security_version=None, _kl_for_server_version=None,
                 _kl_ksc_version=None, _kl_info_updated=False, _kl_info_is_not_found=False):
        self.date_in_domain = _date_in_domain
        self.ad_user_control = _ad_user_control
        self.logon_count = _logon_count
        self.root_catalog = _root_catalog
        self.name = self.set_name(_name)
        self.type = _type
        self.dallas_server = _dallas_server
        self.dallas_status = _dallas_status
        self.local_os = _local_os
        self.crypto_gateway_name = _crypto_gateway_name
        self.isActive = _isActive

        self.last_logon_ad = _last_logon_ad
        self.last_logon_puppet = _last_logon_puppet
        self.last_logon_windows = _last_logon_windows
        self.last_logon_kaspersky = _last_logon_kaspersky
        self.last_logon_local = _last_logon_local

        self.kl_ksc_server = _kl_ksc_server
        self.kl_last_visible = _kl_last_visible
        self.kl_hasDuplicate = _kl_hasDuplicate
        self.kl_ip = _kl_ip
        self.kl_os = _kl_os
        self.kl_status = _kl_status
        self.kl_agent_version = _kl_agent_version
        self.kl_security_version = _kl_security_version
        self.kl_for_server_version = _kl_for_server_version
        self.kl_ksc_version = _kl_ksc_version
        self.kl_info_updated = _kl_info_updated
        self.kl_info_is_not_found = _kl_info_is_not_found

    def set_dallas_server(self, _server_name):
        self.dallas_server = _server_name

    def isAD(self):
        if self.date_in_domain:
            return True
        return False

    def isDallas(self):
        if self.dallas_server is None:
            return False
        return True

    def isPuppet(self):
        if self.last_logon_puppet is None:
            return False
        return True

    def isCataloged(self):
        if self.root_catalog is "":
            return False
        return True

    def isKaspersky(self):
        if self.kl_ksc_server:
            return True
        return False

    def isKaspersky_updated(self):
        if self.kl_info_updated:
            return True
        return False

    def isWindows(self):
        if self.last_logon_windows is None:
            return False
        return True

    def isCG(self):
        if self.crypto_gateway_name is None:
            return False
        return True

    def get_dallas_server(self):
        return self.dallas_server

    def get_os(self):
        os = 'unkw'
        if self.isKaspersky():
            if self.kl_agent_version in Computer.KASPERKSY_VERSIONS['WIN_AGENT']\
               or self.kl_security_version in Computer.KASPERKSY_VERSIONS['WIN_SECURITY']:
                os = 'wind'
            elif self.kl_agent_version in Computer.KASPERKSY_VERSIONS['LIN_AGENT']\
               or self.kl_security_version in Computer.KASPERKSY_VERSIONS['LIN_SECURITY']:
                os = 'linx'
            else:
                os = self.kl_os
            return os
        if self.last_logon_puppet or self.last_logon_windows\
                or self.last_logon_local or self.last_logon_kaspersky:
            logons = ({"puppet": self.last_logon_puppet,
                       "windows": self.last_logon_windows,
                       "local": self.last_logon_local,
                       "kaspersky": self.last_logon_kaspersky
                      })
            key_of_max = None
            for key in logons:
                if key_of_max is None:
                    if logons[key] is not None:
                        key_of_max = key
                        continue
                if logons[key] and logons[key_of_max] and logons[key] > logons[key_of_max]:
                    key_of_max = key
            if key_of_max == 'puppet':
                os = 'linx'
            elif key_of_max == 'windows':
                os = 'wind'
            elif key_of_max == 'local':
                os = self.local_os
            elif key_of_max == 'kaspersky':
                os = self.kl_os
        elif self.dallas_server is not None:
            os = 'wind'
        elif self.logon_count and self.logon_count == 65535:
            os = 'linx'
        else:
            if self.get_last_logon():
                if self.date_in_domain and self.logon_count and (self.logon_count > 2000 and self.date_in_domain.date() < date(2018, 1, 1) and self.ad_user_control < 5000 or
                   self.logon_count < 2000 and self.ad_user_control < 5000):
                    os = 'wind'
                elif self.ad_user_control > 60000:
                    os = 'linx'


        return os

    def set_name(self, name):
        self.name = name.upper()
        return self.name

    def get_name(self):
        return self.name

    # def get_last_logon(self):
    #     sources = []
    #     sources.append(self.last_logon_ad)
    #     sources.append(self.last_logon_windows)
    #     sources.append(self.last_logon_puppet)
    #     sources.append(self.last_logon_kaspersky)
    #     sources.append(self.last_logon_local)
    #     sources = list(filter(None, sources))
    #     if sources == []:
    #         return None
    #     return max(sources)

    def get_last_logon(self):
        if self.kl_last_visible is not None:
            return self.kl_last_visible
        return None


    def get_kl_info(self):
        dic = {
            "server" : self.kl_ksc_server if self.kl_ksc_server else None,
            "ip" : self.kl_ip if self.kl_ip else None,
            "os" : self.kl_os if self.kl_os else None,
            "hasDuplicate" : self.kl_hasDuplicate,
            "products" : {
                "agent" : self.kl_agent_version if self.kl_agent_version else None,
                "security" : self.kl_security_version if self.kl_security_version else self.kl_for_server_version
                                                                                    if self.kl_for_server_version else None,
                "ksc" : self.kl_ksc_version if self.kl_ksc_version else None
            }
        }
        return dic
