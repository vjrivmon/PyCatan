from Classes.Materials import Materials


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
        materials = Materials.from_ids(resource_id, amount)
        materials = materials + self.resources
        self.resources = materials.replace_negative()


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