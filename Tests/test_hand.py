from Classes.Hand import *


class TestHand:
    def test_hand_materials(self):
        hand = Hand()

        # Comprobamos que la mano empieza sin materiales
        assert hand.get_total() == 0

        # Comprobamos que add_material añade materiales correctamente
        hand.add_material(0, 1)
        hand.add_material(1, 1)
        hand.add_material(2, 1)
        hand.add_material(3, 1)
        hand.add_material(4, 1)
        assert hand.resources.cereal == 1 and hand.resources.mineral == 1 and hand.resources.clay == 1 and \
               hand.resources.wood == 1 and hand.resources.wool == 1 and hand.get_total() == 5

        # Comprobamos que la versión por lista funciona correctamente también
        hand.add_material([0, 1, 2, 3, 4], 1)
        assert hand.resources.cereal == 2 and hand.resources.mineral == 2 and hand.resources.clay == 2 and \
               hand.resources.wood == 2 and hand.resources.wool == 2 and hand.get_total() == 10

        # Comprobamos que remove_material elimina materiales correctamente
        hand.remove_material(0, 1)
        hand.remove_material(1, 1)
        hand.remove_material(2, 1)
        hand.remove_material(3, 1)
        hand.remove_material(4, 1)
        assert hand.resources.cereal == 1 and hand.resources.mineral == 1 and hand.resources.clay == 1 and \
               hand.resources.wood == 1 and hand.resources.wool == 1 and hand.get_total() == 5

        # Comprobamos que la versión por lista funciona correctamente también
        hand.remove_material([0, 1, 2, 3, 4], 1)
        assert hand.get_total() == 0

        # Comprobamos que no ocurre ningún problema al quiatar más materiales de los posibles
        hand.remove_material(0, 1)
        assert hand.resources.cereal == 0


if __name__ == '__main__':
    test = TestHand()
    test.test_hand_materials()
