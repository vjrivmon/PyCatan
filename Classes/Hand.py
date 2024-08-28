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

        # logica antigua
        # for id in resource_id:
        #     if amount + self.resources.get_from_id(id) < 0:
        #         return
        #     self.resources = self.resources.add_from_id(id, amount)
        # return

        # lo convertimos a materiales para poder sumarlo: ([1,3],5) -> [0,5,0,5,0]
        resources = Materials(*[ amount if id in resource_id else 0 for id in range(5)]) 
        tmp_resources = self.resources + resources

        # comprobamos que ninguno sea negativo, un jugador no puede tener materiales negativos
        if any([n < 0 for n in tmp_resources]):
            return

        self.resources = tmp_resources


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