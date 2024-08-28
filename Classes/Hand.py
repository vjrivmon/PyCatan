from Classes.Materials import Materials
from functools import singledispatchmethod



class Hand:
    """
    Clase que representa la mano de los jugadores
    """

    def __init__(self):
        self.resources = Materials(0,0,0,0,0)


    def add_material(self, resource_id, amount):
        """
        Suma amount al material o materiales seleccionados (si es negativo lo resta).
        :param resource: (int o list[int]) tipo de recurso(s) a añadir.
        :param amount: (int) cantidad del recurso a añadir.
        :return: None
        """
        # si es un entero lo convertimos en una lista
        if isinstance(resource_id, int):
            resource_id = [resource_id]

        # lo convertimos a materiales para poder sumarlo: ([1,3],5) -> [0,5,0,5,0]
        materials = Materials(*[ amount * resource_id.count(id) for id in range(5)])
        materials = materials + self.resources
        self.resources = Materials(*[0 if n < 0 else n for n in materials])


    def remove_material(self, resource, amount):
        """
        Resta amount al material o materiales seleccionados (si es negativo lo suma).
        :param resource: (int o list[int]) tipo de recurso(s) a quitar.
        :param amount: (int)cantidad del recurso a quitar.
        :return: None
        """
        self.add_material(resource, -amount)


    def get_from_id(self, material_id):
        return self.resources.get_from_id(material_id)

    def get_total(self):
        return sum(self.resources)

    def __str__(self):
        return f'Hand: {str(self.resources)}' 