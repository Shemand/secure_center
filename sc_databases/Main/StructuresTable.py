from sqlalchemy import select


class StructuresTable:
    def __init__(self, db):
        self.db = db

    def add(self, _name, _root_name=None):
        if self.get_one(_name) is None:
            if _root_name is not None:
                _root_id = self.get_one(_root_name)["id"]
            else:
                _root_id = None
            query = self.db.tStructures.insert().values(name=_name, root_id=_root_id)
            self.db.engine.execute(query)
        return self.get_one(_name)["id"]

    def get_one(self, _name):
        if _name is not "":
            query = select([self.db.tStructures]).where(self.db.tStructures.c.name == _name)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_by_id(self, _id):
        if _id is not None:
            query = select([self.db.tStructures]).where(self.db.tStructures.c.id == _id)
            row = self.db.engine.execute(query).fetchone()
            return row
        return None

    def get_by_root_id(self, _root_id):
        query = select([self.db.tStructures]).where(self.db.tStructures.c.root_id == _root_id)
        answer = self.db.engine.execute(query)
        if answer is not None:
            children = []
            for child in answer:
                children.append(child['id'])
                subtree_children = self.get_by_root_id(child['id'])
                for subtree_child in subtree_children:
                    children.append(subtree_child)
            return children
        return []
