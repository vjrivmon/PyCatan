import random

from Classes.Constants import HarborConstants, TerrainConstants, MaterialConstants
from Classes.Utilities import is_even


class Board:
    """
    Clase que representa una instancia del tablero.

    nodes: [{"id": int,
             "adjacent": [int...],
             "harbor": int,
             "roads": [{"player_id": id, "node_id": int}...],
             "has_city": bool,
             "player": int,
             "contacting_terrain": [int...]}] Representa los nodos del tablero. Poseen información de los puertos y
                                              nodos adyacentes

    terrain: [{"id": int,
               "has_thief": bool,
               "probability": int(2,12),
               "terrain_type": int,
               "contacting_nodes": [int...]}]

              Representa una ficha de terreno del tablero. Poseen información de los nodos con
                 los que hacen contacto, si posee al ladrón actualmente y su probabilidad de salir

    La asignación de los ids de nodo y terreno se ha llevado a cabo por filas, de izquierda a derecha y de arriba a abajo.
    """

    def __init__(self, nodes=None, terrain=None):
        # TODO: esto se deberia de poder calcular automaticamente
        self.contacting_nodes = {
            0: [0, 1, 2, 8, 9, 10],
            1: [2, 3, 4, 10, 11, 12],
            2: [4, 5, 6, 12, 13, 14],
            3: [7, 8, 9, 17, 18, 19],
            4: [9, 10, 11, 19, 20, 21],
            5: [11, 12, 13, 21, 22, 23],
            6: [13, 14, 15, 23, 24, 25],
            7: [16, 17, 18, 27, 28, 29],
            8: [18, 19, 20, 29, 30, 31],
            9: [20, 21, 22, 31, 32, 33],
            10: [22, 23, 24, 33, 34, 35],
            11: [24, 25, 26, 35, 36, 37],
            12: [28, 29, 30, 38, 39, 40],
            13: [30, 31, 32, 40, 41, 42],
            14: [32, 33, 34, 42, 43, 44],
            15: [34, 35, 36, 44, 45, 46],
            16: [39, 40, 41, 47, 48, 49],
            17: [41, 42, 43, 49, 50, 51],
            18: [43, 44, 45, 51, 52, 53],
        }

        self.probabilities = {
            0: 11,      1: 12,      2: 9,       3: 4,       4: 6,
            5: 5,       6: 10,      7: 7,       8: 3,       9: 11,
            10: 4,      11: 8,      12: 8,      13: 10,     14: 9,
            15: 3,      16: 5,      17: 2,      18: 6
        }

        self.terrain_types = {
            0: TerrainConstants.WOOD, 1: TerrainConstants.WOOL, 2: TerrainConstants.CEREAL,
            3: TerrainConstants.CLAY, 4: TerrainConstants.MINERAL, 5: TerrainConstants.CLAY,
            6: TerrainConstants.WOOL, 7: TerrainConstants.DESERT, 8: TerrainConstants.WOOD,
            9: TerrainConstants.CEREAL, 10: TerrainConstants.WOOD, 11: TerrainConstants.CEREAL,
            12: TerrainConstants.CLAY, 13: TerrainConstants.WOOL, 14: TerrainConstants.WOOL,
            15: TerrainConstants.MINERAL, 16: TerrainConstants.MINERAL, 17: TerrainConstants.CEREAL,
            18: TerrainConstants.WOOD
        }

        self.harbors = {
            0: HarborConstants.WOOD, 1: HarborConstants.WOOD,
            3: HarborConstants.CEREAL, 4: HarborConstants.CEREAL,
            14: HarborConstants.CLAY, 15: HarborConstants.CLAY,
            28: HarborConstants.MINERAL, 38: HarborConstants.MINERAL,
            50: HarborConstants.WOOL, 51: HarborConstants.WOOL,
            7: HarborConstants.ALL, 17: HarborConstants.ALL, 26: HarborConstants.ALL, 37: HarborConstants.ALL,
            45: HarborConstants.ALL, 46: HarborConstants.ALL, 47: HarborConstants.ALL, 48: HarborConstants.ALL
        }

        if nodes:
            self.nodes = nodes
        else:
            self.nodes = []  # 0 a 53
            for i in range(54):
                self.nodes.append({
                    "id": i,
                    "adjacent": self.__get_adjacent_nodes__(i),
                    "harbor": self.__get_harbors__(i),
                    "roads": [],
                    "has_city": False,
                    "player": -1,
                    "contacting_terrain": self.__get_contacting_terrain__(i),
                })

        if terrain:
            self.terrain = terrain
        else:
            self.terrain = []  # 0 a 18
            for j in range(19):
                probability = self.__get_probability__(j)
                has_thief = probability == 7
                self.terrain.append({
                    "id": j,
                    "has_thief": has_thief,
                    "probability": probability if not has_thief else 0,
                    "terrain_type": self.__get_terrain_type__(j),
                    "contacting_nodes": self.__get_contacting_nodes__(j),
                })



        return

    def visualize_board(self):
        print('Nodos:')
        for node in self.nodes:
            print('ID: ' + str(node['id']))
            print('Adjacent: ' + str(node['adjacent']))
            print('Harbor: ' + str(node['harbor']))
            print('Player: ' + str(node['player']))
            print('Roads: ' + str(node['roads']))
            print('---\n')

        print('Terreno:')
        for terrain in self.terrain:
            print(terrain[m]['id'])
            print(terrain[m]['probability'])
            print(terrain[m]['contacting_nodes'])
            print(terrain[m]['terrain_type'])
            print('---\n')

    def get_board(self):
        return self.__class__()

    def __get_contacting_terrain__(self, node_id):
        """
        Indica todas las piezas de terreno a los que el nodo es adyacente, para por ejemplo repartir materiales
        :param node_id: El ID de la pieza del terreno actual
        :return: [terrain_id, terrain_id, terrain_id, terrain_id, terrain_id, terrain_id]
        """
        contact = [terrain_id for terrain_id, nodes in self.contacting_nodes.items() if node_id in nodes]
        return contact

    def __get_contacting_nodes__(self, terrain_id):
        """
        Indica todos los nodos a los que la casilla "terreno" es adyacente, para como por ejemplo repartir materiales
        :param terrain_id: El ID de la pieza del terreno actual
        :return: [node_id, node_id, node_id, node_id, node_id, node_id]
        """
        return self.contacting_nodes.get(terrain_id, TerrainConstants.DESERT)

    def __get_probability__(self, terrain_id):
        return self.probabilities[terrain_id]

    def __get_terrain_type__(self, terrain_id):
        return self.terrain_types[terrain_id]

    def __get_adjacent_nodes__(self, node_id):
        """
        Función que obtiene los nodos adyacentes de manera automática
        :param node_id: Id del nodo del que se quieren los ID de los nodos adyacentes
        :return: [int, ...]
        """
        adjacent_nodes = []

        if 0 <= node_id < 7:
            if node_id != 0:
                adjacent_nodes.append(node_id - 1)
            if node_id != 6:
                adjacent_nodes.append(node_id + 1)

            if is_even(node_id):
                adjacent_nodes.append(node_id + 8)

        elif 7 <= node_id < 16:
            if node_id != 7:
                adjacent_nodes.append(node_id - 1)
            if node_id != 15:
                adjacent_nodes.append(node_id + 1)

            if is_even(node_id):
                adjacent_nodes.append(node_id - 8)
            else:
                adjacent_nodes.append(node_id + 10)

        elif 16 <= node_id < 27:
            if node_id != 16:
                adjacent_nodes.append(node_id - 1)
            if node_id != 26:
                adjacent_nodes.append(node_id + 1)

            if is_even(node_id):
                adjacent_nodes.append(node_id + 11)
            else:
                adjacent_nodes.append(node_id - 10)

        elif 27 <= node_id < 38:
            if node_id != 27:
                adjacent_nodes.append(node_id - 1)
            if node_id != 37:
                adjacent_nodes.append(node_id + 1)

            if is_even(node_id):
                adjacent_nodes.append(node_id + 10)
            else:
                adjacent_nodes.append(node_id - 11)

        elif 38 <= node_id < 47:
            if node_id != 37:
                adjacent_nodes.append(node_id - 1)
            if node_id != 46:
                adjacent_nodes.append(node_id + 1)

            if is_even(node_id):
                adjacent_nodes.append(node_id - 10)
            else:
                adjacent_nodes.append(node_id + 8)

        elif 47 <= node_id < 54:
            if node_id != 47:
                adjacent_nodes.append(node_id - 1)
            if node_id != 53:
                adjacent_nodes.append(node_id + 1)

            if not is_even(node_id):
                adjacent_nodes.append(node_id - 8)

        return adjacent_nodes

    def __get_harbors__(self, node_id):
        return self.harbors.get(node_id, HarborConstants.NONE)

    def build_town(self, player, node=-1):
        """
        Permite construir un pueblo por el jugador especificado en el cruce escrito
        Cambia la variable nodes para colocar un pueblo en ello
        :param player: Número que representa al jugador
        :param node: Número que representa un nodo en el tablero
        :return: {bool, string}. Devuelve si se ha podido o no construir el poblado, y en caso de no el porqué
        """
        if self.nodes[node]['player'] == -1:
            can_build = False
            for roads in self.nodes[node]['roads']:
                if roads['player_id'] == player:
                    can_build = True

            if not self.adjacent_nodes_dont_have_towns(node):
                return {'response': False, 'error_msg': 'Hay un pueblo o ciudad muy cercano al nodo'}
            if can_build:
                self.nodes[node]['player'] = player
                self.nodes[node]['has_city'] = False
                return {'response': True, 'error_msg': ''}
            else:
                return {'response': False,
                        'error_msg': 'Debes poseer una carretera hasta el nodo para poder construir un pueblo'}
        else:
            return {'response': False, 'error_msg': 'No se puede construir en un nodo que le pertenece a otro jugador'}

    def build_city(self, player, node=-1):
        """
        Permite construir una ciudad por el jugador especificado en el cruce escrito
        Cambia la variable nodes para colocar una ciudad en ello
        :param player: Número que representa al jugador
        :param node: Número que representa un nodo en el tablero
        :return: {bool, string}. Envía si se ha podido construir la ciudad y en caso de no haberse podido el porqué
        """
        if self.nodes[node]['player'] == player:
            if self.nodes[node]['has_city']:
                return {'response': False, 'error_msg': 'Ya hay una ciudad tuya en el nodo'}
            # self.nodes[node]['player'] = player
            self.nodes[node]['has_city'] = True
            return {'response': True, 'error_msg': ''}
        elif self.nodes[node]['player'] == -1:
            return {'response': False, 'error_msg': 'Primero debe construirse un poblado'}
        else:
            return {'response': False, 'error_msg': 'Ya posee el nodo otro jugador'}

    def build_road(self, player, starting_node=-1, finishing_node=-1):
        """
        Permite construir una carretera por el jugador especificado en la carretera especificada
        Cambia la variable roads para colocar una carretera del jugador designado en ella
        :param player: Número que representa al jugador
        :param starting_node: Nodo desde el que se inicia la carretera
        :param finishing_node: Nodo al que llega la carretera. Debe ser adyacente
        :return: {bool, string}. Envía si se ha podido construir la carretera y en caso de no haberse podido el porqué
        """
        can_build = False
        # Comprueba si ya había una carretera puesta que le pertenezca al jugador
        for road in self.nodes[starting_node]['roads']:
            if road['node_id'] == finishing_node:
                # Dejamos de mirar si ya hay una carretera hacia el nodo final
                return {'response': False, 'error_msg': 'Ya hay una carretera aquí'}
            if (road['player_id'] == player and
                    (self.nodes[starting_node]['player'] == -1 or self.nodes[starting_node]['player'] == player)):
                can_build = True

        for road in self.nodes[finishing_node]['roads']:
            if road['node_id'] == starting_node:
                # Dejamos de mirar si ya hay una carretera hacia el nodo final
                return {'response': False, 'error_msg': 'Ya hay una carretera aquí'}
            if road['player_id'] == player:
                can_build = True

        if self.nodes[starting_node]['player'] == player:
            can_build = True

        # Si le pertenece el nodo inicial o tiene una carretera, deja construir
        if can_build:
            self.nodes[starting_node]['roads'].append({'player_id': player, 'node_id': finishing_node})
            self.nodes[finishing_node]['roads'].append({'player_id': player, 'node_id': starting_node})

            return {'response': True, 'error_msg': ''}
        else:
            return {'response': False,
                    'error_msg': 'No puedes hacer una carretera aquí,' +
                                 ' no hay una carretera o nodo adyacente que te pertenezca'}

    def move_thief(self, terrain=-1):
        """
        Permite mover el ladrón a la casilla de terreno especificada
        Cambia la variable terrain para colocar al ladrón en el terreno correspondiente
        :param terrain: Número que representa un hexágono en el tablero
        :return: {bool, string}. Envía si se ha podido move al ladrón y en caso de no haberse podido el porqué
        """
        if self.terrain[terrain]['has_thief']:
            self.terrain[terrain]['has_thief'] = False

            rand_terrain = terrain
            while rand_terrain == terrain:
                rand_terrain = random.randint(0, 18)

            self.terrain[rand_terrain]['has_thief'] = True
            return {'response': False,
                    'error_msg': 'No se puede mover al ladrón a la misma casilla',
                    'terrain_id': rand_terrain,
                    'last_thief_terrain': terrain}
        else:
            # Quitamos el ladrón del terreno que lo posea
            last_terrain_id = -1
            for square in self.terrain:
                if square['has_thief']:
                    square['has_thief'] = False
                    last_terrain_id = square['id']
                    break

            self.terrain[terrain]['has_thief'] = True
            return {'response': True,
                    'error_msg': '',
                    'terrain_id': terrain,
                    'last_thief_terrain': last_terrain_id}

    def adjacent_nodes_dont_have_towns(self, node_id):
        """
        Comprueba si los nodos a una casilla de distancia del node_id tienen pueblo o ciudad
        :param node_id:
        :return: bool
        """
        for adjacent_id in self.nodes[node_id]['adjacent']:
            if self.nodes[adjacent_id]['player'] != -1:
                return False
        return True

    def is_it_a_coastal_node(self, node_id):
        coastal_nodes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 25, 26, 27, 28, 36, 37, 38, 39, 45, 46, 47, 48, 49,
                         50, 51, 52, 53]
        if node_id in coastal_nodes:
            return True
        else:
            return False

    def valid_town_nodes(self, player_id):
        """
        Devuelve un array del ID de los nodos válidos donde el jugador puede poner un pueblo.
        Deberían de no haber ID repetidos
        :param player_id: int
        :return: [int...]
        """
        valid_nodes = []
        for node in self.nodes:
            for road in node['roads']:
                if (road['player_id'] == player_id
                        and self.adjacent_nodes_dont_have_towns(node['id'])
                        and node['player'] == -1
                        and node['id'] not in valid_nodes):
                    valid_nodes.append(node['id'])
        return valid_nodes

    def valid_city_nodes(self, player_id):
        """
        Devuelve un array de las ids de los nodos válidos para convertir pueblos en ciudades
        :param player_id: int
        :return: [int...]
        """
        valid_nodes = []
        for node in self.nodes:
            if node['player'] == player_id and not node['has_city']:
                valid_nodes.append(node['id'])
        return valid_nodes

    def valid_road_nodes(self, player_id):
        """
        Devuelve un array de diccionarios con los nodos iniciales y finales en los que se puede hacer una carretera
        :param player_id:
        :return: [{'starting_node': int, 'finishing_node': int}, ...]
        """
        valid_nodes = []
        # Por cada nodo que existe
        for node in self.nodes:
            # Se comprueban sus nodos adyacentes
            for adjacent_node_id in node['adjacent']:
                # Se crea una variable para ver si se puede construir
                allowed_to_build = False
                # Se comprueba que el nodo ADYACENTE sea del jugador o no tenga jugador antes siquiera de mirar si
                # se puede construir. Si se quiere llegar al pueblo de otro jugador, cuando se esté en ese nodo,
                # al mirar el adyacente verá que puede construir y dejará hacer la carretera.
                # Sin embargo, esto evitará que se pueda atravesar pueblos de otros jugadores.

                # if (node['player'] == player_id or node['player'] == -1) \
                #         and (self.nodes[adjacent_node_id] == player_id or self.nodes[adjacent_node_id] == -1):
                if self.nodes[adjacent_node_id]['player'] == player_id or self.nodes[adjacent_node_id]['player'] == -1:

                    # Por cada carretera que haya en el nodo adyacente
                    for road in self.nodes[adjacent_node_id]['roads']:
                        # Si la carretera no es una carretera de vuelta
                        if road['node_id'] != node['id']:
                            if road['player_id'] == player_id:
                                # En caso de que sea legal Y no sea una carretera de vuelta, se permite construir
                                allowed_to_build = True
                            # En caso de que no sea legal, no se permite construir
                            else:
                                allowed_to_build = False
                        # En caso de haber una carretera de vuelta, independientemente de qué jugador,
                        # se corta inmediatamente y se prohíbe construir
                        else:
                            allowed_to_build = False
                            break
                if allowed_to_build:
                    valid_nodes.append({'starting_node': adjacent_node_id, 'finishing_node': node['id']})

        return valid_nodes

    def valid_starting_nodes(self):
        """
        Devuelve un array con el ID de todos los nodos viables para el posicionamiento inicial.
        No necesita número del jugador porque es cualquier nodo que no tenga un jugador en él y no sea costero
        :return: [int]
        """

        valid_nodes = []
        for node in self.nodes:
            if (node['player'] == -1 and
                    self.adjacent_nodes_dont_have_towns(node['id']) and
                    not self.is_it_a_coastal_node(node['id'])):
                valid_nodes.append(node['id'])

        return valid_nodes

    def check_for_player_harbors(self, player, material_harbor=None):
        """
        Comprueba qué puertos tiene el jugador. Material_harbor sirve para buscar puertos 2:1 de ese tipo
        :param player: int
        :param material_harbor: int/None
        :return: int
        """
        harbor_3_1_nodes = [7, 17, 26, 37, 45, 46, 47, 48]

        if material_harbor == MaterialConstants.CEREAL:
            if self.nodes[3]['player'] == player or self.nodes[4]['player'] == player:
                return HarborConstants.CEREAL
        elif material_harbor == MaterialConstants.MINERAL:
            if self.nodes[28]['player'] == player or self.nodes[38]['player'] == player:
                return HarborConstants.MINERAL
        elif material_harbor == MaterialConstants.CLAY:
            if self.nodes[14]['player'] == player or self.nodes[15]['player'] == player:
                return HarborConstants.CLAY
        elif material_harbor == MaterialConstants.WOOD:
            if self.nodes[0]['player'] == player or self.nodes[1]['player'] == player:
                return HarborConstants.WOOD
        elif material_harbor == MaterialConstants.WOOL:
            if self.nodes[50]['player'] == player or self.nodes[51]['player'] == player:
                return HarborConstants.WOOL

        for node in harbor_3_1_nodes:
            if self.nodes[node]['player'] == player:
                return HarborConstants.ALL

        return HarborConstants.NONE
