from flask import g, session
from sc_databases import db as database
from sc_http.common.decorators import requires_auth


def tangle_session():
    g.username = None
    if 'user_id' in session:
        user = database.Users.get_by_id(session['user_id'])
        if user is not None:
            g.username = user['name']
            g.isAdmin = user['isAdmin']
            g.computers = database.Users.available_computers(session['user_id'])
            unit_list = []
            if user['Structures_id_access']:
                unit_list.append(database.Structures.get_by_id(user['Structures_id_access'])['name'])
                ids = database.Structures.get_by_root_id(database.Users.get_by_id(session['user_id'])['Structures_id_access'])
            else:
                 ids = []
            for id in ids:
                unit_list.append(database.Structures.get_by_id(id)['name'])
            g.unit_list = unit_list

@requires_auth
def get_computers_by_root():
    user = database.Users.get_by_id(session['user_id'])
    if user:
        structure = database.Structures.get_by_id(user['Structures_id_access'])
        if structure:
            return database.ARMs.get_by_root(structure['name'])
    return []

def computer_isAccess(computername):
    computers = get_computers_by_root()
    for computer in computers:
        if computer['name'] == computername:
            return True
    return False

def device_isAccess(devicename):
    user = database.Users.get_by_id(session['user_id'])
    if user and user['Structures_id_access']:
        struct = database.Structures.get_by_id(user['Structures_id_access'])
        if struct:
            devices = database.Devices.get_by_root(struct['name'])
            for device in devices:
                if device['name'] == devicename:
                    return True
    return False