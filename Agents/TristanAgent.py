import random
import math
from functools import lru_cache

from Classes.Constants import MaterialConstants, BuildConstants
from Classes.Constants import DevelopmentCardConstants
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface


@lru_cache(maxsize=None)
def evaluate_node(node_id, board_instance):
    numbers = [board_instance.terrain[v]['probability'] for v in board_instance.nodes[node_id]['contacting_terrain']]
    # print(f"probability of neightbors from node_id {node_id}: {numbers}")
    number_score = 0

    #here, for each adjacent terrain, we assign a score based on the probability of the associated number
    for number in numbers:
        if number in [6, 8]:
            number_score += 3
        elif number in [5, 9]:
            number_score += 2
        elif number in [4, 10]:
            number_score += 1
        elif number in [3, 11]:
            number_score -= 1
        elif number in [2, 12]:
            number_score -= 2

    resources = [board_instance.terrain[v]['terrain_type'] for v in board_instance.nodes[node_id]['contacting_terrain']]
    # print(f"terrain_type of neightbors from node_id {node_id}: {resources}")

    #here, we check the number and the type of the adjacent resources
    #we discard nodes with only 2 adjacent resources (desert included), so the ones on the sea
    resource_score = 0
    if len(resources)<3:
        resource_score -= 10
    for resource in resources: #to do enum
        if resource == 1: #mineral
            resource_score += 3
        elif resource == 0: #cereal
            resource_score += 2
        elif resource in [3, 2]: #wood or clay
            resource_score += 1
        elif resource == 4: #wool
            resource_score -= 1
        elif resource == -1: #desert
            resource_score -= 5 #we discard nodes with the desert adjacent

    return number_score + resource_score

class TristanAgent(AgentInterface):
    """
    Es necesario poner super().nombre_de_funcion() para asegurarse de que coge la función del padre
    """
    def __init__(self, agent_id):
        self.town_number = 0
        self.road_number = 0
        super().__init__(agent_id)

    
    def best_node(self, nodes, board_instance):
        best_node = None
        best_score = -math.inf 

        for node in nodes: 
            score = evaluate_node(node, board_instance)
            if score > best_score:
                best_score = score
                best_node = node
                
        return best_node


    def evaluate_terrain(self, terrain_id, board_instance):
        #similar to node scoring,
        #assign a score to a terrain based on the resource and the number
        #avoiding terrains in which I have a town or city
        self.board = board_instance
        number = self.board.terrain[terrain_id]['probability']
        number_score = 0
        if number in [6, 8]:
            number_score += 3
        elif number in [5, 9]:
            number_score += 2
        elif number in [4, 10]:
            number_score += 1
        elif number in [3, 11]:
            number_score -= 1
        elif number in [2, 12]:
            number_score -= 2
        
        resource = self.board.terrain[terrain_id]['terrain_type']
        resource_score = 0
        if resource == 1: #mineral
            resource_score += 3
        elif resource == 0: #cereal
            resource_score += 2
        elif resource in [3, 2]: #wood or clay
            resource_score += 1
        elif resource == 4: #wool
            resource_score -= 1
        elif resource == -1: #desert
            resource_score -= 5
        
        im_here = False
        for node in self.board.terrain[terrain_id]['contacting_nodes']:
            if self.board.nodes[node]['player'] == self.id:
                im_here = True
        if im_here:
            return -100
        else:
            return number_score + resource_score
        
    
    def best_terrain(self, terrains, board_instance):
        best_terrain = None
        best_score = -math.inf 

        for terrain in terrains: 
            score = self.evaluate_terrain(terrain, board_instance)
            if score > best_score:
                best_score = score
                best_terrain = terrain
                
        return best_terrain

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_making_offer=int):
        gives = offer.gives
        receives = offer.receives
        #accept if they offer mineral without asking for it, asking for at most 3 other cards
        if gives.mineral>0 and sum(receives)<4 and receives.mineral==0:
            return True
        #refuse if they offer only wool
        elif gives.wool == sum(gives) and gives.wool>0:
            return False
        #if they offer more than they ask, but not mineral, accept
        elif sum(receives) <= sum(gives) and receives.mineral==0:
            return True
        #accept preferred couples 
        elif self.hand.resources.mineral>0 and gives.cereal>0:
            return True
        elif self.hand.resources.wood>0 and gives.clay>0:
            return True
        elif self.hand.resources.clay>0 and gives.wood>0:
            return True
        else:
            return False

    def on_turn_start(self):
        for i in range(0, len(self.development_cards_hand.hand)):
            # Play night
            if self.development_cards_hand.hand[i].type == DevelopmentCardConstants.KNIGHT:
                return self.development_cards_hand.select_card(i)

        return None

    def on_having_more_than_7_materials_when_thief_is_called(self):
        if self.hand.resources.has_more(BuildConstants.CITY):
            while self.hand.get_total() > 7:
                if self.hand.resources.wool > 0:
                    self.hand.remove_material(4, 1)

                if self.hand.resources.cereal > 2:
                    self.hand.remove_material(0, 1)
                if self.hand.resources.mineral > 3:
                    self.hand.remove_material(1, 1)

                if self.hand.resources.clay > 0:
                    self.hand.remove_material(2, 1)
                if self.hand.resources.wood > 0:
                    self.hand.remove_material(3, 1)
        # Si no tiene materiales para hacer una ciudad descarta de manera aleatoria cartas de su mano
        return self.hand

    def on_moving_thief(self):
        terrains = range(19)
        terrain = self.best_terrain(terrains, self.board)
        player = -1
       #choose the player near to that terrain 
        for node in self.board.terrain[terrain]['contacting_nodes']:
            if self.board.nodes[node]['player'] != -1 and self.board.nodes[node]['player'] != self.id:
                player = self.board.nodes[node]['player']
        return {'terrain': terrain, 'player': player}

    def on_turn_end(self):
        for i in range(0, len(self.development_cards_hand.hand)):
            # Play Victory Card
            if self.development_cards_hand.hand[i].type == DevelopmentCardConstants.VICTORY_POINT:
                return self.development_cards_hand.select_card(i)

        return None
    
    def total_material(self, material: Materials) -> int:
        return material.wool + material.wood + material.cereal + material.mineral + material.clay
    
    # need: How many resources should be obtained
    # rest: How many should be kept
    # We trade a maximum of 2:1 and offer lower value items first
    def calc_give_offer(self, need, wool=0, wood=0, cereal=0, mineral=0, clay=0) -> Materials:
        TRADE_FACTOR = 2
        result = Materials(0,0,0,0,0)
        
        result.add_from_id(MaterialConstants.WOOL, max(0, min(need * TRADE_FACTOR, self.hand.resources.wool - wool)))
        
        if self.total_material(result) < need * TRADE_FACTOR: 
            result.add_from_id(MaterialConstants.WOOD, max(0, min(need * TRADE_FACTOR, self.hand.resources.wood - wood)))
            
        if self.total_material(result) < need * TRADE_FACTOR: 
            result.add_from_id(MaterialConstants.CEREAL, max(0, min(need * TRADE_FACTOR, self.hand.resources.cereal - cereal)))

        if self.total_material(result) < need * TRADE_FACTOR: 
            result.add_from_id(MaterialConstants.MINERAL, max(0, min(need * TRADE_FACTOR, self.hand.resources.mineral - mineral)))

        if self.total_material(result) < need * TRADE_FACTOR: 
            result.add_from_id(MaterialConstants.CLAY,max(0, min(need * TRADE_FACTOR, self.hand.resources.clay - clay)))
            
        return result
    
    def on_commerce_phase(self):
        # Always Play Monopoly Card
        for i in range(0, len(self.development_cards_hand.hand)):
            if self.development_cards_hand.hand[i].effect == DevelopmentCardConstants.MONOPOLY_EFFECT:
                return self.development_cards_hand.select_card(i)

        # We do not trade because we have enough resources to build a city
        if self.town_number >= 1 and self.hand.resources.has_more(BuildConstants.CITY):
            return None
        
        # If we are missing only 1 recources for a city we try to trade
        if self.town_number >= 1:
            # One Ore missing
            if self.hand.resources.mineral == 2 and self.hand.resources.cereal >= 2:
                gives = self.calc_give_offer(need=1, mineral=3, cereal=2)

                receives = Materials(0,0,0,0,0)
                receives.add_from_id(MaterialConstants.MINERAL, 1) 
                
                return TradeOffer(gives, receives)
            # One Grain missing
            elif self.hand.resources.mineral >= 3 and self.hand.resources.cereal == 1:
                gives = self.calc_give_offer(need=1, mineral=3, cereal=2)

                receives = Materials(0,0,0,0,0)
                receives.add_from_id(MaterialConstants.CEREAL, 1) 
                
                return TradeOffer(gives, receives)
            # One Ore and one Grain missing
            elif self.hand.resources.mineral == 2 and self.hand.resources.cereal == 2:
                gives = self.calc_give_offer(need=2, mineral=3, cereal=2)

                receives = Materials(0,0,0,0,0)
                receives.add_from_id(MaterialConstants.MINERAL, 1) 
                receives.add_from_id(MaterialConstants.CEREAL, 1) 
                
                return TradeOffer(gives, receives)

        # If we are missing only 1 recources for a settlement we try to trade
        # Missing wood
        if self.hand.resources.wood == 0 and self.hand.resources.clay >= 1 and self.hand.resources.wool >= 1 and self.hand.resources.cereal >= 1:
            gives = self.calc_give_offer(need=1, clay=1, wool=1, cereal=1)
            receives = Materials(0,0,0,0,0)
            receives.add_from_id(MaterialConstants.WOOD, 1) 
            return TradeOffer(gives, receives)
            
        if self.hand.resources.wood >= 1 and self.hand.resources.clay == 0 and self.hand.resources.wool >= 1 and self.hand.resources.cereal >= 1:
            gives = self.calc_give_offer(need=1, wood=1, wool=1, cereal=1)
            receives = Materials(0,0,0,0,0)
            receives.add_from_id(MaterialConstants.CLAY,1) 
            return TradeOffer(gives, receives)

        if self.hand.resources.wood >= 1 and self.hand.resources.clay >= 1 and self.hand.resources.wool == 0 and self.hand.resources.cereal >= 1:
            gives = self.calc_give_offer(need=1, wood=1, clay=1, cereal=1)
            receives = Materials(0,0,0,0,0)
            receives.add_from_id(MaterialConstants.WOOL, 1) 
            return TradeOffer(gives, receives)

        if self.hand.resources.wood >= 1 and self.hand.resources.clay >= 1 and self.hand.resources.wool >= 1 and self.hand.resources.cereal == 0:
            gives = self.calc_give_offer(need=1, wood=1, clay=1, wool=1)
            receives = Materials(0,0,0,0,0)
            receives.add_from_id(MaterialConstants.CEREAL, 1) 
            return TradeOffer(gives, receives)

        # If we are missing a recource we try to obtain it using the bank if possible
        if self.hand.resources.clay == 0:
            if self.hand.resources.wood > 6:
                return {'gives': MaterialConstants.WOOD, 'receives': MaterialConstants.CLAY}
            elif self.hand.resources.wool > 6:
                return {'gives': MaterialConstants.WOOL, 'receives': MaterialConstants.CLAY}
            elif self.hand.resources.cereal > 6:
                return {'gives': MaterialConstants.CEREAL, 'receives': MaterialConstants.CLAY}
            elif self.hand.resources.mineral > 6:
                return {'gives': MaterialConstants.MINERAL, 'receives': MaterialConstants.CLAY}

        if self.hand.resources.wood == 0:
            if self.hand.resources.clay > 6:
                return {'gives': MaterialConstants.CLAY, 'receives': MaterialConstants.WOOD}
            elif self.hand.resources.wool > 6:
                return {'gives': MaterialConstants.WOOL, 'receives': MaterialConstants.WOOD}
            elif self.hand.resources.cereal > 6:
                return {'gives': MaterialConstants.CEREAL, 'receives': MaterialConstants.WOOD}
            elif self.hand.resources.mineral > 6:
                return {'gives': MaterialConstants.MINERAL, 'receives': MaterialConstants.WOOD}

        if self.hand.resources.wool == 0:
            if self.hand.resources.clay > 6:
                return {'gives': MaterialConstants.CLAY, 'receives': MaterialConstants.WOOL}
            elif self.hand.resources.wood > 6:
                return {'gives': MaterialConstants.WOOD, 'receives': MaterialConstants.WOOL}
            elif self.hand.resources.cereal > 6:
                return {'gives': MaterialConstants.CEREAL, 'receives': MaterialConstants.WOOL}
            elif self.hand.resources.mineral > 6:
                return {'gives': MaterialConstants.MINERAL, 'receives': MaterialConstants.WOOL}

        if self.hand.resources.cereal == 0:
            if self.hand.resources.clay > 6:
                return {'gives': MaterialConstants.CLAY, 'receives': MaterialConstants.CEREAL}
            elif self.hand.resources.wood > 6:
                return {'gives': MaterialConstants.WOOD, 'receives': MaterialConstants.CEREAL}
            elif self.hand.resources.wool > 6:
                return {'gives': MaterialConstants.WOOL, 'receives': MaterialConstants.CEREAL}
            elif self.hand.resources.mineral > 6:
                return {'gives': MaterialConstants.MINERAL, 'receives': MaterialConstants.CEREAL}

        if self.hand.resources.mineral == 0:
            if self.hand.resources.clay > 6:
                return {'gives': MaterialConstants.CLAY, 'receives': MaterialConstants.MINERAL}
            elif self.hand.resources.wood > 6:
                return {'gives': MaterialConstants.WOOD, 'receives': MaterialConstants.MINERAL}
            elif self.hand.resources.wool > 6:
                return {'gives': MaterialConstants.WOOL, 'receives': MaterialConstants.MINERAL}
            elif self.hand.resources.cereal > 6:
                return {'gives': MaterialConstants.CEREAL, 'receives': MaterialConstants.MINERAL}

        return None

    def on_build_phase(self, board_instance):
        self.board = board_instance

        # Cities:
        if self.hand.resources.has_more(BuildConstants.CITY) and len(self.board.valid_city_nodes(self.id)) > 0:
            valid_nodes = self.board.valid_city_nodes(self.id)
            city_node = self.best_node(valid_nodes, self.board)

            self.town_number -= 1
            return {'building': BuildConstants.CITY, 'node_id': city_node}

        # Play development card
        if len(self.development_cards_hand.hand):
            for i in range(0, len(self.development_cards_hand.hand)):
                # Play Year of the Plenty
                if self.development_cards_hand.hand[i].effect == DevelopmentCardConstants.YEAR_OF_PLENTY_EFFECT:
                    return self.development_cards_hand.select_card(i)

                # Build Roads if possible
                if self.development_cards_hand.hand[i].effect == DevelopmentCardConstants.ROAD_BUILDING_EFFECT and \
                         len(self.board.valid_road_nodes(self.id)) >= 2:
                    return self.development_cards_hand.select_card(i)

        # Pueblo 
        if self.hand.resources.has_more(BuildConstants.TOWN):
            # Elegimos aleatoriamente si hacer un pueblo o una carretera
            if len(self.board.valid_town_nodes(self.id)) > 0:
                valid_nodes = self.board.valid_town_nodes(self.id)
                town_node = self.best_node(valid_nodes, self.board)

                self.town_number += 1
                return {'building': BuildConstants.TOWN, 'node_id': town_node}
            
        # carretera
        if self.hand.resources.has_more(BuildConstants.ROAD) \
        and len(self.board.valid_road_nodes(self.id)) > 0 \
        and self.road_number <= self.town_number + 4:
            valid_nodes = self.board.valid_road_nodes(self.id)
            
            best_start = None
            best_finish = None
            best_score = -math.inf

            for v in valid_nodes: 
                start, finish = v["starting_node"], v["finishing_node"]
                score = evaluate_node(finish, self.board)
                
                if score > best_score:
                    best_start = start
                    best_finish = finish
                    best_score = best_score

            self.road_number += 1
            return {'building': BuildConstants.ROAD,
                        'node_id': best_start,
                        'road_to': best_finish}

        return None

    def on_game_start(self, board_instance):
        self.board = board_instance
        free_nodes = board_instance.valid_starting_nodes()
        
        #evaluation of the available nodes:
        node_id = self.best_node(free_nodes, board_instance)
        #random allocation for the road
        possible_roads = self.board.nodes[node_id]['adjacent']
        road = possible_roads[random.randint(0, len(possible_roads) - 1)]
        return node_id, road

    def on_monopoly_card_use(self):
        return 4

    # noinspection DuplicatedCode
    def on_road_building_card_use(self):
        valid_nodes = self.board.valid_road_nodes(self.id)
        if len(valid_nodes) > 1:
            scores = []
            for v in valid_nodes: 
                start, finish = v["starting_node"], v["finishing_node"]
                score = evaluate_node(finish, self.board)
                scores.append((start,finish, score))
            scores.sort(key=lambda x: x[1], reverse = True)
            return{'node_id':scores[0][0],
                   'road_to':scores[0][1],
                   'node_id_2': scores[1][0],
                   'road_to_2': scores[1][1]}
        elif len(valid_nodes) == 1:
            return {'node_id': valid_nodes[0]['starting_node'],
                    'road_to': valid_nodes[0]['finishing_node'],
                    'node_id_2': None,
                    'road_to_2': None,
                    }
        return None

    def on_year_of_plenty_card_use(self):
        return {'material': 1, 'material_2': 0}
