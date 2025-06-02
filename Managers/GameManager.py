from copy import copy
from Classes.Board import Board
from Classes.Constants import *
from Classes.DevelopmentCards import *
from Classes.TradeOffer import TradeOffer
from Classes.Hand import *
from Managers.AgentManager import AgentManager
from Managers.CommerceManager import CommerceManager
from Managers.TurnManager import TurnManager
import json


class GameManager:
    """
    Clase que representa el game manager, entidad que tiene todas las acciones que pueden hacer los jugadores
    """
    MAX_COMMERCE_DEPTH = 2
    MAX_COMMERCE_TRADES = 2

    def __init__(self, for_test=False, agents=None, game_file_path=None):
        self.already_played_development_card = False
        self.last_dice_roll = 0
        self.largest_army = 2
        self.largest_army_player = {}
        self.longest_road = {'longest_road': 4, 'player': -1}

        if game_file_path:
            # Si se proporciona un archivo de juego, cargarlo.
            # Primero inicializamos los managers básicos que load_game_from_json podría necesitar indirectamente
            # o para evitar errores si la carga falla parcialmente y luego se intenta acceder a ellos.
            self.turn_manager = TurnManager()
            self.commerce_manager = CommerceManager()
            self.agent_manager = AgentManager(for_test, agents=agents)
            self.development_cards_deck = DevelopmentDeck() # El mazo se podría restaurar también desde el JSON
            self.load_game_from_json(game_file_path)
            # Es importante que load_game_from_json actualice self.board y otros estados.
        else:
            # Si no se proporciona un archivo, inicializar un juego nuevo por defecto.
            self.board = Board()
            self.development_cards_deck = DevelopmentDeck()
            self.turn_manager = TurnManager()
            self.commerce_manager = CommerceManager()
            self.agent_manager = AgentManager(for_test, agents=agents)
        return

    def load_game_from_json(self, file_path):
        """
        Carga el estado del juego desde un archivo JSON.
        Esto incluye el estado del tablero (nodos y terrenos),
        las manos de los jugadores, cartas de desarrollo, etc.

        :param file_path: Ruta al archivo JSON que contiene el estado del juego.
        :return: None
        """
        try:
            with open(file_path, 'r') as f:
                game_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: El archivo {file_path} no fue encontrado.")
            # Considera lanzar una excepción o manejar el error de otra forma.
            return
        except json.JSONDecodeError:
            print(f"Error: El archivo {file_path} no contiene un JSON válido.")
            # Considera lanzar una excepción o manejar el error de otra forma.
            return

        # Cargar el estado del tablero
        # Basado en la estructura de game_1.json: game_data -> setup -> board -> board_nodes/board_terrain
        if 'setup' in game_data and 'board' in game_data['setup']:
            board_data = game_data['setup']['board']
            if 'board_nodes' in board_data and 'board_terrain' in board_data:
                self.board = Board(nodes=board_data['board_nodes'], terrain=board_data['board_terrain'])
                print("Tablero cargado desde JSON.")
            else:
                print("Advertencia: Faltan 'board_nodes' o 'board_terrain' en los datos del tablero del JSON. Se usará un tablero por defecto.")
                self.board = Board() # Fallback a tablero por defecto si los datos no son completos
        else:
            print("Advertencia: No se encontró la estructura 'setup.board' en el JSON. Se usará un tablero por defecto.")
            self.board = Board() # Fallback a tablero por defecto

        # TODO: Cargar otros estados del juego desde game_data
        # Por ejemplo:
        # - Manos de los jugadores (self.agent_manager.players[X]['resources'])
        # - Cartas de desarrollo (self.development_cards_deck, self.agent_manager.players[X]['development_cards'])
        # - Turno actual (self.turn_manager)
        # - Largest army, longest road, etc.
        # Esta parte es crucial para una restauración completa del juego.

        print(f"Partida cargada desde {file_path}")

    def reset_game_values(self):
        """
        Reinicia las variables al valor inicial
        :return: None
        """
        self.already_played_development_card = False
        self.last_dice_roll = 0
        self.largest_army = 2
        self.largest_army_player = {}
        self.longest_road = {'longest_road': 4, 'player': -1}

        self.board = Board()
        self.development_cards_deck = DevelopmentDeck()
        self.turn_manager = TurnManager()
        self.agent_manager.reset_game_values()
        return

    def throw_dice(self):
        """
        Función que devuelve un valor entre el 2 y el 12, simulando una tirada de 2d6
        :return: integer entre 2 y 12
        """
        first_d6 = random.randint(1, 6)
        second_d6 = random.randint(1, 6)
        self.last_dice_roll = first_d6 + second_d6
        return

    def give_resources(self):
        """
        Función que entrega materiales a cada uno de los jugadores en función de la tirada de dados
        :return: None
        """
        # Por cada pieza de terreno en el tablero
        for terrain in self.board.terrain:
            # Si la probabilidad coincide
            if terrain['probability'] == self.last_dice_roll:
                # Se miran los nodos adyacentes
                for node in terrain['contacting_nodes']:
                    # Si tiene jugador, implica que hay pueblo
                    if self.board.nodes[node]['player'] != -1:
                        player = self.agent_manager.players[self.board.nodes[node]['player']]
                        # Si tiene ciudad se dan 2 en lugar de 1 material

                        if self.board.nodes[node]['has_city']:
                            player['player'].hand.add_material(terrain['terrain_type'], 2)
                            player['resources'].add_material(terrain['terrain_type'], 2)
                        else:
                            player['player'].hand.add_material(terrain['terrain_type'], 1)
                            player['resources'].add_material(terrain['terrain_type'], 1)
        return

    def _give_all_resources(self):
        """
        Función que otorga a todos los jugadores 5 de todos los recursos. Usado solo para debugging
        :return: None
        """
        for player in self.agent_manager.players:
            player['resources'].add_material(MaterialConstants.CEREAL, 5)
            player['resources'].add_material(MaterialConstants.MINERAL, 5)
            player['resources'].add_material(MaterialConstants.CLAY, 5)
            player['resources'].add_material(MaterialConstants.WOOD, 5)
            player['resources'].add_material(MaterialConstants.WOOL, 5)
            player['player'].hand = player['resources']

        return

    def send_trade_to_everyone(self, trade_offer=TradeOffer()):
        """
        Permite enviar una oferta a todos los jugadores en la mesa. Si alguno acepta se hará el intercambio
        :param trade_offer: Oferta de comercio con el jugador, debe incluir qué se entrega y qué se recibe
        :return: array [...dict {}]
        """
        answer_object = []

        receivers = self.agent_manager.players.copy()
        giver = receivers.pop(self.turn_manager.whose_turn_is_it)

        # Se aleatorizan el orden en el que se va a recibir la oferta para evitar que J1 tenga ventaja
        random.shuffle(receivers)

        original_trade_offer = trade_offer

        for receiver in receivers:
            on_tradeoffer_response = []
            trade_offer = original_trade_offer

            count = 1
            offer = True
            while offer:
                # Se hace un bucle de contraofertas hasta que se llegue a una decisión de True o False
                if count % 2 == 0:
                    # Giver toma el papel de receiver porque es una contraoferta
                    response_obj = self._on_tradeoffer_response(giver, receiver, count, trade_offer)
                else:
                    response_obj = self._on_tradeoffer_response(receiver, giver, count, trade_offer)

                if isinstance(response_obj["response"], TradeOffer):
                    trade_offer = response_obj['response']
                    response_obj['response'] = True
                    on_tradeoffer_response.append(response_obj)
                    count += 1
                else:
                    on_tradeoffer_response.append(response_obj)
                    offer = False
            if on_tradeoffer_response[(len(on_tradeoffer_response) - 1)]['response']:
                if count % 2 == 0:
                    done = self._trade_with_player(trade_offer, giver, receiver)
                else:
                    done = self._trade_with_player(trade_offer, receiver, giver)

                if done:
                    on_tradeoffer_response[(len(on_tradeoffer_response) - 1)]['completed'] = True
                    answer_object.append(on_tradeoffer_response)

                    return answer_object

            on_tradeoffer_response[(len(on_tradeoffer_response) - 1)]['completed'] = False
            answer_object.append(on_tradeoffer_response)
        return answer_object

    def _on_tradeoffer_response(self, receiver, giver, count, trade_offer):
        """
        Función llamada cuando llega una oferta de comercio como respuesta a una oferta de comercio
        :param giver: Player()
        :param receiver: Player()
        :param count: Int
        :param trade_offer: TradeOffer()
        :return json_obj: Objeto json al que se le añaden datos para poder exportarlo correctamente
        :return: json_obj {'count': int, 'giver': Player(), 'receiver': Player(),
                             'trade_offer': TradeOffer(), 'response': True/False}
        """
        json_obj = {
            'count': count,
            'trade_offer': trade_offer.__to_object__(),
            'giver': giver['id'],
            'receiver': receiver['id'],
        }
        response = receiver['player'].on_trade_offer(copy(self.board), trade_offer, giver['id'])

        if count > self.MAX_COMMERCE_DEPTH:
            json_obj['response'] = False
        else:
            json_obj['response'] = response
        return json_obj

    def _trade_with_player(self, trade_offer=None, giver=None, receiver=None):
        """
        Función que hace el intercambio entre dos jugadores.
        :param trade_offer: (TradeOffer()) El intercambio que se va a hacer.
        :param giver: ({AgentInterface(), Hand(), int, DevelopmentCardHand()}) El jugador que da materiales.
        :param receiver: ({AgentInterface(), Hand(), int, DevelopmentCardHand()}) El jugador que recibe materiales.
        :return: bool
        """
        if trade_offer is None or giver is None or receiver is None:
            return False

        # Si receiver o giver no tiene materiales se le ignora
        if (receiver['resources'].resources.has_more(trade_offer.receives) and
                giver['resources'].resources.has_more(trade_offer.gives)):

            materials = ['cereal', 'mineral', 'clay', 'wood', 'wool']

            for i in range(len(materials)):
                material_quantity = getattr(trade_offer.gives, materials[i])
                giver['resources'].remove_material(i, material_quantity)  # Se resta lo que giver entrega
                receiver['resources'].add_material(i, material_quantity)  # Se añade lo que receiver recibe del giver

                material_quantity = getattr(trade_offer.receives, materials[i])
                receiver['resources'].remove_material(i, material_quantity)  # Se resta lo que receiver entrega
                giver['resources'].add_material(i, material_quantity)  # Se añade lo que giver recibe del receiver

            giver['player'].hand = giver['resources']
            receiver['player'].hand = receiver['resources']

            return True
        else:
            return False

    # -- -- -- --  Board functions  -- -- -- --
    def build_town(self, player_id, node):
        """
        Permite construir un pueblo en el nodo seleccionado.
        :param player_id: (int) Número que representa al jugador.
        :param node: (Tree()) Número que representa un nodo en el tablero.
        :return: {bool, string}. Devuelve si se ha podido o no construir el poblado, y en caso negativo, la razón.
        """
        if self.agent_manager.players[player_id]['resources'].resources.has_more('town'):
            build_town_obj = self.board.build_town(player_id, node)

            if build_town_obj['response']:
                self.agent_manager.players[player_id]['resources'].remove_material([MaterialConstants.CEREAL,
                                                                                    MaterialConstants.CLAY,
                                                                                    MaterialConstants.WOOD,
                                                                                    MaterialConstants.WOOL
                                                                                    ], 1)
                self.agent_manager.players[player_id]['player'].hand = self.agent_manager.players[player_id]['resources']

            return build_town_obj
        else:
            return {'response': False, 'error_msg': 'Falta de materiales'}

    def build_city(self, player_id, node):
        """
        Permite construir una ciudad en el nodo seleccionado.
        :param player_id: (int) Número que representa al jugador.
        :param node: (Tree()) Número que representa un nodo en el tablero.
        :return: {bool, string}. Devuelve si se ha podido o no construir la ciudad, y en caso negativo, la razón.
        """
        if self.agent_manager.players[player_id]['resources'].resources.has_more('city'):
            build_city_obj = self.board.build_city(player_id, node)

            if build_city_obj['response']:
                self.agent_manager.players[player_id]['resources'].remove_material(MaterialConstants.CEREAL, 2)
                self.agent_manager.players[player_id]['resources'].remove_material(MaterialConstants.MINERAL, 3)

                self.agent_manager.players[player_id]['player'].hand = self.agent_manager.players[player_id]['resources']

            return build_city_obj
        else:
            return {'response': False, 'error_msg': 'Falta de materiales'}

    def build_road(self, player_id, node, road, free=False):
        """
        Permite construir una carretera en el camino seleccionado.
        :param player_id: (int) Número que representa al jugador.
        :param node: (Tree()) Número que representa.
        :param road: (Tree()) Número que representa una carretera en el tablero.
        :param free: (bool) Usado solo para cuando construyes carreteras gratis con una carta de desarrollo.
        :return: {bool, string}. Devuelve si se ha podido o no construir la carretera, y en caso negativo, la razón.
        """
        if self.agent_manager.players[player_id]['resources'].resources.has_more('road') or free:
            build_road_obj = self.board.build_road(player_id, node, road)

            if build_road_obj['response'] and not free:
                self.agent_manager.players[player_id]['resources'].remove_material([MaterialConstants.CLAY,
                                                                                    MaterialConstants.WOOD
                                                                                    ], 1)
                self.agent_manager.players[player_id]['player'].hand = self.agent_manager.players[player_id]['resources']

            return build_road_obj
        else:
            return {'response': False, 'error_msg': 'Falta de materiales'}

    def build_development_card(self, player_id):
        """
        Permite construir una carta de desarrollo.
        :param player_id: (int) Número que representa al jugador.
        :return: {bool, string, string, string}. Devuelve si se ha podido o no construir la carta de desarrollo,
                                                 el ID de la carta, el tipo de carta que es, el efecto de la carta
                                                 y si no se ha podido hacer, la razón.
        """
        card_drawn = self.development_cards_deck.draw_card()
        if card_drawn is not None:

            if self.agent_manager.players[player_id]['resources'].resources.has_more('card'):
                self.agent_manager.players[player_id]['resources'].remove_material([MaterialConstants.CEREAL,
                                                                                    MaterialConstants.MINERAL,
                                                                                    MaterialConstants.WOOL
                                                                                    ], 1)
                self.agent_manager.players[player_id]['player'].hand = self.agent_manager.players[player_id]['resources']

                if card_drawn.type == DevelopmentCardConstants.VICTORY_POINT:
                    self.agent_manager.players[player_id]['hidden_victory_points'] += 1

                self.agent_manager.players[player_id]['development_cards'].add_card(card_drawn)
                self.agent_manager.players[player_id]['player'].development_cards_hand.hand = \
                    self.agent_manager.players[player_id]['development_cards'].hand

                return {'response': True, 'card_type': card_drawn.type,
                        'card_effect': card_drawn.effect}
            else:
                return {'response': False, 'error_msg': 'Falta de materiales'}
        else:
            return {'response': False, 'error_msg': 'No hay más cartas que crear'}

    def move_thief(self, terrain, adjacent_player):
        """
        Permite mover al ladrón a la casilla de terreno seleccionada y en caso de que haya un poblado o ciudad de otro
        jugador adyacente a dicha casilla permite robarle un material aleatorio de la mano.
        :param terrain: Número que representa un hexágono en el tablero
        :param adjacent_player: Número de un jugador que esté adyacente al hexágono seleccionado
        :return: None
        """
        move_thief_obj = self.board.move_thief(terrain)
        move_thief_obj['robbed_player'] = -1
        move_thief_obj['stolen_material_id'] = -1
        if move_thief_obj['response']:
            if adjacent_player != -1:
                for node in self.board.terrain[move_thief_obj['terrain_id']]['contacting_nodes']:
                    if self.board.nodes[node]['player'] == adjacent_player:
                        move_thief_obj['stolen_material_id'] = self._steal_from_player(adjacent_player)
                        move_thief_obj['robbed_player'] = adjacent_player
                        break
            else:
                move_thief_obj['error_msg'] = 'No se ha podido robar a otro jugador ya que no hay ninguno'
        return move_thief_obj

    def _steal_from_player(self, player):
        """
        Función que permite robar de manera aleatoria un material de la mano de un jugador.
        :param player: Número que representa al jugador a robar
        :return: int
        """
        player_obj = self.agent_manager.players[player]
        actual_player_obj = self.agent_manager.players[self.agent_manager.actual_player]

        material_id = -1
        total = player_obj["resources"].get_total()
        new_total = player_obj["resources"].get_total()

        while new_total == total and total != 0:
            material_id = random.randint(0, 4)
            player_obj['resources'].remove_material(material_id, 1)
            new_total = player_obj['resources'].get_total()

        actual_player_obj['resources'].add_material(material_id, 1)

        player_obj['player'].hand = player_obj['resources']
        actual_player_obj['player'].hand = actual_player_obj['resources']
        return material_id

    def on_game_start_build_towns_and_roads(self, player):
        """
        Función que te permite poner un pueblo y una carretera. Te las pone automáticamente si no pones un nodo válido
        :param player: contador externo que indica a qué jugador le toca
        :return: node_id, road_to
        """
        # Le da a los agentes 2 intentos de poner bien los pueblos y carreteras. Si no, el GameManager lo hará por ellos.
        valid_nodes = self.board.valid_starting_nodes()
        materials = []

        for count in range(3):
            try:
                node_id, road_to = self.agent_manager.players[player]['player'].on_game_start(copy(self.board))
            except Exception as e:
                print(f"Error: {e}. Agente: {self.agent_manager.players[player]['player']}")
                node_id, road_to = None, None

            if node_id in valid_nodes or count == 2:

                if count == 2:
                    if not valid_nodes:
                        raise Exception("No hay nodos válidos disponibles para iniciar el juego")
                    else:
                        node_id = random.choice(valid_nodes)

                    possible_roads = self.board.nodes[node_id]['adjacent']
                    road_to = random.choice(possible_roads)


                terrain_ids = self.board.nodes[node_id]['contacting_terrain']
                for ter_id in terrain_ids:
                    materials.append(self.board.terrain[ter_id]['terrain_type'])

                self.board.nodes[node_id]['player'] = player

                # Se le dan materiales al AgentManager y este a los agentes para que sepan cuantos tienen en realidad
                self.agent_manager.players[player]['resources'].add_material(materials, 1)
                self.agent_manager.players[player]['player'].hand = self.agent_manager.players[player]['resources']

                self.agent_manager.players[player]['victory_points'] += 1

                # Parte carreteras
                if self.board.build_road(player, node_id, road_to)['response']:
                    return node_id, road_to
                else:
                    possible_roads = self.board.nodes[node_id]['adjacent']
                    road_to = random.choice(possible_roads) 
                    self.board.build_road(player, node_id, road_to)
                    return node_id, road_to

    def longest_road_calculator(self, node, depth, longest_road_obj, player_id, visited_nodes):
        """
        Función que calcula la carretera más larga a partir de un nodo
        :param node:
        :param depth:
        :param longest_road_obj:
        :param player_id:
        :param visited_nodes:
        :return: {'longest_road': int, 'player': int}
        """
        for road in node['roads']:
            if ((road['node_id'] not in visited_nodes) and (road['player_id'] == player_id or player_id == -1) and
                    (road['player_id'] == node['player'] or node['player'] == -1)):
                visited_nodes.append(road['node_id'])

                if depth > longest_road_obj['longest_road']:
                    longest_road_obj['longest_road'] = depth
                    longest_road_obj['player'] = player_id

                longest_road_obj = self.longest_road_calculator(self.board.nodes[road['node_id']], depth + 1,
                                                                longest_road_obj, road['player_id'], visited_nodes)
        return {'longest_road': longest_road_obj['longest_road'], 'player': longest_road_obj['player']}

    def play_development_card(self, player_id, card, winner):
        """Si la carta que llega existe en la mano del AgentManager se elimina y se hace el efecto, si no, se hace
        un return nulo. Si la carta es un punto de victoria no se borra de la mano.
        Después se iguala la mano del jugador a la del AgentManager para evitar trampas.
        :param player_id:
        :param card:
        :param winner: bool
        :return: {'id': int, 'type': string, 'effect': int}, bool
        """
        card_obj = {}

        if card in self.agent_manager.players[player_id]['development_cards'].hand:
            if card.type != DevelopmentCardConstants.VICTORY_POINT:
                self.agent_manager.players[player_id]['development_cards'].delete_card(card)  # Borramos la carta

                self.agent_manager.players[player_id]['player'].development_cards_hand.hand = \
                    self.agent_manager.players[player_id]['development_cards'].hand

        else:
            self.agent_manager.players[player_id]['player'].development_cards_hand.hand = \
                self.agent_manager.players[player_id]['development_cards'].hand  # Hacen trampas

            card_obj['played_card'] = 'none'
            card_obj['reason'] = 'Trying to use cards they don\'t have'

            return card_obj, winner

        if card.type == DevelopmentCardConstants.KNIGHT:
            # se le suma un nuevo caballero al jugador y se le pide mover al ladrón
            self.agent_manager.players[player_id]['knights'] += 1

            if self.agent_manager.players[player_id]['knights'] > self.largest_army:
                if self.largest_army_player == {}:
                    # Definimos el nuevo poseedor con el ejército más grande
                    self.largest_army_player = self.agent_manager.players[player_id]
                    self.largest_army_player['largest_army'] = 1
                    self.largest_army_player['victory_points'] += 2
                else:
                    # Le quitamos los beneficios al anterior poseedor del ejército grande
                    self.largest_army_player['largest_army'] = 0
                    self.largest_army_player['victory_points'] -= 2

                    # Definimos el nuevo poseedor con el ejército más grande
                    self.largest_army_player = self.agent_manager.players[player_id]
                    self.largest_army_player['largest_army'] = 1
                    self.largest_army_player['victory_points'] += 2

            on_moving_thief = self.agent_manager.players[player_id]['player'].on_moving_thief()
            move_thief_obj = self.move_thief(on_moving_thief['terrain'], on_moving_thief['player'])

            # se pasan los cambios al objeto
            card_obj['played_card'] = 'knight'
            card_obj['total_knights'] = self.agent_manager.players[player_id]['knights']
            card_obj['past_thief_terrain'] = move_thief_obj['last_thief_terrain']
            card_obj['thief_terrain'] = move_thief_obj['terrain_id']
            card_obj['robbed_player'] = move_thief_obj['robbed_player']
            card_obj['stolen_material_id'] = move_thief_obj['stolen_material_id']

            self.already_played_development_card = True
            return card_obj, winner

        elif card.type == DevelopmentCardConstants.VICTORY_POINT:
            # Si tienen suficientes puntos de victoria para ganar. Ganan automáticamente, si no, no pasa nada

            if (self.agent_manager.players[player_id]['victory_points'] +
                self.agent_manager.players[player_id]['hidden_victory_points']) >= 10:

                card_obj['played_card'] = 'victory_point'
                self.agent_manager.players[player_id]['victory_points'] = 10
                winner = True

                self.already_played_development_card = True
                return card_obj, winner
            else:
                card_obj['played_card'] = 'failed_victory_point'

            return card_obj, winner

        elif card.type == DevelopmentCardConstants.PROGRESS_CARD:

            if card.effect == DevelopmentCardConstants.MONOPOLY_EFFECT:
                # Elige material
                material_chosen = self.agent_manager.players[player_id]['player'].on_monopoly_card_use()
                material_sum = 0

                if material_chosen is None:
                    material_chosen = random.randint(0, 4)

                # Se elimina el material de la mano de todos los jugadores
                for player in self.agent_manager.players:
                    material_sum += player['resources'].get_from_id(material_chosen)
                    player['resources'].remove_material(material_chosen,
                                                        player['resources'].get_from_id(material_chosen))
                    player['player'].hand = player['resources']

                # Se le dan todos los materiales eliminados al que usó la carta
                self.agent_manager.players[player_id]['resources'].add_material(material_chosen, material_sum)
                self.agent_manager.players[player_id]['player'].hand = self.agent_manager.players[player_id]['resources']

                # Se añade al objeto el material, la suma, y las nuevas manos tras la resta de materiales
                card_obj['played_card'] = 'monopoly'
                card_obj['material_chosen'] = material_chosen
                card_obj['material_sum'] = material_sum
                for i in range(4):
                    card_obj['hand_P' + str(i)] = self.agent_manager.players[i]['resources'].resources.__to_object__()

                self.already_played_development_card = True
                return card_obj, winner

            elif card.effect == DevelopmentCardConstants.ROAD_BUILDING_EFFECT:

                # Se piden en qué puntos quieren construir carreteras
                road_nodes = self.agent_manager.players[player_id]['player'].on_road_building_card_use()
                card_obj['played_card'] = 'road_building'

                # Si hay al menos una carretera
                if road_nodes is not None:
                    built = {'response': False}
                    # Si existe una segunda carretera
                    if road_nodes['node_id_2'] is not None:
                        built_2 = {'response': False}
                    else:
                        built_2 = {'response': True}

                    # Mientras no estén construidas las carreteras se vuelve a intentar
                    while not built['response'] and not built_2['response']:
                        # Si ya está construida se ignora
                        if not built['response']:
                            built = self.build_road(player_id, road_nodes['node_id'], road_nodes['road_to'], free=True)
                        if not built_2['response']:
                            built_2 = self.build_road(player_id, road_nodes['node_id_2'], road_nodes['road_to_2'],
                                                      free=True)

                        if isinstance(built, dict):
                            if built['response']:
                                card_obj['valid_road_1'] = True
                            else:
                                card_obj['valid_road_1'] = False

                                # Si no se ha podido construir se cambia de carretera a una aleatoria posible
                                valid_nodes = self.board.valid_road_nodes(player_id)
                                if len(valid_nodes):
                                    road_node = random.choice(valid_nodes) 
                                    road_nodes['node_id'] = valid_nodes[road_node]['starting_node']
                                    road_nodes['road_to'] = valid_nodes[road_node]['finishing_node']
                                else:
                                    # Si no hay más carreteras posibles se rompe el bucle
                                    card_obj['error_msg'] = 'No hay más nodos válidos para construir una carretera'
                                    break

                        if isinstance(built_2, dict):
                            if built['response']:
                                card_obj['valid_road_2'] = True
                            else:
                                card_obj['valid_road_2'] = False

                                valid_nodes = self.board.valid_road_nodes(player_id)
                                if len(valid_nodes):
                                    road_node = random.choice(valid_nodes) 
                                    road_nodes['node_id_2'] = valid_nodes[road_node]['starting_node']
                                    road_nodes['road_to_2'] = valid_nodes[road_node]['finishing_node']
                                else:
                                    card_obj['error_msg'] = 'No hay más nodos válidos para construir una carretera'
                                    break

                    # Después del bucle ponemos donde se han construido las carreteras y devolvemos el objeto
                    card_obj['roads'] = road_nodes

                    self.already_played_development_card = True
                    return card_obj, winner
                else:
                    # Si el objeto carreteras es None implica que no hay carreteras construidas
                    card_obj['roads'] = None

                    self.already_played_development_card = True
                    return card_obj, winner

            elif card.effect == DevelopmentCardConstants.YEAR_OF_PLENTY_EFFECT:
                card_obj['played_card'] = 'year_of_plenty'

                # Eligen 2 materiales (puede ser el mismo 2 veces)
                materials_selected = self.agent_manager.players[player_id]['player'].on_year_of_plenty_card_use()
                card_obj['materials_selected'] = materials_selected

                if materials_selected is None:
                    material, material2 = random.randint(0, 4), random.randint(0, 4)
                    materials_selected = {'material': material, 'material_2': material2}

                # Obtienen una carta de ese material elegido
                self.agent_manager.players[player_id]['resources'].add_material(materials_selected['material'], 1)
                self.agent_manager.players[player_id]['resources'].add_material(materials_selected['material_2'], 1)

                # Se actualiza la mano
                self.agent_manager.players[player_id]['player'].hand = self.agent_manager.players[player_id]['resources']

                card_obj['hand_P' + str(player_id)] = self.agent_manager.players[
                    player_id]['resources'].resources.__to_object__()

                self.already_played_development_card = True
                return card_obj, winner

        return card_obj, winner

    def check_player_hands(self):
        for i in range(4):
            print('P' + str(i + 1))
            print(self.agent_manager.players[i]['development_cards'].hand)

        print('Players: ')
        for i in range(4):
            print('P' + str(i + 1))
            print(self.agent_manager.players[i]['player'].development_cards_hand.hand)

    def get_turn(self):
        """
        :return: int
        """
        return self.turn_manager.turn

    def set_turn(self, turn=0):
        """
        :param turn: int
        :return: None
        """
        self.turn_manager.set_turn(turn)
        return

    def get_whose_turn_is_it(self):
        """
        :return: int
        """
        return self.turn_manager.whose_turn_is_it

    def set_whose_turn_is_it(self, turn=0):
        """
        :param turn: int
        :return: None
        """
        self.turn_manager.set_whose_turn_is_it(turn)
        return

    def set_phase(self, phase=0):
        """
        :param phase: int
        :return: None
        """
        self.turn_manager.set_phase(phase)
        return

    def get_round(self):
        """
        :return: int
        """
        return self.turn_manager.round

    def set_round(self, round=0):
        """
        :param round: int
        :return: NOne
        """
        self.turn_manager.set_round(round)
        return

    def get_players(self):
        """
        :return: list
        """
        return self.agent_manager.players

    def set_actual_player(self, player_id=0):
        """
        :param player_id: int
        :return: None
        """
        self.turn_manager.actual_player = player_id
        return

    def get_last_dice_roll(self):
        """
        :return: int
        """
        return self.last_dice_roll

    def set_longest_road(self, new_longest_road):
        """
        :param new_longest_road: dict
        :return: None
        """
        self.longest_road = new_longest_road
        return

    def get_longest_road(self):
        """
        :return: dict
        """
        return self.longest_road

    def player_resources_total(self, player_id):
        """
        :return: int
        """
        return self.agent_manager.players[player_id]['resources'].get_total()

    def player_resources_to_object(self, player_id):
        """
        :return: dict
        """
        return self.agent_manager.players[player_id]['resources'].resources.__to_object__()

    def call_to_agent_on_turn_start(self, player):
        """
        :param player: int
        :return: DevelopmentCard, None
        """
        return self.agent_manager.players[player]['player'].on_turn_start()

    def call_to_agent_on_turn_end(self, player_id):
        """
        :param player_id: int
        :return: DevelopmentCard, None
        """
        return self.agent_manager.players[player_id]['player'].on_turn_end()

    def call_to_agent_on_commerce_phase(self, player_id):
        """
        :param player_id: int
        :return: TradeOffer, dict{'gives': int, 'receives': int}, None
        """
        return self.agent_manager.players[player_id]['player'].on_commerce_phase()

    def call_to_agent_on_build_phase(self, player_id):
        """
        :param player_id: int
        :return: dict{'building': str, 'node_id': int, 'road_to': int/None}, None
        """
        return self.agent_manager.players[player_id]['player'].on_build_phase(copy(self.board))

    def get_board_nodes(self):
        """
        :return: nodes
        """
        return self.board.nodes

    def get_board_terrain(self):
        """
        :return: terrain
        """
        return self.board.terrain

    def get_card_used(self):
        """
        :return: bool
        """
        return self.already_played_development_card

    def set_card_used(self, used):
        """
        :param used: bool
        :return: None
        """
        self.already_played_development_card = used
        return

    def check_if_thief_is_called(self, start_turn_object, player_id=0):
        """
        :param player_id: int
        :param start_turn_object: dict
        :return: start_turn_object, dict
        """
        if self.last_dice_roll == 7:
            for obj in self.agent_manager.players:
                if obj['resources'].get_total() > 7:
                    total = obj['player'].on_having_more_than_7_materials_when_thief_is_called().get_total()
                    max_hand = math.floor(total / 2)

                    while total > max_hand:
                        obj['resources'].remove_material(random.randint(0, 4), 1)
                        total = obj['resources'].get_total()

            on_moving_thief = self.agent_manager.players[player_id]['player'].on_moving_thief()
            move_thief_obj = self.move_thief(on_moving_thief['terrain'], on_moving_thief['player'])

            start_turn_object['past_thief_terrain'] = move_thief_obj['last_thief_terrain']
            start_turn_object['thief_terrain'] = move_thief_obj['terrain_id']
            start_turn_object['robbed_player'] = move_thief_obj['robbed_player']
            start_turn_object['stolen_material_id'] = move_thief_obj['stolen_material_id']
        return start_turn_object

    def on_commerce_response(self, commerce_phase_object, commerce_response, depth, player_id, winner):
        """
        :param commerce_phase_object: dict
        :param commerce_response: TradeOffer(), dict, DevelopmentCard, None
        :param depth: int
        :param player_id: int
        :param winner: bool
        :return: dict
        """
        if isinstance(commerce_response, TradeOffer) and depth <= self.MAX_COMMERCE_TRADES:
            commerce_phase_object['trade_offer'] = commerce_response.__to_object__()
            commerce_phase_object['harbor_trade'] = False

            if self.agent_manager.players[player_id]['resources'].resources.has_more(
                    commerce_response.gives):
                commerce_phase_object['inviable'] = False
                answer_object = self.send_trade_to_everyone(commerce_response)
                commerce_phase_object['answers'] = answer_object
            else:
                commerce_phase_object['inviable'] = True

            return commerce_phase_object, winner

        elif isinstance(commerce_response, dict):

            commerce_phase_object['trade_offer'] = commerce_response
            commerce_phase_object['harbor_trade'] = True

            harbor_type = self.board.check_for_player_harbors(player_id, commerce_response['gives'])

            if harbor_type == HarborConstants.NONE:
                response = self.commerce_manager.trade_without_harbor(
                    self.agent_manager.players[player_id]['resources'], commerce_response['gives'],
                    commerce_response['receives'])
            elif harbor_type == HarborConstants.ALL:
                response = self.commerce_manager.trade_through_harbor(
                    self.agent_manager.players[player_id]['resources'], commerce_response['gives'],
                    commerce_response['receives'])
            else:
                response = self.commerce_manager.trade_through_special_harbor(
                    self.agent_manager.players[player_id]['resources'], commerce_response['gives'],
                    commerce_response['receives'])

            if isinstance(response, Hand):
                self.agent_manager.players[player_id]['resources'] = response
                self.agent_manager.players[player_id]['player'].hand = self.agent_manager.players[player_id]['resources']
                commerce_phase_object['answer'] = response.resources.__to_object__()

                return commerce_phase_object, winner
            else:
                commerce_phase_object['answer'] = response

            return commerce_phase_object, winner

        elif isinstance(commerce_response, DevelopmentCard) and not self.already_played_development_card:
            played_card_obj, winner = self.play_development_card(player_id, commerce_response, winner)
            commerce_phase_object['trade_offer'] = 'played_card'
            commerce_phase_object['harbor_trade'] = False
            commerce_phase_object['development_card_played'] = played_card_obj

            return commerce_phase_object, winner
        else:
            commerce_phase_object['trade_offer'] = 'None'
            return commerce_phase_object, winner

    def build_phase_object(self, build_phase_object, build_response, player_id, winner):
        """
         :param build_phase_object: dict
         :param build_response: dict, DevelopmentCard, None
         :param player_id: int
         :param winner: bool
         :return: dict, bool
         """
        if isinstance(build_response, dict):
            build_phase_object = build_response

            if build_response['building'] == BuildConstants.TOWN:
                built = self.build_town(player_id, build_response['node_id'])

            elif build_response['building'] == BuildConstants.CITY:
                built = self.build_city(player_id, build_response['node_id'])

            elif build_response['building'] == BuildConstants.CARD:
                built = self.build_development_card(player_id)

            elif build_response['building'] == BuildConstants.ROAD:
                built = self.build_road(player_id, build_response['node_id'], build_response['road_to'])

            else:
                build_phase_object['finished'] = False
                build_phase_object['error_msg'] = 'Se intenta constrir algo fuera de las reglas'
                return build_phase_object, winner

            if built['response']:
                if build_response['building'] in [BuildConstants.TOWN, BuildConstants.CITY]:
                    self.agent_manager.players[player_id]['victory_points'] += 1

                if build_response['building'] == BuildConstants.CARD:
                    build_phase_object['card_id'] = built['card_effect']
                    build_phase_object['card_type'] = built['card_type']
                    build_phase_object['card_effect'] = built['card_effect']

                build_phase_object['finished'] = True

                return build_phase_object, winner
            else:
                build_phase_object['finished'] = False
                build_phase_object['error_msg'] = 'Falta de materiales'
                return build_phase_object, winner

        elif isinstance(build_response, DevelopmentCard) and not self.already_played_development_card:
            played_card_obj, winner = self.play_development_card(player_id, build_response, winner)
            build_phase_object['building'] = 'played_card'
            build_phase_object['finished'] = True
            build_phase_object['development_card_played'] = played_card_obj

            return build_phase_object, winner
        else:
            build_phase_object['building'] = 'None'
            return build_phase_object, winner
