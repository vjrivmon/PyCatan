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
                    MaterialConstants.WOOL: 0.7, MaterialConstants.CEREAL: 0.9, MaterialConstants.MINERAL: 1.0
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
                    MaterialConstants.WOOL: 0.6, MaterialConstants.CEREAL: 1.0, MaterialConstants.MINERAL: 1.2
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
                    MaterialConstants.WOOL: 0.8, MaterialConstants.CEREAL: 0.9, MaterialConstants.MINERAL: 0.7
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
                    MaterialConstants.WOOL: 0.7, MaterialConstants.CEREAL: 1.0, MaterialConstants.MINERAL: 1.0
                },
                "target_opponent_with_most_vps_bias": 0.5, # Un pequeño extra si se puede identificar al líder
                "avoid_own_nodes_penalty": -5.0, # Fuerte penalización por bloquearse a sí mismo
                "randomness_factor": 0.1 # Para evitar predictibilidad total
            },
            # Pesos para descartar cartas
            "discard_heuristics": {
                "resource_value_priority": { # Cuanto más bajo, más probable descartar
                    MaterialConstants.WOOD: 0.8, MaterialConstants.CLAY: 0.8,
                    MaterialConstants.WOOL: 1.0, # La lana a menudo es más fácil de descartar
                    MaterialConstants.CEREAL: 0.7, MaterialConstants.MINERAL: 0.6
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
                    MaterialConstants.WOOL: 0.8, MaterialConstants.CEREAL: 0.5, MaterialConstants.MINERAL: 0.5
                },
                "resource_needed_importance": { # Qué tan importante es obtener un recurso necesitado
                     MaterialConstants.WOOD: 1.2, MaterialConstants.CLAY: 1.2,
                    MaterialConstants.WOOL: 1.0, MaterialConstants.CEREAL: 1.3, MaterialConstants.MINERAL: 1.3
                },
                "bank_trade_ratio_modifier": -0.2, # Penalización por comerciar 4:1 con el banco
                "port_trade_ratio_modifier": -0.1, # Penalización menor por comerciar 3:1 o 2:1 con puerto
                "accept_offer_resource_gain_factor": 1.0,
                "accept_offer_fairness_threshold": 0.8, # Si la oferta es al menos 80% "justa" en valor
                "min_score_for_self_initiated_trade": 0.5
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

    def _is_terrain_desert(self, terrain_dict):
        """
        Determina si un terreno es desértico de forma robusta.

        Un terreno se considera desierto si:
        1. El atributo `MaterialConstants.DESERT` está definido y el tipo de terreno
           coincide con él.
        2. El atributo `MaterialConstants.DESERT` NO está definido Y la probabilidad
           del terreno es 7 (heurística común para el desierto).

        Args:
            terrain_dict (dict): El diccionario de información del terreno.

        Returns:
            bool: True si el terreno se considera desértico, False en caso contrario.
        """
        if hasattr(MaterialConstants, 'DESERT'):
            # Si MaterialConstants.DESERT existe, esa es la fuente autoritativa.
            return terrain_dict.get('terrain_type') == MaterialConstants.DESERT
        else:
            # Si MaterialConstants.DESERT no existe, usamos la heurística de la probabilidad 7.
            return terrain_dict.get('probability') == 7

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
            # MODIFICADO: Usar el método auxiliar _is_terrain_desert
            if not self._is_terrain_desert(terrain):
                resource_type = terrain.get('terrain_type')
                if resource_type is not None: # Asegurar que el tipo de terreno existe
                    resource_types_at_node.add(resource_type)

                terrain_number = terrain.get('probability') # Usar .get para seguridad
                if terrain_number is not None and terrain_number != 7: # Excluir 7 explícitamente
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
                # MODIFICADO: Usar el método auxiliar _is_terrain_desert
                if not self._is_terrain_desert(terrain):
                    resources_at_road_end.add(terrain.get('terrain_type'))
                    if terrain.get('probability') != 7:
                        numbers_at_road_end.add(terrain.get('probability'))
            
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
        # MODIFICADO: Usar valid_starting_nodes() para obtener los nodos válidos para la colocación inicial.
        valid_nodes_ids = self.board.valid_starting_nodes()

        if not valid_nodes_ids:
            all_nodes_ids = [n['id'] for n in self.board.nodes]
            fallback_node_id = random.choice(all_nodes_ids) if all_nodes_ids else 0
            adj_nodes = self.board.nodes[fallback_node_id]['adjacent']
            fallback_road_to = random.choice(adj_nodes) if adj_nodes else (fallback_node_id + 1) % len(self.board.nodes)
            return fallback_node_id, fallback_road_to

        best_settlement_node_id = -1
        max_settlement_score = -float('inf')

        scored_settlements = []
        for node_id in valid_nodes_ids:
            score = self._heuristic_initial_settlement_location(node_id)
            scored_settlements.append({"id": node_id, "score": score})
        
        if not scored_settlements: 
             fallback_node_id = random.choice(valid_nodes_ids)
             adj_nodes = self.board.nodes[fallback_node_id]['adjacent']
             fallback_road_to = random.choice(adj_nodes) if adj_nodes else (fallback_node_id + 1) % len(self.board.nodes)
             return fallback_node_id, fallback_road_to

        best_settlement_options = sorted(scored_settlements, key=lambda x: x["score"], reverse=True)
        best_settlement_node_id = best_settlement_options[0]["id"]
        
        first_settlement_resources = set()
        first_settlement_numbers = set()
        for terrain_idx in self.board.nodes[best_settlement_node_id]['contacting_terrain']:
            terrain = self.board.terrain[terrain_idx]
            if not self._is_terrain_desert(terrain):
                resource_type = terrain.get('terrain_type')
                if resource_type is not None: 
                    first_settlement_resources.add(resource_type)
                terrain_number = terrain.get('probability')
                if terrain_number is not None and terrain_number != 7:
                    first_settlement_numbers.add(terrain_number)

        # Ahora, encontrar la mejor carretera desde este asentamiento
        possible_roads = []
        # INICIO DE LA SECCIÓN MODIFICADA PARA VALIDAR CARRETERA INICIAL
        for neighbor_node_id in self.board.nodes[best_settlement_node_id]['adjacent']:
            is_road_path_free = True
            # Verificar si ya existe una carretera entre best_settlement_node_id y neighbor_node_id
            # en la lista de carreteras del nodo de origen.
            for road_segment in self.board.nodes[best_settlement_node_id]['roads']:
                if road_segment['node_id'] == neighbor_node_id:
                    is_road_path_free = False
                    break
            
            if is_road_path_free:
                # Adicionalmente, verificar en la lista de carreteras del nodo destino
                # para asegurar consistencia y que no haya una carretera en la dirección opuesta.
                for road_segment in self.board.nodes[neighbor_node_id]['roads']:
                    if road_segment['node_id'] == best_settlement_node_id:
                        is_road_path_free = False
                        break
            
            if is_road_path_free:
                # Si el camino está libre, se considera una carretera válida para la heurística.
                # La lógica de la carretera inicial (is_initial_road=True) se maneja aquí
                # al no verificar costos de recursos y al partir del asentamiento inicial.
                score = self._heuristic_initial_road_location(best_settlement_node_id, neighbor_node_id, first_settlement_resources, first_settlement_numbers)
                possible_roads.append({"to_node": neighbor_node_id, "score": score})
        # FIN DE LA SECCIÓN MODIFICADA

        if not possible_roads:
            adj_nodes = self.board.nodes[best_settlement_node_id]['adjacent']
            if adj_nodes:
                road_to_node_id = random.choice(adj_nodes)
            else: 
                road_to_node_id = (best_settlement_node_id + 1) % len(self.board.nodes)
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
        # Solo proceder si self.hand tiene el atributo 'development_cards' y este, a su vez,
        # tiene el método 'has_development_card'.
        can_check_dev_cards = hasattr(self.hand, 'development_cards') and \
                              hasattr(self.hand.development_cards, 'has_development_card')

        if can_check_dev_cards and self.hand.development_cards.has_development_card(DevelopmentCard.KNIGHT):
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
        Se llama al inicio de la fase de comercio para realizar una oferta (con banco/puerto).
        Evalúa necesidades y excedentes para proponer el mejor intercambio posible.

        :return: Dict {'gives': material_id, 'receives': material_id, 'quantity_gives': int, 'quantity_receives': 1} 
                 o None si no se propone ningún intercambio.
        """
        best_trade_offer = None
        max_trade_score = -float('inf')
        
        trade_heuristics = self.chromosome.get("trade_heuristics", {})
        if not trade_heuristics: # Si no hay heurísticas de comercio, no hacer nada.
            return None

        # Definir el orden de los materiales según la NamedTuple Materials y las constantes.
        # MaterialConstants: CEREAL=0, MINERAL=1, CLAY=2, WOOD=3, WOOL=4
        # NamedTuple Materials(cereal, mineral, clay, wood, wool)
        ordered_material_constants = [
            MaterialConstants.CEREAL, 
            MaterialConstants.MINERAL, 
            MaterialConstants.CLAY, 
            MaterialConstants.WOOD, 
            MaterialConstants.WOOL
        ]
        # Mapeo inverso para facilitar la obtención del índice desde la constante
        material_to_index_map = {const: i for i, const in enumerate(ordered_material_constants)}

        needed_resources = []
        # Esta lista se usaba para crear `all_material_ids`, pero ahora tenemos ordered_material_constants
        # all_material_ids = [MaterialConstants.WOOD, MaterialConstants.CLAY, MaterialConstants.WOOL, MaterialConstants.CEREAL, MaterialConstants.MINERAL]
        
        next_build_goal_cost = None
        num_settlements = sum(1 for n_data in self.board.nodes if n_data['player'] == self.id and not n_data['has_city'])
        num_cities = sum(1 for n_data in self.board.nodes if n_data['player'] == self.id and n_data['has_city'])

        if num_settlements > 0 and num_cities < 4:
            next_build_goal_cost = self._get_cost_of_buildable(BuildConstants.CITY)
        elif num_settlements < 5:
            next_build_goal_cost = self._get_cost_of_buildable(BuildConstants.TOWN)
        else: 
            next_build_goal_cost = self._get_cost_of_buildable(BuildConstants.CARD)
        
        if next_build_goal_cost:
            # next_build_goal_cost es un objeto Materials (NamedTuple)
            # Iteramos sobre él usando enumerate para obtener el índice y la cantidad (count_needed)
            for i, count_needed in enumerate(next_build_goal_cost):
                if count_needed > 0: # Solo si se necesita este material para el objetivo
                    material_id = ordered_material_constants[i] # El MaterialConstant actual
                    
                    # self.hand.resources es también un objeto Materials. Accedemos por índice.
                    count_has = self.hand.resources[i]
                    
                if count_has < count_needed:
                        for _ in range(count_needed - count_has): 
                            needed_resources.append(material_id)
        
        if not needed_resources: 
            # Rellenar con lo que menos tengamos si no hay un objetivo claro
            # o ya tenemos todo para él.
            # Crear una lista de tuplas (cantidad, material_id)
            hand_material_quantities = []
            for i, count_in_hand in enumerate(self.hand.resources):
                hand_material_quantities.append((count_in_hand, ordered_material_constants[i]))
            
            hand_material_quantities.sort(key=lambda item: item[0]) # Ordenar por cantidad ascendente

            # Añadir los que no tiene en absoluto
            for material_const in ordered_material_constants:
                idx = material_to_index_map[material_const]
                if self.hand.resources[idx] == 0:
                    needed_resources.append(material_const)
            
            # Añadir los que tiene menos hasta tener al menos 2 tipos en la lista de necesitados
            for _, mat_id_sorted in hand_material_quantities:
                if len(needed_resources) < 2 and mat_id_sorted not in needed_resources:
                    needed_resources.append(mat_id_sorted)
                elif len(needed_resources) >= 2:
                    break
            
            if not needed_resources: 
                 needed_resources = random.sample(ordered_material_constants, min(2, len(ordered_material_constants)))


        # 2. Iterar sobre los recursos que podríamos dar (excedentes)
        # self.hand.resources es un objeto Materials.
        for i, count_we_have in enumerate(self.hand.resources):
            if count_we_have == 0: continue # No podemos dar lo que no tenemos

            material_to_give_id = ordered_material_constants[i]
            if material_to_give_id is None: continue # Salvaguarda, aunque no debería ocurrir

            qty_to_give, qty_to_receive, port_type = self._get_best_trade_ratio(material_to_give_id)
            
            if count_we_have >= qty_to_give: 
                for material_to_receive_id in needed_resources:
                    if material_to_receive_id is None or material_to_receive_id == material_to_give_id: 
                        continue

                    current_trade_score = trade_heuristics.get("willingness_to_trade_general", 0.5)
                    
                    surplus_factor = count_we_have - qty_to_give 
                    surplus_value = surplus_factor * trade_heuristics.get("resource_surplus_importance", {}).get(material_to_give_id, 0.1)
                    current_trade_score += surplus_value

                    need_intensity = needed_resources.count(material_to_receive_id)
                    needed_value = need_intensity * trade_heuristics.get("resource_needed_importance", {}).get(material_to_receive_id, 1.0)
                    current_trade_score += needed_value

                    if qty_to_give == 4:
                        current_trade_score += trade_heuristics.get("bank_trade_ratio_modifier", -0.2)
                    elif qty_to_give == 3 or qty_to_give == 2:
                        current_trade_score += trade_heuristics.get("port_trade_ratio_modifier", -0.1)
                    
                    if current_trade_score > max_trade_score:
                        max_trade_score = current_trade_score
                        best_trade_offer = {
                            'gives': material_to_give_id,
                            'receives': material_to_receive_id,
                            'quantity_gives': qty_to_give,
                            'quantity_receives': qty_to_receive 
                        }
        
        min_score_for_trade = trade_heuristics.get("min_score_for_self_initiated_trade", 0.5) 
        if max_trade_score > min_score_for_trade and best_trade_offer is not None:
            return best_trade_offer
        
        return None

    def on_trade_offer(self, board_instance, incoming_trade_offer=None, player_making_offer=None):
        """
        Gestiona la recepción de una oferta de comercio de otro jugador.

        Esta función se invoca cuando otro jugador propone un intercambio. El agente
        evalúa la oferta basándose en las heurísticas de comercio definidas en su
        cromosoma genético y decide si aceptarla o rechazarla. Actualmente, no
        implementa la capacidad de realizar contraofertas, centrándose en la
        aceptación o el rechazo directo.

        Args:
            board_instance (Board): La instancia actual del tablero, que proporciona
                                    el contexto del estado del juego.
            incoming_trade_offer (TradeOffer, optional): El objeto TradeOffer que
                                                        representa la oferta recibida.
                                                        Por defecto es None.
            player_making_offer (int, optional): El ID del jugador que realiza la
                                                 oferta. Por defecto es None.

        Returns:
            bool: True si el agente decide aceptar la oferta, False en caso contrario.
        """
        self.board = board_instance  # Actualiza la referencia al tablero

        # Validación inicial de la oferta
        if not incoming_trade_offer or not incoming_trade_offer.gives or not incoming_trade_offer.receives:
            return False  # La oferta es inválida o incompleta

        # Definir el orden de los materiales según la NamedTuple Materials y las constantes.
        # MaterialConstants: CEREAL=0, MINERAL=1, CLAY=2, WOOD=3, WOOL=4
        # NamedTuple Materials(cereal, mineral, clay, wood, wool)
        # Este array mapea el índice de la NamedTuple al MaterialConstant correspondiente.
        ordered_material_constants = [
            MaterialConstants.CEREAL, 
            MaterialConstants.MINERAL, 
            MaterialConstants.CLAY, 
            MaterialConstants.WOOD, 
            MaterialConstants.WOOL
        ]

        # Verificar si el agente posee los recursos solicitados en la oferta
        # incoming_trade_offer.gives es un objeto Materials (NamedTuple).
        # Iteramos sobre sus valores usando enumerate para obtener el índice y la cantidad.
        # El índice 'i' corresponde a la posición en la NamedTuple y en ordered_material_constants.
        for i, quantity_demanded in enumerate(incoming_trade_offer.gives):
            if quantity_demanded > 0: # Solo procesar si se demanda algo de este material
                # self.hand.resources es también un objeto Materials. Accedemos por índice.
                if self.hand.resources[i] < quantity_demanded:
                    return False  # No dispone de suficientes recursos para el intercambio

        # Cargar las heurísticas de comercio del cromosoma
        trade_heuristics = self.chromosome.get("trade_heuristics", {})
        if not trade_heuristics:
            return False  # No hay heurísticas definidas para tomar una decisión

        value_receives = 0  # Valor percibido de los recursos a recibir
        cost_gives = 0      # Costo percibido de los recursos a entregar

        # Calcular el valor de los recursos que el agente recibiría
        needed_importance = trade_heuristics.get("resource_needed_importance", {})
        # Iterar sobre incoming_trade_offer.receives (objeto Materials)
        for i, quantity_received in enumerate(incoming_trade_offer.receives):
            if quantity_received > 0:
                material_id = ordered_material_constants[i] # Obtener el MaterialConstant correcto
                value_receives += quantity_received * needed_importance.get(material_id, 1.0)

        # Calcular el costo de los recursos que el agente entregaría
        discard_value_priority = self.chromosome.get("discard_heuristics", {}).get("resource_value_priority", {})
        surplus_importance = trade_heuristics.get("resource_surplus_importance", {})

        # Iterar sobre incoming_trade_offer.gives (objeto Materials)
        for i, quantity_given in enumerate(incoming_trade_offer.gives):
            if quantity_given > 0:
                material_id = ordered_material_constants[i] # Obtener el MaterialConstant correcto
                base_cost_factor = 1.5 - discard_value_priority.get(material_id, 0.75)
                cost = quantity_given * base_cost_factor

                # Ajuste por excedente:
                # self.hand.resources es un objeto Materials. Accedemos por índice.
                current_surplus = self.hand.resources[i] - quantity_given
                
                surplus_modifier = current_surplus * surplus_importance.get(material_id, 0.05)
                cost -= surplus_modifier
            
                cost_gives += max(0.05, cost) # Asegurar un costo mínimo

        # Calcular la puntuación neta de la oferta
        trade_score = value_receives - cost_gives
        
        trade_score *= trade_heuristics.get("accept_offer_resource_gain_factor", 1.0)

        min_acceptance_score = trade_heuristics.get("accept_offer_fairness_threshold", 0.1)
        
        if trade_score >= min_acceptance_score:
            return True
        else:
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
        # Corrección: Iterar directamente sobre los nodos si self.board.nodes es una lista de diccionarios.
        # La variable 'n' en la comprensión de lista ya es el diccionario del nodo.
        num_settlements = len([n for n in self.board.nodes if n['player'] == self.id and not n['has_city']])
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
        # Corrección: Similar a num_settlements, 'n' ya es el diccionario del nodo.
        num_cities = len([n for n in self.board.nodes if n['player'] == self.id and n['has_city']])
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
            terrain_info = self.board.terrain[terrain_idx] # Obtenemos el diccionario del terreno
            # MODIFICADO: Usar el método auxiliar _is_terrain_desert
            if terrain_idx not in terrains_player_has_access_to and \
               not self._is_terrain_desert(terrain_info):
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
                    terrain_info = self.board.terrain[terrain_idx]
                    
                    # MODIFICADO: Usar el método auxiliar _is_terrain_desert
                    if not self._is_terrain_desert(terrain_info):
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
            # MODIFICADO: Usar el método auxiliar _is_terrain_desert
            if not self._is_terrain_desert(terrain): # El desierto no produce
                resource_type = terrain.get('terrain_type')
                if resource_type is not None: # Asegurar que el tipo de terreno existe
                    resource_types_at_node.add(resource_type)
                
                terrain_number = terrain.get('probability') # Este es el número que debe salir en los dados
                if terrain_number is not None and terrain_number != 7: # Solo consideramos números que producen
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
                        # MODIFICADO: Usar el método auxiliar _is_terrain_desert
                        if not self._is_terrain_desert(terrain_info):
                            resource_type = terrain_info.get('terrain_type')
                            if resource_type is not None:
                                current_player_resources.add(resource_type)
            
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
            # MODIFICADO: Usar el método auxiliar _is_terrain_desert
            if not self._is_terrain_desert(terrain): # El desierto no produce
                resource_type = terrain.get('terrain_type')
                terrain_number = terrain.get('probability') # Número que debe salir en los dados

                if terrain_number is not None and terrain_number != 7: # Solo consideramos números que producen
                    prob_dots = dice_roll_to_dots.get(terrain_number, 0)
                    prob_real = prob_dots / 36.0
                    
                    resource_weight = city_chrom_heuristics["resource_priority"].get(resource_type, 0.1)
                    exponent = city_chrom_heuristics["production_probability_exponent"]
                    
                    # Una ciudad duplica la producción, por eso el * 2
                    production_from_terrain = 2 * (prob_real ** exponent) * resource_weight
                    node_resource_production_value += production_from_terrain
        
        heuristic_score = node_resource_production_value * city_chrom_heuristics["resource_value_base"]
        
        return heuristic_score

    def _heuristic_robber_terrain_assessment(self, terrain_id):
        """
        Calcula una puntuación heurística para colocar el ladrón en un terreno específico.

        :param terrain_id: El ID del terreno a evaluar.
        :return: float, la puntuación heurística del terreno.
        """
        heuristic_score = 0.0
        terrain_data = self.board.terrain[terrain_id]
        robber_heuristics = self.chromosome.get("robber_placement_heuristics", {})
        dice_roll_to_dots_map = self._get_dice_roll_to_dots_map()

        # MODIFICADO: Usar el método auxiliar _is_terrain_desert
        if self._is_terrain_desert(terrain_data):
            return -float('inf') # Nunca colocar en el desierto si hay otras opciones

        # 1. Valor de producción del terreno (suma de "dots" de los nodos adyacentes)
        terrain_production_potential = 0
        has_my_node = False
        opponent_nodes_count = 0

        # MODIFICADO: Acceder a contacting_nodes directamente desde el diccionario del terreno
        for node_id in terrain_data["contacting_nodes"]:
            node_data = self.board.nodes[node_id]
            terrain_number_on_node = terrain_data['probability'] # El número del terreno en sí
            terrain_production_potential += dice_roll_to_dots_map.get(terrain_number_on_node, 0)
            
            if node_data['player'] == self.id:
                has_my_node = True
            elif node_data['player'] != -1 and node_data['player'] is not None:
                opponent_nodes_count +=1
        
        # Normalizamos un poco el potencial de producción para que no escale demasiado.
        # Un terreno tiene entre 2 y 3 nodos que le dan su número.
        # Max dots es 5 (para 6 y 8). Así que un terreno muy bueno podría tener 10-15.
        # Dividimos por un factor, ej. 10, para mantenerlo en un rango razonable.
        normalized_production_value = terrain_production_potential / 10.0 
        heuristic_score += normalized_production_value * robber_heuristics.get("target_high_production_node_multiplier", 1.0)

        # 2. Prioridad de bloquear recurso específico que produce el terreno
        resource_produced = terrain_data['terrain_type']
        block_priority = robber_heuristics.get("block_specific_resource_priority", {})
        heuristic_score += block_priority.get(resource_produced, 0.0)

        # 3. Penalización por tener nodos propios en el terreno
        if has_my_node:
            heuristic_score += robber_heuristics.get("avoid_own_nodes_penalty", -5.0)
        
        # 4. Si no hay oponentes en el terreno, es menos útil (a menos que sea para desbloquearse)
        if opponent_nodes_count == 0 and not has_my_node: # No me afecta, no afecta a nadie
            heuristic_score -= 2.0 # Penalización leve
        elif opponent_nodes_count == 0 and has_my_node: # Me afecta solo a mí, y quiero moverlo de aquí
             heuristic_score += robber_heuristics.get("knight_immediate_threat_bonus", 1.0) # Reusamos este bonus como "desbloquearme"

        # 5. Factor de aleatoriedad (pequeño)
        heuristic_score += random.uniform(0, robber_heuristics.get("randomness_factor", 0.1))
        
        return heuristic_score

    def on_moving_thief(self):
        """
        Se llama cuando el ladrón debe ser movido (por un 7 o carta de caballero).
        Decide dónde mover el ladrón y a qué jugador robar.

        :return: Un diccionario {'terrain': terrain_id, 'player': player_id}
                 indicando la nueva ubicación del ladrón y a qué jugador robar (o -1 si a nadie).
        """
        current_thief_terrain_id = -1
        for t_idx, terrain_info in enumerate(self.board.terrain):
            if terrain_info['has_thief']:
                current_thief_terrain_id = t_idx
                break

        possible_terrains_to_move = []
        for t_idx, terrain_info in enumerate(self.board.terrain):
            if t_idx != current_thief_terrain_id:
                score = self._heuristic_robber_terrain_assessment(t_idx)
                possible_terrains_to_move.append({"id": t_idx, "score": score})
        
        if not possible_terrains_to_move:
            # No debería ocurrir si hay más de un terreno en el juego.
            # Si solo hay un terreno (absurdo) o current_thief_terrain_id no se encontró.
            # Devolvemos el primer terreno no desértico o el 0 como último recurso.
            fallback_terrain = 0
            for t_idx, t_info in enumerate(self.board.terrain):
                # MODIFICADO: Usar el método auxiliar _is_terrain_desert
                if not self._is_terrain_desert(t_info):
                    fallback_terrain = t_idx
                    break
            return {'terrain': fallback_terrain, 'player': -1}

        best_terrains = sorted(possible_terrains_to_move, key=lambda x: x["score"], reverse=True)
        chosen_terrain_id = best_terrains[0]["id"]
        chosen_terrain_data = self.board.terrain[chosen_terrain_id] # Obtenemos los datos del terreno elegido

        # Ahora, seleccionar a qué jugador robar en el 'chosen_terrain_id'
        players_on_chosen_terrain = []
        # MODIFICADO: Acceder a contacting_nodes directamente desde el diccionario del terreno elegido
        for node_id in chosen_terrain_data["contacting_nodes"]:
            node_data = self.board.nodes[node_id]
            if node_data['player'] is not None and node_data['player'] != -1 and node_data['player'] != self.id: # Añadida condición para no robar a -1 (nadie)
                # Solo considerar oponentes con recursos (más de 0 cartas)
                # Esta información no la tenemos aquí. Asumimos que si está en el nodo, es robable.
                # El GameManager validará si el jugador tiene cartas para robar.
                players_on_chosen_terrain.append(node_data['player'])
        
        player_to_rob_id = -1
        if players_on_chosen_terrain:
            # Estrategia de selección de jugador:
            # Podríamos intentar priorizar al jugador con más PVs si tuviéramos esa info.
            # Por ahora, si hay varios, elegimos uno al azar para no ser predecibles.
            # El cromosoma tiene `target_opponent_with_most_vps_bias` pero no lo usamos activamente sin datos de PV.
            # Es un placeholder para mejora futura.
            unique_players = list(set(players_on_chosen_terrain))
            if unique_players:
                player_to_rob_id = random.choice(unique_players)
        
        # print(f"Agente {self.id} mueve ladrón a terreno {chosen_terrain_id} y roba a jugador {player_to_rob_id}")
        return {'terrain': chosen_terrain_id, 'player': player_to_rob_id}

    def _get_cost_of_buildable(self, build_constant):
        """
        Devuelve el costo (objeto Materials) de un tipo de construcción.
        :param build_constant: Constante del tipo de construcción (ej. BuildConstants.TOWN).
        :return: Objeto Materials con el costo, o None si no es válido.
        """
        if build_constant in BuildMaterialsConstants:
            return Materials.from_iterable(BuildMaterialsConstants[build_constant])
        return None

    def _get_best_trade_ratio(self, material_to_give_id):
        """
        Determina el mejor ratio de intercambio que el agente puede obtener para dar un material específico.
        Considera puertos específicos, puertos generales y el banco.

        :param material_to_give_id: El ID del material que el agente quiere intercambiar.
        :return: tupla (ratio_da:int, ratio_recibe:int, tipo_puerto:HarborConstants/None) 
                 Ej. (2, 1, MaterialConstants.WOOD) para puerto de madera,
                     (3, 1, HarborConstants.ALL) para puerto general,
                     (4, 1, None) para el banco.
        """
        # Chequear puerto específico para el material a dar
        # self.board.check_for_player_harbors(self.id, material_to_give_id) 
        # devuelve el TIPO de puerto (ej. MaterialConstants.WOOD) si tiene ese puerto específico.
        # O HarborConstants.NONE si no lo tiene.

        # El método check_for_player_harbors busca si el jugador TIENE un puerto de ESE tipo.
        # No es si el NODO donde está el puerto es de ese tipo.
        player_specific_harbor = self.board.check_for_player_harbors(self.id, material_harbor=material_to_give_id)
        if player_specific_harbor == material_to_give_id: # El jugador tiene un puerto 2:1 para este material
            return 2, 1, material_to_give_id

        # Chequear puerto general 3:1
        player_general_harbor = self.board.check_for_player_harbors(self.id, material_harbor=HarborConstants.ALL)
        if player_general_harbor == HarborConstants.ALL: # El jugador tiene un puerto 3:1
            return 3, 1, HarborConstants.ALL
        
        # Por defecto, banco 4:1
        return 4, 1, None 

    def on_having_more_than_7_materials_when_thief_is_called(self):
        """
        Se llama cuando el jugador tiene más de 7 cartas de recurso y sale un 7.
        Debe decidir qué cartas descartar basándose en las heurísticas del cromosoma.

        :return: Hand() con los materiales a descartar.
        """
        num_to_discard = self.hand.get_total() // 2
        discard_hand = Hand() # Mano que contendrá las cartas a descartar

        if num_to_discard == 0:
            return discard_hand

        discard_heuristics = self.chromosome.get("discard_heuristics", {})
        resource_value_priority = discard_heuristics.get("resource_value_priority", {})

        card_scores = []

        cost_settlement = self._get_cost_of_buildable(BuildConstants.TOWN)
        cost_city = self._get_cost_of_buildable(BuildConstants.CITY)
        cost_card = self._get_cost_of_buildable(BuildConstants.CARD)

        # ASEGÚRATE DE QUE ESTA LÍNEA ESTÉ ASÍ:
        # Se itera sobre self.hand.resources usando enumerate.
        # 'material_id' será el índice (0 para Cereal, 1 para Mineral, etc.)
        # 'count' será la cantidad de ese material.
        for material_id, count in enumerate(self.hand.resources):
            if count > 0: # Solo procesar si el agente tiene este material
                for _ in range(count): # Generar una puntuación para cada carta individual de este material
                    score = resource_value_priority.get(material_id, 1.0) 
                    # Verificar si este material es necesario para los objetivos de construcción
                    # Accedemos a los costos (que son objetos Materials) por índice
                    if cost_settlement and cost_settlement[material_id] > 0:
                        score += discard_heuristics.get("keep_for_settlement_bonus", -0.5)
                    if cost_city and cost_city[material_id] > 0:
                        score += discard_heuristics.get("keep_for_city_bonus", -0.6)
                    if cost_card and cost_card[material_id] > 0:
                        score += discard_heuristics.get("keep_for_card_bonus", -0.3)
                    card_scores.append({"material_id": material_id, "score": score})

        # Ordenar para descartar los de mayor score (prioridad más alta para descarte)
        card_scores.sort(key=lambda x: x["score"], reverse=True) 

        for i in range(min(num_to_discard, len(card_scores))):
            discard_hand.add_material(card_scores[i]["material_id"], 1)
        return discard_hand

    def on_turn_end(self):
        """
        Se llama al final del turno.
        Utilizado para jugar cartas de desarrollo (no Caballeros) si es estratégico y no se han usado.
        La decisión se basa en las heurísticas del cromosoma.

        :return: DevelopmentCard a jugar o None si no se juega ninguna.
        """
        card_to_play = None
        best_score = -float('inf')

        play_heuristics = self.chromosome.get("play_dev_card_heuristics", {})

        # Solo proceder con la lógica de cartas de desarrollo si self.hand está configurado para ello.
        can_check_dev_cards = hasattr(self.hand, 'development_cards') and \
                              hasattr(self.hand.development_cards, 'has_development_card')

        if not can_check_dev_cards:
            # Si no podemos verificar las cartas de desarrollo (porque self.hand.development_cards no existe
            # o no tiene el método esperado), no se puede jugar ninguna carta de desarrollo.
            return None

        # Evaluar Monopolio
        if self.hand.development_cards.has_development_card(DevelopmentCard.MONOPOLY):
            score = play_heuristics.get("monopoly_bonus", 0) 
            if score > best_score: 
                best_score = score
                card_to_play = DevelopmentCard.MONOPOLY
        
        # Evaluar Año de la Abundancia
        if self.hand.development_cards.has_development_card(DevelopmentCard.YEAR_OF_PLENTY):
            score = play_heuristics.get("year_of_plenty_immediate_build_bonus", 0)
            if score > best_score:
                best_score = score
                card_to_play = DevelopmentCard.YEAR_OF_PLENTY

        # Evaluar Construcción de Carreteras
        if self.hand.development_cards.has_development_card(DevelopmentCard.ROAD_BUILDING):
            score = play_heuristics.get("road_building_strategic_spot_bonus", 0)
            if score > best_score:
                best_score = score
                card_to_play = DevelopmentCard.ROAD_BUILDING
        
        return card_to_play


    def on_monopoly_card_use(self):
        """
        Se llama cuando el agente decide usar una carta de Monopolio.
        Debe elegir qué recurso monopolizar.
        La decisión se basa en las heurísticas del cromosoma.

        :return: Un entero representando el MaterialConstants elegido.
        """
        play_heuristics = self.chromosome.get("play_dev_card_heuristics", {})
        # `monopoly_potential_gain_threshold` no se usa directamente para ELEGIR,
        # sino para decidir SI JUGAR la carta de monopolio. Aquí ya decidimos jugarla.
        
        # Estrategia:
        # 1. Identificar los recursos que más necesita el agente para sus próximos objetivos de construcción.
        # 2. Opcionalmente, identificar recursos que los oponentes puedan tener en abundancia (esto es difícil sin info).
        # 3. Dar prioridad a los recursos que el agente necesita y que probablemente otros tengan.

        needed_resources_score = {}
        all_materials = [MaterialConstants.WOOD, MaterialConstants.CLAY, MaterialConstants.WOOL, MaterialConstants.CEREAL, MaterialConstants.MINERAL]

        # Evaluar necesidad basada en el próximo objetivo de construcción
        next_build_goal_cost = None
        num_settlements = sum(1 for n_data in self.board.nodes if n_data['player'] == self.id and not n_data['has_city'])
        num_cities = sum(1 for n_data in self.board.nodes if n_data['player'] == self.id and n_data['has_city'])

        potential_goals = []
        if num_cities < 4 and num_settlements > 0 : potential_goals.append(self._get_cost_of_buildable(BuildConstants.CITY))
        if num_settlements < 5: potential_goals.append(self._get_cost_of_buildable(BuildConstants.TOWN))
        potential_goals.append(self._get_cost_of_buildable(BuildConstants.CARD))

        for goal_cost in potential_goals:
            if goal_cost:
                for mat_id, count_needed in goal_cost.resources.items():
                    count_has = self.hand.resources.get(mat_id, 0)
                    deficit = count_needed - count_has
                    if deficit > 0:
                        needed_resources_score[mat_id] = needed_resources_score.get(mat_id, 0) + deficit * self.chromosome["trade_heuristics"]["resource_needed_importance"].get(mat_id, 1.0)

        # Si no hay un déficit claro, considerar los recursos con alta prioridad general en el cromosoma.
        if not needed_resources_score:
            for mat_id in all_materials:
                needed_resources_score[mat_id] = self.chromosome["trade_heuristics"]["resource_needed_importance"].get(mat_id, 1.0)
        
        if not needed_resources_score: # Fallback si todo lo demás falla
            return random.choice(all_materials)

        # Elegir el recurso con la puntuación de necesidad más alta
        best_resource = max(needed_resources_score, key=needed_resources_score.get)
        # print(f"Agente {self.id} usa Monopolio y elige: {best_resource}")
        return best_resource


    def on_road_building_card_use(self):
        """
        Se llama cuando el agente decide usar una carta de Construcción de Carreteras.
        Debe elegir dónde construir dos carreteras.
        Utiliza la heurística _heuristic_road_location.

        :return: Dict con la ubicación de las dos carreteras.
                 Ej: {'node_id': int, 'road_to': int, 'node_id_2': int, 'road_to_2': int}
                 o None si no se pueden colocar.
        """
        possible_first_roads = []
        valid_road_spots = self.board.valid_road_nodes(self.id, two_roads_for_card=True) # Indica que es para la carta

        for road_option in valid_road_spots:
            from_node = road_option['starting_node']
            to_node = road_option['finishing_node']
            # Es importante que valid_road_nodes ya filtre carreteras existentes.
            score = self._heuristic_road_location(from_node, to_node)
            possible_first_roads.append({"from_node": from_node, "to_node": to_node, "score": score})

        if not possible_first_roads:
            return None # No hay lugares válidos para la primera carretera

        possible_first_roads.sort(key=lambda x: x["score"], reverse=True)
        
        # Intentar encontrar la mejor combinación de dos carreteras
        # Esto puede ser complejo. Una simplificación: tomar la mejor primera, luego la mejor segunda
        # que no colisione y sea válida DESPUÉS de la primera (simulada).

        for first_road_choice in possible_first_roads:
            # Simular la colocación de la primera carretera (temporalmente) para encontrar la segunda
            # Esto es difícil sin modificar el estado real del tablero o tener una copia.
            # Por ahora, asumimos que `valid_road_nodes` puede manejar esto o
            # que la segunda carretera se elige de una lista que no dependa de la primera.
            # Una aproximación más simple: elegir las dos mejores carreteras no superpuestas de la lista inicial.

            # Para una implementación robusta, necesitaríamos:
            # 1. Colocar la primera carretera (simulada).
            # 2. Recalcular _heuristic_road_location para la segunda desde el final de la primera o desde otros puntos.
            # Esto excede la simplicidad actual.

            # Simplificación V1: Elegir la mejor primera. Luego, elegir la mejor segunda de las restantes
            # que no sea la misma y que aún sea "válida" (sin una simulación compleja).
            # La función valid_road_nodes(self.id, two_roads_for_card=True) debería devolver
            # todos los inicios posibles de carretera.
            # La lógica de conexión la debe manejar el GameDirector al aplicar.

            best_first_road = first_road_choice
            
            possible_second_roads = []
            # La segunda carretera puede partir del final de la primera, o de cualquier otro lugar válido.
            # `valid_road_nodes` con `initial_road_node_id=best_first_road['to_node']` si quisiéramos forzar conexión.
            # O buscar una segunda carretera independiente.

            # Para la segunda carretera, recalculamos las opciones, excluyendo la primera.
            # Y considerando que la primera ya podría estar (aunque no la "construimos" aquí).
            # `valid_road_nodes` debería ser llamado de nuevo, o filtrar la lista actual.

            # Vamos a buscar una segunda carretera que sea distinta a la primera y también tenga buena puntuación.
            # Idealmente, la segunda carretera debería ser evaluada *después* de que la primera se considera colocada.
            
            temp_board_state_after_first_road = None # Idealmente, clonar y modificar
            
            # Dado que no podemos simular fácilmente, buscaremos la segunda mejor carretera de la lista original
            # que no sea idéntica ni inversa a la primera.
            
            # Re-evaluar la segunda carretera:
            # Podríamos usar _find_best_second_road(board_after_first_road, first_road_end_node)
            # Para simplificar: buscamos otra carretera de la lista `possible_first_roads`
            # que sea distinta.
            
            second_road_options_filtered = [
                r for r in possible_first_roads 
                if r['score'] > -float('inf') and \
                   (r['from_node'] != best_first_road['from_node'] or r['to_node'] != best_first_road['to_node']) and \
                   (r['from_node'] != best_first_road['to_node'] or r['to_node'] != best_first_road['from_node'])
            ]

            # Priorizar carreteras que se conectan a la primera
            connected_second_roads = []
            other_second_roads = []

            # El método valid_road_nodes debería poder decirnos qué carreteras son construibles
            # desde el final de la primera carretera.
            # Asumimos que valid_road_nodes(..., initial_road_node_id=node) funciona.
            # Esta es una dependencia en cómo el GameManager/Board interpreta la construcción de la segunda carretera.
            
            # Opción A: Segunda carretera conectada a la primera.
            potential_starts_for_second_road = [best_first_road['to_node']]
            # También podría empezar desde el mismo nodo que la primera, si se ramifica.
            # if self.board.nodes[best_first_road['from_node']]['player'] == self.id or \
            #    any(r['player_id'] == self.id for r in self.board.nodes[best_first_road['from_node']]['roads']):
            #    potential_starts_for_second_road.append(best_first_road['from_node'])


            for start_node_for_second in potential_starts_for_second_road:
                # Necesitamos una forma de obtener carreteras válidas desde `start_node_for_second`
                # asumiendo que la primera carretera (best_first_road) ya está colocada.
                # Esta es la parte compleja sin una simulación.
                # Por ahora, filtramos de `valid_road_spots`
                for road_opt in valid_road_spots: # Reutilizar la lista original
                    if road_opt['starting_node'] == start_node_for_second:
                        # Segunda carretera es (start_node_for_second -> road_opt['finishing_node'])
                        # Primera carretera es (best_first_road['from_node'] -> best_first_road['to_node'])
                        # donde start_node_for_second == best_first_road['to_node']
                        
                        # Evitar que la segunda carretera sea la inversa de la primera.
                        # Si best_first_road es (F,T), la segunda parte de T.
                        # La inversa de la primera es (T,F).
                        # Entonces, si road_opt['finishing_node'] es F, la segunda carretera (T,F) es la inversa.
                        if road_opt['finishing_node'] == best_first_road['from_node']:
                            continue # Es la inversa, saltar.

                        # No es necesario comprobar explícitamente si es la "misma" que la primera,
                        # ya que la segunda carretera parte del nodo final de la primera.
                        # Si la primera es A->B, la segunda parte de B. Solo podría ser la misma si A->B es un bucle (A=B).
                        # La heurística de carretera debería manejar carreteras A->A si son válidas y el tablero lo permite.

                        score = self._heuristic_road_location(road_opt['starting_node'], road_opt['finishing_node'])
                        
                        # La puntuación ya refleja la calidad de la carretera.
                        # No se necesita una penalización adicional aquí si la heurística es correcta.
                        # El 'continue' anterior ya evita la inversa directa.
                        
                        if score > -float('inf'): # Considerar solo carreteras con puntuación válida
                            connected_second_roads.append({
                                "from_node": road_opt['starting_node'], 
                                "to_node": road_opt['finishing_node'], 
                                "score": score
                            })
            
            # Opción B: Segunda carretera independiente (si no hay conectadas buenas)
            if not connected_second_roads:
                for r_opt in second_road_options_filtered:
                    # Asegurarse que no es la primera carretera (de nuevo, por si acaso)
                    if r_opt['from_node'] == best_first_road['from_node'] and r_opt['to_node'] == best_first_road['to_node']:
                        continue
                    other_second_roads.append(r_opt) # Ya tienen score

            best_second_road = None
            if connected_second_roads:
                connected_second_roads.sort(key=lambda x: x["score"], reverse=True)
                best_second_road = connected_second_roads[0]
            elif other_second_roads:
                other_second_roads.sort(key=lambda x: x["score"], reverse=True)
                best_second_road = other_second_roads[0]

            if best_second_road:
                # print(f"Agente {self.id} usa Road Building: Carretera 1 ({best_first_road['from_node']} -> {best_first_road['to_node']}), Carretera 2 ({best_second_road['from_node']} -> {best_second_road['to_node']})")
                return {
                    'node_id': best_first_road['from_node'], 
                    'road_to': best_first_road['to_node'],
                    'node_id_2': best_second_road['from_node'],
                    'road_to_2': best_second_road['to_node']
                }
        
        # Fallback: si solo se pudo encontrar una carretera o ninguna
        if possible_first_roads: # Tomar la mejor y dejar la segunda como None o error.
            best_single_road = possible_first_roads[0]
            # print(f"Agente {self.id} usa Road Building: Solo pudo determinar una carretera ({best_single_road['from_node']} -> {best_single_road['to_node']})")
            # El GameManager deberá manejar esto (quizás permitir solo una o ninguna).
            # Para ser estrictos, deberíamos devolver None si no podemos encontrar DOS.
            # Sin embargo, el juego podría permitir construir una si la segunda no es válida.
            # Por seguridad, devolvemos la primera si es la única opción razonable.
            # Pero la interfaz espera DOS. Es mejor devolver None si no se cumplen las dos.
            return None # No se pudieron determinar dos carreteras válidas
        
        return None


    def on_year_of_plenty_card_use(self):
        """
        Se llama cuando el agente decide usar una carta de Año de la Abundancia.
        Debe elegir qué dos recursos tomar del banco.
        La decisión se basa en las necesidades para los próximos objetivos de construcción.

        :return: Dict con los dos materiales elegidos. Ej: {'material': MaterialConstants, 'material_2': MaterialConstants}
                 o None si no se pueden determinar.
        """
        # play_heuristics = self.chromosome.get("play_dev_card_heuristics", {})
        # `year_of_plenty_immediate_build_bonus` se usa para decidir SI jugar la carta.
        # Aquí ya decidimos jugarla y necesitamos elegir los recursos.

        resource_needs = {}
        all_materials = [MaterialConstants.WOOD, MaterialConstants.CLAY, MaterialConstants.WOOL, MaterialConstants.CEREAL, MaterialConstants.MINERAL]

        # Calcular déficit para posibles construcciones
        potential_goals = []
        cost_town = self._get_cost_of_buildable(BuildConstants.TOWN)
        cost_city = self._get_cost_of_buildable(BuildConstants.CITY)
        cost_card = self._get_cost_of_buildable(BuildConstants.CARD)

        num_settlements = sum(1 for n_data in self.board.nodes if n_data['player'] == self.id and not n_data['has_city'])
        num_cities = sum(1 for n_data in self.board.nodes if n_data['player'] == self.id and n_data['has_city'])

        # Ponderar objetivos: Ciudad > Poblado > Carta
        if num_cities < 4 and num_settlements > 0: potential_goals.append({"cost": cost_city, "priority": 3})
        if num_settlements < 5: potential_goals.append({"cost": cost_town, "priority": 2})
        potential_goals.append({"cost": cost_card, "priority": 1})
        
        for mat_id in all_materials:
            resource_needs[mat_id] = 0

        for goal_info in potential_goals:
            goal_cost = goal_info["cost"]
            priority = goal_info["priority"]
            if goal_cost:
                for mat_id, count_needed in goal_cost.resources.items():
                    count_has = self.hand.resources.get(mat_id, 0)
                    deficit = count_needed - count_has
                    if deficit > 0:
                        # Ponderar por la importancia del recurso y la prioridad del objetivo
                        importance_weight = self.chromosome["trade_heuristics"]["resource_needed_importance"].get(mat_id, 1.0)
                        resource_needs[mat_id] += deficit * importance_weight * priority
        
        if not any(need > 0 for need in resource_needs.values()):
            # Si no hay déficit específico, tomar los recursos con mayor "necesidad" general del cromosoma
            for mat_id in all_materials:
                resource_needs[mat_id] = self.chromosome["trade_heuristics"]["resource_needed_importance"].get(mat_id, 1.0)

        # Ordenar recursos por necesidad descendente
        sorted_needs = sorted(resource_needs.items(), key=lambda item: item[1], reverse=True)

        if not sorted_needs: # Fallback extremo
            res1 = random.choice(all_materials)
            res2 = random.choice(all_materials)
            return {'material': res1, 'material_2': res2}

        material1 = sorted_needs[0][0]
        material2 = None
        if len(sorted_needs) > 1:
            material2 = sorted_needs[1][0]
        else: # Si solo un recurso es "necesario", o la lista es corta
            material2 = material1 # Tomar dos del mismo si es muy necesitado

        # Si por alguna razón material2 sigue siendo None (lista de necesidades muy corta y extraña)
        if material2 is None:
            material2 = random.choice([m for m in all_materials if m != material1] or all_materials)


        # print(f"Agente {self.id} usa Año de la Abundancia y elige: {material1}, {material2}")
        return {'material': material1, 'material_2': material2}

    # Métodos auxiliares que podrían ser útiles (a definir según la estrategia)
    # def can_build_settlement(self): ...
    # def heuristic_settlement(self): ...
    # def can_build_city(self): ...
    # def heuristic_city(self): ...
    # etc. 