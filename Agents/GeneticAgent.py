from Interfaces.AgentInterface import AgentInterface
from Classes.Board import Board
from Classes.DevelopmentCards import DevelopmentCardsHand, DevelopmentCard
from Classes.Hand import Hand
from Classes.TradeOffer import TradeOffer
from Classes.Constants import MaterialConstants, BuildConstants, BuildMaterialsConstants
from Classes.Materials import Materials
import random # Importamos random para las implementaciones base


class GeneticAgent(AgentInterface):
    """
    Agente inteligente para el juego de Catán que optimiza su comportamiento
    mediante un algoritmo genético.
    """

    def __init__(self, agent_id, chromosome=None):
        """
        Constructor del GeneticAgent.

        :param agent_id: Identificador único del agente.
        :param chromosome: Una lista o diccionario representando los pesos genéticos
                           que guiarán las decisiones del agente. Si es None,
                           se podrían inicializar pesos por defecto o aleatorios.
        """
        super().__init__(agent_id)
        self.chromosome = chromosome if chromosome is not None else self._initialize_default_chromosome()
        # Podríamos necesitar registrar el 'board_instance' más persistentemente
        # self.board_instance = None

    def _initialize_default_chromosome(self):
        """
        Inicializa un cromosoma con pesos por defecto o aleatorios.
        Esta estructura de pesos será optimizada por el algoritmo genético.
        Los valores iniciales son solo placeholders.
        """
        return {
            # Pesos principales para cada tipo de acción de construcción
            "build_actions": {
                BuildConstants.TOWN: 1.0,
                BuildConstants.CITY: 0.9,
                BuildConstants.ROAD: 0.7,
                BuildConstants.CARD: 0.5
            },
            # Pesos para heurísticas específicas de construcción de poblados
            "settlement_heuristics": {
                "resource_value_base": 1.0, # Multiplicador general para el valor de recursos del nodo
                "resource_priority": { # Pesos individuales por tipo de recurso
                    MaterialConstants.WOOD: 0.8,
                    MaterialConstants.CLAY: 0.8, # Ladrillo
                    MaterialConstants.WOOL: 0.7, # Lana
                    MaterialConstants.CEREAL: 0.9, # Trigo
                    MaterialConstants.MINERAL: 1.0 # Ore
                },
                "production_probability_exponent": 1.0, # Exponente para la probabilidad (más alto = más peso a números comunes)
                "new_resource_type_bonus": 0.5, # Bonus por cada nuevo tipo de recurso al que da acceso
                "port_access_bonus": 0.3, # Bonus general por estar en un puerto
                "specific_port_match_bonus": 0.4, # Bonus si el puerto coincide con un recurso del nodo
                "number_diversity_bonus": 0.2 # Bonus por diversidad de números en los terrenos adyacentes
            },
            # Pesos para heurísticas específicas de construcción de carreteras
            "road_heuristics": {
                "to_potential_settlement_spot_bonus": 0.6, # Bonus si la carretera lleva a un buen sitio para un futuro poblado
                "connects_to_own_settlement_bonus": 0.3, # Bonus por conectar dos asentamientos propios (no directamente, sino parte de una red)
                "longest_road_contribution_bonus": 0.5, # Bonus por contribuir al camino más largo
                "port_access_bonus": 0.4, # Bonus si la carretera da acceso a un puerto
                "expansion_to_new_terrain_bonus": 0.3 # Bonus por expandirse hacia nuevos terrenos/recursos
            },
            # Pesos para heurísticas específicas de construcción de ciudades
            "city_heuristics": { # Similar a settlement, pero enfocado en la mejora de producción
                "resource_value_base": 1.2, # Las ciudades suelen ser más valiosas
                "resource_priority": { # Pueden ser diferentes a los de poblado
                    MaterialConstants.WOOD: 0.5,
                    MaterialConstants.CLAY: 0.5,
                    MaterialConstants.WOOL: 0.6,
                    MaterialConstants.CEREAL: 1.0,
                    MaterialConstants.MINERAL: 1.2
                },
                "production_probability_exponent": 1.1,
            },
            # Pesos para heurísticas de compra de cartas de desarrollo
            "dev_card_heuristics": {
                "base_value": 1.0, # Valor base de comprar una carta
                "knight_potential_bonus": 0.3, # Si se está compitiendo por el ejército más grande
                "vp_card_late_game_bonus": 0.4, # Si las cartas de PV son cruciales (final de partida)
            },
            # Pesos para la colocación inicial (ej. por tipo de recurso adyacente)
            "initial_placement_resource_priority": {
                MaterialConstants.WOOD: 0.7, MaterialConstants.CLAY: 0.7,
                MaterialConstants.WOOL: 0.6, MaterialConstants.CEREAL: 0.8,
                MaterialConstants.MINERAL: 0.9
            },
            "initial_placement_diversity_bonus": 0.5, # Bonus por tener más tipos de recursos
            # Pesos para mover el ladrón
            "thief_placement_block_opponent_points_factor": 0.7, # Factor por puntos del oponente
            "thief_placement_resource_priority": { # Prioridad de recurso a bloquear
                MaterialConstants.WOOD: 0.5, MaterialConstants.CLAY: 0.5,
                MaterialConstants.WOOL: 0.4, MaterialConstants.CEREAL: 0.6,
                MaterialConstants.MINERAL: 0.7
            },
            "thief_placement_on_high_prob_terrain_bonus": 0.6, # Bonus por ponerlo en un terreno con alta probabilidad
            "thief_placement_self_unblock_priority": 0.8 # Prioridad para desbloquearse a sí mismo
        }

    def on_game_start(self, board_instance):
        """
        Decide la ubicación del primer pueblo y la carretera adyacente.
        Esta implementación es un placeholder y será reemplazada por una lógica
        guiada por el cromosoma genético.

        :param board_instance: Instancia del tablero con la información actual.
        :return: Una tupla (node_id, road_to) donde node_id es la ubicación
                 del pueblo y road_to es el nodo destino de la carretera.
        """
        self.board = board_instance # Guardamos la instancia del tablero
        # Lógica de decisión basada en self.chromosome para elegir el mejor nodo y carretera
        # Por ahora, se mantiene la lógica aleatoria de la interfaz como placeholder.
        
        # TODO: Implementar lógica de selección de nodo basada en el cromosoma
        # Por ejemplo, evaluar nodos por los recursos que producen y su número (probabilidad)
        # y aplicar los pesos de self.chromosome["initial_placement_resource_priority"]

        all_nodes = list(self.board.nodes.keys())
        valid_nodes = [n for n in all_nodes if self.board.can_place_settlement(self.id, n, is_initial_settlement=True)]

        if not valid_nodes:
            # Fallback muy básico si no se encuentra ningún nodo válido (no debería ocurrir en el inicio)
            node_id = random.choice(all_nodes)
        else:
            # Aquí iría la evaluación de 'valid_nodes' usando el cromosoma
            node_id = random.choice(valid_nodes)


        possible_roads = []
        if self.board.nodes[node_id]['player'] is None or self.board.nodes[node_id]['player'] == self.id : # Puede ser None o ser yo mismo si es la segunda ronda de colocación
            for neighbor_node_id in self.board.nodes[node_id]['adjacent']:
                if self.board.can_place_road(self.id, node_id, neighbor_node_id, is_initial_road=True):
                    possible_roads.append(neighbor_node_id)
        
        if not possible_roads:
             # Fallback si no hay carreteras posibles (muy improbable en el inicio)
             # Intentar encontrar cualquier carretera posible desde un nodo válido
            for n_id in valid_nodes:
                for neighbor_node_id in self.board.nodes[n_id]['adjacent']:
                     if self.board.can_place_road(self.id, n_id, neighbor_node_id, is_initial_road=True):
                        return n_id, neighbor_node_id # Devolver la primera que se encuentre
            # Si aun así no se encuentra, devolver algo aleatorio (aunque esto indica un problema)
            node_id = random.choice(all_nodes)
            adj_nodes = self.board.nodes[node_id]['adjacent']
            if not adj_nodes: # Si un nodo no tiene adyacentes (imposible en Catan estandar)
                return 0, 1 # Valores por defecto absurdos
            return node_id, random.choice(adj_nodes)


        road_to = random.choice(possible_roads) # TODO: Evaluar carreteras también

        return node_id, road_to

    def on_turn_start(self):
        """
        Se llama al inicio del turno, antes de tirar los dados.
        Utilizado para jugar cartas de desarrollo si es estratégico.
        Esta implementación es un placeholder.

        :return: DevelopmentCard a jugar o None si no se juega ninguna.
        """
        # TODO: Implementar lógica de decisión basada en self.chromosome
        # para jugar cartas de desarrollo estratégicamente.
        return None

    def on_commerce_phase(self):
        """
        Se llama al inicio de la fase de comercio para realizar una oferta.
        Esta implementación es un placeholder.

        :return: TradeOffer, dict{'gives': int, 'receives': int}, o None.
        """
        # TODO: Implementar lógica de decisión basada en self.chromosome
        # para proponer intercambios.
        return None

    def on_trade_offer(self, board_instance, incoming_trade_offer=TradeOffer(), player_making_offer=int):
        """
        Se llama cuando se recibe una oferta de comercio de otro jugador.
        Esta implementación es un placeholder.

        :param board_instance: Estado actual del tablero.
        :param incoming_trade_offer: La oferta recibida.
        :param player_making_offer: ID del jugador que hace la oferta.
        :return: True para aceptar, un nuevo TradeOffer para contraoferta, o False para rechazar.
        """
        self.board = board_instance
        # TODO: Implementar lógica de decisión basada en self.chromosome
        # para aceptar, rechazar o contraofertar.
        return False

    def on_build_phase(self, board_instance):
        """
        Se llama durante la fase de construcción para decidir qué construir.
        Debe evaluar construir carreteras, poblados, ciudades o comprar cartas de desarrollo.
        La decisión se basará en los pesos del cromosoma genético.

        :param board_instance: Instancia del tablero con la información actual.
        :return: Un diccionario {building: str, node_id: int, road_to: int/None}
                 que indica qué construir y dónde, o None si no se construye nada.
        """
        self.board = board_instance # Actualizamos la referencia al tablero

        best_action_to_take = self._get_best_build_action()

        if best_action_to_take:
            action_type = best_action_to_take["type"]
            details = best_action_to_take["details"]

            if action_type == BuildConstants.ROAD:
                return {
                    "building": BuildConstants.ROAD,
                    "node_id": details["from_node"], # Nodo de inicio de la carretera
                    "road_to": details["to_node"]    # Nodo de fin de la carretera
                }
            elif action_type == BuildConstants.TOWN:
                return {
                    "building": BuildConstants.TOWN,
                    "node_id": details["node_id"],   # Nodo donde construir el poblado
                    "road_to": None                  # No aplica para poblados
                }
            elif action_type == BuildConstants.CITY:
                return {
                    "building": BuildConstants.CITY,
                    "node_id": details["node_id"],   # Nodo (con poblado existente) a mejorar a ciudad
                    "road_to": None                  # No aplica para ciudades
                }
            elif action_type == BuildConstants.CARD:
                # La compra de cartas de desarrollo se maneja de forma diferente por el GameDirector.
                # El GameDirector espera el nombre de la carta o una acción específica.
                # Por ahora, señalamos la intención de comprar una carta.
                # El GameDirector debe tener una forma de procesar esto.
                # Este retorno podría necesitar ajuste según cómo el GameDirector espere esta acción.
                # Si on_build_phase debe devolver la carta específica, necesitaríamos cambiar esto.
                # Asumiendo que el GameDirector maneja la compra si se retorna BuildConstants.CARD.
                return {
                    "building": BuildConstants.CARD, # Indicamos que queremos comprar una carta
                    "node_id": None, # No aplica
                    "road_to": None  # No aplica
                }
        
        return None # No se construye nada

    def _get_best_build_action(self):
        """
        Analiza todas las posibles acciones de construcción (poblado, ciudad, carretera, carta de desarrollo),
        las evalúa usando heurísticas y pesos del cromosoma, y devuelve la mejor acción.

        :return: Un diccionario representando la mejor acción y sus detalles, o None si no hay acciones viables.
        """
        possible_actions = []

        # 1. Evaluar Comprar Carta de Desarrollo
        cost_card = Materials.from_iterable(BuildMaterialsConstants[BuildConstants.CARD])
        if self.hand.resources.has_more(cost_card): # Usar el objeto Materials para el coste
            heuristic_val = self._heuristic_dev_card()
            score = heuristic_val * self.chromosome["build_actions"][BuildConstants.CARD]
            possible_actions.append({"type": BuildConstants.CARD, "score": score, "details": None, "cost": cost_card})

        # 2. Evaluar Construir Carretera
        cost_road = Materials.from_iterable(BuildMaterialsConstants[BuildConstants.ROAD])
        if self.hand.resources.has_more(cost_road):
            # Asumiendo que valid_road_nodes devuelve [(from_node, to_node), ...]
            # Necesitamos verificar que el método exista y funcione como se espera.
            # Por ahora, creamos una lista vacía si el método no existe para evitar errores.
            valid_roads = []
            if hasattr(self.board, 'valid_road_locations_for_player'): # Nombre más probable o similar
                 valid_roads = self.board.valid_road_locations_for_player(self.id)
            elif hasattr(self.board, 'valid_road_nodes'): # Plan B
                 valid_roads = self.board.valid_road_nodes(self.id)


            for from_node, to_node in valid_roads:
                heuristic_val = self._heuristic_road_location(from_node, to_node)
                score = heuristic_val * self.chromosome["build_actions"][BuildConstants.ROAD]
                possible_actions.append({
                    "type": BuildConstants.ROAD,
                    "score": score,
                    "details": {"from_node": from_node, "to_node": to_node},
                    "cost": cost_road
                })
        
        # 3. Evaluar Construir Poblado
        cost_town = Materials.from_iterable(BuildMaterialsConstants[BuildConstants.TOWN])
        # También verificar límite de poblados (generalmente 5)
        num_settlements = len([n for n in self.board.nodes if self.board.nodes[n]['player'] == self.id and not self.board.nodes[n]['has_city']])
        if self.hand.resources.has_more(cost_town) and num_settlements < 5:
            valid_nodes_for_town = []
            if hasattr(self.board, 'valid_settlement_locations_for_player'):
                valid_nodes_for_town = self.board.valid_settlement_locations_for_player(self.id)
            elif hasattr(self.board, 'valid_town_nodes'): # Plan B
                valid_nodes_for_town = self.board.valid_town_nodes(self.id)

            for node_id in valid_nodes_for_town:
                heuristic_val = self._heuristic_settlement_location(node_id)
                score = heuristic_val * self.chromosome["build_actions"][BuildConstants.TOWN]
                possible_actions.append({
                    "type": BuildConstants.TOWN,
                    "score": score,
                    "details": {"node_id": node_id},
                    "cost": cost_town
                })

        # 4. Evaluar Construir Ciudad
        cost_city = Materials.from_iterable(BuildMaterialsConstants[BuildConstants.CITY])
        # También verificar límite de ciudades (generalmente 4)
        num_cities = len([n for n in self.board.nodes if self.board.nodes[n]['player'] == self.id and self.board.nodes[n]['has_city']])
        if self.hand.resources.has_more(cost_city) and num_cities < 4:
            valid_nodes_for_city_upgrade = []
            if hasattr(self.board, 'valid_city_upgrade_locations_for_player'):
                 valid_nodes_for_city_upgrade = self.board.valid_city_upgrade_locations_for_player(self.id)
            elif hasattr(self.board, 'valid_city_nodes'): # Plan B, asume que da nodos propios para mejorar
                 valid_nodes_for_city_upgrade = self.board.valid_city_nodes(self.id)
            
            for node_id in valid_nodes_for_city_upgrade: # Estos son nodos donde YA TENGO UN POBLADO
                heuristic_val = self._heuristic_city_location(node_id)
                score = heuristic_val * self.chromosome["build_actions"][BuildConstants.CITY]
                possible_actions.append({
                    "type": BuildConstants.CITY,
                    "score": score,
                    "details": {"node_id": node_id},
                    "cost": cost_city
                })

        if not possible_actions:
            return None

        # Seleccionar la mejor acción. Podríamos añadir una lógica para desempatar o un umbral mínimo de score.
        # Por ahora, simplemente la de mayor puntuación.
        best_action = max(possible_actions, key=lambda x: x["score"])
        
        # Opcional: Verificar si la mejor acción tiene un score mínimo para ser considerada
        # min_score_threshold = 0.1 # Ejemplo de umbral, podría ser parte del cromosoma
        # if best_action["score"] < min_score_threshold:
        #     return None
            
        return best_action

    # --- Funciones de Heurística (Implementaciones Placeholder) ---
    def _heuristic_dev_card(self):
        """ Placeholder para la heurística de comprar una carta de desarrollo. """
        # TODO: Implementar heurística real basada en self.chromosome["dev_card_heuristics"]
        # y el estado del juego (ej. puntos de victoria, cartas de caballero de oponentes, etc.)
        return 1.0 * self.chromosome["dev_card_heuristics"]["base_value"]

    def _heuristic_road_location(self, from_node_id, to_node_id):
        """ Placeholder para la heurística de construir una carretera en una ubicación específica. """
        # TODO: Implementar heurística real basada en self.chromosome["road_heuristics"]
        # y propiedades del tablero (ej. acceso a puertos, expansión, conexión a nodos valiosos,
        # contribución al camino más largo).
        # Ejemplo:
        # score = 0
        # if self.board.nodes[to_node_id]['harbor'] != HarborConstants.NONE :
        #    score += self.chromosome["road_heuristics"]["port_access_bonus"]
        # ... más lógica ...
        return 1.0

    def _heuristic_settlement_location(self, node_id):
        """ Placeholder para la heurística de construir un poblado en un nodo específico. """
        # TODO: Implementar heurística real basada en self.chromosome["settlement_heuristics"]
        # y las propiedades del nodo (recursos adyacentes, números, puertos, etc.).
        # Ejemplo de cálculo de valor de recursos:
        # node_resource_value = 0
        # for terrain_idx in self.board.nodes[node_id]['contacting_terrain']:
        #    terrain = self.board.terrain[terrain_idx]
        #    if terrain['terrain_type'] != TerrainConstants.DESERT:
        #        prob = (6 - abs(terrain['probability'] - 7)) / 36.0 # Probabilidad de sacar el número
        #        resource_type = terrain['terrain_type']
        #        resource_weight = self.chromosome["settlement_heuristics"]["resource_priority"].get(resource_type, 0.1)
        #        node_resource_value += (prob ** self.chromosome["settlement_heuristics"]["production_probability_exponent"]) * resource_weight
        # return node_resource_value * self.chromosome["settlement_heuristics"]["resource_value_base"]
        return 1.0

    def _heuristic_city_location(self, node_id):
        """ Placeholder para la heurística de mejorar un poblado a ciudad en un nodo específico. """
        # TODO: Implementar heurística real basada en self.chromosome["city_heuristics"].
        # Similar a _heuristic_settlement_location pero los recursos cuentan doble y los pesos pueden ser diferentes.
        return 1.2 # Las ciudades suelen ser inherentemente un poco mejores

    def on_moving_thief(self):
        """
        Se llama cuando el ladrón debe ser movido (por un 7 o carta de caballero).
        La decisión se basará en los pesos del cromosoma genético.
        Esta implementación es un placeholder.

        :return: Un diccionario {terrain: terrain_id, player: player_id}
                 indicando la nueva ubicación del ladrón y a qué jugador robar.
        """
        # Placeholder: Lógica de decisión basada en self.chromosome
        # 1. Evaluar todas las casillas posibles para el ladrón (excepto la actual).
        # 2. Para cada casilla, evaluar a qué jugador se podría robar.
        # 3. Calcular una puntuación para cada combinación (casilla, jugador_a_robar)
        #    usando los pesos del cromosoma (ej. "thief_placement_block_opponent_points",
        #    "thief_placement_resource_priority").
        # 4. Seleccionar la mejor opción.

        # Implementación base de la interfaz (mueve al mismo sitio o -1 si no sabe)
        # Esto debe ser mejorado significativamente.
        terrain_id_current_thief = 0
        for terrain_info in self.board.terrain:
            if terrain_info['has_thief']:
                terrain_id_current_thief = terrain_info['id']
                break
        
        # TODO: Seleccionar 'best_terrain_id' y 'best_player_to_rob_id' usando el cromosoma.
        # Por ahora, se mantiene una lógica muy básica o aleatoria.
        
        possible_terrains = [t['id'] for t in self.board.terrain if not t['has_thief']]
        if not possible_terrains: # No debería ocurrir si hay más de una casilla de terreno
            best_terrain_id = terrain_id_current_thief # No mover si no hay opciones
        else:
            best_terrain_id = random.choice(possible_terrains)

        # Lógica para seleccionar jugador al que robar (muy simplificada)
        players_on_selected_terrain = []
        for node_id in self.board.terrain_node_config[best_terrain_id]:
            node = self.board.nodes[node_id]
            if node['player'] is not None and node['player'] != self.id:
                players_on_selected_terrain.append(node['player'])
        
        best_player_to_rob_id = -1 # No robar a nadie por defecto
        if players_on_selected_terrain:
            best_player_to_rob_id = random.choice(list(set(players_on_selected_terrain)))


        return {'terrain': best_terrain_id, 'player': best_player_to_rob_id}

    def on_having_more_than_7_materials_when_thief_is_called(self):
        """
        Se llama cuando el jugador tiene más de 7 cartas de recurso y sale un 7.
        Debe decidir qué cartas descartar.
        Esta implementación es un placeholder.

        :return: Hand() con los materiales a descartar.
        """
        # TODO: Implementar lógica de decisión basada en self.chromosome
        # para elegir qué recursos descartar de forma estratégica.
        # Por ejemplo, descartar los que menos se necesiten o los más abundantes.

        # Implementación base: descarta aleatoriamente si es necesario.
        num_to_discard = self.hand.get_total_materials() // 2
        discard_hand = Hand()
        
        if num_to_discard == 0:
            return discard_hand

        # Esta es una forma muy básica de descarte. Una mejor estrategia consideraría
        # el valor de los recursos, los próximos objetivos de construcción, etc.
        all_cards = []
        for material_id, count in self.hand.resources.items():
            all_cards.extend([material_id] * count)
        
        random.shuffle(all_cards)
        
        for i in range(min(num_to_discard, len(all_cards))):
            discard_hand.add_material(all_cards[i], 1)
            
        return discard_hand
        

    def on_turn_end(self):
        """
        Se llama al final del turno.
        Utilizado para jugar cartas de desarrollo si es estratégico.
        Esta implementación es un placeholder.

        :return: DevelopmentCard a jugar o None si no se juega ninguna.
        """
        # TODO: Implementar lógica de decisión basada en self.chromosome.
        return None

    def on_monopoly_card_use(self):
        """
        Se llama cuando el agente decide usar una carta de Monopolio.
        Debe elegir qué recurso monopolizar.
        Esta implementación es un placeholder.

        :return: Un entero representando el material elegido (0-4).
        """
        # TODO: Implementar lógica de decisión basada en self.chromosome.
        # Por ejemplo, elegir el recurso que más necesitan los oponentes o que más necesita el agente.
        return random.randint(0, 4) # Placeholder: elige un recurso al azar

    def on_road_building_card_use(self):
        """
        Se llama cuando el agente decide usar una carta de Construcción de Carreteras.
        Debe elegir dónde construir dos carreteras.
        Esta implementación es un placeholder.

        :return: Dict con la ubicación de las dos carreteras.
                 Ej: {'node_id': int, 'road_to': int, 'node_id_2': int, 'road_to_2': int}
        """
        # TODO: Implementar lógica de decisión basada en self.chromosome.
        # Encontrar las mejores ubicaciones para dos carreteras.
        # Esto es complejo y requiere una buena evaluación del tablero.
        # Por ahora, devolvemos None para que el GameDirector maneje la aleatoriedad si es necesario.
        return None

    def on_year_of_plenty_card_use(self):
        """
        Se llama cuando el agente decide usar una carta de Año de la Abundancia.
        Debe elegir qué dos recursos tomar del banco.
        Esta implementación es un placeholder.

        :return: Dict con los dos materiales elegidos. Ej: {'material': int, 'material_2': int}
        """
        # TODO: Implementar lógica de decisión basada en self.chromosome.
        # Elegir los recursos más necesarios para los objetivos actuales.
        return {'material': random.randint(0, 4), 'material_2': random.randint(0, 4)} # Placeholder

    # Métodos auxiliares que podrían ser útiles (a definir según la estrategia)
    # def can_build_settlement(self): ...
    # def heuristic_settlement(self): ...
    # def can_build_city(self): ...
    # def heuristic_city(self): ...
    # etc. 