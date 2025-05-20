import random
from Classes.Constants import *
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface

class PabloAleixAlexAgent(AgentInterface):

    def __init__(self, agent_id):
        super().__init__(agent_id)
        self.board = None
        self.town_number = 0
        self.material_given_more_than_three = None
        self.year_of_plenty_material_one = MaterialConstants.CEREAL
        self.year_of_plenty_material_two = MaterialConstants.MINERAL

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_making_offer=int):
        if offer.gives.has_more(offer.receives):
            return True
        else:
            return False

    def on_turn_start(self):
        if self.development_cards_hand.hand:
            for i, card in enumerate(self.development_cards_hand.hand):
                if card.type == DevelopmentCardConstants.KNIGHT:
                    return self.development_cards_hand.select_card(i)
        return None

    def on_having_more_than_7_materials_when_thief_is_called(self):
        if self.hand.get_total() > 7:
            for mat in [MaterialConstants.WOOL, MaterialConstants.CEREAL, MaterialConstants.MINERAL, MaterialConstants.CLAY, MaterialConstants.WOOD]:
                if self.hand.get_from_id(mat) > 1:
                    self.hand.remove_material(mat, 1)
                    return self.hand
        return None

    def on_moving_thief(self):
        terrain_with_thief_id = -1

        for terrain in self.board.terrain:
            if not terrain['has_thief'] and (terrain['probability'] == 6 or terrain['probability'] == 8):
                nodes = self.board.__get_contacting_nodes__(terrain['id'])
                has_own_town = any(self.board.nodes[node_id]['player'] == self.id for node_id in nodes)
                enemy = next((self.board.nodes[node_id]['player'] for node_id in nodes if self.board.nodes[node_id]['player'] != -1), -1)

                if not has_own_town and enemy != -1:
                    return {'terrain': terrain['id'], 'player': enemy}
            elif terrain['has_thief']:
                terrain_with_thief_id = terrain['id']

        return {'terrain': terrain_with_thief_id, 'player': -1}

    def on_turn_end(self):
        development_cards = self.development_cards_hand.hand

        for i, card in enumerate(development_cards):
            if card.type == DevelopmentCardConstants.VICTORY_POINT:
                return self.development_cards_hand.select_card(i)

        return None

    def on_commerce_phase(self):
        if self.hand.resources.has_more(Materials(2, 3, 0, 0, 0)):
            return None

        gives = Materials(0,0,0,0,0)
        receives = Materials(0,0,0,0,0)

        if self.town_number >= 1 and self.hand.resources.has_more(BuildConstants.CITY):
            return None
        elif self.town_number >= 1:
            cereal_hand = self.hand.resources.cereal
            mineral_hand = self.hand.resources.mineral
            wood_hand = self.hand.resources.wood
            clay_hand = self.hand.resources.clay
            wool_hand = self.hand.resources.wool
            total_given_materials = (5 - cereal_hand - mineral_hand - wood_hand - clay_hand - wool_hand)

            if total_given_materials > 0:
                materials_to_give = Materials(0,0,0,0,0)
                for mat, current_amount in {
                    MaterialConstants.CEREAL: cereal_hand,
                    MaterialConstants.MINERAL: mineral_hand,
                    MaterialConstants.WOOD: wood_hand,
                    MaterialConstants.CLAY: clay_hand,
                    MaterialConstants.WOOL: wool_hand,
                }.items():
                    if current_amount > 0:
                        self.hand.remove_material(mat, 1)
                        materials_to_give.add_from_id(MaterialConstants.MINERAL, mat)
                        total_given_materials -= 1
                        if total_given_materials == 0:
                            break

                gives = materials_to_give

        elif self.town_number == 0:
            materials_to_receive = Materials(
                1 - self.hand.resources.cereal,
                0 - self.hand.resources.mineral,
                1 - self.hand.resources.clay,
                1 - self.hand.resources.wood,
                1 - self.hand.resources.wool
            )

            for mat, current_amount in {
                MaterialConstants.CEREAL: self.hand.resources.cereal,
                MaterialConstants.MINERAL: self.hand.resources.mineral,
                MaterialConstants.CLAY: self.hand.resources.clay,
                MaterialConstants.WOOD: self.hand.resources.wood,
                MaterialConstants.WOOL: self.hand.resources.wool,
            }.items():
                if materials_to_receive.get_from_id(mat) < 0 and current_amount > 0:
                    self.hand.remove_material(mat, 1)
                    receives.add_from_id(MaterialConstants.MINERAL, mat)

        trade_offer = TradeOffer(gives, receives)
        return trade_offer

    def on_build_phase(self, board_instance):
        self.board = board_instance

        def calculate_probability_sum(node_id):
            return sum(self.board.terrain[terrain_piece_id]['probability'] for terrain_piece_id in self.board.nodes[node_id]['contacting_terrain'])

        if self.hand.resources.has_more(BuildConstants.CITY) and self.town_number > 0:
            possibilities = self.board.valid_city_nodes(self.id)
            if possibilities:
                best_node_id = max(possibilities, key=calculate_probability_sum)
                self.town_number -= 1
                return {'building': BuildConstants.CITY, 'node_id': best_node_id}

        if self.hand.resources.has_more(BuildConstants.TOWN):
            possibilities = self.board.valid_town_nodes(self.id)
            if possibilities:
                best_node_id = max(possibilities, key=calculate_probability_sum)
                self.town_number += 1
                return {'building': BuildConstants.TOWN, 'node_id': best_node_id}

        if self.hand.resources.has_more(BuildConstants.ROAD):
            road_possibilities = self.board.valid_road_nodes(self.id)
            if road_possibilities:
                random_road = random.choice(road_possibilities)
                return {'building': BuildConstants.ROAD,
                        'node_id': random_road['starting_node'],
                        'road_to': random_road['finishing_node']}

        if self.hand.resources.has_more(BuildConstants.CARD):
            return {'building': BuildConstants.CARD}

        return None


    def on_game_start(self, board_instance):
        self.board = board_instance
        possibilities = self.board.valid_starting_nodes()
        chosen_node_id = -1
        if possibilities:
            chosen_node_id = random.choice(possibilities)
        
        self.town_number += 1
        possible_roads = self.board.nodes[chosen_node_id]['adjacent']
        chosen_road_to_id = random.choice(possible_roads)

        return chosen_node_id, chosen_road_to_id

    def on_monopoly_card_use(self):
        return self.year_of_plenty_material_one
    
    def on_road_building_card_use(self):
        valid_nodes = self.board.valid_road_nodes(self.id)

        if not valid_nodes:
            return None
        
        def calculate_node_score(node):
            return node['probability'] + len(node['adjacent']) - 2 * self.board.count_opponent_towns(node['starting_node'])
        
        valid_nodes.sort(key=calculate_node_score, reverse=True)

        if len(valid_nodes) > 1:
            return {
                'node_id': valid_nodes[0]['starting_node'],
                'road_to': random.choice(valid_nodes[0]['adjacent']),  # Choose a random adjacent node
                'node_id_2': valid_nodes[1]['starting_node'],
                'road_to_2': random.choice(valid_nodes[1]['adjacent'])  # Choose a random adjacent node
            }
        elif len(valid_nodes) == 1:
            return {
                'node_id': valid_nodes[0]['starting_node'],
                'road_to': random.choice(valid_nodes[0]['adjacent']),  # Choose a random adjacent node
                'node_id_2': None,
                'road_to_2': None
            }
        
        return None

    def on_year_of_plenty_card_use(self):
        return self.year_of_plenty_material_one, self.year_of_plenty_material_two
