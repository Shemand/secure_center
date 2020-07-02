import base64
import ipaddress
import json
import threading
from datetime import datetime

import requests
import urllib3
from requests import ReadTimeout, ConnectTimeout
from requests.adapters import HTTPAdapter
from queue import Queue

from urllib3.exceptions import MaxRetryError, NewConnectionError


class KSC_server:
    def __init__(self):

        lock = threading.Lock()
        self.local = threading.local()
        self.queue = Queue()
        self.lock = threading.Lock()
        self.local.accessor = None
        self.session = requests.Session()
        self.computer_records = {}
        adapter = HTTPAdapter(pool_maxsize=100, pool_connections=100)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.ignore_list = ['ROSGVARD', 'Нераспределенные устройства', 'VV']

        login = base64.b64encode("ksc-szo-001".encode("UTF-8")).decode("UTF-8")
        password = base64.b64encode("#00ktnCG<!!!".encode("UTF-8")).decode("UTF-8")

        self.auth_headers = {"Authorization": 'KSCBasic user="' + login + '", pass="' + password + '"',
                             "Content-Type": "application/json",
                             "Content-Length" : "2"}
        self.common_headers = {"Content-Type": "application/json"}

        self.local.current_server = "2659"
        self.__base_url = {
            "2659": "https://10.3.130.4:13299",
            # "3526": "https://10.3.132.7:13299",
            # "3644": "https://10.3.138.132:13299",
            # "3693": "https://10.3.139.182:13299",
            # "3705": "https://10.3.138.20:13299",
            # "3798": "https://10.3.138.87:13299",
            # "5134": "https://10.3.137.7:13299",
            # "6716": "https://10.3.134.250:13299",
            # "6717": "https://11.196.3.130:13299",
            # "6821": "https://10.3.133.132:13299",
            # "6832": "https://10.3.136.6:13299",
            # "6944": "https://10.3.131.73:13299",
            # "T210": "https://10.222.110.187:13299",
            # "T211": "https://10.222.111.240:13299",
            # "T229": "https://10.222.129.98:13299",
            # "T235": "https://10.222.135.106:13299",
            # "T239": "https://10.222.139.247:13299",
            # "T251" : "https://10.222.151.201:13299",
            # "T253" : "https://10.222.153.8:13299",
            # "T278" : "https://10.222.198.4:13299",
            # "UVO": "https://10.222.235.200:13299",
            # "T283": "https://10.222.183.3:13299",
            # "T260": "https://10.222.60.8:13299",
            # "6931" : "https://10.3.141.4:13299",
            # "SZO": "https://10.3.128.23:13299"
        }
        self.urls = {
            "create_connection" : "/api/v1.0/login",
            "get_groups" : "/api/v1.0/HostGroup.FindGroups",
            "get_hosts" : "/api/v1.0/HostGroup.FindHosts",
            "get_search_results": "/api/v1.0/ChunkAccessor.GetItemsChunk",
            "get_count" : "/api/v1.0/ChunkAccessor.GetItemsCount",
            "get_AdGroups" : "/api/v1.0/VServers.GetVServers",
            "get_host_products" : "/api/v1.0/HostGroup.GetHostProducts",
            "get_host_info": "/api/v1.0/HostGroup.GetHostInfo",
            "get_static_info" : "/api/v1.0/HostGroup.GetStaticInfo",
            "get_child_servers" : "/api/v1.0/ServerHierarchy.GetChildServers",
            "get_find_slave_servers": "/api/v1.0/ServerHierarchy.FindSlaveServers"
        }

    def __convert_name(self, name):
        name = name.upper()
        edited = True
        while edited:
            edited = False
            if name.rfind('~~') != -1:
                name = name[0:name.find('~~')]
                edited = True
            if name.rfind('.ROSGVARD.RU') != -1:
                name = name[0:name.rfind('.ROSGVARD.RU')]
                edited = True
            if name.rfind('.') != -1:
                name = name[0:name.rfind('.')]
                edited = True
            if name.rfind('(') != -1:
                name = name[0:name.rfind('(')]
                edited = True
            if name.rfind('[') != -1:
                name = name[0:name.rfind('[')]
                edited = True
            if name.rfind(' ') != -1:
                name = name[0:name.rfind(' ')]
                edited = True
        return name

    def get_url(self, url):
        return self.__base_url[self.local.current_server] + self.urls[url]

    def create_connection(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            response = self.session.post(url=self.get_url('create_connection'), headers=self.auth_headers, data="{}", verify=False, timeout=30)
            if response.status_code == 401:
                print("[ERROR] (" + self.local.current_server + ") Authentication required. Check the policies or privileges of account!")
                return None
        except ReadTimeout:
            print("thread of connection to " + self.get_url('create_connection') + " (" + self.local.current_server + ") ended with timeout")
            return None
        except ConnectTimeout:
            print("thread of connection to " + self.get_url('create_connection') + " (" + self.local.current_server + ") ended with max retries exceeded (perhaps no privileges)")
            return None
        except requests.exceptions.ConnectionError:
            print("thread of connection to " + self.get_url('create_connection') + " (" + self.local.current_server + ") ended with max retries exceeded (perhaps no privileges)")
            return None
        except MaxRetryError:
            print("thread of connection to " + self.get_url('create_connection') + " (" + self.local.current_server + ") ended with max retries exceeded (perhaps no privileges)")
            return None
        except NewConnectionError as Err:
            if Err.errno == 113:
                print("thread of connection to " + self.get_url('create_connection') + " (" + self.local.current_server + ") ended with error 'No route to host'")
            else:
                print("While connection to " + self.get_url('create_connection') + " with error 'NewConnectionError' (errno not a 113)")
            return None
        print("connection created: " + self.local.current_server + " - status is - " + str(response.status_code))
        return response.status_code

    def get_accessor(self, type, group_id=None):
        if type == "groups":
            data = {
                "wstrFilter" : "",
                "vecFieldsToReturn": ["id", "name", "KLSRVH_SRV_DN"],
                "lMaxLifeTime" : 100
            }
            url = self.get_url('get_groups')
        elif type == "hosts":
            if group_id is not None:
                data = {
                    "wstrFilter" : "(&(KLHST_WKS_GROUPID =" + str(group_id) + ")(KLHST_WKS_FROM_UNASSIGNED = False))",
                    "vecFieldsToReturn": ["KLHST_WKS_FQDN", "KLHST_WKS_HOSTNAME", "KLHST_LOCATION"],
                    "lMaxLifeTime" : 100
                }
                url = self.get_url('get_hosts')
            else:
                print("GROUP ID in get Accessor is None")
                return None
        response = self.session.post(url=url, headers=self.common_headers, data=json.dumps(data), verify=False)
        self.local.accessor = json.loads(response.text)["strAccessor"]
        return self.local.accessor

    def __get_count(self, accessor):
        data = { "strAccessor" : accessor }
        response = self.session.post(url=self.get_url('get_count'), data=json.dumps(data))
        return json.loads(response.text)['PxgRetVal']

    def get_search_results(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        items_count = self.__get_count(self.local.accessor)
        start = 0
        step = 100000
        result = list()
        while start < items_count:
            data = {"strAccessor" : self.local.accessor, "nStart" : start, "nCount" : items_count }
            response = self.session.post(url=self.get_url('get_search_results'), headers=self.common_headers, data=json.dumps(data), verify=False)
            result += json.loads(response.text)["pChunk"]["KLCSP_ITERATOR_ARRAY"]
            start += step
        return result

    def get_groups(self, server_name):
        self.local.current_server = server_name
        self.local.accessor = self.get_accessor(type="groups")
        return self.get_search_results()

    def get_hosts(self, server_name, group_id):
        self.local.current_server = server_name
        self.local.accessor = self.get_accessor(type="hosts", group_id=group_id)
        return self.get_search_results()

    def get_computers_id(self, server_name):
        computers = []
        self.local.current_server = server_name
        groups = self.get_groups(server_name)
        with self.lock:
            print(server_name + ": have " + str(len(groups)) + " groups")
        for group in groups:
            if not (group['value']['name'] in self.ignore_list):
                for host in self.get_hosts(server_name, group['value']['id']):
                    if not host:
                        break
                    else:
                        computers.append(host['value']['KLHST_WKS_HOSTNAME'])
        return computers

    def __get_computers_by_threads(self):
        srv_name = self.queue.get()
        with self.lock:
            print(srv_name + ": begin take data")
        servers_arm = self.get_computers_id(srv_name)
        records = self.data_taker(srv_name, servers_arm)
        with self.lock:
            if records:
                for computer_name in records:
                    old_name = computer_name
                    if computer_name == "T260-S5-1111":
                        print("we have this computer")
                    computer_name = self.__convert_name(computer_name)
                    if computer_name not in self.computer_records:
                        self.computer_records[computer_name] = records[old_name]
                    else:
                        cr_visible = self.computer_records[computer_name]['last_visible']
                        rec_visible = records[old_name]['last_visible']
                        self.computer_records[computer_name]['hasDuplicate'] = True
                        records[old_name]['hasDuplicate'] = True
                        if cr_visible and rec_visible and cr_visible < rec_visible:
                            self.computer_records[computer_name] = records[old_name]
                        elif not cr_visible and rec_visible:
                            self.computer_records[computer_name] = records[old_name]
                        elif not cr_visible and not rec_visible:
                            if len(self.computer_records[computer_name]['products']) < len(records[old_name]['products']):
                                self.computer_records[computer_name] = records[old_name]
        self.queue.task_done()
        with self.lock:
            print(srv_name + ": data was took")

    def update_computer_records(self):
        self.computer_records = {}
        for server_name in self.__base_url:
            self.local.current_server = server_name
            response = self.create_connection()
            if response:
                self.queue.put(server_name)
        for server_name in self.__base_url:
            trd = threading.Thread(target=self.__get_computers_by_threads)
            trd.setDaemon(True)
            trd.start()
        self.queue.join()

    def get_computers_by_server(self, srv_name):
        print("KSC server name: " + srv_name)
        servers_arm = self.get_computers_id(srv_name)
        return self.data_taker(srv_name, servers_arm)

    def get_host_products(self, host_name):
        data = {
            "strHostName" : str(host_name)
        }
        response = self.session.post(url=self.get_url('get_host_products'), headers=self.common_headers, data=json.dumps(data), verify=False)
        return response.text

    def get_host_info(self, host_name):
        data = {
            "strHostName": str(host_name),
            "pFields2Return":
                [
                    "KLHST_WKS_DN",
                    "KLHST_WKS_LAST_UPDATE",
                    "KLHST_WKS_WINHOSTNAME",
                    "KLHST_WKS_WINDOMAIN",
                    "KLHST_WKS_VIRUS_COUNT",
                    "KLHST_WKS_IP_LONG",
                    "KLHST_WKS_OS_NAME",
                    "KLHST_WKS_STATUS_ID",
                    "KLHST_WKS_FROM_UNASSIGNED",
                    "KLHST_WKS_LAST_SYSTEM_START",
                    "KLHST_WKS_RTP_STATE",
                    "KLSHT_WKS_KEEP_CONNECTION",
                    "KLSHT_MANAGED_OTHER_SERVER",
                    "KLHST_WKS_LAST_VISIBLE",
                    "KLHST_WKS_DNSNAME",
                    "KLHST_WKS_LAST_SYSTEM_START"
                ]
        }
        response = self.session.post(url=self.get_url('get_host_info'), headers=self.common_headers, data=json.dumps(data), verify=False)
        return response.text

    def get_static_info(self, host_name):
        data = {
            "strHostName": str(host_name),
            "pValues" : []
        }
        response = self.session.post(url=self.get_url('get_static_info'), data=json.dumps(data), verify=False)
        return response.text

    def data_taker(self, server_name, computer_records):
        computers = []
        self.local.current_server = server_name
        for computer_record in computer_records:
            info = json.loads(KSC.get_host_info(computer_record))
            products = json.loads(KSC.get_host_products(computer_record))
            computers.append({
                "products": products['PxgRetVal'] if 'PxgRetVal' in products else {},
                "info": info['PxgRetVal'] if 'PxgRetVal' in info else None,
                #            "static_info" : json.loads(KSC.get_static_info(computer_record["computer_id"]))['PxgRetVal']
            })
        def computer_products(value):
            products = []
            if value:
                for raw_product in value:
                    version = list(value[raw_product]['value'].keys())[0]
                    if version:
                        product = value[raw_product]['value'][version]['value']
                        products.append({ "caption": product['DisplayName'] if 'DisplayName' in product
                                                                            else product['ConnDisplayName'] if 'ConnDisplayName' in product else None ,
                                          "name": product['FileName'] if 'FileName' in product else None,
                                          "version": product['ProdVersion'] if 'ProdVersion' in product
                                                                            else product['ConnProdVersion'] if 'ConnProdVersion' in product else None,
                                          "installed": datetime.strptime(product['InstallTime']['value'], "%Y-%m-%dT%H:%M:%SZ") if 'InstallTime' in product and 'value' in product['InstallTime'] else None,
                                          })
            return products
        if computers:
            computers = {computer['info']['KLHST_WKS_DN'].upper() : {
                "server": server_name,
                "hasDuplicate" : False,
                "ip": str(ipaddress.ip_address(computer['info']['KLHST_WKS_IP_LONG']['value'])) if "KLHST_WKS_IP_LONG" in computer['info'] else None,
                "os": computer['info']['KLHST_WKS_OS_NAME'] if 'KLHST_WKS_OS_NAME' in computer['info'] else None,
                "virus": computer['info']['KLHST_WKS_VIRUS_COUNT']['value'] if "KLHST_WKS_VIRUS_COUNT" in computer['info'] else None,
                "domain": computer['info']['KLHST_WKS_WINDOMAIN'] if "KLHST_WKS_WINDOMAIN" in computer['info'] else None,
                "status": computer['info']['KLHST_WKS_STATUS_ID'] if "KLHST_WKS_STATUS_ID" in computer['info'] else None,
                "last_visible" : datetime.strptime(computer['info']['KLHST_WKS_LAST_VISIBLE']['value'], "%Y-%m-%dT%H:%M:%SZ") if "KLHST_WKS_LAST_VISIBLE" in computer['info'] and "value" in computer['info']['KLHST_WKS_LAST_VISIBLE'] else None,
                "dns_name" : str(computer['info']['KLHST_WKS_DNSNAME']).upper() if "KLHST_WKS_DNSNAME" in computer['info'] and computer['info']['KLHST_WKS_DNSNAME'] else None,
                "products": computer_products(computer['products'])
            } for computer in computers if computer['info'] and computer['products']}
        return computers

    def attach_computer(self, computer):

        def inner_attach():
            computer.kl_ksc_server = self.computer_records[computer.name]['server']
            computer.kl_ip = self.computer_records[computer.name]['ip']
            computer.kl_os = 'linx' if str(self.computer_records[computer.name]['os']).lower().find("lin") != -1 else\
                             'wind' if str(self.computer_records[computer.name]['os']).lower().find("win") != -1 else None
            computer.kl_status = self.computer_records[computer.name]['status']
            computer.last_logon_kaspersky = self.computer_records[computer.name]['last_visible']
            computer.kl_hasDuplicate = self.computer_records[computer.name]['hasDuplicate']

            def get_version(computername, product_name, addiction_product_name=None):
                for product in self.computer_records[computername]['products']:
                    if product['name'] and (product['name'].lower() == product_name or product['name'].lower() == addiction_product_name):
                        return product['version']
                return None
            computer.kl_agent_version = get_version(computer.get_name(), "klnagent")
            computer.kl_security_version = get_version(computer.get_name(), "avpcon.dll", addiction_product_name="libconnector.so")
            computer.kl_for_server_version = get_version(computer.get_name(), "ak_conn.dll")
            computer.kl_ksc_version = get_version(computer.get_name(), "klserver")


        if computer.get_name() in self.computer_records:
            inner_attach()
        else:
            for record in self.computer_records:
                if str(self.computer_records[record]['dns_name']) == "":
                    if computer.get_name() == record['dns_name']:
                        inner_attach()
                        break

    def add_host(self):

        def get_search_results():
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            items_count = 1000
            start = 0
            step = 1000
            result = list()
            while start < items_count:
                data = {"strAccessor": self.local.accessor, "nStart": start, "nCount": items_count}
                response = self.session.post(url=self.get_url('get_chunks'), headers=self.common_headers,
                                             data=json.dumps(data), verify=False)
                result += json.loads(response.text)["pChunk"]["KLCSP_ITERATOR_ARRAY"]
                start += step
            return result

        def get_accessor(type, group_id=None):
            data = {
                "wstrFilter": "",
                "vecFieldsToReturn": ["id", "name", "KLSRVH_SRV_DN"],
                "lMaxLifeTime": 100
            }
            url = self.get_url('get_groups')
            response = self.session.post(url=url, headers=self.common_headers, data=json.dumps(data), verify=False)
            self.local.accessor = json.loads(response.text)["strAccessor"]
            return self.local.accessor

        def get_groups():
            self.local.accessor = get_accessor(type="groups")
            return get_search_results()

        def update_host(key):
            data = {
                "strHostName" : key,
                "pInfo" : {
                    "KLHST_WKS_COMMENT" : "11.0.0.29"
                }
            }
            response = self.session.post(url=self.get_url('update_host'), headers=self.common_headers, data=json.dumps(data), verify=False)
            return response

        self.local.current_server = "SZO"
        self.create_connection()
        groups = get_groups()
        data = {
                "pInfo" : {
                "KLHST_WKS_DN" : "SZO-555-I001TEST",
                "KLHST_WKS_GROUPID" : 0,
                "KLHST_WKS_WINDOMAIN" : "ROSGVARD",
                "KLHST_WKS_WINHOSTNAME" : "SZO-555-I001TEST",
                "KLHST_WKS_DNSDOMAIN" : "ROSGVARD.RU",
                "KLHST_WKS_DNSNAME" : "SZO-555-I001TEST"
            }
        }
        data = json.dumps(data)
        response = self.session.post(
            url=self.get_url('add_host'),
            headers=self.common_headers, data=data, verify=False)
        obj = json.loads(response.text)
        accessor = obj['PxgRetVal']
        update_host(accessor)

KSC = KSC_server()
