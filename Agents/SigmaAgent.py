import random
from Classes.Constants import *
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface

class SigmaAgent(AgentInterface):
    def __init__(self, agent_id):
        super().__init__(agent_id)
        # Prioridad de materiales para el agente
        self.material_priority_order = [MaterialConstants.WOOD, MaterialConstants.CLAY, MaterialConstants.WOOL,
                                        MaterialConstants.CEREAL, MaterialConstants.MINERAL]
        # Materiales a seleccionar en la carta Year of Plenty
        self.year_of_plenty_material_one = MaterialConstants.WOOD
        self.year_of_plenty_material_two = MaterialConstants.CEREAL

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_making_offer=int):
        """
        Toma decisiones sobre ofertas de intercambio entrantes.
        """
        if offer.gives.has_more(offer.receives):
            return True # Aceptar la oferta si se reciben más materiales de los que se dan
        else:
            return False  # Rechazar la oferta en otro caso

    def on_turn_start(self):
        """
        Toma decisiones al comienzo del turno.
        """
        if len(self.development_cards_hand.hand):
            for i, card in enumerate(self.development_cards_hand.hand):
                if card.type == DevelopmentCardConstants.KNIGHT:
                    return self.development_cards_hand.select_card(i)
        return None # No jugar carta al comienzo del turno si no hay cartas de Caballero disponibles

    def on_having_more_than_7_materials_when_thief_is_called(self):
        """
        Descarta recursos en exceso cuando se mueve el ladrón.
        """
        while self.hand.get_total() > 7:
            for material in self.material_priority_order:
                if self.hand.resources.get_from_id(material) > 0:
                    self.hand.remove_material(material, 1)
                    break # Descartar solo un recurso a la vez
        return self.hand

    def on_moving_thief(self):
        """
        Toma decisiones sobre dónde mover al ladrón.
        """
        terrain_with_thief_id = -1
        for terrain in self.board.terrain:
            if not terrain['has_thief']:
                if terrain['probability'] == 6 or terrain['probability'] == 8:
                    nodes = self.board.__get_contacting_nodes__(terrain['id'])
                    has_own_town = False
                    has_enemy_town = False
                    enemy = -1
                    for node_id in nodes:
                        if self.board.nodes[node_id]['player'] == self.id:
                            has_own_town = True
                            break
                        if self.board.nodes[node_id]['player'] != -1:
                            has_enemy_town = True
                            enemy = self.board.nodes[node_id]['player']

                    if not has_own_town and has_enemy_town:
                        return {'terrain': terrain['id'], 'player': enemy}
            else:
                terrain_with_thief_id = terrain['id']

        return {'terrain': terrain_with_thief_id, 'player': -1}

    def on_turn_end(self):
        """
        Toma decisiones al final del turno.
        """
        if len(self.development_cards_hand.hand):
            for i, card in enumerate(self.development_cards_hand.hand):
                if card.type == DevelopmentCardConstants.VICTORY_POINT:
                    return self.development_cards_hand.select_card(i)
        return None  # No jugar carta al final del turno si no hay cartas de Punto de Victoria disponibles

    def on_commerce_phase(self):
        """
        Toma decisiones durante la fase de comercio.
        """
        gives = Materials(0,0,0,0,0)
        receives = Materials(0,0,0,0,0)

        if self.hand.resources.has_more(BuildConstants.CITY):
            self.material_given_more_than_three = None
            return None # No realizar intercambios si hay suficientes recursos para una ciudad

        # Ejemplo lógico para comerciar según necesidades actuales
        if self.hand.resources.has_more(BuildConstants.TOWN):
            return TradeOffer(Materials(0, 0, 1, 1, 1), Materials(1, 0, 0, 0, 0))

        return None # No realizar intercambios si no se cumplen las condiciones anteriores

    def on_build_phase(self, board_instance):
        """
        Toma decisiones durante la fase de construcción.
        """
        self.board = board_instance

        if self.hand.resources.has_more(BuildConstants.CITY):
            possibilities = self.board.valid_city_nodes(self.id)
            if possibilities:
                node_id = random.choice(possibilities)
                return {'building': BuildConstants.CITY, 'node_id': node_id}

        if self.hand.resources.has_more(BuildConstants.TOWN):
            possibilities = self.board.valid_town_nodes(self.id)
            if possibilities:
                node_id = random.choice(possibilities)
                return {'building': BuildConstants.TOWN, 'node_id': node_id}

        if self.hand.resources.has_more(BuildConstants.ROAD):
            possibilities = self.board.valid_road_nodes(self.id)
            if possibilities:
                road_obj = random.choice(possibilities)
                return {'building': BuildConstants.ROAD,
                        'node_id': road_obj['starting_node'],
                        'road_to': road_obj['finishing_node']}

        return None

    def on_game_start(self, board_instance):
        """
        Toma decisiones al inicio del juego.
        """
        self.board = board_instance
        possibilities = self.board.valid_starting_nodes()

        if possibilities:
            node_id = random.choice(possibilities)
            return node_id, random.choice(self.board.nodes[node_id]['adjacent'])

        return -1, -1

    def on_monopoly_card_use(self):
        """
        Toma decisiones al usar la carta Monopolio.
        """
        return random.choice(self.material_priority_order)

    def on_road_building_card_use(self):
        """
        Toma decisiones al usar la carta de Construcción de Carreteras.
        """
        valid_nodes = self.board.valid_road_nodes(self.id)
        if len(valid_nodes) > 1:
            road_obj = random.sample(valid_nodes, 2)
            return {'node_id': road_obj[0]['starting_node'],
                    'road_to': road_obj[0]['finishing_node'],
                    'node_id_2': road_obj[1]['starting_node'],
                    'road_to_2': road_obj[1]['finishing_node']}
        elif len(valid_nodes) == 1:
            road_obj = valid_nodes[0]
            return {'node_id': road_obj['starting_node'],
                    'road_to': road_obj['finishing_node'],
                    'node_id_2': None,
                    'road_to_2': None}
        return None

    def on_year_of_plenty_card_use(self):
        """
        Toma decisiones al usar la carta Year of Plenty.
        """
        return {'material': self.year_of_plenty_material_one, 'material_2': self.year_of_plenty_material_two}
