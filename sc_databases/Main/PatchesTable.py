import threading
from datetime import datetime

from sqlalchemy import select, and_, update, func


class PatchesTable:
    def __init__(self, db):
        self.db = db
        self.lock = threading.Lock()

    def add(self, _patch_name):
            patch = self.get_one(_patch_name)
            if patch is None:
                add = self.db.tPatches.insert().values(name=_patch_name)
                self.db.engine.execute(add)
            return self.get_one(_patch_name)["id"]

    def get_one(self, _patch_name):
        if _patch_name is not "":
            query = select([self.db.tPatches]).where(self.db.tPatches.c.name == _patch_name)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_by_id(self, _id):
        if _id:
            query = select([self.db.tPatches]).where(self.db.tPatches.c.id == _id)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def attach_patch(self, _ARM_name, _Patch_name):
        with self.lock:
            row = None
            query = select([self.db.tARMs.c.id.label('ARM_id'),
                            self.db.tPatches.c.id.label('Patch_id')]).select_from(self.db.tARMs.join(self.db.tPatches,
                                                                             and_(self.db.tARMs.c.name == _ARM_name,
                                                                                  self.db.tPatches.c.name == _Patch_name)))
            arm_patch = self.db.engine.execute(query).fetchone()
            arm_patch = dict(arm_patch.items()) if arm_patch else { "ARM_id" : self.db.ARMs.get_one(_ARM_name)['id'],
                                                                    "Patch_id" : None}
            if not arm_patch['Patch_id']:
                self.add(_Patch_name)
                arm_patch['Patch_id'] = self.get_one(_Patch_name)['id']
            elif arm_patch['ARM_id'] and arm_patch['Patch_id']:
                query = select([self.db.tARMs_and_Patches]).where(and_(self.db.tARMs_and_Patches.c.ARMs_id == arm_patch['ARM_id'],
                                                                       self.db.tARMs_and_Patches.c.Patches_id == arm_patch['Patch_id']))
                row = self.db.engine.execute(query).fetchone()

            if row:
                return
            else:
                query = self.db.tARMs_and_Patches.insert().values(ARMs_id=arm_patch['ARM_id'], Patches_id=arm_patch['Patch_id'])
                self.db.engine.execute(query)

    def get_ARM_pathes(self, _computername):
        computer = self.db.ARMs.get_one(_computername)
        if computer:
            patches = []
            query = ([self.db.tPatches.c.name]).select_from(self.db.tARMs.join(self.db.tARMs_and_Patches,
                                                                                    self.db.tARMs_and_Patches.c.Patches_id == self.db.tPatches.c.id,
                                                                                    isouter=True)).where(self.db.tARMs_and_Patches.c.id == computer['id'])
            rows = self.db.engine.execute(query)
            for row in rows:
                patches.append(row.name)
            return patches
        return []

