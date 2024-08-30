from Classes.Constants import BuildConstants, MaterialConstants
from Classes.Materials import *


class TestMaterials:
    def test_add_materials(self):
        materials = Materials(1, 2, 3, 4, 5)

        mc = [MaterialConstants.CEREAL, MaterialConstants.MINERAL, MaterialConstants.CLAY,
              MaterialConstants.WOOD, MaterialConstants.WOOL]
        for i in range(5):
            assert materials.get_from_id(mc[i]) == i + 1

    def test_has_more_materials_than_build_values(self):
        # Comprobamos que el mínimo funciona correctamente
        materials_for_town = Materials(1, 0, 1, 1, 1)
        assert materials_for_town.has_more(BuildConstants.TOWN)

        materials_for_city = Materials(2, 3, 0, 0, 0)
        assert materials_for_city.has_more(BuildConstants.CITY)

        materials_for_road = Materials(0, 0, 1, 1, 0)
        assert materials_for_road.has_more(BuildConstants.ROAD)

        materials_for_card = Materials(1, 1, 0, 0, 1)
        assert materials_for_card.has_more(BuildConstants.CARD)

        # Comprobamos que falla correctamente también
        assert not materials_for_town.has_more(BuildConstants.CITY)

        # Y también que funciona si se tiene materiales suficientes
        assert materials_for_town.has_more(BuildConstants.ROAD)

        # Y debería de tener materiales suficientes
        materials = Materials(1, 0, 4, 2, 7)
        assert materials.has_more(BuildConstants.TOWN)

        # Nos aseguramos de que no acepta valores negativos
        materials = Materials(1, 0, 4, 2, 7)
        assert not materials.has_more(Materials(1, 0, -1, 1, 1))


if __name__ == '__main__':
    test = TestMaterials()
    test.test_add_materials()
    test.test_has_more_materials_than_build_values()