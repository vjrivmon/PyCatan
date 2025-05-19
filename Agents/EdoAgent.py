import random

from Classes.Constants import MaterialConstants, BuildConstants
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface
from math import floor
from .helpers import *
from math import log2
from Classes.Constants import DevelopmentCardConstants as Dcc
import itertools

class EdoAgent(AgentInterface):
    """
    Es necesario poner super().nombre_de_funcion() para asegurarse de que coge la función del padre
    """
    def __init__(self, bot_id):
        
        super().__init__(bot_id)
        self.turn_counter = 0 # contador de turnos
        self.goals = [ # lista con orden de prioridades de los objetivos inmediatos
            "build_town",
            "build_town",
            "buy_card",
            "buy_card",
            "buy_card",
            "buy_card",
            "build_town",
            "build_city",
            "build_city",
            "build_city",
            "build_city",
        ]

        self.traded = False

    def get_mat(self):
        return materials_to_mat(self.hand.resources)

    def on_commerce_phase(self):
        for i in range(len(self.goals)):
            excess, needed = create_exchange(self.get_mat(), self.goals[:i])
            if sum(needed) > 0 and sum(excess) > 0:
                break
        
        if sum(needed) == 0 or sum(excess) == 0:
            return None
        
        excess_index = weighted_material_choice(excess)
        gives = index_to_mat(excess_index)
        excess = msub(excess, gives)

        if random.randint(0, 1) and sum(excess) > 0:
            excess_index_2 = weighted_material_choice(excess)
            gives_2 = index_to_mat(excess_index_2)
            gives = madd(gives, gives_2)
        _gives = Materials(*gives)

        needed_index = weighted_material_choice(needed)
        receives = index_to_mat(needed_index)
        _receives = Materials(*receives)

        # print(f"({self.turn_counter}) {self.goals[0]}: {receives} -> {gives}")
        return TradeOffer(_receives, _gives)

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_making_offer=int):
        
        receives = materials_to_mat(offer.receives)
        gives = materials_to_mat(offer.gives)

        if sum(gives) < sum(receives):
            return False

        excess, needed = create_exchange(self.get_mat(), self.goals[:2])
        
        if sum(excess) == 0:
            return False

        if sum(mpos(msub(needed, receives))) > 0:
            receives = mpos(msub(needed, receives))
            return TradeOffer(mat_to_materials(receives),offer.gives)
        
        return True

    def on_turn_start(self):
        self.traded = False
        self.turn_counter += 1

        if not self.goals:
            self.goals = ["build_city"]
        if self.goals[0] == "build_city" and not self.board.valid_city_nodes(self.id):
            self.goals.insert(0, "build_town")
        elif self.goals[0] == "build_town" and not self.board.valid_town_nodes(self.id):
            self.goals.insert(0, "build_road")

        # If thief is on a terrain with a town, play a knight card
        town_nodes = get_town_nodes(self.board, self.id)
        thief_nodes = get_thief_nodes(self.board)
        if set(town_nodes).intersection(set(thief_nodes)):
            card = get_development_card(self.development_cards_hand.hand, Dcc.KNIGHT_EFFECT)
            if card:
                return self.development_cards_hand.select_card(card)
            elif self.goals[0] != "buy_card" and random.randint(0, 4) == 0:
                self.goals.insert(0, "buy_card")

        for effect in [Dcc.ROAD_BUILDING_EFFECT, Dcc.YEAR_OF_PLENTY_EFFECT, Dcc.MONOPOLY_EFFECT]:
            card = get_development_card(self.development_cards_hand.hand, effect)
            if card:
                return self.development_cards_hand.select_card(card)

        return None

    def on_having_more_than_7_materials_when_thief_is_called(self):
        excess_count_rule = int(floor(self.hand.get_total()/2))
        excess = excess_materials(self.get_mat(), self.goals[:1])
        excess_count_excess = sum(excess)
        for i in range(min(excess_count_rule, excess_count_excess)):
            max_index = excess.index(max(excess))
            self.hand.remove_material(max_index, 1)
        return self.hand

    def on_moving_thief(self):
        town_nodes = get_town_nodes(self.board, self.id)
        terrain_nodes = [get_adjacent_terrain(self.board, node) for node in town_nodes]
        others_terrain = set(range(18)) - set(itertools.chain(*terrain_nodes))
        return {'terrain': random.choice(list(others_terrain)), 'player': random.choice(list({0,1,2,3}-{self.id}))}

    def on_turn_end(self):
        card = get_development_card(self.development_cards_hand.hand, Dcc.ROAD_BUILDING_EFFECT)
        if card:
            return self.development_cards_hand.select_card(card)
        return None

    def on_build_phase(self, board_instance):
        self.board = board_instance

        if not self.goals:
            self.goals = ["build_city"]
            
        goal = self.goals[0]
        
        if goal == "build_town" and self.hand.resources.has_more('town'):
            valid_nodes = self.board.valid_town_nodes(self.id)
            if len(valid_nodes):
                node_resources = [get_node_resources(board_instance, node) for node in valid_nodes]
                sorted_nodes = [x for _, x in sorted(zip(node_resources, valid_nodes), key=lambda pair: pair[0])]
                self.goals.remove(goal)
                return {'building': BuildConstants.TOWN, 'node_id': sorted_nodes[0]}
            
        elif goal == "build_city" and self.hand.resources.has_more('city'):
            valid_nodes = self.board.valid_city_nodes(self.id)
            if len(valid_nodes):
                node_resources = [get_node_resources(board_instance, node) for node in valid_nodes]
                sorted_nodes = [x for _, x in sorted(zip(node_resources, valid_nodes), key=lambda pair: pair[0])]
                self.goals.remove(goal)
                return {'building': BuildConstants.CITY, 'node_id': sorted_nodes[0]}
        
        elif goal == "build_road" and self.hand.resources.has_more('road'):
            road_ends = get_road_ends(self.board, self.id)
            for end in road_ends:
                adjacent_roads = get_adjacent_road(self.board, end, self.id)
                best_road = None
                best_materials = Mat(0, 0, 0, 0, 0)
                for adjacent in adjacent_roads:
                    materials = get_node_resources(self.board, adjacent['finishing_node'])
                    if sum(materials) > sum(best_materials):
                        best_materials = materials
                        best_road = adjacent
                if best_road:
                    self.goals.remove(goal)
                    return {'building': BuildConstants.ROAD,
                            'node_id': adjacent['starting_node'],
                            'road_to': adjacent['finishing_node']}


        elif goal == "buy_card" and self.hand.resources.has_more('card'):
            self.goals.remove(goal)
            return {'building': BuildConstants.CARD}

        return None

    def on_game_start(self, board_instance):
        free = get_free_nodes(board_instance)
        current_town_nodes = get_town_nodes(board_instance, self.id)
        current_resources = list(Mat(0, 0, 0, 0, 0))
        node_resources = [get_node_resources(board_instance, node) for node in free]
        if current_town_nodes:
            current_resources = reduce(lambda x, y: madd(x,y), [get_node_resources(board_instance, node) for node in current_town_nodes])
        node_resources = [madd(x, current_resources) for x in node_resources]
        node_resources = [sum([log2(x+1) for x in node]) for node in node_resources]
        sorted_free = [x for _, x in sorted(zip(node_resources, free), key=lambda pair: pair[0])]
        adjacent = board_instance.__get_adjacent_nodes__(sorted_free[0]) #TODO: mejorable
        return (sorted_free[0], adjacent[0])

    def on_monopoly_card_use(self):
        excess, needed = create_exchange(self.get_mat(), self.goals)
        max_index = needed.index(max(needed))
        return max_index

    def on_road_building_card_use(self):
        # esto es muy cutre
        ret = None
        road_ends = get_road_ends(self.board, self.id)
        for end in road_ends:
            adjacent_roads = get_adjacent_road(self.board, end, self.id)
            best_road = None
            best_materials = Mat(0, 0, 0, 0, 0)
            for adjacent in adjacent_roads:
                materials = get_node_resources(self.board, adjacent['finishing_node'])
                if sum(materials) > sum(best_materials):
                    best_materials = materials
                    best_road = adjacent
            if best_road:
                ret = {'node_id': best_road['starting_node'],
                        'road_to': best_road['finishing_node']}
                break
            else:
                return None

        road_ends.remove(best_road['starting_node'])
        road_ends.append(best_road['finishing_node'])
        for end in road_ends:
            adjacent_roads = get_adjacent_road(self.board, end, self.id)
            best_road = None
            best_materials = Mat(0, 0, 0, 0, 0)
            for adjacent in adjacent_roads:
                materials = get_node_resources(self.board, adjacent['finishing_node'])
                if sum(materials) > sum(best_materials):
                    best_materials = materials
                    best_road = adjacent
            if best_road:
                ret.update({'node_id_2': best_road['starting_node'],
                        'road_to_2': best_road['finishing_node']})
                break
            
        return ret

    def on_year_of_plenty_card_use(self):
        for g in range(len(self.goals)):
            excess, needed = create_exchange(self.get_mat(), self.goals[:g])
            if sum(needed) >=2:
                break
        
        needed = list(needed)
        m1 = needed.index(max(needed))
        needed[m1] = 0
        m2 = needed.index(max(needed))

        return {'material': m1, 'material_2': m2}
