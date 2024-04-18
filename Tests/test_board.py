from Classes.Board import Board
from Classes.Constants import *


class TestBoard:

    def test_build_town(self):
        board = Board()

        # Comprobamos que el nodo no es de ningún jugador y que no tiene ciudad (estado inicial)
        node = board.nodes[0]
        assert node['player'] == -1 and node['has_city'] is False

        # Para poder construir un pueblo, se necesita una carretera adyacente, así pues, se añade directamente.
        # Esto añade una carretera del nodo 0 al 1 y viceversa, poseída por el jugador 0
        finishing_node = board.nodes[1]
        node['roads'].append({'player_id': 0, 'node_id': 1})
        finishing_node['roads'].append({'player_id': 0, 'node_id': 0})

        # Construimos un pueblo y comprobamos que existe
        board.build_town(0, 0)
        assert node['player'] == 0 and node['has_city'] is False

        # Para poder intentar construir un pueblo, el jugador 2 necesita una carretera que apunte al nodo 0
        finishing_node = board.nodes[8]
        node['roads'].append({'player_id': 2, 'node_id': 8})
        finishing_node['roads'].append({'player_id': 2, 'node_id': 0})

        # Intentamos construir un pueblo donde ya había uno, esto no es posible, no debería de pasar nada
        board.build_town(2, 0)
        assert node['player'] != 2

        # Construimos un pueblo adyacente al inicial (ya hay una carretera que apunta al nodo 1), no debería de dejar
        node = board.nodes[1]
        board.build_town(0, 1)
        assert node['player'] == -1 and node['has_city'] is False

        # Sí que debería dejar en el nodo 2, asumiendo que hay una carretera que lo conecta
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 2})
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 1})

        # Construimos un pueblo y comprobamos que existe el pueblo
        node = board.nodes[2]
        board.build_town(0, 2)
        assert node['player'] == 0 and node['has_city'] is False
        return

    def test_build_city(self):
        board = Board()

        # Comprobamos que el nodo no es de ningún jugador y que no tiene ciudad (estado inicial)
        node = board.nodes[0]
        assert node['player'] == -1 and node['has_city'] is False

        # Para poder construir un pueblo, se necesita una carretera adyacente, así pues, se añade directamente.
        # Esto añade una carretera del nodo 0 al 1 y viceversa, poseída por el jugador 0
        finishing_node = board.nodes[1]
        node['roads'].append({'player_id': 0, 'node_id': 1})
        finishing_node['roads'].append({'player_id': 0, 'node_id': 0})

        # Construimos la ciudad sobre el nodo 0 y comprobamos que no existe, dado que no había un pueblo antes
        board.build_city(0, 0)
        assert node['player'] == -1 and node['has_city'] is False

        # Construimos un pueblo y comprobamos que existe el pueblo
        board.build_town(0, 0)
        assert node['player'] == 0 and node['has_city'] is False

        # Construimos la ciudad sobre el nodo 0 y comprobamos que existe
        board.build_city(0, 0)
        assert node['player'] == 0 and node['has_city'] is True

        # Para poder intentar construir un pueblo, el jugador 2 necesita una carretera que apunte al nodo 0
        finishing_node = board.nodes[8]
        node['roads'].append({'player_id': 2, 'node_id': 8})
        finishing_node['roads'].append({'player_id': 2, 'node_id': 0})

        # Intentamos construir un pueblo donde ya había una ciudad, esto no es posible, no debería de pasar nada
        board.build_town(2, 0)
        assert node['player'] != 2

        # Intentamos construir una ciudad donde ya había una, esto no es posible, no debería de pasar nada
        board.build_city(2, 0)
        assert node['player'] != 2

        # Construimos un pueblo adyacente al inicial (ya hay una carretera que apunta al nodo 1), no debería de dejar
        node = board.nodes[1]
        board.build_town(0, 1)
        assert node['player'] == -1 and node['has_city'] is False

        # Construimos una ciudad adyacente a la inicial (ya hay una carretera que apunta al nodo 1), no debería de dejar
        node = board.nodes[1]
        board.build_city(0, 1)
        assert node['player'] == -1 and node['has_city'] is False

        # Sí que debería dejar en el nodo 2, asumiendo que hay una carretera que lo conecta
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 2})
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 1})

        # Construimos un pueblo y luego una ciudad y comprobamos que existe la ciudad
        node = board.nodes[2]
        board.build_town(0, 2)
        board.build_city(0, 2)
        assert node['player'] == 0 and node['has_city'] is True
        return

    def test_build_road(self):
        board = Board()

        # Comprobamos que no hay ninguna carretera en el nodo y que no es de ningún jugador
        node = board.nodes[0]
        assert len(node['roads']) == 0 and node['player'] == -1 and node['has_city'] is False

        # Para poder construir una carretera se necesita un pueblo, así que lo ponemos directamente sin usar la función
        node['player'] = 0

        # Construimos una carretera dirección al nodo 1 desde el nodo 0 y comprobamos que existe en ambos nodos
        finishing_node = board.nodes[1]

        board.build_road(0, 0, 1)
        assert node['roads'] == [{'player_id': 0, 'node_id': 1}] and \
               finishing_node['roads'] == [{'player_id': 0, 'node_id': 0}]

        # Transformamos el pueblo en una ciudad y construimos una carretera al nodo 8
        board.build_city(0, 0)
        finishing_node = board.nodes[8]

        board.build_road(0, 0, 8)
        assert node['roads'] == [{'player_id': 0, 'node_id': 1}, {'player_id': 0, 'node_id': 8}] and \
               finishing_node['roads'] == [{'player_id': 0, 'node_id': 0}]

        # Probamos a construir una carretera desde la que ya existe en el nodo 1, hasta el nodo 2
        node = board.nodes[1]
        finishing_node = board.nodes[2]

        board.build_road(0, 1, 2)
        assert node['roads'] == [{'player_id': 0, 'node_id': 0}, {'player_id': 0, 'node_id': 2}] and \
               finishing_node['roads'] == [{'player_id': 0, 'node_id': 1}]

        # Aseguramos que no se puede construir una carretera donde ya existe una, para eso le damos el nodo 8 al
        # jugador 2 y apuntamos al nodo 0 con la carretera. Debería de seguir perteneciéndole al jugador 0
        board.nodes[8]['player'] = 2

        node = board.nodes[8]
        finishing_node = board.nodes[0]

        board.build_road(2, 8, 0)
        assert node['roads'] == [{'player_id': 0, 'node_id': 0}] and \
               finishing_node['roads'] == [{'player_id': 0, 'node_id': 1}, {'player_id': 0, 'node_id': 8}]

        # Aseguramos que no se puede construir una carretera empezando en el pueblo de un rival,
        # adyacente a una carretera nuestra
        node = board.nodes[8]
        finishing_node = board.nodes[9]

        board.build_road(0, 8, 9)
        assert node['roads'] == [{'player_id': 0, 'node_id': 0}] and \
               len(finishing_node['roads']) == 0

        # Aseguramos que no se puede construir una carretera empezando en la ciudad de un rival,
        # adyacente a una carretera nuestra
        board.build_city(2, 8)
        node = board.nodes[8]
        finishing_node = board.nodes[9]

        board.build_road(0, 8, 9)
        assert node['roads'] == [{'player_id': 0, 'node_id': 0}] and \
               len(finishing_node['roads']) == 0

        # Aseguramos que no se puede construir una carretera empezando en la carretera de un rival
        board.build_road(2, 8, 9)
        node = board.nodes[9]
        finishing_node = board.nodes[10]

        board.build_road(0, 8, 9)
        assert node['roads'] == [{'player_id': 2, 'node_id': 8}] and \
               len(finishing_node['roads']) == 0

        return

    def test_move_thief(self):
        # Ver que el ladrón cambia de casilla de su inicial a una secundaria
        # Que cambia de la secundaria a otra diferente
        # Que no se puede colocar el ladrón en el mismo lugar
        board = Board()

        # Vemos que el desierto empieza con el ladrón
        terrain = board.terrain
        assert terrain[7]['has_thief']

        # Lo movemos a la ficha de terreno 5, y comprobamos que ya no está en el desierto.
        # También nos aseguramos de que la respuesta sea correcta
        response = board.move_thief(5)
        assert terrain[5]['has_thief'] and not terrain[7]['has_thief'] and response['response']

        # Lo movemos a la 3, luego comprobamos que no está ni en la 5 ni en el desierto.
        # También nos aseguramos de que la respuesta sea correcta
        response = board.move_thief(3)
        assert terrain[3]['has_thief'] and not terrain[5]['has_thief'] and not terrain[7]['has_thief'] and response[
            'response']

        # Lo volvemos a mover a la 3, lo que causa que se mueva a una ficha aleatoria (que no sea donde ya estaba)
        # dado que el ladrón no puede moverse al mismo lugar. Comprobamos que está en la pieza que nos dice la
        # respuesta, que su "response" es False y que no está en la casilla 3.
        response = board.move_thief(3)
        assert terrain[response['terrain_id']]['has_thief'] and not terrain[3]['has_thief'] and not response['response']

        return

    def test_valid_town_nodes(self):
        # Comprobamos que, dado un estado inicial conocido, valid_town_nodes solo devuelve los nodos donde
        # el jugador puede construir pueblos
        board = Board()

        # Ponemos carreteras del jugador 0 que enlazan los nodos 0, 1 y 2
        board.nodes[0]['roads'].append({'player_id': 0, 'node_id': 1})
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 0})
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 2})
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 1})

        # Al llamar a valid_town_nodes debería de devolver un array con 0, 1 y 2
        # (dado que como no hay otros pueblos, todos los nodos con carretera son posibles)
        valid_nodes = board.valid_town_nodes(0)
        assert valid_nodes == [0, 1, 2]

        # Si ahora ponemos un pueblo de otro jugador en el nodo 2, solo debería devolver un array con el nodo 0
        board.nodes[2]['player'] = 1  # Así se pone un pueblo en un nodo, se indica de quién es el nodo y ya
        valid_nodes = board.valid_town_nodes(0)
        assert valid_nodes == [0]

        # Si eliminamos dicho pueblo y ponemos un pueblo en el nodo 1, no debería de devolver ningún nodo
        board.nodes[2]['player'] = -1  # Así se elimina un pueblo de un nodo, indicando que no tiene jugador con un -1
        board.nodes[1]['player'] = 1
        valid_nodes = board.valid_town_nodes(0)
        assert valid_nodes == []

        # El resto de jugadores no tendrían que tener nodos posibles (dado que no tienen carreteras)
        valid_nodes_j1 = board.valid_town_nodes(1)
        valid_nodes_j2 = board.valid_town_nodes(2)
        valid_nodes_j3 = board.valid_town_nodes(3)
        assert valid_nodes_j1 == [] and valid_nodes_j2 == [] and valid_nodes_j3 == []

        return

    def test_valid_city_nodes(self):
        # Comprobamos que, dado un estado inicial conocido, valid_town_nodes solo devuelve los nodos donde
        # el jugador puede construir ciudades
        board = Board()

        # Le damos los nodos 0 y 53 al J0 y el nodo 4 al J1.
        board.nodes[0]['player'] = 0
        board.nodes[53]['player'] = 0
        board.nodes[4]['player'] = 1

        # Comprobamos que valid_city_nodes solo devuelve 0 y 53 al J0
        valid_nodes = board.valid_city_nodes(0)
        assert valid_nodes == [0, 53]

        # Construimos una ciudad en el nodo 53 y comprobamos que valid_city_nodes solo devuelve el nodo 0
        board.build_city(0, 53)
        valid_nodes = board.valid_city_nodes(0)
        assert valid_nodes == [0]

        # Comprobamos que valid_city_nodes del J1 es solo el nodo 4
        valid_nodes = board.valid_city_nodes(1)
        assert valid_nodes == [4]

        return

    def test_valid_road_nodes(self):
        """
        Respecto a dudas si puede o no construir una carretera atravesando un pueblo:
            https://www.quora.com/The-Settlers-of-Catan-board-game-Is-it-legal-to-build-a-road-through-an-opponents-settlement
        :return: None
        """
        board = Board()

        # Le damos el nodo 0 al J0 y creamos una carretera hasta el nodo 1.
        board.nodes[0]['player'] = 0
        board.nodes[0]['roads'].append({'player_id': 0, 'node_id': 1})
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 0})

        # Comprobamos que valid_road_nodes
        valid_roads = board.valid_road_nodes(0)
        assert valid_roads == [{'starting_node': 1, 'finishing_node': 2}, {'starting_node': 0, 'finishing_node': 8}]

        # Añadimos una carretera del 1 al 2 para el jugador 0
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 2})
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 1})
        valid_roads = board.valid_road_nodes(0)
        assert valid_roads == [{'starting_node': 2, 'finishing_node': 3}, {'starting_node': 0, 'finishing_node': 8},
                               {'starting_node': 2, 'finishing_node': 10}]

        # Ponemos un pueblo del J1 en el nodo 2
        board.nodes[2]['player'] = 1
        # Esto debería de cortar la posibilidad de hacer carreteras a partir del nodo 2
        valid_roads = board.valid_road_nodes(0)
        assert valid_roads == [{'starting_node': 0, 'finishing_node': 8}]

        # Quitamos el pueblo de J1 del nodo 2 y lo ponemos en el nodo 3. Debería de poder hacerse una carretera hasta él
        board.nodes[2]['player'] = -1
        board.nodes[3]['player'] = 1
        valid_roads = board.valid_road_nodes(0)
        assert valid_roads == [{'starting_node': 2, 'finishing_node': 3}, {'starting_node': 0, 'finishing_node': 8},
                               {'starting_node': 2, 'finishing_node': 10}]

        # Añadimos una carretera del nodo 2 al 3 para el jugador 0
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 3})
        board.nodes[3]['roads'].append({'player_id': 0, 'node_id': 2})
        # Y comprobamos que, en efecto, no deja construir más allá del nodo 3
        valid_roads = board.valid_road_nodes(0)
        assert valid_roads == [{'starting_node': 0, 'finishing_node': 8}, {'starting_node': 2, 'finishing_node': 10}]

        # Comprobamos qué pasa, si hay una carretera atravesando el pueblo. Debería de dejar construir sin problema,
        #  dado que para estar ahí, debería de haber estado antes que el pueblo, cortando la carretera por la mitad,
        #  pero permitiendo seguirla
        board.nodes[3]['roads'].append({'player_id': 0, 'node_id': 4})
        board.nodes[4]['roads'].append({'player_id': 0, 'node_id': 3})
        valid_roads = board.valid_road_nodes(0)
        assert valid_roads == [{'starting_node': 4, 'finishing_node': 5}, {'starting_node': 0, 'finishing_node': 8},
                               {'starting_node': 2, 'finishing_node': 10}, {'starting_node': 4, 'finishing_node': 12}]
        return

    def test_valid_starting_nodes(self):
        board = Board()
        # valid_starting_nodes devuelve todos los nodos que no son costeros (hard_coded cuáles son costeros)
        # y que no sea de ningún jugador o adyacentes a un pueblo de un jugador
        valid_nodes = board.valid_starting_nodes()
        assert valid_nodes == [9, 10, 11, 12, 13, 18, 19, 20, 21, 22, 23, 24, 29, 30, 31, 32, 33, 34, 35, 40, 41, 42,
                               43, 44]

        # Hacemos un pueblo en el nodo 11, lo que debería eliminar de la selección los nodos 10, 11, 12 y 21
        board.nodes[11]['player'] = 0
        valid_nodes = board.valid_starting_nodes()
        assert valid_nodes == [9, 13, 18, 19, 20, 22, 23, 24, 29, 30, 31, 32, 33, 34, 35, 40, 41, 42, 43, 44]

        return

    def test_check_for_player_harbors(self):
        # Comprobar que devuelve puerto de trigo cuando el jugador tiene uno, y que devuelve puerto de todos
        # si no tiene el puerto del material elegido (o es None)
        board = Board()

        # Le damos al J0 un puerto genérico y uno de trigo. Al J1 le damos un puerto de minerales.
        board.nodes[3]['player'] = 0
        board.nodes[7]['player'] = 0
        board.nodes[28]['player'] = 1

        # Comprobamos que el puerto que devuelve al J0 en caso de poner cereal es el de cereal
        harbor_response = board.check_for_player_harbors(0, MaterialConstants.CEREAL)
        assert harbor_response == HarborConstants.CEREAL

        # En caso de ser el J1, debería de no devolver puerto
        harbor_response = board.check_for_player_harbors(1, MaterialConstants.CEREAL)
        assert harbor_response == HarborConstants.NONE

        # Comprobamos que el puerto que devuelve al J1 en caso de poner mineral es mineral
        harbor_response = board.check_for_player_harbors(1, MaterialConstants.MINERAL)
        assert harbor_response == HarborConstants.MINERAL

        # En caso de ser el J0, debería devolver puerto genérico
        harbor_response = board.check_for_player_harbors(0, MaterialConstants.MINERAL)
        assert harbor_response == HarborConstants.ALL

        return


if __name__ == '__main__':
    test = TestBoard()
    test.test_build_town()
    test.test_build_city()
    test.test_build_road()
    test.test_move_thief()
    test.test_valid_town_nodes()
    test.test_valid_city_nodes()
    test.test_valid_road_nodes()
    test.test_valid_starting_nodes()
    test.test_check_for_player_harbors()
