from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer


class TestTradeOffer:
    def test_trade_offer(self):
        gives = Materials(1, 2, 0, 3, 0)
        receives = Materials(0, 0, 5, 0, 1)
        trade_offer = TradeOffer(gives, receives)

        assert trade_offer.gives == gives and trade_offer.receives == receives
        assert trade_offer.__to_object__() == {'gives': gives.__to_object__(), 'receives': receives.__to_object__()}


if __name__ == '__main__':
    test = TestTradeOffer()
    test.test_trade_offer()
