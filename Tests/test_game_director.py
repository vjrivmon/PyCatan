from Managers.GameDirector import GameDirector
from Classes.Constants import DevelopmentCardConstants
from Classes.DevelopmentCards import *


class TestGameDirector:
    game_director = GameDirector(for_test="test_específico")

    def test_reset_game_values(self):
        self.game_director.game_manager.already_played_development_card = True
        self.game_director.game_manager.last_dice_roll = 4
        self.game_director.game_manager.largest_army = 5
        self.game_director.game_manager.largest_army_player = {"name": "<NAME>"}
        self.game_director.game_manager.longest_road = {"name": "<NAME>"}
        self.game_director.game_manager.board.build_town(0, 0)
        self.game_director.game_manager.board.build_city(0, 0)
        self.game_director.game_manager.board.build_town(2, 7)
        self.game_director.game_manager.development_cards_deck.draw_card()
        self.game_director.game_manager.set_turn(2)
        self.game_director.game_manager.set_whose_turn_is_it(3)
        self.game_director.game_manager.set_phase(1)
        self.game_director.game_manager.set_round(10)
        self.game_director.game_manager.agent_manager.players[0]['victory_points'] = 5

        self.game_director.trace_loader.current_trace = {"name": "<NAME>"}

        self.game_director.reset_game_values()

        assert self.game_director.game_manager.already_played_development_card is False
        assert self.game_director.game_manager.last_dice_roll == 0
        assert (self.game_director.game_manager.largest_army_player == {} and
                self.game_director.game_manager.largest_army == 2)
        assert self.game_director.game_manager.longest_road == {'longest_road': 4, 'player': -1}
        assert (self.game_director.game_manager.board.nodes[0]['player'] == -1 and
                self.game_director.game_manager.board.nodes[0]['has_city'] is False)
        assert (self.game_director.game_manager.board.nodes[0]['player'] == -1 and
                self.game_director.game_manager.board.nodes[0]['has_city'] is False)
        assert (self.game_director.game_manager.board.nodes[2]['player'] == -1 and
                self.game_director.game_manager.board.nodes[7]['has_city'] is False)
        assert (self.game_director.game_manager.development_cards_deck.deck != [] and
                self.game_director.game_manager.development_cards_deck.current_index == 0)
        assert (self.game_director.game_manager.turn_manager.turn == 0 and
                self.game_director.game_manager.turn_manager.whose_turn_is_it == 0 and
                self.game_director.game_manager.turn_manager.phase == 0 and
                self.game_director.game_manager.turn_manager.round == 0)
        assert self.game_director.game_manager.agent_manager.players[0]['victory_points'] == 0

        assert self.game_director.trace_loader.current_trace == {}

    def test_start_turn(self):
        self.game_director.reset_game_values()

        start_turn_object, winner = self.game_director.start_turn(True, 0)

        assert winner is True
        assert len(start_turn_object) == 1

        start_turn_object, winner = self.game_director.start_turn(False, 0)

        assert winner is False
        assert type(start_turn_object['dice']) is int

        # Al ganar con una carta de desarrollo
        self.game_director.reset_game_values()

        self.game_director.game_manager.agent_manager.players[0]['victory_points'] = 9
        self.game_director.game_manager.agent_manager.players[0]['hidden_victory_points'] = 1
        self.game_director.game_manager.agent_manager.players[0]['development_cards'].add_card(
            DevelopmentCard(17, DevelopmentCardConstants.VICTORY_POINT, DevelopmentCardConstants.VICTORY_POINT_EFFECT))
        self.game_director.game_manager.agent_manager.players[0]['player'].development_cards_hand.hand = \
            self.game_director.game_manager.agent_manager.players[0]['development_cards'].hand

        start_turn_object, winner = self.game_director.start_turn(False, 0)

        assert winner is True
        assert len(start_turn_object['development_card_played']) == 1

    def test_end_turn(self):
        self.game_director.reset_game_values()

        self.game_director.game_manager.board.nodes[0]['player'] = 0
        self.game_director.game_manager.board.build_road(0, 0, 1)
        self.game_director.game_manager.board.build_road(0, 1, 2)
        self.game_director.game_manager.board.build_road(0, 0, 8)
        self.game_director.game_manager.board.build_road(0, 8, 9)
        self.game_director.game_manager.board.build_road(0, 9, 10)

        end_turn_object, winner = self.game_director.end_turn(True, 0)

        assert winner is True
        assert self.game_director.game_manager.longest_road == {'longest_road': 4, 'player': -1}
        assert self.game_director.game_manager.agent_manager.players[0]['victory_points'] == 0

        end_turn_object, winner = self.game_director.end_turn(False, 0)

        assert winner is False
        assert self.game_director.game_manager.longest_road == {'longest_road': 5, 'player': 0}
        assert self.game_director.game_manager.agent_manager.players[0]['victory_points'] == 2

        # Al ganar con una carta de desarrollo
        self.game_director.reset_game_values()

        self.game_director.game_manager.agent_manager.players[0]['victory_points'] = 9
        self.game_director.game_manager.agent_manager.players[0]['hidden_victory_points'] = 1
        self.game_director.game_manager.agent_manager.players[0]['development_cards'].add_card(
            DevelopmentCard(17, DevelopmentCardConstants.VICTORY_POINT, DevelopmentCardConstants.VICTORY_POINT_EFFECT))
        self.game_director.game_manager.agent_manager.players[0]['player'].development_cards_hand.hand = \
            self.game_director.game_manager.agent_manager.players[0]['development_cards'].hand

        end_turn_object, winner = self.game_director.end_turn(False, 0)

        assert winner is True
        assert len(end_turn_object['development_card_played']) == 1

    def test_start_commerce_phase(self):
        return

    def test_start_build_phase(self):
        return

    def test_round_start(self):
        self.game_director.reset_game_values()

        round_object, winner = self.game_director.round_start(True)

        assert winner is True
        assert len(round_object) == 0

        round_object, winner = self.game_director.round_start(False)

        assert winner is False
        assert len(round_object) != 0

        # Al ganar con una carta de desarrollo
        self.game_director.reset_game_values()

        self.game_director.game_manager.agent_manager.players[0]['victory_points'] = 9
        self.game_director.game_manager.agent_manager.players[0]['hidden_victory_points'] = 1
        self.game_director.game_manager.agent_manager.players[0]['development_cards'].add_card(
            DevelopmentCard(17, DevelopmentCardConstants.VICTORY_POINT, DevelopmentCardConstants.VICTORY_POINT_EFFECT))
        self.game_director.game_manager.agent_manager.players[0]['player'].development_cards_hand.hand = \
            self.game_director.game_manager.agent_manager.players[0]['development_cards'].hand

        round_object, winner = self.game_director.round_start(False)

        assert winner is True
        assert len(round_object) != 0

    def test_game_start_and_game_loop(self):
        self.game_director.game_start(1)


if __name__ == '__main__':
    test = TestGameDirector()
    test.test_reset_game_values()
    test.test_start_turn()
    test.test_end_turn()
    # test.test_start_commerce_phase()  Testeado realmente en el Manager
    # test.test_start_build_phase()     Testeado realmente en el Manager
    test.test_round_start()
    test.test_round_end()
    test.test_game_start_and_game_loop()
