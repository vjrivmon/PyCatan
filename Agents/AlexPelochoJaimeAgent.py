import random
from Classes.Constants import *
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface

class AlexPelochoJaimeAgent(AgentInterface):
    town_number = 0
    material_given_more_than_three = None
    board = 0
    def __init__(self, agent_id):
        super().__init__(agent_id)

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_making_offer=int):
        """
        Hay que tener en cuenta que gives se refiere a los materiales que da el jugador que hace la oferta,
        luego en este caso es lo que recibe
        :param offer:
        :return:
        """
        if offer.gives.has_more(offer.receives):
            return True
        else:
            return False
        # return super().on_trade_offer(offer)    

    def on_commerce_phase(self):
        """
        Se podría complicar mucho más la negociación, cambiando lo que hace en función de si tiene o no puertos y demás
        """
        # Juega monopolio si ha entregado más de 3 del mismo tipo de material a un jugador en el intercambio
        if self.material_given_more_than_three is not None:
            if len(self.development_cards_hand.hand):
                # Mira todas las cartas
                for i in range(0, len(self.development_cards_hand.hand)):
                    # Si una es un punto de monopolio
                    if self.development_cards_hand.hand[i].effect == DevelopmentCardConstants.MONOPOLY_EFFECT:
                        # La juega
                        return self.development_cards_hand.select_card(i)

        gives = Materials(0,0,0,0,0)
        receives = Materials(0,0,0,0,0)

        # No pide nada porque puede hacer una ciudad
        if self.town_number >= 1 and self.hand.resources.has_more(BuildConstants.CITY):
            self.material_given_more_than_three = None
            return None
        # Pedir lo que falte para una ciudad, ofrece el resto de materiales iguales a los que pide
        elif self.town_number >= 1:
            cereal_hand = self.hand.resources.cereal
            mineral_hand = self.hand.resources.mineral
            wood_hand = self.hand.resources.wood
            clay_hand = self.hand.resources.clay
            wool_hand = self.hand.resources.wool
            total_given_materials = (2 - cereal_hand) + (3 - mineral_hand)

            # Si hay más materiales que los pedidos
            if total_given_materials < (wood_hand + clay_hand + wool_hand):
                materials_to_give = [0, 0, 0, 0, 0]
                for i in range(0, total_given_materials):
                    # Se mezcla el orden de materiales
                    order = [MaterialConstants.CLAY, MaterialConstants.WOOD, MaterialConstants.WOOL]
                    random.shuffle(order)
                    # una vez mezclado se recorre el orden de los materiales y se coge el primero que tenga un valor
                    for mat in order:
                        if self.hand.resources.get_from_id(mat) > 0:
                            self.hand.remove_material(mat, 1)
                            materials_to_give[mat] += 1
                            break
                gives = Materials(materials_to_give[0], materials_to_give[1], materials_to_give[2],
                                  materials_to_give[3], materials_to_give[4])

            # Si no hay más materiales que los pedidos, simplemente se prueba a entregar todos lo que se tenga en mano
            else:
                gives = Materials(0, 0, clay_hand, wood_hand, wool_hand)

            receives = Materials(2, 3, 0, 0, 0)

        # Como no puede construir una ciudad pide materiales para hacer un pueblo
        elif self.town_number == 0:
            # Si tiene materiales para hacer un pueblo directamente no comercia
            if self.hand.resources.has_more(Materials(1, 0, 1, 1, 1)):
                return None
            # Si no los tiene hace un intercambio
            else:
                # Puedes cambiar materiales repetidos o minerales
                materials_to_receive = [0, 0, 0, 0, 0]
                materials_to_give = [0, 0, 0, 0, 0]

                number_of_materials_received = 0

                materials_to_receive[0] = 1 - self.hand.resources.cereal
                materials_to_receive[1] = 0 - self.hand.resources.mineral
                materials_to_receive[2] = 1 - self.hand.resources.clay
                materials_to_receive[3] = 1 - self.hand.resources.wood
                materials_to_receive[4] = 1 - self.hand.resources.wool

                # Nos aseguramos de que solo pida materiales que necesita, y que no hayan negativos
                for i in range(0, len(materials_to_receive)):
                    if materials_to_receive[i] <= 0:
                        materials_to_receive[i] = 0
                    else:
                        number_of_materials_received += 1

                # Por cada material que recibe, ofrece 1 de entre los que tiene en mano,
                #   pero guardándose al menos 1 de cada uno de los necesarios para hacer un pueblo
                for j in range(0, number_of_materials_received):
                    # Se mezcla el orden de materiales
                    order = [MaterialConstants.CEREAL, MaterialConstants.MINERAL, MaterialConstants.CLAY,
                             MaterialConstants.WOOD, MaterialConstants.WOOL]
                    random.shuffle(order)
                    # una vez mezclado se recorre el orden de los materiales y se coge el primero que tenga un valor
                    for mat in order:
                        if self.hand.resources.get_from_id(mat) > 1 or mat == MaterialConstants.MINERAL:
                            self.hand.remove_material(mat, 1)
                            materials_to_give[mat] += 1
                            break

                gives = Materials(materials_to_give[0], materials_to_give[1], materials_to_give[2],
                                  materials_to_give[3], materials_to_give[4])
                receives = Materials(materials_to_receive[0], materials_to_receive[1], materials_to_receive[2],
                                     materials_to_receive[3], materials_to_receive[4])

        trade_offer = TradeOffer(gives, receives)
        return trade_offer
    
    def on_game_start(self, board_instance):
        self.board = board_instance

        # Obtener todos los nodos disponibles para el primer pueblo
        possibilities = self.board.valid_starting_nodes()

        # Inicializar variables para almacenar el resultado final
        chosen_node_id = -1
        chosen_road_to_id = -1

        # Buscar un nodo ideal basado en las condiciones dadas
        for node_id in possibilities:
            # Verificar los terrenos adyacentes al nodo actual
            if node_id in self.board.nodes and 'adjacent' in self.board.nodes[node_id]:
                for adj_node_id in self.board.nodes[node_id]['adjacent']:
                    if adj_node_id in self.board.nodes and 'number' in self.board.nodes[adj_node_id]:
                        if self.board.terrain[self.board.nodes[adj_node_id]['terrain']]['probability'] in [6, 8]:
                            # Encontrar el siguiente número más cercano a 7
                            adjacent_numbers = [self.board.nodes[adj_node_id]['number'] for adj_node_id in self.board.nodes[node_id]['adjacent']]
                            closest_to_7 = min(adjacent_numbers, key=lambda x: abs(x - 7))

                            # Elegir el nodo si está desocupado
                            if closest_to_7 not in [self.board.nodes[adj_node_id]['number'] for adj_node_id in self.board.nodes[node_id]['adjacent']]:
                                chosen_node_id = node_id
                                break

        # Si no se encontró un nodo ideal, elegir aleatoriamente uno de las posibilidades
        if chosen_node_id == -1 and possibilities:
            chosen_node_id = random.choice(possibilities)

        # Incrementar el número de pueblos creados
        self.town_number += 1

        # Elegir una carretera aleatoria entre todas las opciones del nodo elegido
        if chosen_node_id in self.board.nodes and 'adjacent' in self.board.nodes[chosen_node_id]:
            possible_roads = self.board.nodes[chosen_node_id]['adjacent']
            chosen_road_to_id = random.choice(possible_roads)

        return chosen_node_id, chosen_road_to_id
    
    def on_turn_start(self):
        # Verificar si hay cartas de desarrollo disponibles para jugar
        if self.development_cards_hand:
            # Buscar la primera carta de desarrollo tipo KNIGHT en la mano y jugarla si es posible
            for i in range(0, len(self.development_cards_hand.hand)):
                # Si una es un caballero
                if self.development_cards_hand.hand[i].type == DevelopmentCardConstants.KNIGHT:
                    # La juega
                    return self.development_cards_hand.select_card(i)

        # Si no se juega ninguna carta de desarrollo
        return None

    def on_build_phase(self, board_instance):
        self.board = board_instance

        # Check if there are development cards to play
        # Check if there are development cards to play
        if len(self.development_cards_hand.hand):
            for i, card in enumerate(self.development_cards_hand.hand):
                if (card.effect == DevelopmentCardConstants.YEAR_OF_PLENTY_EFFECT or
                        card.effect == DevelopmentCardConstants.ROAD_BUILDING_EFFECT):
                    return self.development_cards_hand.select_card(i)


        # Build a city if possible and beneficial based on adjacent terrain probabilities
        if self.hand.resources.has_more(BuildConstants.CITY) and self.town_number > 0:
            city_nodes = self.board.valid_city_nodes(self.id)
            for node_id in city_nodes:
                for terrain_id in self.board.nodes[node_id]['contacting_terrain']:
                    probability = self.board.terrain[terrain_id]['probability']
                    if probability in [5, 6, 8, 9]:
                        self.town_number -= 1
                        return {'building': BuildConstants.CITY, 'node_id': node_id}

        # Build a settlement if materials are available and suitable terrain is adjacent
        if self.hand.resources.has_more(BuildConstants.TOWN):
            town_nodes = self.board.valid_town_nodes(self.id)
            for node_id in town_nodes:
                for terrain_id in self.board.nodes[node_id]['contacting_terrain']:
                    probability = self.board.terrain[terrain_id]['probability']
                    if probability in [4, 5, 6, 8, 9, 10]:
                        self.town_number += 1
                        return {'building': BuildConstants.TOWN, 'node_id': node_id}

        # Build a road to a coastal node with a harbor if possible, otherwise build randomly
        if self.hand.resources.has_more(BuildConstants.ROAD):
            road_nodes = self.board.valid_road_nodes(self.id)

            # Check for coastal node with a harbor to prioritize
            for road_obj in road_nodes:
                if self.board.is_coastal_node(road_obj['finishing_node']) and \
                self.board.nodes[road_obj['finishing_node']]['harbor'] != HarborConstants.NONE:
                    return {'building': BuildConstants.ROAD,
                            'node_id': road_obj['starting_node'],
                            'road_to': road_obj['finishing_node']}

            # If no coastal node with a harbor, build a road randomly (60% of the time)
            if random.random() < 0.6 and len(road_nodes) > 0:
                road_obj = random.choice(road_nodes)
                return {'building': BuildConstants.ROAD,
                        'node_id': road_obj['starting_node'],
                        'road_to': road_obj['finishing_node']}

        # Build a development card if materials are available
        if self.hand.resources.has_more(BuildConstants.CARD):
            return {'building': BuildConstants.CARD}

        return None
    
    def on_turn_end(self):
        # Si tiene mano de cartas de desarrollo
        if len(self.development_cards_hand.hand):
            # Mira todas las cartas
            for i in range(0, len(self.development_cards_hand.hand)):
                # Si una es un punto de victoria
                if self.development_cards_hand.hand[i].type == DevelopmentCardConstants.VICTORY_POINT:
                    # La juega
                    return self.development_cards_hand.select_card(i)
        return None
    
    def on_having_more_than_7_materials_when_thief_is_called(self):
        # Obtener los materiales actuales en la mano del jugador
        hand_resources = self.hand.resources
        
        # Calcular cuántos materiales exceden los 7 permitidos
        total_excess = sum([
            max(0, hand_resources.cereal - 7),
            max(0, hand_resources.mineral - 7),
            max(0, hand_resources.clay - 7),
            max(0, hand_resources.wood - 7),
            max(0, hand_resources.wool - 7)
        ])
        
        if total_excess <= 0:
            # No hay materiales para descartar, retornar la mano original
            return self.hand

        # Preparar lista para almacenar los materiales a descartar
        materials_to_discard = Materials(
            cereal=max(0, hand_resources.cereal - 7),
            mineral=max(0, hand_resources.mineral - 7),
            clay=max(0, hand_resources.clay - 7),
            wood=max(0, hand_resources.wood - 7),
            wool=max(0, hand_resources.wool - 7)
        )

        if hand_resources.has_more('city'):
            # Priorizar los descartes necesarios para construir una ciudad
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
        else:
            # Descartar de manera aleatoria cartas de su mano
            while self.hand.get_total() > 7:
                # Obtener los índices de las cartas disponibles en la mano
                available_indices = [idx for idx, count in enumerate(self.hand.resources) if count > 0]
                
                if not available_indices:
                    break
                
                # Elegir aleatoriamente un índice de la lista de disponibles
                idx_to_discard = random.choice(available_indices)
                
                # Descartar una unidad de ese tipo de carta
                self.hand.remove_material(idx_to_discard, 1)

        # Devolver la mano actualizada después de descartar
        return self.hand
    
    def on_moving_thief(self):
        # Bloquea un número 6 u 8 donde no tenga un pueblo, pero que tenga uno del rival
        # Si no se dan las condiciones lo deja donde está, lo que hace que el GameManager lo ponga en un lugar aleatorio
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
    
    def on_monopoly_card_use(self):
        # Obtener los recursos actuales del jugador
        hand_resources = self.hand.resources

        # Determinar qué recurso tiene más cantidad actualmente
        max_resource = max(hand_resources, key=lambda k: hand_resources[k])

        # Devolver el ID del recurso más abundante
        return max_resource
    
    def on_road_building_card_use(self):
        # Elige dos carreteras aleatorias entre las opciones
        valid_nodes = self.board.valid_road_nodes(self.id)
        # Se supone que solo se ha usado la carta si hay más de 2 carreteras disponibles a construir,
        # pero se dejan por si acaso
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
        # Inicializar los materiales a elegir
        chosen_materials = {'material': None, 'material_2': None}

        # Evaluar cuáles son los materiales más necesarios para el jugador
        needed_materials = {
            MaterialConstants.CEREAL: 2 - self.hand.resources.cereal,
            MaterialConstants.MINERAL: 3 - self.hand.resources.mineral,
            MaterialConstants.CLAY: 1 - self.hand.resources.clay,
            MaterialConstants.WOOD: 1 - self.hand.resources.wood,
            MaterialConstants.WOOL: 1 - self.hand.resources.wool
        }

        # Ordenar los materiales por la cantidad necesaria en orden ascendente
        sorted_needed_materials = sorted(needed_materials.items(), key=lambda x: x[1])

        # Elegir los dos materiales más necesarios disponibles
        chosen_materials['material'] = sorted_needed_materials[0][0]
        chosen_materials['material_2'] = sorted_needed_materials[1][0]

        return chosen_materials