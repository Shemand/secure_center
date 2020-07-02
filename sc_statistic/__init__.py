import sys
import threading

from sc_cus import cryptoGateways as CG, load_crypto_gateways, CryptoGateways
from sc_statistic.updaters import update_database
from sc_statistic.kaspersky_taker import KSC
from sc_statistic.AD_taker import ActiveDirectory
from sc_statistic.Config import config
from sc_databases.LinuxDatabase import LinuxComputers
from sc_databases.WindowsDatabase import WindowsComputers
from sc_statistic.Dallas_taker import DallasServer
from sc_cus import cryptoGateways as CG

from sc_databases import db as database


def linux_taker(_computers):
    print("Begin take computers last loggined linux")
    linux_list = LinuxComputers.getComputerNames()
    for name in linux_list:
        exists_flag = 0
        for computer in _computers:
            if computer.name == name:
                pass
                computer.last_logon_puppet = linux_list[name]
                exists_flag = 1
                break
        if not exists_flag:
            print(name)


def windows_taker(_computers):
    print("Begin take computers last loggined windows")
    windows_list = WindowsComputers.getComputerNames()
    for name in windows_list:
        exists_flag = 0
        for computer in _computers:
            if computer.name == name:
                pass
                computer.last_logon_windows = windows_list[name]
                exists_flag = 1
                break
        if not exists_flag:
            print(name)


def structure_builder(_AD):
    print("Building structure from AD")
    for location in _AD.locations:
        prev_node = ""
        i = 0
        for node in location:
            if prev_node == "":
                database.Structures.add(node)
            else:
                if i == len(location) - 1:
                    node = config.locations["ad"][node]["name"]
                database.Structures.add(node, prev_node)
            prev_node = node
            i += 1

def kaspersky_builder(_computers):
    KSC.update_computer_records()
    for computer in _computers:
        KSC.attach_computer(computer)

def crypto_gateway_builder(_computers):
    if load_crypto_gateways():
        CG = CryptoGateways()
        database.Logs.add_update_logs("Data about CG was updated from file.")
    for computer in _computers:
        computer.crypto_gateway_name = CG.get_cryptoGateway_name(computer.kl_ip)

def addresses_builder():
    for cg_name in CG.gateways:
        for address in CG.gateways[cg_name].get_addresses():
            row = database.Addresses.get_one(address)
            if row:
                if row['activeToBlock'] != CG.gateways[cg_name].isActiveToBlock():
                    database.Addresses.update_activeToBlock_by_CG(cg_name, CG.gateways[cg_name].isActiveToBlock())
            else:
                database.Addresses.add(address, CG.gateways[cg_name])

def update_statistics():
    if not database.isUpdating:
        database.isUpdating = True
        try:
            print("Begin take computers from Active Directory")
            database.Logs.add_update_logs("Begin take computers from Active Directory.")
            AD = ActiveDirectory("ou=SZO,ou=FSVNG,dc=rosgvard,dc=ru")
        except Exception:
            print("Take data from Active Directory was ended with error.")
            database.Logs.add_update_logs("Take data from Active Directory was ended with error.")
            database.isUpdating = False
        else:
            computers = AD.get_computers()

            database.ARMs.disactivate_computers(computers)

            print("Begin take computers from Dallas Servers")
            database.Logs.add_update_logs("Begin take computers from Dallas Servers")
            DS = []
            try:
                dallas_paths = ["/home/shemand/PycharmProjects/ff/dallas-001.txt",
                                "/home/shemand/PycharmProjects/ff/dallas-002.txt",
                                "/home/shemand/PycharmProjects/ff/dallas-vch.txt",
                                "/home/shemand/PycharmProjects/ff/dallas-TERO.txt"]
                for path in dallas_paths:
                    DS.append(DallasServer(path))
                for ds in DS:
                    ds.taker(computers)
            except Exception:
                print("Take data from DallasLock file was ended with error.")
                database.Logs.add_update_logs("Take data from DallasLock file was ended with error.")
                database.isUpdating = False
            else:
                try:
                    print("Begin take info from puppet")
                    database.Logs.add_update_logs("Begin take info from puppet.")
                    linux_taker(computers)
                except Exception:
                    print("Take data from puppet file was ended with error.")
                    database.Logs.add_update_logs("Take data from puppet DB was ended with error.")
                    database.isUpdating = False
                else:
                    try:
                        print("Begin take info from windows")
                        database.Logs.add_update_logs("Begin take info from windows.")
                        windows_taker(computers)
                    except Exception:
                        print("Take data from WinDB file was ended with error.")
                        database.Logs.add_update_logs("Take data from WinDB was ended with error.")
                        database.isUpdating = False
                    else:
                        print("Begin take data from Kaspersky")
                        database.Logs.add_update_logs("Begin take data from Kaspersky")
                        kaspersky_builder(computers)

                        print("Begin take data about crypto gateway")
                        database.Logs.add_update_logs("Begin take data about crypto gateway")
                        crypto_gateway_builder(computers)

                        addresses_builder()

                        print("Begin update strucutre")
                        database.Logs.add_update_logs("Begin update structure.")
                        structure_builder(AD)

                        print("Updating computers info")
                        database.Logs.add_update_logs("Begin updating information in database.")
                        for computer in computers:
                            update_database(computer)
                        database.System.full_updated()
                        database.isUpdating = False
                        print("Congratulation. Statistics was updated.")
                        database.Logs.add_update_logs("Congratulation. Statistics was updated.")