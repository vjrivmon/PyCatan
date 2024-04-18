from Classes.Hand import Hand
from Managers.CommerceManager import CommerceManager


class TestCommerceManager:
    def test_commerce_manager(self):
        commerce_manager = CommerceManager()
        hand = Hand()
        hand.add_material(0, 6)

        # Comercio sin puerto
        commerce_manager.trade_without_harbor(hand, 0, 1)
        assert hand.get_from_id(0) == 2 and hand.get_from_id(1) == 1

        # Comercio con puerto
        hand.add_material(2, 5)
        commerce_manager.trade_through_harbor(hand, 2, 3)
        assert hand.get_from_id(2) == 2 and hand.get_from_id(3) == 1

        # Comercio con un puerto especializado
        hand.add_material(4, 4)
        commerce_manager.trade_through_special_harbor(hand, 4, 0)
        assert hand.get_from_id(4) == 2 and hand.get_from_id(0) == 3


if __name__ == '__main__':
    test = TestCommerceManager()
    test.test_commerce_manager()
