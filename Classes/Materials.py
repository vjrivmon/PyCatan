from typing import NamedTuple
from Classes.Constants import MaterialConstants as mc
from Classes.Constants import BuildConstants as bc
from Classes.Constants import BuildMaterialsConstants as bmc
import operator as op

class Materials(NamedTuple):
    """
    Clase que representa los materiales. Se usa tanto en la mano de los jugadores como en las ofertas
    """
    cereal: int
    mineral: int
    clay: int
    wood: int
    wool: int
    
    # constructores alternativos
    @classmethod
    def from_ids(cls, ids, amount = 1):
        if isinstance(ids, int):
            ids = [ids]
        return Materials(*[amount * ids.count(id) for id in range(5)])
        
    @classmethod
    def from_iterable(cls, iterable):
        return Materials(*iterable)

    @classmethod
    def from_building(cls, building):
        if building not in bmc.keys():
            return False
        return cls.from_iterable(bmc[building])

    def replace_negative(self):
        return Materials(*[0 if n < 0 else n for n in self])

    def is_empty(self):
        return all([n == 0 for n in self])

    def check_negative(self):
        return any([n < 0 for n in self])

    def get_from_id(self, material_constant):
        return self[material_constant]
    
    def add_from_id(self, material_constant, amount):
        return self + Materials.from_ids(material_constant, amount) 
    
    def remove_from_id(self, material_constant, amount):
        return self.add_from_id(material_constant, -amount)

    def has_more(self, materials): #TODO: añadir tipos
        """
        Si le llega otra clase Materials() comprobará si hay más o igual materiales que los que hay en el parámetro y
        si le llega un string con lo que se quiere construir comprobará si tiene suficiente material para hacerlo.
        :param materials: (str o Materials()) Nombre de lo que se quiere construir o materiales.
        :return: bool
        """
        if isinstance(materials, str):
            materials = Materials.from_building(materials)
            
        return all(materials <= self)
    
    def __str__(self):
        material_icons = ["🥖", "🪨", "🧱", "🪵", "🧶"]
        material_tuples = list(zip(self, material_icons))
        mls = [str(t[0]).rjust(2)+t[1] for t in material_tuples]
        return " ".join(mls)

    def __to_object__(self):
        return {'cereal': str(self.cereal), 'mineral': str(self.mineral), 'clay': str(self.clay),
                'wood': str(self.wood), 'wool': str(self.wool)}

    def __repr__(self):
        return 'Materials()'

    # aqui hay demasiado codigo repetido, debe haber una mejor forma
    def __eq__(self, other):
        return map(op.eq, self, other)

    def __lt__(self, other):
        return map(op.lt, self, other)

    def __le__(self, other):
        return map(op.le, self, other)

    def __gt__(self, other):
        return map(op.gt, self, other)
        
    def __ge__(self, other):
        return map(op.ge, self, other)

    def __sub__(self, other):
        return Materials(*map(op.sub, self, other))
    
    def __add__(self, other):
        return Materials(*map(op.add, self, other))
    
    def __mul__(self, other):
        return Materials(*map(op.mul, self, other))
    
    def __rmul__(self, other):
        return self.__mul__(other)