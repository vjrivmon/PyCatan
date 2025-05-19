from Interfaces.AgentInterface import AgentInterface
from Classes.Board import Board
from Classes.DevelopmentCards import DevelopmentCardsHand, DevelopmentCard
from Classes.Hand import Hand
from Classes.TradeOffer import TradeOffer
from Classes.Constants import MaterialConstants, BuildConstants, BuildMaterialsConstants, HarborConstants
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
        self.id = agent_id # Aseguramos que el agent_id se almacena como self.id
        if chromosome is None:
            self.chromosome = self._initialize_default_chromosome()
        else:
            self.chromosome = chromosome
        # self.agent_manager = agent_manager_ref # Eliminado: No podemos garantizar esta referencia
        # Podríamos necesitar registrar el 'board_instance' más persistentemente
        # self.board_instance = None

    def _initialize_default_chromosome(self):
        """
        Inicializa un cromosoma con pesos por defecto o aleatorios.
        Esta estructura de pesos será optimizada por el algoritmo genético.
        """
        return {
            "build_actions": {
                BuildConstants.TOWN: 1.0,
                BuildConstants.CITY: 0.9,
                BuildConstants.ROAD: 0.7,
                BuildConstants.CARD: 0.5
            },
            "settlement_heuristics": {
                "resource_value_base": 1.0,
                "resource_priority": {
                    MaterialConstants.WOOD: 0.8, MaterialConstants.CLAY: 0.8,
                    MaterialConstants.SHEEP: 0.7, MaterialConstants.WHEAT: 0.9, MaterialConstants.STONE: 1.0
                },
                "production_probability_exponent": 1.0,
                "new_resource_type_bonus": 0.5,
                "port_access_bonus": 0.3,
                "specific_port_match_bonus": 0.4,
                "number_diversity_bonus": 0.2
            },
            "road_heuristics": {
                "to_potential_settlement_spot_bonus": 0.6,
                "connects_to_own_settlement_bonus": 0.3, # Renombrado de 'expand_network' para claridad
                "longest_road_contribution_bonus": 0.5,
                "port_access_bonus": 0.4, # Renombrado de 'to_new_harbor_bonus'
                "expansion_to_new_terrain_bonus": 0.3 # Renombrado de 'to_new_terrain_bonus'
            },
            "city_heuristics": {
                "resource_value_base": 1.2,
                "resource_priority": {
                    MaterialConstants.WOOD: 0.5, MaterialConstants.CLAY: 0.5,
                    MaterialConstants.SHEEP: 0.6, MaterialConstants.WHEAT: 1.0, MaterialConstants.STONE: 1.2
                },
                "production_probability_exponent": 1.1,
            },
            "dev_card_heuristics": {
                "base_value": 5.0,
                "knight_bonus": 3.0,
                "victory_point_bonus": 7.0,
                "monopoly_bonus": 4.0,
                "road_building_bonus": 4.0,
                "year_of_plenty_bonus": 4.0
            },
            # Heurísticas para la colocación inicial
            "initial_placement_settlement": {
                "resource_production_base": 1.0,
                "resource_priority": {
                    MaterialConstants.WOOD: 1.0, MaterialConstants.CLAY: 1.0,
                    MaterialConstants.SHEEP: 0.8, MaterialConstants.WHEAT: 0.9, MaterialConstants.STONE: 0.7
                },
                "production_probability_exponent": 1.0,
                "new_resource_type_bonus": 1.5, # Muy importante al inicio
                "port_access_bonus": 0.2, # Menos prioritario para el primer asentamiento
                "specific_port_match_bonus": 0.1,
                "number_diversity_bonus": 0.5,
                "avoid_single_resource_concentration_penalty": -2.0 # Penalización si todos los terrenos adyacentes son del mismo recurso escaso o demasiado común
            },
            "initial_placement_road":{
                "to_second_potential_settlement_spot_bonus": 0.8, # Hacia dónde podría ir el segundo poblado
                "resource_variety_expansion_bonus": 0.5, # Si la carretera da acceso a nuevos tipos de recursos/números
                "general_expansion_bonus": 0.2, # Bonus general por una carretera inicial segura
                "connect_to_high_prob_numbers_bonus": 0.4 # Bonus si la carretera se dirige a números de alta probabilidad no cubiertos por el primer asentamiento
            },
            # Pesos para mover el ladrón
            "robber_placement_heuristics": { # Renombrado de thief_placement...
                "target_high_production_node_multiplier": 1.0, # Multiplicador para el valor de producción del nodo
                "block_specific_resource_priority": { # Prioridad de recurso a bloquear
                    MaterialConstants.WOOD: 0.8, MaterialConstants.CLAY: 0.8,
                    MaterialConstants.SHEEP: 0.7, MaterialConstants.WHEAT: 1.0, MaterialConstants.STONE: 1.0
                },
                "target_opponent_with_most_vps_bias": 0.5, # Un pequeño extra si se puede identificar al líder
                "avoid_own_nodes_penalty": -5.0, # Fuerte penalización por bloquearse a sí mismo
                "randomness_factor": 0.1 # Para evitar predictibilidad total
            },
            # Pesos para descartar cartas
            "discard_heuristics": {
                "resource_value_priority": { # Cuanto más bajo, más probable descartar
                    MaterialConstants.WOOD: 0.8, MaterialConstants.CLAY: 0.8,
                    MaterialConstants.SHEEP: 1.0, # La lana a menudo es más fácil de descartar
                    MaterialConstants.WHEAT: 0.7, MaterialConstants.STONE: 0.6
                },
                "keep_for_settlement_bonus": -0.5, # Bonus negativo (hace menos probable descartar) si se acerca a un poblado
                "keep_for_city_bonus": -0.6,
                "keep_for_card_bonus": -0.3
            },
            # Heurísticas para decisiones de comercio
            "trade_heuristics": {
                "willingness_to_trade_general": 0.5, # Factor base
                "resource_surplus_importance": { # Qué tan importante es tener excedente para comerciar (más alto = más dispuesto)
                    MaterialConstants.WOOD: 0.6, MaterialConstants.CLAY: 0.6,
                    MaterialConstants.SHEEP: 0.8, MaterialConstants.WHEAT: 0.5, MaterialConstants.STONE: 0.5
                },
                "resource_needed_importance": { # Qué tan importante es obtener un recurso necesitado
                     MaterialConstants.WOOD: 1.2, MaterialConstants.CLAY: 1.2,
                    MaterialConstants.SHEEP: 1.0, MaterialConstants.WHEAT: 1.3, MaterialConstants.STONE: 1.3
                },
                "bank_trade_ratio_modifier": -0.2, # Penalización por comerciar 4:1 con el banco
                "port_trade_ratio_modifier": -0.1, # Penalización menor por comerciar 3:1 o 2:1 con puerto
                "accept_offer_resource_gain_factor": 1.0,
                "accept_offer_fairness_threshold": 0.8 # Si la oferta es al menos 80% "justa" en valor
            },
            # Heurísticas para jugar cartas de desarrollo
            "play_dev_card_heuristics":{
                "knight_immediate_threat_bonus": 1.0, # Si hay un ladrón bloqueando algo importante
                "knight_take_largest_army_bonus": 1.5,
                "monopoly_potential_gain_threshold": 4, # Jugar si se espera ganar al menos 4 del recurso
                "year_of_plenty_immediate_build_bonus": 1.2, # Si permite construir algo importante inmediatamente
                "road_building_strategic_spot_bonus": 1.0, # Si permite alcanzar un punto estratégico
                "min_score_to_play_knight_on_start": 0.75 # Ejemplo de umbral del cromosoma
            }
        }

    def _get_dice_roll_to_dots_map(self):
        """
        Devuelve un mapeo de la tirada de dados a los "puntos" de probabilidad (de 36).
        """
        return {
            2: 1, 3: 2, 4: 3, 5: 4, 6: 5,
            7: 0, # El ladrón se mueve, no hay producción directa.
            8: 5, 9: 4, 10: 3, 11: 2, 12: 1
        }

    def _heuristic_initial_settlement_location(self, node_id):
        """
        Calcula una puntuación heurística para la colocación de un asentamiento inicial en un nodo.
        Utiliza los pesos de "initial_placement_settlement" del cromosoma.
        Prioriza diversidad de recursos, buenos números y evita concentraciones únicas pobres.

        :param node_id: El ID del nodo a evaluar.
        :return: float, la puntuación heurística del nodo para un asentamiento inicial.
        """
        heuristic_score = 0.0
        if node_id is None or node_id < 0 or node_id >= len(self.board.nodes):
            return -float('inf') # Nodo inválido

        node_data = self.board.nodes[node_id]
        chrom_heur = self.chromosome["initial_placement_settlement"]
        dice_roll_to_dots = self._get_dice_roll_to_dots_map()

        # 1. Valor de Producción de Recursos
        node_resource_production_value = 0.0
        resource_types_at_node = set()
        numbers_at_node = set()
        terrain_types_count = {} # Para la penalización por concentración

        for terrain_idx in node_data['contacting_terrain']:
            terrain = self.board.terrain[terrain_idx]
            if terrain['terrain_type'] != MaterialConstants.DESERT:
                resource_type = terrain['terrain_type']
                resource_types_at_node.add(resource_type)
                terrain_types_count[resource_type] = terrain_types_count.get(resource_type, 0) + 1

                terrain_number = terrain['probability']
                if terrain_number != 7:
                    numbers_at_node.add(terrain_number)
                    prob_dots = dice_roll_to_dots.get(terrain_number, 0)
                    prob_real = prob_dots / 36.0
                    resource_weight = chrom_heur["resource_priority"].get(resource_type, 0.1)
                    exponent = chrom_heur["production_probability_exponent"]
                    node_resource_production_value += (prob_real ** exponent) * resource_weight
        
        heuristic_score += node_resource_production_value * chrom_heur["resource_production_base"]

        # 2. Bonus por Nuevos Tipos de Recurso (en el contexto inicial, todos son "nuevos")
        heuristic_score += len(resource_types_at_node) * chrom_heur["new_resource_type_bonus"]

        # 3. Bonus por Acceso a Puerto
        harbor_type = node_data['harbor']
        if harbor_type != HarborConstants.NONE:
            heuristic_score += chrom_heur["port_access_bonus"]
            if harbor_type != HarborConstants.ALL and harbor_type in resource_types_at_node:
                heuristic_score += chrom_heur["specific_port_match_bonus"]

        # 4. Bonus por Diversidad de Números
        heuristic_score += len(numbers_at_node) * chrom_heur["number_diversity_bonus"]

        # 5. Penalización por Concentración de un Solo Tipo de Recurso
        # Si todos los terrenos productivos son del mismo tipo.
        if len(resource_types_at_node) == 1 and len(node_data['contacting_terrain']) > 1:
             # Se podría refinar más esta penalización (ej. si es un recurso raro vs común)
            heuristic_score += chrom_heur["avoid_single_resource_concentration_penalty"]
        elif len(terrain_types_count) > 0 and max(terrain_types_count.values()) == len(node_data['contacting_terrain']) and len(resource_types_at_node) > 0 :
             # Si todos los terrenos son productivos y del mismo tipo
             heuristic_score += chrom_heur["avoid_single_resource_concentration_penalty"]


        return heuristic_score

    def _heuristic_initial_road_location(self, from_node_id, to_node_id, first_settlement_resources, first_settlement_numbers):
        """
        Calcula una puntuación heurística para la colocación de una carretera inicial.
        
        :param from_node_id: Nodo de inicio (donde se colocó el primer asentamiento).
        :param to_node_id: Nodo de destino potencial para la carretera.
        :param first_settlement_resources: set de MaterialConstants de los recursos del primer asentamiento.
        :param first_settlement_numbers: set de números de producción del primer asentamiento.
        :return: float, la puntuación heurística de la carretera.
        """
        heuristic_score = 0.0
        if to_node_id is None or to_node_id < 0 or to_node_id >= len(self.board.nodes) or \
           from_node_id is None or from_node_id < 0 or from_node_id >= len(self.board.nodes):
            return -float('inf')

        chrom_heur = self.chromosome["initial_placement_road"]
        dice_roll_to_dots = self._get_dice_roll_to_dots_map()

        # 1. Bonus por dirigirse a un potencial buen sitio para el segundo asentamiento
        # Evaluamos el nodo 'to_node_id' como si fuera un asentamiento inicial.
        # Asegurarnos de que to_node_id sea un lugar válido para un futuro asentamiento (vacío y cumple regla de distancia)
        if self.board.nodes[to_node_id]['player'] == -1 and self.board.empty_adjacent_nodes(to_node_id):
            potential_second_spot_value = self._heuristic_initial_settlement_location(to_node_id)
            heuristic_score += potential_second_spot_value * chrom_heur["to_second_potential_settlement_spot_bonus"]

        # 2. Bonus por expandir a variedad de recursos/números no cubiertos por el primer asentamiento
        resources_at_road_end = set()
        numbers_at_road_end = set()
        if self.board.nodes[to_node_id]['player'] == -1: # Solo si es un nodo libre
            for terrain_idx in self.board.nodes[to_node_id]['contacting_terrain']:
                terrain = self.board.terrain[terrain_idx]
                if terrain['terrain_type'] != MaterialConstants.DESERT:
                    resources_at_road_end.add(terrain['terrain_type'])
                    if terrain['probability'] != 7:
                        numbers_at_road_end.add(terrain['probability'])
            
            new_resources_by_road = resources_at_road_end - first_settlement_resources
            new_numbers_by_road = numbers_at_road_end - first_settlement_numbers
            heuristic_score += (len(new_resources_by_road) + len(new_numbers_by_road)) * chrom_heur["resource_variety_expansion_bonus"]

        # 3. Bonus general por expansión segura
        heuristic_score += chrom_heur["general_expansion_bonus"]
        
        # 4. Bonus por conectar a números de alta probabilidad no cubiertos por el primer asentamiento
        high_prob_numbers_gained = 0
        for num in numbers_at_road_end:
            if num not in first_settlement_numbers and dice_roll_to_dots.get(num, 0) >= 4: # 6, 8, 5, 9, 4, 10
                high_prob_numbers_gained += 1
        heuristic_score += high_prob_numbers_gained * chrom_heur["connect_to_high_prob_numbers_bonus"]

        return heuristic_score

    def on_game_start(self, board_instance):
        self.board = board_instance
        valid_nodes = [n['id'] for n in self.board.nodes if self.board.can_place_settlement(self.id, n['id'], is_initial_settlement=True)]

        if not valid_nodes:
            # Fallback si no hay nodos válidos (extremadamente improbable)
            # Esto podría indicar un error en la lógica de can_place_settlement o en el estado del tablero.
            # Devolvemos una opción aleatoria o fija para evitar un crash.
            all_nodes_ids = [n['id'] for n in self.board.nodes]
            fallback_node_id = random.choice(all_nodes_ids) if all_nodes_ids else 0
            # Intentar encontrar una carretera válida desde el fallback_node_id
            adj_nodes = self.board.nodes[fallback_node_id]['adjacent']
            fallback_road_to = random.choice(adj_nodes) if adj_nodes else (fallback_node_id + 1) % len(self.board.nodes) # Absurdo pero evita error
            return fallback_node_id, fallback_road_to


        best_settlement_node_id = -1
        max_settlement_score = -float('inf')

        scored_settlements = []
        for node_id in valid_nodes:
            score = self._heuristic_initial_settlement_location(node_id)
            scored_settlements.append({"id": node_id, "score": score})
        
        if not scored_settlements: # Si por alguna razón no se puntuó ninguno
             fallback_node_id = random.choice(valid_nodes)
             adj_nodes = self.board.nodes[fallback_node_id]['adjacent']
             fallback_road_to = random.choice(adj_nodes) if adj_nodes else (fallback_node_id + 1) % len(self.board.nodes)
             return fallback_node_id, fallback_road_to

        # Ordenar por puntuación y tomar el mejor
        best_settlement_options = sorted(scored_settlements, key=lambda x: x["score"], reverse=True)
        # Podríamos añadir una pizca de aleatoriedad aquí si hay varios "mejores" o para exploración.
        # Por ejemplo, elegir entre los N mejores. Para esta V1, tomamos el mejor absoluto.
        best_settlement_node_id = best_settlement_options[0]["id"]
        
        # Extraer información del mejor nodo de asentamiento para la heurística de carretera
        first_settlement_resources = set()
        first_settlement_numbers = set()
        for terrain_idx in self.board.nodes[best_settlement_node_id]['contacting_terrain']:
            terrain = self.board.terrain[terrain_idx]
            if terrain['terrain_type'] != MaterialConstants.DESERT:
                first_settlement_resources.add(terrain['terrain_type'])
                if terrain['probability'] != 7:
                    first_settlement_numbers.add(terrain['probability'])

        # Ahora, encontrar la mejor carretera desde este asentamiento
        possible_roads = []
        for neighbor_node_id in self.board.nodes[best_settlement_node_id]['adjacent']:
            if self.board.can_place_road(self.id, best_settlement_node_id, neighbor_node_id, is_initial_road=True):
                score = self._heuristic_initial_road_location(best_settlement_node_id, neighbor_node_id, first_settlement_resources, first_settlement_numbers)
                possible_roads.append({"to_node": neighbor_node_id, "score": score})
        
        if not possible_roads:
            # Fallback si no hay carreteras válidas (improbable si el asentamiento fue válido)
            # Tomar cualquier adyacente, o el primero si solo hay uno.
            adj_nodes = self.board.nodes[best_settlement_node_id]['adjacent']
            # Es vital que can_place_road con is_initial_road=True no falle si el nodo de asentamiento es válido.
            # Si adj_nodes está vacío, es un error de tablero.
            # Si no hay carreteras construibles, esto es un problema.
            # Para un fallback robusto, deberíamos re-evaluar asentamientos si no hay carreteras.
            # Por ahora, un random si falla todo.
            if adj_nodes:
                # Para el fallback, no podemos usar la heurística si falló, solo tomar uno.
                # En un caso real, esto indicaría un problema con `can_place_road` o el estado del tablero.
                # Se elige un vecino aleatorio como carretera si la heurística no produjo opciones válidas.
                road_to_node_id = random.choice(adj_nodes)
            else: # Nodo aislado, imposible en Catan estándar.
                road_to_node_id = (best_settlement_node_id + 1) % len(self.board.nodes) # Absurdo, pero evita crash
            return best_settlement_node_id, road_to_node_id

        best_road_options = sorted(possible_roads, key=lambda x: x["score"], reverse=True)
        best_road_to_node_id = best_road_options[0]["to_node"]

        return best_settlement_node_id, best_road_to_node_id

    def on_turn_start(self):
        """
        Se llama al inicio del turno, antes de tirar los dados.
        Principalmente para jugar cartas de Caballero si es estratégico (ej. mover ladrón de un tile importante).
        Otras cartas de desarrollo se suelen jugar en on_build_phase o on_turn_end.

        :return: DevelopmentCard (ej. DevelopmentCard.KNIGHT) a jugar o None si no se juega ninguna.
        """
        # Verificar si tenemos cartas de caballero jugables.
        # Asumimos que self.hand.development_cards es una instancia de DevelopmentCardsHand
        # y que tiene un método para ver las cartas o podemos iterar sobre ellas.
        # También necesitamos una forma de saber si una carta es jugable en este turno.
        # Por ahora, vamos a asumir que podemos obtener una lista de cartas jugables.

        # TODO: El GameDirector o GameManager es quien realmente valida si se puede jugar la carta.
        # El agente solo decide si quiere INTENTAR jugar una carta.

        # Prioridad 1: Jugar Caballero si es ventajoso
        if self.hand.has_development_card(DevelopmentCard.KNIGHT):
            # Comprobar si la carta de caballero es jugable (no comprada este turno)
            # Esta lógica podría estar en self.hand.development_cards.can_play(DevelopmentCard.KNIGHT, self.board.turn_number)
            # o ser manejada por el GameManager. Aquí asumimos que si la tiene, podría querer jugarla.
            # La validación final de si es *legal* jugarla la hará el GameManager.

            play_knight_score = 0
            knight_heuristics = self.chromosome.get("play_dev_card_heuristics", {})

            # Heurística 1: Ladrón es una amenaza inmediata
            thief_terrain_id = -1
            for t_idx, terrain_info in enumerate(self.board.terrain):
                if terrain_info['has_thief']:
                    thief_terrain_id = t_idx
                    break
            
            if thief_terrain_id != -1:
                is_my_production_blocked = False
                for node_id in self.board.terrain_node_config[thief_terrain_id]:
                    if self.board.nodes[node_id]['player'] == self.id:
                        # Podríamos ser más específicos: ¿es un número/recurso importante para mí?
                        # Por ahora, cualquier bloqueo en mis nodos es una amenaza.
                        is_my_production_blocked = True
                        break
                if is_my_production_blocked:
                    play_knight_score += knight_heuristics.get("knight_immediate_threat_bonus", 1.0)

            # Heurística 2: Potencial para tomar/mantener Ejército Más Grande
            # Esto es difícil de evaluar perfectamente sin el estado global del juego (GameManager).
            # Haremos una estimación simple: si jugar un caballero me acerca a 3 (o más que el actual poseedor),
            # y el cromosoma le da importancia.
            # Asumimos que `self.hand.development_cards.played_knights` existe o lo podemos inferir.
            # Esta información normalmente reside en AgentManager/GameManager, así que es una simplificación.
            # Por ahora, solo usaremos el peso del cromosoma como un indicador general de la voluntad de usarlo para esto.
            play_knight_score += knight_heuristics.get("knight_take_largest_army_bonus", 0.5) # Valor base por esta intención

            # TODO: Añadir un umbral o una comparación más directa si tuviéramos datos del GameManager.
            # Por ejemplo, si `play_knight_score > self.chromosome["play_dev_card_heuristics"].get("min_score_to_play_knight_on_start", 1.0)`
            # Por ahora, si hay algún bonus positivo, y tenemos un caballero, lo consideramos.
            # La decisión final de *cuál* carta jugar si hay varias opciones se simplifica a la primera que cumpla.

            min_score_to_play_knight = knight_heuristics.get("min_score_to_play_knight_on_start", 0.75) # Ejemplo de umbral del cromosoma

            if play_knight_score >= min_score_to_play_knight:
                # Antes de devolver, asegurarnos de que la carta es jugable este turno
                # (no comprada este mismo turno). Esta validación la debería hacer DevelopmentCardsHand o GameManager.
                # Aquí solo expresamos la intención.
                # print(f"Agente {self.id} decide jugar CABALLERO en on_turn_start (score: {play_knight_score})")
                return DevelopmentCard.KNIGHT 

        # Por ahora, no se considerará jugar otras cartas de desarrollo en on_turn_start
        # para mantener la lógica enfocada. Se podrían añadir más adelante si es necesario.

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
        if self.hand.resources.has_more(cost_card):
            heuristic_val = self._heuristic_dev_card(self.board)
            score = heuristic_val * self.chromosome["build_actions"][BuildConstants.CARD]
            possible_actions.append({"type": BuildConstants.CARD, "score": score, "details": None, "cost": cost_card})

        # 2. Evaluar Construir Carretera
        cost_road = Materials.from_iterable(BuildMaterialsConstants[BuildConstants.ROAD])
        if self.hand.resources.has_more(cost_road):
            valid_roads = self.board.valid_road_nodes(self.id) # Usamos el método confirmado
            for road_option in valid_roads:
                from_node = road_option['starting_node']
                to_node = road_option['finishing_node']
                # Adicionalmente, verificar que no exista ya una carretera aquí por si valid_road_nodes no lo hace
                # (aunque build_road sí lo comprueba, es bueno ser defensivo si la heurística es costosa)
                road_already_exists = False
                for existing_road in self.board.nodes[from_node]['roads']:
                    if existing_road['node_id'] == to_node:
                        road_already_exists = True
                        break
                if road_already_exists:
                    continue # Saltar esta opción si la carretera ya existe

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
        num_settlements = 0
        for node_data in self.board.nodes:
            if node_data['player'] == self.id and not node_data['has_city']:
                 num_settlements += 1
        # num_settlements = len([n for n in self.board.nodes if self.board.nodes[n]['player'] == self.id and not self.board.nodes[n]['has_city']])
        if self.hand.resources.has_more(cost_town) and num_settlements < 5:
            valid_nodes_for_town = self.board.valid_town_nodes(self.id) # Usamos el método confirmado
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
        num_cities = 0
        for node_data in self.board.nodes:
            if node_data['player'] == self.id and node_data['has_city']:
                 num_cities += 1        
        # num_cities = len([n for n in self.board.nodes if self.board.nodes[n]['player'] == self.id and self.board.nodes[n]['has_city']])
        if self.hand.resources.has_more(cost_city) and num_cities < 4:
            valid_nodes_for_city_upgrade = self.board.valid_city_nodes(self.id) # Usamos el método confirmado
            for node_id in valid_nodes_for_city_upgrade: 
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

    def _heuristic_dev_card(self, board_instance):
        """
        Calcula el valor heurístico de comprar una carta de desarrollo.
        Dado que no tenemos acceso garantizado al GameManager/AgentManager,
        esta heurística será más simple y se basará en el cromosoma.

        Args:
            board_instance (Board): La instancia actual del tablero.

        Returns:
            float: El valor heurístico de comprar una carta de desarrollo.
        """
        score = self.chromosome["dev_card_heuristics"]["base_value"]

        # Bonus por potencial de Caballero. Como no conocemos el estado del Ejército Más Grande,
        # este es un valor más abstracto.
        score += self.chromosome["dev_card_heuristics"]["knight_bonus"]

        # Bonus por Punto de Victoria. Como no conocemos el estado de la partida (ej. PVs actuales),
        # este es un valor más abstracto.
        score += self.chromosome["dev_card_heuristics"]["victory_point_bonus"] # Cambiado de victory_point_bonus_late_game a un genérico

        # Otros posibles bonus (Monopolio, Construcción de Carreteras, Año de la Abundancia)
        # podrían tener sus propios pesos en el cromosoma si se desea mayor granularidad.
        # Por ahora, están implícitos en el base_value o podrían añadirse.
        # score += self.chromosome["dev_card_heuristics"]["monopoly_bonus"] # Ejemplo
        # score += self.chromosome["dev_card_heuristics"]["road_building_bonus"] # Ejemplo
        # score += self.chromosome["dev_card_heuristics"]["year_of_plenty_bonus"] # Ejemplo
        
        # Considerar si el jugador tiene suficientes recursos para comprar otras cosas.
        # Si el jugador está muy limitado en recursos para construir, una carta de desarrollo
        # podría ser una opción relativamente mejor. Esta lógica es más compleja y podría
        # integrarse en _get_best_build_action.

        # Logging para depuración (opcional, eliminar en producción)
        # print(f"Agente {self.id}: Heurística DevCard calculada: {score}")
        # print(f"  Base: {self.chromosome['dev_card_heuristics']['base_value']}")
        # print(f"  Knight Bonus: {self.chromosome['dev_card_heuristics']['knight_bonus']}")
        # print(f"  VP Bonus: {self.chromosome['dev_card_heuristics']['victory_point_bonus']}")

        return score

    def _heuristic_road_location(self, from_node_id, to_node_id):
        """ 
        Calcula una puntuación heurística para construir una carretera entre from_node_id y to_node_id.
        Considera varios factores estratégicos ponderados por el cromosoma:
        1. Dirigirse hacia un buen lugar para un futuro poblado.
        2. Expandir la red del jugador hacia un nodo desocupado.
        3. Contribuir al camino más largo (implementación actual simplificada).
        4. Ganar acceso a un nuevo tipo de puerto.
        5. Expandirse hacia nuevos terrenos/recursos.

        :param from_node_id: El ID del nodo de inicio de la carretera.
        :param to_node_id: El ID del nodo de fin de la carretera.
        :return: Un valor flotante representando la puntuación heurística de la carretera.
        """
        heuristic_score = 0.0
        road_heur_weights = self.chromosome["road_heuristics"]

        # 1. Bonus por Dirigirse a un Potencial Punto de Asentamiento
        if self._is_node_potential_settlement_spot(to_node_id):
            # Usamos la heurística de poblado para evaluar el valor del nodo destino
            potential_settlement_value = self._heuristic_settlement_location(to_node_id)
            heuristic_score += potential_settlement_value * road_heur_weights["to_potential_settlement_spot_bonus"]

        # 2. Bonus por Expansión de Red (hacia nodo desocupado)
        if self.board.nodes[to_node_id]['player'] == -1:
            heuristic_score += road_heur_weights["connects_to_own_settlement_bonus"]

        # 3. Bonus por Contribución al Camino Más Largo (Implementación Simplificada V1)
        # TODO: Implementar una función robusta _calculate_player_longest_road(player_id, board, prospective_road=None)
        # Por ahora, un bonus simple si expande la red a un nodo seguro (no de oponente) y el jugador no tiene ya el max de carreteras.
        # Esta es una gran simplificación.
        player_owns_from_node_or_connected_road = False
        if self.board.nodes[from_node_id]['player'] == self.id:
            player_owns_from_node_or_connected_road = True
        else:
            for road in self.board.nodes[from_node_id]['roads']:
                if road['player_id'] == self.id:
                    player_owns_from_node_or_connected_road = True
                    break
        
        if player_owns_from_node_or_connected_road and \
           (self.board.nodes[to_node_id]['player'] == -1 or self.board.nodes[to_node_id]['player'] == self.id):
            # Podríamos añadir una comprobación de si el jugador está activamente buscando el camino más largo
            # o si ya lo tiene y esta carretera lo asegura/extiende.
            # Por ahora, un bonus simple por extensión segura.
            heuristic_score += road_heur_weights["longest_road_contribution_bonus"] * 0.25 # Factor de reducción por simplificación

        # 4. Bonus por Acceso a Puerto
        port_at_to_node = self.board.nodes[to_node_id]['harbor']
        if port_at_to_node != HarborConstants.NONE:
            # check_for_player_harbors devuelve el tipo de puerto si el jugador lo tiene, o NONE.
            # Si el puerto en to_node es específico (ej. WOOD) y el jugador NO tiene ESE puerto específico:
            if port_at_to_node != HarborConstants.ALL and \
               self.board.check_for_player_harbors(self.id, material_harbor=port_at_to_node) == HarborConstants.NONE:
                heuristic_score += road_heur_weights["port_access_bonus"]
            # Si el puerto en to_node es general (ALL) y el jugador NO tiene un puerto general:
            elif port_at_to_node == HarborConstants.ALL and \
                 self.board.check_for_player_harbors(self.id, material_harbor=HarborConstants.ALL) == HarborConstants.NONE:
                 heuristic_score += road_heur_weights["port_access_bonus"] # Mismo bonus, o podría ser diferente

        # 5. Bonus por Expansión a Nuevos Terrenos
        terrains_player_has_access_to = self._get_player_accessible_terrains()
        terrains_at_to_node = self.board.nodes[to_node_id]['contacting_terrain']
        
        count_newly_accessible_productive_terrains = 0
        for terrain_idx in terrains_at_to_node:
            if terrain_idx not in terrains_player_has_access_to and \
               self.board.terrain[terrain_idx]['terrain_type'] != MaterialConstants.DESERT:
                count_newly_accessible_productive_terrains += 1
        
        if count_newly_accessible_productive_terrains > 0:
            heuristic_score += count_newly_accessible_productive_terrains * road_heur_weights["expansion_to_new_terrain_bonus"]

        return heuristic_score

    def _is_node_potential_settlement_spot(self, node_id):
        """
        Verifica si un nodo es un lugar potencial para un nuevo asentamiento (para cualquier jugador).
        Comprueba si el nodo está vacío y cumple la regla de distancia.
        :param node_id: El ID del nodo a verificar.
        :return: True si es un lugar potencial, False en caso contrario.
        """
        if self.board.nodes[node_id]['player'] == -1 and self.board.empty_adjacent_nodes(node_id):
            return True
        return False

    def _get_player_accessible_terrains(self):
        """
        Obtiene un conjunto de todos los índices de terreno a los que el agente
        actualmente tiene acceso a través de sus poblados y ciudades.
        :return: set de IDs de terrenos accesibles.
        """
        accessible_terrains = set()
        for node_data in self.board.nodes:
            if node_data['player'] == self.id:
                for terrain_idx in node_data['contacting_terrain']:
                    if self.board.terrain[terrain_idx]['terrain_type'] != MaterialConstants.DESERT:
                        accessible_terrains.add(terrain_idx)
        return accessible_terrains

    def _heuristic_settlement_location(self, node_id):
        """ 
        Calcula una puntuación heurística para la construcción de un poblado en un nodo específico.
        Esta heurística considera:
        1. El valor de producción de recursos del nodo (tipos de recurso, probabilidad, pesos del cromosoma).
        2. Bonus por acceder a nuevos tipos de recursos que el agente aún no produce.
        3. Bonus por acceso a puertos (general y específico si coincide con recursos del nodo).
        4. Bonus por la diversidad de números de producción de los terrenos adyacentes.

        :param node_id: El ID del nodo a evaluar.
        :return: Un valor flotante representando la puntuación heurística del nodo para un poblado.
        """
        heuristic_score = 0.0
        node_data = self.board.nodes[node_id]

        # Mapeo de números de dado a "puntos" de probabilidad (de 36 posibles resultados con 2d6)
        # El 7 no produce recursos directamente por tirada.
        dice_roll_to_dots = {
            2: 1, 3: 2, 4: 3, 5: 4, 6: 5,
            7: 0, # El ladrón se mueve, no hay producción directa por el 7.
            8: 5, 9: 4, 10: 3, 11: 2, 12: 1
        }

        # --- 1. Valor de Producción de Recursos del Nodo ---
        node_resource_production_value = 0.0
        contacting_terrain_indices = node_data['contacting_terrain']
        resource_types_at_node = set()
        numbers_at_node = set()

        for terrain_idx in contacting_terrain_indices:
            terrain = self.board.terrain[terrain_idx]
            if terrain['terrain_type'] != MaterialConstants.DESERT: # El desierto no produce
                resource_type = terrain['terrain_type']
                resource_types_at_node.add(resource_type)
                
                terrain_number = terrain['probability'] # Este es el número que debe salir en los dados
                if terrain_number != 7: # Solo consideramos números que producen
                    numbers_at_node.add(terrain_number)
                    
                    prob_dots = dice_roll_to_dots.get(terrain_number, 0)
                    prob_real = prob_dots / 36.0
                    
                    resource_weight = self.chromosome["settlement_heuristics"]["resource_priority"].get(resource_type, 0.1)
                    exponent = self.chromosome["settlement_heuristics"]["production_probability_exponent"]
                    
                    node_resource_production_value += (prob_real ** exponent) * resource_weight
        
        heuristic_score += node_resource_production_value * self.chromosome["settlement_heuristics"]["resource_value_base"]

        # --- 2. Bonus por Nuevos Tipos de Recurso ---
        # Primero, determinamos los recursos que el agente ya produce.
        # Esto es una simplificación; una forma más precisa sería ver los terrenos adyacentes a todos sus asentamientos.
        # Por ahora, lo mantenemos simple. Idealmente, el agente tendría una lista actualizada de los recursos a los que tiene acceso.
        # Aquí, vamos a suponer que el agente quiere diversificar con CADA nuevo poblado.
        # Para una evaluación más precisa, necesitaríamos saber a qué recursos ya tiene acceso el agente.
        # Por el momento, este bonus se aplicará si el nodo ofrece recursos.
        # Una mejora sería:
        # agent_produced_resources = set()
        # for n_idx, n_info in enumerate(self.board.nodes):
        #    if n_info['player'] == self.id:
        #        for t_idx in n_info['contacting_terrain']:
        #            if self.board.terrain[t_idx]['terrain_type'] != MaterialConstants.DESERT:
        # agent_produced_resources.add(self.board.terrain[t_idx]['terrain_type'])
        # new_resources_from_this_node = resource_types_at_node - agent_produced_resources
        # heuristic_score += len(new_resources_from_this_node) * self.chromosome["settlement_heuristics"]["new_resource_type_bonus"]
        
        # Simplificación para este paso: Asumimos que cualquier diversidad es buena.
        # Contamos los tipos únicos de recursos en este nodo.
        # Un enfoque más robusto requeriría que el agente "recuerde" a qué recursos ya tiene acceso.
        # Por ahora, recompensamos la diversidad local del nodo.
        # Si quisiéramos ser más precisos, necesitaríamos una forma de que el agente sepa a qué recursos ya tiene acceso.
        # Para esta implementación, damos un bonus por el simple hecho de que el nodo tenga recursos diversos.
        # Consideraremos un bonus por cada recurso único que ofrece el nodo, asumiendo que la diversificación es buena.
        # Esto se puede refinar más tarde para considerar solo los *nuevos* para el agente.
        # Por ahora, la heurística de "resource_priority" ya pondera los tipos de recursos.
        # El "new_resource_type_bonus" se aplicará de forma más genérica aquí.
        # Si el nodo ofrece al menos un recurso no desértico, le damos un pequeño bonus.
        # Esto se puede refinar más adelante para una verdadera detección de "nuevos" recursos.
        if resource_types_at_node: # Si el nodo tiene al menos un recurso productivo
             # Para una implementación más precisa de "nuevos" recursos:
            current_player_resources = set()
            for n_data in self.board.nodes: # Iterar sobre la lista de nodos
                if n_data['player'] == self.id:
                    for t_idx in n_data['contacting_terrain']:
                        terrain_info = self.board.terrain[t_idx]
                        if terrain_info['terrain_type'] != MaterialConstants.DESERT:
                            current_player_resources.add(terrain_info['terrain_type'])
            
            newly_accessed_resources = resource_types_at_node - current_player_resources
            heuristic_score += len(newly_accessed_resources) * self.chromosome["settlement_heuristics"]["new_resource_type_bonus"]


        # --- 3. Bonus por Acceso a Puerto ---
        harbor_type = node_data['harbor']
        if harbor_type != HarborConstants.NONE:
            heuristic_score += self.chromosome["settlement_heuristics"]["port_access_bonus"]
            
            # Bonus si el puerto es específico y coincide con algún recurso del nodo
            if harbor_type != HarborConstants.ALL: # ALL es el puerto genérico 3:1
                # harbor_type directamente es el MaterialConstant del puerto (0 para Cereal, 1 Mineral, etc.)
                if harbor_type in resource_types_at_node:
                    heuristic_score += self.chromosome["settlement_heuristics"]["specific_port_match_bonus"]

        # --- 4. Bonus por Diversidad de Números ---
        # numbers_at_node ya contiene los números únicos (no 7) de los terrenos productivos.
        heuristic_score += len(numbers_at_node) * self.chromosome["settlement_heuristics"]["number_diversity_bonus"]
        
        return heuristic_score

    def _heuristic_city_location(self, node_id):
        """ 
        Calcula una puntuación heurística para mejorar un poblado a ciudad en un nodo específico.
        El valor principal de una ciudad radica en la duplicación de la producción de recursos.
        Esta heurística utiliza los pesos específicos para ciudades del cromosoma.

        :param node_id: El ID del nodo donde se encuentra el poblado a mejorar.
        :return: Un valor flotante representando la puntuación heurística del nodo para una ciudad.
        """
        heuristic_score = 0.0
        node_data = self.board.nodes[node_id]

        # Mapeo de números de dado a "puntos" de probabilidad (de 36 posibles resultados con 2d6)
        dice_roll_to_dots = {
            2: 1, 3: 2, 4: 3, 5: 4, 6: 5,
            7: 0, # El ladrón se mueve, no hay producción directa por el 7.
            8: 5, 9: 4, 10: 3, 11: 2, 12: 1
        }

        city_chrom_heuristics = self.chromosome["city_heuristics"]
        node_resource_production_value = 0.0
        contacting_terrain_indices = node_data['contacting_terrain']

        for terrain_idx in contacting_terrain_indices:
            terrain = self.board.terrain[terrain_idx]
            if terrain['terrain_type'] != MaterialConstants.DESERT: # El desierto no produce
                resource_type = terrain['terrain_type']
                terrain_number = terrain['probability'] # Número que debe salir en los dados

                if terrain_number != 7: # Solo consideramos números que producen
                    prob_dots = dice_roll_to_dots.get(terrain_number, 0)
                    prob_real = prob_dots / 36.0
                    
                    resource_weight = city_chrom_heuristics["resource_priority"].get(resource_type, 0.1)
                    exponent = city_chrom_heuristics["production_probability_exponent"]
                    
                    # Una ciudad duplica la producción, por eso el * 2
                    production_from_terrain = 2 * (prob_real ** exponent) * resource_weight
                    node_resource_production_value += production_from_terrain
        
        heuristic_score = node_resource_production_value * city_chrom_heuristics["resource_value_base"]
        
        return heuristic_score

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