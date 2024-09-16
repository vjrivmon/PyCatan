import random

from Classes.Constants import *
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface


# ATENCIÓN: AGENTE PREPARADO SOLO PARA TESTING. NO UTILIZAR EN UNA PARTIDA REAL
class AlexPastorAgent(AgentInterface):
    """
    Es necesario poner super().nombre_de_funcion() para asegurarse de que coge la función del padre
    """

    def __init__(self, agent_id):
        super().__init__(agent_id)

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_id=int):
        """
        Hay que tener en cuenta que gives se refiere a los materiales que da el jugador que hace la oferta,
         luego en este caso es lo que recibe
        :param offer:
        :return:
        """
        return True

    def on_turn_start(self):
        # Si tiene una carta de desarrollo la usa
        if len(self.development_cards_hand.hand):
            return self.development_cards_hand.select_card(0)
        return

    def on_turn_end(self):
        # Si tiene una carta de desarrollo la usa
        if len(self.development_cards_hand.hand):
            return self.development_cards_hand.select_card(0)
        return

    def on_having_more_than_7_materials_when_thief_is_called(self):
        return self.hand

    def on_moving_thief(self):
        # Pone el ladrón donde haya un jugador adyacente para robarle.
        # Si no se da la condición lo deja donde está, lo que hace que el GameManager lo ponga en un lugar aleatorio
        terrain_with_thief_id = -1
        for terrain in self.board.terrain:
            if not terrain['has_thief']:
                nodes = terrain['contacting_nodes']
                for node_id in nodes:
                    if self.board.nodes[node_id]['player'] not in [self.id, -1]:
                        enemy = self.board.nodes[node_id]['player']

                        return {'terrain': terrain['id'], 'player': enemy}
            else:
                terrain_with_thief_id = terrain['id']

        return {'terrain': terrain_with_thief_id, 'player': -1}

    def on_commerce_phase(self):
        if len(self.development_cards_hand.hand) and random.randint(0, 1):
            return self.development_cards_hand.select_card(0)

        answer = random.randint(0, 1)
        if answer:
            if self.hand.resources.cereal >= 4:
                return {'gives': MaterialConstants.CEREAL, 'receives': MaterialConstants.MINERAL}
            if self.hand.resources.mineral >= 4:
                return {'gives': MaterialConstants.MINERAL, 'receives': MaterialConstants.CEREAL}
            if self.hand.resources.clay >= 4:
                return {'gives': MaterialConstants.CLAY, 'receives': MaterialConstants.CEREAL}
            if self.hand.resources.wood >= 4:
                return {'gives': MaterialConstants.WOOD, 'receives': MaterialConstants.CEREAL}
            if self.hand.resources.wool >= 4:
                return {'gives': MaterialConstants.WOOL, 'receives': MaterialConstants.CEREAL}

            return None
        else:
            gives = Materials(random.randint(0, self.hand.resources.cereal),
                              random.randint(0, self.hand.resources.mineral),
                              random.randint(0, self.hand.resources.clay),
                              random.randint(0, self.hand.resources.wood),
                              random.randint(0, self.hand.resources.wool))
            receives = Materials(random.randint(0, self.hand.resources.cereal),
                                 random.randint(0, self.hand.resources.mineral),
                                 random.randint(0, self.hand.resources.clay),
                                 random.randint(0, self.hand.resources.wood),
                                 random.randint(0, self.hand.resources.wool))
            trade_offer = TradeOffer(gives, receives)
            return trade_offer

    def on_build_phase(self, board_instance):
        self.board = board_instance

        if len(self.development_cards_hand.hand) and random.randint(0, 1):
            return self.development_cards_hand.select_card(0)

        answer = random.randint(0, 2)
        # Pueblo / carretera
        if self.hand.resources.has_more(BuildConstants.TOWN) and answer == 0:
            answer = random.randint(0, 1)
            # Elegimos aleatoriamente si hacer un pueblo o una carretera
            if answer:
                valid_nodes = self.board.valid_town_nodes(self.id)
                if len(valid_nodes):
                    town_node = random.randint(0, len(valid_nodes) - 1)
                    return {'building': BuildConstants.TOWN, 'node_id': valid_nodes[town_node]}
            else:
                valid_nodes = self.board.valid_road_nodes(self.id)
                if len(valid_nodes):
                    road_node = random.randint(0, len(valid_nodes) - 1)
                    return {'building': BuildConstants.ROAD,
                            'node_id': valid_nodes[road_node]['starting_node'],
                            'road_to': valid_nodes[road_node]['finishing_node']}

        # Ciudad
        elif self.hand.resources.has_more(BuildConstants.CITY) and answer == 1:
            valid_nodes = self.board.valid_city_nodes(self.id)
            if len(valid_nodes):
                city_node = random.randint(0, len(valid_nodes) - 1)
                return {'building': BuildConstants.CITY, 'node_id': valid_nodes[city_node]}

        # Carta de desarrollo
        elif self.hand.resources.has_more(BuildConstants.CARD) and answer == 2:
            return {'building': BuildConstants.CARD}

        return None

    def on_game_start(self, board_instance):
        return super().on_game_start(board_instance)

    def on_monopoly_card_use(self):
        material = random.randint(0, 4)
        return material

    def on_road_building_card_use(self):
        valid_nodes = self.board.valid_road_nodes(self.id)
        if len(valid_nodes) > 1:
            while True:
                road_node = random.randint(0, len(valid_nodes) - 1)
                road_node_2 = random.randint(0, len(valid_nodes) - 1)
                if road_node != road_node_2:
                    return {'node_id': valid_nodes[road_node]['starting_node'],
                            'road_to': valid_nodes[road_node]['finishing_node'],
                            'node_id_2': valid_nodes[road_node_2]['starting_node'],
                            'road_to_2': valid_nodes[road_node_2]['finishing_node'],
                            }
        elif len(valid_nodes) == 1:
            return {'node_id': valid_nodes[0]['starting_node'],
                    'road_to': valid_nodes[0]['finishing_node'],
                    'node_id_2': None,
                    'road_to_2': None,
                    }
        return None

    def on_year_of_plenty_card_use(self):
        material, material2 = random.randint(0, 4), random.randint(0, 4)
        return {'material': material, 'material_2': material2}
