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

        self.coastal_nodes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 25, 26, 27, 28, 36, 37, 38, 39, 45, 46, 47, 48, 49, 50, 51, 52, 53]

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

    def __get_adjacent_nodes__(self, node_id): #TODO
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

    def build_town(self, player: int, node: int =-1):
        """
        Construye un pueblo.
        :param player: id del jugador.
        :param node: id del nodo.
        :return: {bool, string}. Devuelve si se ha podido o no construir el poblado, y en caso de no el porqué
        """
        if self.nodes[node]['player'] != -1:
            return {'response': False, 'error_msg': 'No se puede construir en un nodo que le pertenece a otro jugador'}
        
        if not self.empty_adjacent_nodes(node):
            return {'response': False, 'error_msg': 'Hay un pueblo o ciudad muy cercano al nodo'}

        can_build = any([road['player_id'] == player for road in self.nodes[node]['roads']])
        if not can_build:
            return {'response': False, 'error_msg': 'Debes poseer una carretera hasta el nodo para poder construir un pueblo'}
        
        self.nodes[node]['player'] = player
        self.nodes[node]['has_city'] = False
        return {'response': True, 'error_msg': ''}
            
            
    def build_city(self, player, node=-1):
        """
        Permite construir una ciudad por el jugador especificado en el cruce escrito
        Cambia la variable nodes para colocar una ciudad en ello
        :param player: Número que representa al jugador
        :param node: Número que representa un nodo en el tablero
        :return: {bool, string}. Envía si se ha podido construir la ciudad y en caso de no haberse podido el porqué
        """
        if self.nodes[node]['player'] != player:
            return {'response': False, 'error_msg': 'Ya posee el nodo otro jugador'}
        
        if self.nodes[node]['player'] == -1:
            return {'response': False, 'error_msg': 'Primero debe construirse un poblado'}

        if self.nodes[node]['has_city']:
            return {'response': False, 'error_msg': 'Ya hay una ciudad tuya en el nodo'}
        
        self.nodes[node]['has_city'] = True
        return {'response': True, 'error_msg': ''}
            


    def build_road(self, player, start=-1, end=-1):
        """
        Permite construir una carretera por el jugador especificado en la carretera especificada
        Cambia la variable roads para colocar una carretera del jugador designado en ella
        :param player: Número que representa al jugador
        :param start: Nodo desde el que se inicia la carretera
        :param finishing_node: Nodo al que llega la carretera. Debe ser adyacente
        :return: {bool, string}. Envía si se ha podido construir la carretera y en caso de no haberse podido el porqué
        """
        # Comprobamos si ya existe una carretera. Dado que las carreteras se registran en
        # ambas direcciones (como se puede ver al final de la función), solo es necesario
        # comprobar una de las dos direcciones
        already_built = any([road['node_id'] == end for road in self.nodes[start]['roads']])
        if already_built:
            return {'response': False, 'error_msg': 'Ya hay una carretera aquí'}

        # comprobamos si el jugador se puede conectar a la carretera, ya sea mediante otra carretera o
        # una ciudad o pueblo
        conected_road = any([road['player_id'] in [player] for road in self.nodes[start]['roads']])
        player_owns_node = self.nodes[start]['player'] == player
        if not (conected_road or player_owns_node):
            return {'response': False, 'error_msg': 'No puedes hacer una carretera aquí,' +
                        ' no hay una carretera, ciudad o pueblo adyacente que te pertenezca.'}

        self.nodes[start]['roads'].append({'player_id': player, 'node_id': end})
        self.nodes[end]['roads'].append({'player_id': player, 'node_id': start})
        return {'response': True, 'error_msg': ''}
            

    def move_thief(self, terrain_id):
        """
        Permite mover el ladrón a la casilla de terreno especificada
        Cambia la variable terrain para colocar al ladrón en el terreno correspondiente
        :param terrain: Número que representa un hexágono en el tablero
        :return: {bool, string}. Envía si se ha podido move al ladrón y en caso de no haberse podido el porqué
        """
        if self.terrain[terrain_id]['has_thief']: # Yo aqui hacia un raise exception y me quedaba muy agusto
            
            # prupuesta:
            # rand_terrain = random.choice([x for x in range(19) if x != terrain_id])
            # hay que regenerar tests
            rand_terrain = terrain_id 
            while rand_terrain == terrain_id:
                rand_terrain = random.randint(0, 18)

            self.terrain[terrain_id]['has_thief'] = False
            self.terrain[rand_terrain]['has_thief'] = True
            return {'response': False,
                    'error_msg': 'No se puede mover al ladrón a la misma casilla, movido a una casilla aleatoria',
                    'terrain_id': rand_terrain,
                    'last_thief_terrain': terrain_id}
        
        last_terrain = next(filter(lambda square: square['has_thief'], self.terrain)) # buscamos el ladron
        last_terrain['has_thief'] = False # movemos el ladron
        self.terrain[terrain_id]['has_thief'] = True
        return {'response': True,
                'error_msg': '',
                'terrain_id': terrain_id,
                'last_thief_terrain': last_terrain['id']}

    def empty_adjacent_nodes(self, node_id):
        """
        Comprueba si los nodos a una casilla de distancia del node_id tienen pueblo o ciudad
        :param node_id:
        :return: bool
        """
        for adjacent_id in self.nodes[node_id]['adjacent']:
            if self.nodes[adjacent_id]['player'] != -1:
                return False
        return True

    def is_coastal_node(self, node_id):
        return node_id in self.coastal_nodes

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
                if (
                    road['player_id'] == player_id and
                    self.empty_adjacent_nodes(node['id']) and
                    node['player'] == -1 and
                    node['id'] not in valid_nodes
                ):
                    valid_nodes.append(node['id'])
        return valid_nodes

    def valid_city_nodes(self, player_id):
        """
        Devuelve un array de las ids de los nodos válidos para convertir pueblos en ciudades
        :param player_id: int
        :return: [int...]
        """
        valid_city_node = lambda node: node['player'] == player_id and node['has_city'] == False
        return [node['id'] for node in self.nodes if valid_city_node(node)]


    def valid_road_nodes(self, player_id): # TODO
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

                if self.nodes[adjacent_node_id]['player'] in [player_id, -1]:

                    # Por cada carretera que haya en el nodo adyacente
                    for road in self.nodes[adjacent_node_id]['roads']:
                        # Si la carretera no es una carretera de vuelta
                        if road['node_id'] != node['id']:
                            allowed_to_build = road['player_id'] == player_id
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
        valid_node = lambda n: n['player'] == -1 and self.empty_adjacent_nodes(n['id']) and not self.is_coastal_node(n['id'])
        return [node['id'] for node in self.nodes if valid_node(node)]


    def check_for_player_harbors(self, player, material_harbor=None):
        """
        Comprueba qué puertos tiene el jugador. Material_harbor sirve para buscar puertos 2:1 de ese tipo
        :param player: int
        :param material_harbor: int/None
        :return: int
        """
        # create the inverted dictionary of harbors: {harbor: [nodes...]}
        inverted_harbors = {harbor: [] for harbor in self.harbors.values()}
        for node, harbor in self.harbors.items():
                inverted_harbors[harbor].append(node)

        # specific resource nodes
        harbor_nodes = inverted_harbors[material_harbor]
        if any([self.nodes[node_id]['player'] == player for node_id in harbor_nodes]):
            return material_harbor

        # 3:1 nodes
        harbor_nodes = inverted_harbors[HarborConstants.ALL]
        if any([self.nodes[harbor]['player'] == player for harbor in harbor_nodes]):
            return HarborConstants.ALL

        return HarborConstants.NONE
