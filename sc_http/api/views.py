import json
import threading
from datetime import datetime

from flask import Blueprint, jsonify, session, request

from sc_http.common.functions import tangle_session, get_computers_by_root, computer_isAccess, device_isAccess
from sc_http.common.decorators import requires_auth, requires_be_admin
from sc_statistic import update_statistics as upd_stat

mod = Blueprint('api', __name__, url_prefix='/api/')

@mod.before_request
def before_request():
    tangle_session()

@mod.route('/get_computers/', methods=["GET"])
@requires_auth
def get_computers():
    computers = []
    user = database.Users.get_by_id(session['user_id'])
    unit_row = database.Structures.get_by_id(user['Structures_id_access'])
    unit = unit_row['name'] if unit_row else None
    data = database.ARMs.get_ready_data_for_root(unit)
    dallas_status = {
        4 : "Установлен",
        5 : "Установлен",
        6 : "Критическая ошибка",
        9 : "Критическая ошибка",
        37 : "Неизвестная ошибка",
    }
    for computer in data:
        dic = {
            "unit" : computer['unit'],
            "CG_name" : computer['CG_name'] if computer['CG_name'] else "Неизв.",
            "name" : computer['name'],
            "ad" : str(computer['ad_added']) if computer['ad_added'] else "Не зарегистрирован",
            "dallas" : dallas_status[computer['dallas']] if computer['dallas'] in dallas_status else "Неизвестный код ошибки" if computer['dallas'] else "Отсутствует",
            "kl_security" : computer['kl_security'] if computer['kl_security'] else "Отсутствует",
            "kl_agent" : computer['kl_agent'] if computer['kl_agent'] else "Отсутствует",
            "kl_ip" : computer['kl_ip'] if computer['kl_ip'] else "Неизвестно",
            "isLocked" : True if computer['isLocked'] else False,
            "isBlocking" : True if computer['activeToBlock'] else False,
            "hasDuplicate" : True if computer['hasDuplicate'] else False,
            "os" : "Windows" if computer['os'] == "wind" else "Linux" if computer['os'] == "linx" else "Неизвестно",
            "dallas_server" : computer['dallas_server'] if computer['dallas_server'] else "Отсутствует",
            "loggined" : str(computer['last_logon']) if computer['last_logon'] else "Неизвестно",
            "type" : computer['type'] if computer['type'] else "1",
            "comment" : computer['comment'] if computer['comment'] else ""
        }
        computers.append(dic)
    return jsonify({ "last_updated" : int(database.System.get('full_updated')['value'].timestamp())*1000, "computers" : computers})

@mod.route('/devices', methods=['GET'])
@requires_auth
def get_devices():
    user = database.Users.get_by_id(session['user_id'])
    unit_row = database.Structures.get_by_id(user['Structures_id_access'])
    if unit_row:
        records = database.Devices.get_ready_data_for_root(unit_row['name'])
        devices = []
        for record in records:
            devices.append({
                "unit": record['unit'],
                "CG_name": record['CG_name'] if record['CG_name'] else "Неизв.",
                "name": record['name'],
                "ip": record['ip'] if record['ip'] else "Неизвестно",
                "isLocked": True if record['isLocked'] else False,
                "isBlocking": True if record['activeToBlock'] else False,
                "type": record['type'] if record['type'] else "1",
                "comment": record['comment'] if record['comment'] else ""
            })
        return jsonify(devices)
    return jsonify({})

@mod.route('/devices', methods=['PUT'])
@requires_auth
def add_device():
    data = json.loads(request.get_data())
    if data['name'] and data['ip'] and data['crypto_gateway'] and data['type']:
        user = database.Users.get_by_id(session['user_id'])
        unit_row = database.Structures.get_by_id(user['Structures_id_access'])
        if unit_row:
            if database.CryptoGateways.isAccess_by_structure(data['crypto_gateway'], unit_row['id']):
                device = database.Devices.add(data['name'], data['ip'], data['type'], data['comment'])
                if device:
                    data = {
                        "unit" : database.Structures.get_by_id(device['Structures_id'])['name'],
                        "CG_name" : data['crypto_gateway'],
                        "name" : data['name'],
                        "ip" : data['ip'],
                        "type" : data['type'],
                        "comment" : data['comment']
                    }
                    return '{ "status" : "ok", "message" : "Device was added.", "data" : ' + json.dumps(data) + '}'
                return '{ "status" : "bad", "message" : "Error while add device" }'
    return '{}'

@mod.route('/devices/<devicename>', methods=['DELETE'])
@requires_auth
def remove_device(devicename):
    if devicename:
        if database.Devices.remove(devicename):
            return '{ "status" : "ok", "message" : "' + devicename + ' was deleted" }'
        return '{ "status" : "bad", "message" : "Some problems while deleting" }'
    return '{ "status" : "ok", "message" : "need device name" }'


@mod.route('/now', methods=['GET'])
def get_now():
    return str(int(datetime.now().timestamp() * 1000))

@mod.route('/os_notificate/<computername>/', methods=['POST'])
def os_notificate(computername):
    print(request.get_data())
    data = json.loads(request.get_data())
    print(data)
    database.Logons.login(computername, data['username'], data['os'], data['adapters'], _domain_server=data['domain_server'])
    for patch in data['patches']:
        database.Patches.attach_patch(computername, patch)
    return "{}"

@mod.route('/table/computer/<computername>/comment/', methods=['POST'])
@requires_auth
def change_computer_comment(computername):
    result = None
    data = json.loads(request.get_data())
    if computer_isAccess(computername):
        result = database.ARMs.update_comment(computername, data['comment'])
        if result:
            return '{ "status" : "ok" , "message" : "comment was updated" }'
    return '{ "status" : "bad" , "message" : "comment updating ended with error" }'

@mod.route('/table/device/<devicename>/comment/', methods=['POST'])
@requires_auth
def change_device_comment(devicename):
    result = None
    data = json.loads(request.get_data())
    if device_isAccess(devicename):
        result = database.Devices.update_comment(devicename, data['comment'])
        if result:
            return '{ "status" : "ok" , "message" : "comment was updated" }'
    return '{ "status" : "bad" , "message" : "comment updating ended with error" }'

@mod.route('/table/computer/<computername>/type/<type>', methods=['POST'])
@requires_auth
def change_computer_type(computername, type):
    result = None
    if computer_isAccess(computername):
        try:
            if int(type) in database.ARMs.TYPES:
                result = database.ARMs.change_type(computername, int(type))
        except Exception:
            return '{ "status" : "bad", "message" : "changing type of computer ended with error"}'
        if result:
            return '{ "status" : "ok", "message" : "computer type was updated"}'
    return '{ "status" : "bad", "message" : "changing type of computer ended with error"}'

@mod.route('/table/device/<devicename>/type/<type>', methods=['POST'])
@requires_auth
def change_device_type(devicename, type):
    result = None
    if device_isAccess(devicename):
        if int(type) in database.Devices.TYPES:
            result = database.Devices.change_type(devicename, int(type))
        if result:
            return '{ "status" : "ok", "message" : "device type was updated"}'
    return '{ "status" : "bad", "message" : "changing type of device ended with error"}'

@mod.route('/update_statistic', methods=['POST'])
@requires_auth
@requires_be_admin
def update_statistic():
    if not database.isUpdating:
        trd = threading.Thread(target=upd_stat)
        trd.start()
        trd.join()
        return '{ "status" : "ok", "message" : "data was updated" }'
    database.Logs.add_update_logs("Imposable update statistics, because updating already in progress.")
    return '{ "status" : "bad", "message" : "update in progress" }'

@mod.route('/update_logs', methods=['GET'])
@requires_auth
@requires_be_admin
def get_update_logs():
    data = database.Logs.get_last_100_update_logs()
    for record in data:
        record['date'] = record['date'].timestamp() * 1000
    return json.dumps(data)

@mod.route('/user/isadmin', methods=['GET'])
@requires_auth
def get_isAdmin():
    user = database.Users.get_by_id(session['user_id'])
    if user:
        if user['isAdmin']:
            return '{ "status" : "ok" , "message" : "user is admin" }'
    return '{ "status" : "bad" , "message" : "unknown" }'

@mod.route('/computer/unlock/<computername>', methods=["POST"])
@requires_auth
@requires_be_admin
def unlock_computer(computername):
    if computer_isAccess(computername):
        computer = database.ARMs.get_ready_data(computername)
        if computer['kl_ip']:
            if database.Addresses.unlock(computer['kl_ip']):
                return '{ "status" : "ok", "message" : "computer was unlocked" }'
            else:
                return '{ "status" : "ok", "message" : "ip address doesn\'t exists" }'
        else:
            return '{ "status" : "bad", "message" : "computer haven\'t ip" }'
    else:
        return '{ "status" : "bad", "message" : "u haven\'t access to computer" }'

@mod.route('/computer/lock/<computername>', methods=["POST"])
@requires_auth
@requires_be_admin
def lock_computer(computername):
    if computer_isAccess(computername):
        computer = database.ARMs.get_ready_data(computername)
        if computer['kl_ip']:
            if database.Addresses.lock(computer['kl_ip']):
                return '{ "status" : "ok", "message" : "computer was locked" }'
            else:
                return '{ "status" : "ok", "message" : "ip address doesn\'t exists" }'
        else:
            return '{ "status" : "bad", "message" : "computer haven\'t ip" }'
    else:
        return '{ "status" : "bad", "message" : "u haven\'t access to computer" }'


@mod.route('/available/crypto_gateways', methods=['GET'])
@requires_auth
def get_crypto_gateways():
    user = database.Users.get_by_id(session['user_id'])
    if user and user['Structures_id_access']:
        units = database.Structures.get_by_root_id(user['Structures_id_access'])
        units.append(user['Structures_id_access'])
        if units:
            crypto_gateways = []
            for unit in units:
                gateways = database.CryptoGateways.get_by_structure_id(unit)
                for gateway in gateways:
                    crypto_gateways.append(gateway['name'])
            return jsonify(crypto_gateways)
    return jsonify([])

@mod.route('/available/ip/crypto_gateway/<crypto_gateway>', methods=['GET'])
@requires_auth
def get_ip_by_crypto_gateways(crypto_gateway):
    user = database.Users.get_by_id(session['user_id'])
    if user and user['Structures_id_access']:
        if database.CryptoGateways.isAccess_by_structure(crypto_gateway, user['Structures_id_access']):
            return jsonify(database.Addresses.get_by_CG(crypto_gateway, free=True))
    return '{}'