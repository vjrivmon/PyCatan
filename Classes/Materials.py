from typing import NamedTuple
from Classes.Constants import MaterialConstants as mc
from Classes.Constants import BuildConstants as bc
from Classes.Constants import BuildMaterialsConstants as bmc

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
        return Materials(*[amount if i in ids else 0 for i in range(5)])

    @classmethod
    def from_iterable(cls, iterable):
        return Materials(*iterable)

    @classmethod
    def from_building(cls, building):
        if building not in bmc.keys():
            return False
        return cls.from_iterable(bmc[building])

    # utilidades #####
    def non_negative(self):
        return Materials(*[0 if n < 0 else n for n in self])

    def is_empty(self):
        return sum(self) == 0

    def check_negative(self):
        return any([n < 0 for n in self])

    def get_from_id(self, material_constant):
        return self[material_constant]
    
    def add_from_id(self, material_constant, amount):
        return self + Materials.from_ids(material_constant, amount) 
    
    def remove_from_id(self, material_constant, amount):
        return self.add_from_id(material_constant, -amount)

    # adders #####
    def add_cereal(self, amount):
        return self.add_from_id(mc.CEREAL, amount)

    def add_mineral(self, amount):
        return self.add_from_id(mc.MINERAL, amount)

    def add_clay(self, amount):
        return self.add_from_id(mc.CLAY, amount)

    def add_wood(self, amount):
        return self.add_from_id(mc.WOOD, amount)

    def add_wool(self, amount):
        return self.add_from_id(mc.WOOL, amount)
    
    def has_this_more_materials(self, materials):
        """
        Si le llega otra clase Materials() comprobará si hay más o igual materiales que los que hay en el parámetro y
        si le llega un string con lo que se quiere construir comprobará si tiene suficiente material para hacerlo.
        :param materials: (str o Materials()) Nombre de lo que se quiere construir o materiales.
        :return: bool
        """
        if isinstance(materials, str):
            materials = Materials.from_building(materials)
            
        if isinstance(materials, Materials):
            return not (self - materials).check_negative()
        else:
            return False
        
    def __sub__(self, other):
        return Materials(*[self[i] - other[i] for i in range(5)])
    
    def __add__(self, other):
        return Materials(*[self[i] + other[i] for i in range(5)])
    
    def __mul__(self, other):
        return Materials(*[self[i] * other for i in range(5)])
    
    def __rmul__(self, other):
        return self.__mul__(other)

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