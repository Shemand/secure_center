import base64
import ipaddress
import json
import threading
from datetime import datetime
from time import sleep

import requests
import urllib3
from requests import ReadTimeout, ConnectTimeout
from requests.adapters import HTTPAdapter
from queue import Queue


from sc_databases.Computers import Computers

from urllib3.exceptions import MaxRetryError, NewConnectionError

from sc_databases.Database import DatabaseClass


class KSC_server:
    def __init__(self):

        lock = threading.Lock()
        self.local = threading.local()
        self.queue = Queue()
        self.lock = threading.Lock()
        self.local.accessor = None
        self.session = requests.Session()
        self.computer_records = {}

        self.computers = Computers()
        self.db = DatabaseClass()

        adapter = HTTPAdapter(pool_maxsize=100, pool_connections=100)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        login = base64.b64encode("ksc-szo-001".encode("UTF-8")).decode("UTF-8")
        password = base64.b64encode("#00ktnCG<!!!".encode("UTF-8")).decode("UTF-8")

        self.auth_headers = {"Authorization": 'KSCBasic user="' + login + '", pass="' + password + '"',
                             "Content-Type": "application/json",
                             "Content-Length": "2"}
        self.common_headers = {"Content-Type": "application/json"}

        self.local.current_server = "2659"
        self.__base_url = {
            "2659" : "https://10.3.130.4:13299",
            "3526" : "https://10.3.132.7:13299",
            "3644" : "https://10.3.138.132:13299",
            "3693" : "https://10.3.139.182:13299",
            "3705" : "https://11.196.4.140:13299",
            "3798" : "https://10.3.138.87:13299",
            "5134" : "https://10.3.137.7:13299",
            "6716" : "https://10.3.134.250:13299",
            "6717" : "https://11.196.3.130:13299",
            "6821" : "https://10.3.133.132:13299",
            "6832" : "https://10.3.136.6:13299",
            "6944" : "https://10.3.131.73:13299",
            "T210" : "https://10.222.110.187:13299",
            "T211" : "https://10.222.111.240:13299",
            "T229" : "https://10.222.129.98:13299",
            "T235" : "https://10.222.135.106:13299",
            "T239" : "https://10.222.139.247:13299",
            "T251" : "https://10.222.151.201:13299",
            "T253" : "https://10.222.153.8:13299",
            "T278" : "https://10.222.198.4:13299",
            "UVO"  : "https://10.222.235.200:13299",
            "T283" : "https://10.222.183.3:13299",
            "T260" : "https://10.222.60.8:13299",
            "6931" : "https://10.3.141.4:13299",
            "SZO"  : "https://10.3.128.23:13299",
            "SZO_new" : "https://10.3.128.28:13299"
        }
        self.urls = {
            "create_connection": "/api/v1.0/login",
            "get_groups": "/api/v1.0/HostGroup.FindGroups",
            "get_hosts": "/api/v1.0/HostGroup.FindHosts",
            "get_chunks": "/api/v1.0/ChunkAccessor.GetItemsChunk",
            "get_count": "/api/v1.0/ChunkAccessor.GetItemsCount",
            "get_AdGroups": "/api/v1.0/VServers.GetVServers",
            "get_host_products": "/api/v1.0/HostGroup.GetHostProducts",
            "get_host_info": "/api/v1.0/HostGroup.GetHostInfo",
            "get_static_info": "/api/v1.0/HostGroup.GetStaticInfo",
            "get_child_servers": "/api/v1.0/ServerHierarchy.GetChildServers",
            "get_find_slave_servers": "/api/v1.0/ServerHierarchy.FindSlaveServers",
            "get_async_hosts" : "/api/v1.0/HostGroup.FindHostsAsync",
            "chunk_release" : "/api/v1.0/ChunkAccessor.Release",
            "get_async_status" : "/api/v1.0/AsyncActionStateChecker.CheckActionState",
            "get_async_accessor" : "/api/v1.0/HostGroup.FindHostsAsyncGetAccessor",
            "add_host" : "/api/v1.0/HostGroup.AddHost",
            "update_host": "/api/v1.0/HostGroup.UpdateHost"
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
            response = self.session.post(url=self.get_url('create_connection'), headers=self.auth_headers, data="{}",
                                         verify=False, timeout=30)
            if response.status_code == 401:
                # database.Logs.add_update_logs("Data of " + self.local.current_server + " wasn't took")
                print(
                    "[ERROR] (" + self.local.current_server + ") Authentication required. Check the policies or privileges of account!")
                return None
        except ReadTimeout:
            # database.Logs.add_update_logs("Data of " + self.local.current_server + " wasn't took")
            print("thread of connection to " + self.get_url(
                'create_connection') + " (" + self.local.current_server + ") ended with timeout")
            return None
        except ConnectTimeout:
            # database.Logs.add_update_logs("Data of " + self.local.current_server + " wasn't took")
            print("thread of connection to " + self.get_url(
                'create_connection') + " (" + self.local.current_server + ") ended with max retries exceeded (perhaps no privileges)")
            return None
        except requests.exceptions.ConnectionError:
            # database.Logs.add_update_logs("Data of " + self.local.current_server + " wasn't took")
            print("thread of connection to " + self.get_url(
                'create_connection') + " (" + self.local.current_server + ") ended with max retries exceeded (perhaps no privileges)")
            return None
        except MaxRetryError:
            # database.Logs.add_update_logs("Data of " + self.local.current_server + " wasn't took")
            print("thread of connection to " + self.get_url(
                'create_connection') + " (" + self.local.current_server + ") ended with max retries exceeded (perhaps no privileges)")
            return None
        except NewConnectionError as Err:
            if Err.errno == 113:
                # database.Logs.add_update_logs("Data of " + self.local.current_server + " wasn't took")
                print("thread of connection to " + self.get_url(
                    'create_connection') + " (" + self.local.current_server + ") ended with error 'No route to host'")
            else:
                # database.Logs.add_update_logs("Data of " + self.local.current_server + " wasn't took")
                print("While connection to " + self.get_url(
                    'create_connection') + " with error 'NewConnectionError' (errno not a 113)")
            return None
        # database.Logs.add_update_logs("Data of " + self.local.current_server + " was took done")
        print("connection created: " + self.local.current_server + " - status is - " + str(response.status_code))
        return response.status_code

    def __get_computers_by_threads(self):
        srv_name = self.queue.get()
        self.local.current_server = srv_name
        with self.lock:
            print(srv_name + ": begin take data")
        records = self.get_all_hosts()
        with self.lock:
            if records:
                for computer_name in records:
                    old_name = computer_name
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
                            pass
        self.queue.task_done()
        with self.lock:
            print(srv_name + ": data was took")

    def update_computer_records(self):
        self.computer_records = {}
        available_servers = []
        for server_name in self.__base_url:
            self.local.current_server = server_name
            response = self.create_connection()
            if response and response != 403:
                self.queue.put(server_name)
                available_servers.append(server_name)
        for server_name in available_servers:
            self.local.current_server = server_name
            trd = threading.Thread(target=self.__get_computers_by_threads)
            trd.setDaemon(True)
            trd.start()
        self.queue.join()
        for adapter in self.session.adapters.values():
            adapter.close()

    def attach_computer(self, computer):

        def inner_attach():
            computer.kl_ksc_server = self.computer_records[computer.name]['server']
            computer.kl_ip = self.computer_records[computer.name]['ip']
            computer.kl_os = 'linx' if str(self.computer_records[computer.name]['os']).lower().find("lin") != -1 else \
                'wind' if str(self.computer_records[computer.name]['os']).lower().find("win") != -1 else None
            computer.last_logon_kaspersky = self.computer_records[computer.name]['started']
            computer.kl_hasDuplicate = self.computer_records[computer.name]['hasDuplicate']

            computer.kl_agent_version = self.computer_records[computer.name]['agent_version']
            computer.kl_security_version = self.computer_records[computer.name]['security_version']
            computer.kl_info_updated = True

        if computer.get_name() in self.computer_records:
            inner_attach()
        else:
            for record in self.computer_records:
                if str(self.computer_records[record]['dns_name']) == "":
                    if computer.get_name() == record['dns_name']:
                        inner_attach()
                        break

    def get_all_hosts(self):
        def check_state(key):
            data = {
                "wstrActionGuid": str(key)
            }
            data = json.dumps(data)
            response = self.session.post(
                url=self.get_url('get_async_status'),
                headers=self.common_headers, data=data, verify=False)
            return response

        data = {
            "wstrFilter": "(&(KLHST_WKS_FROM_UNASSIGNED=0)(KLHST_WKS_STATUS & 4<>0))",
            "vecFieldsToReturn" : [ "KLHST_WKS_OS_NAME",
                                    "KLHST_WKS_IP_LONG",
                                    "KLHST_WKS_DN",
                                    "KLHST_WKS_LAST_VISIBLE",
                                    "KLHST_WKS_CREATED",
                                    "KLHST_WKS_NAG_VERSION",
                                    "KLHST_WKS_RTP_AV_VERSION",
                                    "KLHST_WKS_VIRUS_COUNT",
                                    "KLHST_WKS_LAST_SYSTEM_START",
                                    "KLHST_WKS_DNSNAME"],
            "pParams": {"KLSRVH_SLAVE_REC_DEPTH": 0, "KLGRP_FIND_FROM_CUR_VS_ONLY": False},
            "lMaxLifeTime": 100
        }

        def getAccessor(key):
            data = {
                "strRequestId": str(key)
            }
            data = json.dumps(data)
            response = self.session.post(
                url=self.get_url('get_async_accessor'),
                headers=self.common_headers, data=data, verify=False)
            return json.loads(response.content)['strAccessor']

        def getItemsCount(accessor):
            data = {
                "strAccessor": accessor
            }
            data = json.dumps(data)
            response = self.session.post(
                url=self.get_url('get_count'),
                headers=self.common_headers, data=data, verify=False)
            return json.loads(response.content)["PxgRetVal"]

        def getChunks(accessor, count):
            start = 0
            step = 10000
            data = {
                "strAccessor" : accessor,
                "nStart" : start,
                "nCount" : step
            }
            data = json.dumps(data)
            response = self.session.post(
                url=self.get_url('get_chunks'),
                headers=self.common_headers, data=data, verify=False)
            data = json.loads(response.content)
            data = data['pChunk']['KLCSP_ITERATOR_ARRAY']
            return data

        def Release(accessor):
            data = {
                "strAccessor": accessor
            }
            data = json.dumps(data)
            response = self.session.post(
                url=self.get_url('chunk_release'),
                headers=self.common_headers, data=data, verify=False)

        def zip_data(records):
            data = {}
            for record in records:
                data[ record['value']["KLHST_WKS_DN"].upper() ] = {
                    "server" : self.local.current_server,
                    "hasDuplicate" : False,
                    "os" : record['value']["KLHST_WKS_OS_NAME"] if "KLHST_WKS_OS_NAME" in record['value'] else None,
                    "ip" : str(ipaddress.ip_address(record['value']['KLHST_WKS_IP_LONG']['value'])) if "KLHST_WKS_IP_LONG" in record['value'] else None,
                    "last_visible" : datetime.strptime(str(record['value']["KLHST_WKS_LAST_VISIBLE"]['value']), "%Y-%m-%dT%H:%M:%SZ") if "KLHST_WKS_LAST_VISIBLE" in record['value'] else None,
                    "created" : datetime.strptime(str(record['value']["KLHST_WKS_CREATED"]['value']), "%Y-%m-%dT%H:%M:%SZ") if "KLHST_WKS_CREATED" in record['value'] else None,
                    "agent_version" : record['value']["KLHST_WKS_NAG_VERSION"] if "KLHST_WKS_NAG_VERSION" in record['value'] else None,
                    "security_version" : record['value']["KLHST_WKS_RTP_AV_VERSION"] if "KLHST_WKS_RTP_AV_VERSION" in record['value'] else None,
                    "virus" : record['value']["KLHST_WKS_VIRUS_COUNT"] if "KLHST_WKS_VIRUS_COUNT" in record['value'] else None,
                    "dns_name" : record['value']['KLHST_WKS_DNSNAME'] if "KLHST_WKS_DNSNAME" in record['value'] else None,
                    "started" : datetime.strptime(str(record['value']["KLHST_WKS_LAST_SYSTEM_START"]['value']), "%Y-%m-%dT%H:%M:%SZ") if "KLHST_WKS_LAST_SYSTEM_START" in record['value'] else None
                }
            return data

        data = json.dumps(data)
        response = self.session.post(url=self.get_url('get_async_hosts'),
                                     headers=self.common_headers, data=data, verify=False)
        print(response)
        key = json.loads(response.content)['strRequestId']
        finalized = False
        succeded_finalized = False
        while not finalized and not succeded_finalized:
            sleep(2)
            response = check_state(key)
            data = json.loads(response.content)
            succeded_finalized = data['bSuccededFinalized']
            finalized = data['bFinalized']
            if succeded_finalized:
                accessor = getAccessor(key)
                count = getItemsCount(accessor)
                data = getChunks(accessor, count)
                data = zip_data(data)
                Release(accessor)
                return data
            print(str(data['bFinalized']) + " : " + str(data['bSuccededFinalized']))
        print(response)
        return None

    def update_statistic(self):
        self.update_computer_records()
        for computername in self.computer_records:
            if computername == 'T253-A5-01':
                print('ff')
            record = self.computer_records[computername]
            computer = self.computers.get(computername)
            if not computer and record['dns_name'] != "":
                computer = self.computers.get(record['dns_name'])
            if computer:
                computer.update_kaspersky(self.db.session
                                         , server = record['server']
                                         , agent_version = record['agent_version']
                                         , security_version = record['security_version']
                                         , hasDuplicate = record['hasDuplicate']
                                         , ip = record['ip']
                                         , os = record['os']
                                         )
                computer.update_last_visible(record['started'])
        self.db.session.commit()

KSC = KSC_server()
