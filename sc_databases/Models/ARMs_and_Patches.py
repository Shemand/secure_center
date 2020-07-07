from sc_databases.Database import BaseModel
from sqlalchemy import Integer, ForeignKey, Column


class ARMs_and_Patches(BaseModel):
    __tablename__ = "ARMs_and_Patches"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, auto_increment=True)
    ARMs_id = Column(Integer, ForeignKey('ARMs.id'), nullable=False)
    Patches_id = Column(Integer, ForeignKey('Patches.id'), nullable=False)

    def __repr__(self):
        return "<ARMs_and_Patches model>"