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

    chromosome_para_entrenamiento_actual = None

    def __init__(self, agent_id, chromosome=None):
        """
        Constructor del GeneticAgent.

        :param agent_id: Identificador único del agente.
        :param chromosome: Una lista o diccionario representando los pesos genéticos
                           que guiarán las decisiones del agente. Si es None,
                           se utilizará el cromosoma por defecto (los mejores pesos).
        """
        super().__init__(agent_id)
        self.id = agent_id # Aseguramos que el agent_id se almacena como self.id
        
        if chromosome is not None:
            self.chromosome = chromosome
            # print(f"GeneticAgent {self.id}: Usando cromosoma PROPORCIONADO explícitamente.")
        elif hasattr(GeneticAgent, 'chromosome_para_entrenamiento_actual') and \
             GeneticAgent.chromosome_para_entrenamiento_actual is not None:
            self.chromosome = GeneticAgent.chromosome_para_entrenamiento_actual
            # print(f"GeneticAgent {self.id}: Usando cromosoma DE ENTRENAMIENTO.")
        else:
            # print(f"GeneticAgent {self.id}: Usando cromosoma POR DEFECTO (mejores pesos integrados).")
            self.chromosome = self._initialize_default_chromosome()
        
        self.had_suboptimal_start = False 
        # self.board_instance = None # No es necesario inicializarlo aquí si se pasa en cada método

    def _initialize_default_chromosome(self):
        """
        Inicializa el cromosoma con los mejores pesos optimizados.
        Estos pesos han sido definidos en 'best_chromosome.json'.
        """
        return {
            "build_actions": {
                "town": 0.7730984756915484,
                "city": 0.3309144993831527,
                "road": 0.20595669614283263,
                "card": 0.13651220431020897,
                "late_game_pv_bonus_city": 3.0555464255155464,
                "late_game_pv_card_multiplier": 0.43045716867063977,
                "late_game_vps_threshold": 10.957695971758353,
                "min_overall_score_threshold": 0.05327415506968203,
                "min_road_score_for_deterministic_build": 3.1470296803471376,
                "suboptimal_start_card_buy_bonus": 1.0288644869987553,
                "suboptimal_start_town_build_bonus": 0.5648133990332749,
                "suboptimal_start_road_build_bonus": 0.555770122514022,
                "suboptimal_start_bonus_decay_turn": 40.58057979217617
            },
            "settlement_heuristics": {
                "resource_value_base": 0.5769006434770441,
                "resource_priority": {
                    "3": 0.6822506168265137, # WOOD
                    "2": 0.19886072238117802, # CLAY
                    "4": 0.5121143264846796, # WOOL
                    "0": 0.42099396375613907, # CEREAL
                    "1": 0.20320637510462508  # MINERAL
                },
                "production_probability_exponent": 0.4680019766780623,
                "new_resource_type_bonus": 0.3914754876353038,
                "port_access_bonus": 0.10834160369125057,
                "specific_port_match_bonus": 0.4433835663278458,
                "number_diversity_bonus": 0.47040572699963734
            },
            "road_heuristics": {
                "to_potential_settlement_spot_bonus": 0.6148618501689922,
                "connects_to_own_settlement_bonus": 0.1288175497566187,
                "longest_road_contribution_bonus": 0.4661889677368971,
                "port_access_bonus": 0.41381500014875783,
                "expansion_to_new_terrain_bonus": 0.6064398402119509,
                "fallback_suboptimal_road_build_probability": 0.1257420612708004,
                "fallback_suboptimal_road_action_score": 0.3580571327544674
            },
            "city_heuristics": {
                "resource_value_base": 2.370424157838219,
                "resource_priority": {
                    "3": 1.0,                 # WOOD
                    "2": 0.19719837464546494, # CLAY
                    "4": 0.6723655053655547,  # WOOL
                    "0": 0.7075445348529454,  # CEREAL
                    "1": 0.8821905845443709   # MINERAL
                },
                "production_probability_exponent": 0.24671849303157162,
                "multiple_high_prob_numbers_bonus": 4.665022907116415
            },
            "dev_card_heuristics": {
                "base_value": 2.3949106279195114,
                "knight_bonus": 0.9885894311105975,
                "victory_point_bonus": 4.198805946246691,
                "monopoly_bonus": 3.7188994975172864,
                "road_building_bonus": 1.215713904271329,
                "year_of_plenty_bonus": 1.5183189959212788
            },
            "initial_placement_settlement": {
                "resource_production_base": 0.3068447564573389,
                "resource_priority": {
                    "3": 0.18516386110779742, # WOOD
                    "2": 0.7523845447282291,  # CLAY
                    "4": 0.6919748036826056,  # WOOL
                    "0": 1.0,                 # CEREAL
                    "1": 0.745225777618892    # MINERAL
                },
                "production_probability_exponent": 0.23519288149908685,
                "new_resource_type_bonus": 1.1827752536750873,
                "port_access_bonus": 0.3142729330593753,
                "specific_port_match_bonus": 0.4491897237040623,
                "number_diversity_bonus": 0.4578361794256982,
                "avoid_single_resource_concentration_penalty": -1.0182530681121218,
                "fallback_to_random_if_best_score_below": 2.3721787087097335,
                "use_heuristic_for_fallback_road": 0.004399956195562729,
                "non_initial_player_multipliers": {
                    "resource_diversity_bonus": 3.272693610200753,
                    "number_diversity_bonus": 0.9513472232316531,
                    "port_access_bonus": 1.572610229500408,
                    "resource_production_base": 0.614422715060202
                }
            },
            "initial_placement_road":{
                "to_second_potential_settlement_spot_bonus": 0.4741237697124245,
                "resource_variety_expansion_bonus": 0.13167321593021225,
                "general_expansion_bonus": 0.18389768376789933,
                "connect_to_high_prob_numbers_bonus": 0.3681084132821504
            },
            "robber_placement_heuristics": {
                "target_high_production_node_multiplier": 0.3362773525642698,
                "block_specific_resource_priority": {
                    "3": 0.4235789952882476,  # MADERA
                    "2": 0.267806375625387,   # ARCILLA
                    "4": 0.39599532534641513, # LANA
                    "0": 0.41059712185460007, # CEREAL
                    "1": 0.488033520567543    # MINERAL
                },
                "target_opponent_with_most_vps_bias": 0.6363925911511359,
                "avoid_own_nodes_penalty": -4.171765240023148,
                "randomness_factor": 0.025079101935022968,
                "target_leader_high_production_resource_bonus": 1.7268790463022237,
                "target_needed_resource_on_opponent_bonus": 1.0,
                "leader_vps_advantage_threshold_for_targeting": 3.5766035683933834
            },
            "discard_heuristics": {
                "resource_value_priority": {
                    "3": 0.4209789390700097,  # MADERA
                    "2": 0.8483311721204296,  # ARCILLA
                    "4": 0.4270841736142612,  # LANA
                    "0": 0.30953395890890933, # CEREAL
                    "1": 1.0                   # MINERAL
                },
                "keep_for_settlement_bonus": -0.7064970139000485,
                "keep_for_city_bonus": -0.5227607757677318,
                "keep_for_card_bonus": -0.40044088616598084
            },
            "trade_heuristics": {
                "willingness_to_trade_general": 0.2703541067979195,
                "resource_surplus_importance": {
                    "3": 0.32288162288580113, # MADERA
                    "2": 0.2608196633886547,  # ARCILLA
                    "4": 0.39622204447865006, # LANA
                    "0": 0.616331512525276,   # CEREAL
                    "1": 0.1318730420521943   # MINERAL
                },
                "resource_needed_importance": {
                    "3": 0.6904129983382203,  # MADERA
                    "2": 0.5056612321024686,  # ARCILLA
                    "4": 0.16938007889039497, # LANA
                    "0": 0.47815215420120916, # CEREAL
                    "1": 0.29025779242242167  # MINERAL
                },
                "bank_trade_ratio_modifier": -0.09843227555702758,
                "port_trade_ratio_modifier": -0.1763372700974885,
                "accept_offer_resource_gain_factor": 1.4062096032168099,
                "accept_offer_fairness_threshold": 0.4103828225648573,
                "min_score_for_self_initiated_trade": 1.0,
                "vps_threshold_consider_leader_trade": 3.6737792142849965,
                "penalty_trade_with_leader": 0.28374975210685893,
                "resource_surplus_threshold_for_proactive_trade": 5.010573513810559,
                "proactive_trade_score_bonus": 0.667341259052725
            },
            "play_dev_card_heuristics":{
                "knight_immediate_threat_bonus": 0.15803944757173097,
                "knight_take_largest_army_bonus": 1.4005505050673122,
                "knight_maintain_largest_army_bonus": 0.45557329616315023,
                "knight_contest_largest_army_bonus": 1.0,
                "knight_for_win_bonus": 7.182086991508513,
                "monopoly_potential_gain_threshold": 2.953307915255669,
                "year_of_plenty_immediate_build_bonus": 0.2810892737567539,
                "road_building_strategic_spot_bonus": 0.5236615681105226,
                "min_score_to_play_knight_on_start": 0.5323532713223691,
                "early_game_turn_threshold": 12.468408318355344,
                "early_game_knight_suboptimal_start_boost": 0.5070248617081883,
                "early_game_knight_robber_on_key_tile_boost": 2.041986450016127
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
        base_chrom_heur = self.chromosome["initial_placement_settlement"]
        dice_roll_to_dots = self._get_dice_roll_to_dots_map()

        # INICIO DE MODIFICACIÓN: Aplicar multiplicadores si no es el jugador inicial colocando
        # Determinar si es "jugador inicial" contando asentamientos existentes.
        # Esto es una heurística para saber si estamos en la primera ronda de colocación, primer turno.
        is_initial_player_phase = True # Asumir que sí, a menos que se encuentren otros asentamientos
        for n_info in self.board.nodes:
            if n_info['player'] != -1 and n_info['player'] != self.id:
                is_initial_player_phase = False
                break
        
        # Copiar los pesos para no modificar el cromosoma original directamente
        applied_chrom_heur = {**base_chrom_heur} 
        if not is_initial_player_phase and "non_initial_player_multipliers" in base_chrom_heur:
            multipliers = base_chrom_heur["non_initial_player_multipliers"]
            
            # Aplicar multiplicadores a los pesos relevantes. Usamos .get para seguridad.
            applied_chrom_heur["new_resource_type_bonus"] = base_chrom_heur.get("new_resource_type_bonus", 1.5) * multipliers.get("resource_diversity_bonus", 1.0)
            applied_chrom_heur["number_diversity_bonus"] = base_chrom_heur.get("number_diversity_bonus", 0.5) * multipliers.get("number_diversity_bonus", 1.0) # Corregido nombre de key
            applied_chrom_heur["port_access_bonus"] = base_chrom_heur.get("port_access_bonus", 0.2) * multipliers.get("port_access_bonus", 1.0)
            applied_chrom_heur["resource_production_base"] = base_chrom_heur.get("resource_production_base", 1.0) * multipliers.get("resource_production_base", 1.0)
        # FIN DE MODIFICACIÓN

        # 1. Valor de Producción de Recursos
        node_resource_production_value = 0.0
        resource_types_at_node = set()
        numbers_at_node = set()
        terrain_types_count = {} # Para la penalización por concentración

        for terrain_idx in node_data['contacting_terrain']:
            terrain = self.board.terrain[terrain_idx]
            if not self._is_terrain_desert(terrain):
                resource_type = terrain.get('terrain_type')
                if resource_type is not None: 
                    resource_types_at_node.add(resource_type)

                terrain_number = terrain.get('probability') 
                if terrain_number is not None and terrain_number != 7: 
                    numbers_at_node.add(terrain_number)
                    prob_dots = dice_roll_to_dots.get(terrain_number, 0)
                    prob_real = prob_dots / 36.0
                    # Usar los pesos de applied_chrom_heur
                    resource_weight = applied_chrom_heur["resource_priority"].get(resource_type, 0.1)
                    exponent = applied_chrom_heur["production_probability_exponent"]
                    node_resource_production_value += (prob_real ** exponent) * resource_weight
        
        heuristic_score += node_resource_production_value * applied_chrom_heur["resource_production_base"]

        # 2. Bonus por Nuevos Tipos de Recurso (en el contexto inicial, todos son "nuevos")
        heuristic_score += len(resource_types_at_node) * applied_chrom_heur["new_resource_type_bonus"]

        # 3. Bonus por Acceso a Puerto
        harbor_type = node_data['harbor']
        if harbor_type != HarborConstants.NONE:
            heuristic_score += applied_chrom_heur["port_access_bonus"]
            if harbor_type != HarborConstants.ALL and harbor_type in resource_types_at_node:
                heuristic_score += applied_chrom_heur["specific_port_match_bonus"]

        # 4. Bonus por Diversidad de Números
        heuristic_score += len(numbers_at_node) * applied_chrom_heur["number_diversity_bonus"]

        # 5. Penalización por Concentración de un Solo Tipo de Recurso
        if len(resource_types_at_node) == 1 and len(node_data['contacting_terrain']) > 1:
            heuristic_score += applied_chrom_heur["avoid_single_resource_concentration_penalty"]
        elif len(terrain_types_count) > 0 and max(terrain_types_count.values()) == len(node_data['contacting_terrain']) and len(resource_types_at_node) > 0 :
             heuristic_score += applied_chrom_heur["avoid_single_resource_concentration_penalty"]


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

        scored_settlements = []
        for node_id in valid_nodes_ids:
            score = self._heuristic_initial_settlement_location(node_id)
            scored_settlements.append({"id": node_id, "score": score})
        
        if not scored_settlements: 
             # Fallback si no hay nodos evaluados (ya existía, pero lo mantenemos robusto)
             all_nodes_ids_for_fallback = [n['id'] for n in self.board.nodes] # Renombrado para evitar conflicto
             fallback_node_id = random.choice(valid_nodes_ids) if valid_nodes_ids else (all_nodes_ids_for_fallback[0] if all_nodes_ids_for_fallback else 0)
             adj_nodes = self.board.nodes[fallback_node_id]['adjacent']
             fallback_road_to = random.choice(adj_nodes) if adj_nodes else (fallback_node_id + 1) % len(self.board.nodes)
             return fallback_node_id, fallback_road_to

        best_settlement_options = sorted(scored_settlements, key=lambda x: x["score"], reverse=True)
        best_settlement_node_id = -1 # Inicializar

        # INICIO DE MODIFICACIÓN: Estrategia de fallback para selección de asentamiento inicial
        chrom_init_sett_config = self.chromosome.get("initial_placement_settlement", {})
        fallback_threshold = chrom_init_sett_config.get("fallback_to_random_if_best_score_below", -float('inf'))
        use_heuristic_for_road_on_fallback = chrom_init_sett_config.get("use_heuristic_for_fallback_road", False)

        perform_random_settlement_choice = False
        if best_settlement_options[0]["score"] < fallback_threshold and valid_nodes_ids:
            perform_random_settlement_choice = True
            best_settlement_node_id = random.choice(valid_nodes_ids)
            self.had_suboptimal_start = True # Establecer si se usa fallback aleatorio
            
            if not use_heuristic_for_road_on_fallback:
                # Carretera también aleatoria
                adj_nodes_for_random_road = self.board.nodes[best_settlement_node_id]['adjacent']
                if not adj_nodes_for_random_road:
                    # Nodo aislado, muy improbable pero se maneja
                    road_to_node_id = (best_settlement_node_id + 1) % len(self.board.nodes)
                    if road_to_node_id == best_settlement_node_id and len(self.board.nodes) > 1:
                        road_to_node_id = (best_settlement_node_id + 2) % len(self.board.nodes)
                    elif len(self.board.nodes) == 1:
                        road_to_node_id = best_settlement_node_id # O manejar como error
                else:
                    road_to_node_id = random.choice(adj_nodes_for_random_road)
                return best_settlement_node_id, road_to_node_id
            # Si use_heuristic_for_road_on_fallback es True, la lógica de carretera heurística de abajo se aplicará
        else:
            # Elección heurística normal para el asentamiento
            best_settlement_node_id = best_settlement_options[0]["id"]
            # También considerar subóptimo si el score es bajo, incluso sin fallback aleatorio
            if best_settlement_options[0]["score"] < fallback_threshold:
                 self.had_suboptimal_start = True
        # FIN DE MODIFICACIÓN
        
        # Asegurar que best_settlement_node_id se haya establecido
        if best_settlement_node_id == -1:
            # Esto solo debería ocurrir si best_settlement_options estaba vacío y el fallback inicial falló, lo cual es muy improbable.
            # O si la lógica anterior no asignó un valor por alguna razón.
            all_nodes_ids_final_fallback = [n['id'] for n in self.board.nodes]
            best_settlement_node_id = random.choice(valid_nodes_ids) if valid_nodes_ids else (all_nodes_ids_final_fallback[0] if all_nodes_ids_final_fallback else 0)

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
            current_turn = self.board.turn_number if hasattr(self.board, 'turn_number') else 0 # Asumir turno 0 si no disponible
            early_game_thresh = knight_heuristics.get("early_game_turn_threshold", 10)

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
            # Asumimos que self.hand.development_cards puede dar el conteo de caballeros jugados por el agente,
            # y que self.board puede dar información sobre el estado actual del Mayor Ejército.
            my_played_knights = 0
            if hasattr(self.hand, 'development_cards') and \
               hasattr(self.hand.development_cards, 'get_played_knights_count'): # Método hipotético
                my_played_knights = self.hand.development_cards.get_played_knights_count()

            knights_after_playing_one = my_played_knights + 1
            
            largest_army_info = {'owner_id': None, 'count': 0}
            if hasattr(self.board, 'get_largest_army_info'): # Método hipotético en Board
                largest_army_info = self.board.get_largest_army_info()
                if largest_army_info is None: # Asegurar que largest_army_info sea un dict
                    largest_army_info = {'owner_id': None, 'count': 0}
            
            current_largest_army_owner = largest_army_info.get('owner_id')
            current_largest_army_count = largest_army_info.get('count', 0)

            # Condición 1: Tomar el ejército más grande
            if knights_after_playing_one >= 3 and \
               knights_after_playing_one > current_largest_army_count:
                play_knight_score += knight_heuristics.get("knight_take_largest_army_bonus", 1.5)
            
            # Condición 2: Mantener/Aumentar el ejército si ya lo tengo y alguien se acerca
            elif current_largest_army_owner == self.id and \
                 knights_after_playing_one > current_largest_army_count: \
                play_knight_score += knight_heuristics.get("knight_maintain_largest_army_bonus", 1.0)
            
            # Condición 3: Acercarse significativamente o igualar al líder del ejército (que no soy yo)
            elif knights_after_playing_one >= 2 and \
                 current_largest_army_count >=3 and \
                 (current_largest_army_count - knights_after_playing_one) <= 1 and \
                 current_largest_army_owner != self.id :
                play_knight_score += knight_heuristics.get("knight_contest_largest_army_bonus", 0.8)
            
            # (Opcional) Heurística avanzada: Jugar caballero para ganar la partida.
            # Esto requeriría una estimación precisa de los PV totales del agente (estructurales, cartas, ejército, ruta).
            # player_total_vps = self.get_victory_points() # Necesitaría un método robusto
            # if player_total_vps_before_knight_potentially_gives_army_vps == 8 and \
            #    (condición 1 o 2 se cumple y otorga 2 PVs por Mayor Ejército):
            #    play_knight_score += knight_heuristics.get("knight_for_win_bonus", 5.0)

            # INICIO DE MODIFICACIÓN: Bonus para juego temprano de Caballeros
            if current_turn < early_game_thresh:
                if self.had_suboptimal_start:
                    play_knight_score += knight_heuristics.get("early_game_knight_suboptimal_start_boost", 1.0)
                
                # Comprobar si el ladrón está en una casilla clave del agente
                if thief_terrain_id != -1:
                    # Definir "casilla clave": alta producción para el agente.
                    # Estimación simple: Si el agente tiene un asentamiento/ciudad en el terreno del ladrón
                    # y ese terreno no es el desierto y tiene un número de producción > 0 (no 7).
                    terrain_of_thief = self.board.terrain[thief_terrain_id]
                    if not self._is_terrain_desert(terrain_of_thief) and terrain_of_thief.get('probability', 0) != 7:
                        for node_id_on_thief_terrain in self.board.terrain_node_config[thief_terrain_id]:
                            if self.board.nodes[node_id_on_thief_terrain]['player'] == self.id:
                                play_knight_score += knight_heuristics.get("early_game_knight_robber_on_key_tile_boost", 1.5)
                                break # Bonus aplicado, no necesita seguir verificando nodos en este terreno
            # FIN DE MODIFICACIÓN

            min_score_to_play_knight = knight_heuristics.get("min_score_to_play_knight_on_start", 0.75)

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
        
        # INICIO DE MODIFICACIÓN: Lógica para comercio proactivo por exceso de recursos
        surplus_threshold = trade_heuristics.get("resource_surplus_threshold_for_proactive_trade", 5)
        proactive_bonus = trade_heuristics.get("proactive_trade_score_bonus", 0.3)
        current_max_score_for_proactive = -float('inf') # Reiniciar para esta lógica específica
        best_proactive_offer = None

        for i, count_we_have in enumerate(self.hand.resources):
            if count_we_have >= surplus_threshold:
                material_to_give_id = ordered_material_constants[i]
                if material_to_give_id is None: continue

                qty_to_give, qty_to_receive, port_type = self._get_best_trade_ratio(material_to_give_id)

                if count_we_have >= qty_to_give:
                    # Intentar obtener cualquier otro recurso que NO sea el que tenemos en exceso
                    for material_to_receive_id_idx, other_material_const in enumerate(ordered_material_constants):
                        if other_material_const == material_to_give_id: continue # No intercambiar por sí mismo
                        
                        # Calcular un score base para este comercio proactivo
                        proactive_trade_score = proactive_bonus
                        # Añadir un pequeño incentivo si el recurso a recibir es generalmente valioso
                        proactive_trade_score += trade_heuristics.get("resource_needed_importance", {}).get(other_material_const, 1.0) * 0.1 # Pequeño factor de "necesidad general"

                        if qty_to_give == 4: # Banco
                            proactive_trade_score += trade_heuristics.get("bank_trade_ratio_modifier", -0.2)
                        elif qty_to_give == 3 or qty_to_give == 2: # Puerto
                            proactive_trade_score += trade_heuristics.get("port_trade_ratio_modifier", -0.1)

                        if proactive_trade_score > current_max_score_for_proactive:
                            current_max_score_for_proactive = proactive_trade_score
                            best_proactive_offer = {
                                'gives': material_to_give_id,
                                'receives': other_material_const,
                                'quantity_gives': qty_to_give,
                                'quantity_receives': qty_to_receive
                            }
        
        # Solo realizar el comercio proactivo si su score supera un umbral mínimo (puede ser el mismo min_score_for_trade o uno diferente)
        if best_proactive_offer and current_max_score_for_proactive > min_score_for_trade: # Reutilizar el umbral existente por ahora
            return best_proactive_offer
        # FIN DE MODIFICACIÓN

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

        # INICIO DE MODIFICACIÓN: Ajustes estratégicos a la puntuación del trato
        if player_making_offer is not None and player_making_offer != self.id:
            # Estimación de PVs estructurales del ofertante para identificar líderes potenciales.
            offerer_structural_vps = 0
            # Asumimos que self.board.get_player_structural_victory_points(player_id) podría existir.
            # Por ahora, hacemos un conteo manual si el método no está disponible.
            if hasattr(self.board, 'get_player_structural_victory_points'): 
                offerer_structural_vps = self.board.get_player_structural_victory_points(player_making_offer)
            else:
                for n_data in self.board.nodes:
                    if n_data['player'] == player_making_offer:
                        offerer_structural_vps += 1
                        if n_data['has_city']: offerer_structural_vps +=1
            
            vps_threshold_leader = trade_heuristics.get("vps_threshold_consider_leader_trade", 7)
            penalty_trade_with_leader = trade_heuristics.get("penalty_trade_with_leader", 0.5)

            if offerer_structural_vps >= vps_threshold_leader:
                # Si el ofertante parece ser un líder, se aplica una penalización al score del trato,
                # haciendo al agente más reacio a comerciar con él.
                trade_score -= penalty_trade_with_leader
        # FIN DE MODIFICACIÓN

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
            score = heuristic_val * self.chromosome["build_actions"].get(BuildConstants.CARD, 0.5) 
            possible_actions.append({"type": BuildConstants.CARD, "score": score, "details": None, "cost": cost_card})

        # 2. Evaluar Construir Carretera
        cost_road = Materials.from_iterable(BuildMaterialsConstants[BuildConstants.ROAD])
        best_road_option_details = None
        max_road_score = -float('inf')

        if self.hand.resources.has_more(cost_road):
            valid_roads = self.board.valid_road_nodes(self.id) 
            scored_road_options = []
            for road_option in valid_roads:
                from_node = road_option['starting_node']
                to_node = road_option['finishing_node']
                road_already_exists = False
                for existing_road in self.board.nodes[from_node]['roads']:
                    if existing_road['node_id'] == to_node:
                        road_already_exists = True
                        break
                if road_already_exists:
                    continue
                heuristic_val = self._heuristic_road_location(from_node, to_node)
                scored_road_options.append({"from_node": from_node, "to_node": to_node, "score": heuristic_val})
            
            if scored_road_options:
                best_scored_road_option = max(scored_road_options, key=lambda x: x["score"])
                max_road_score = best_scored_road_option["score"] * self.chromosome["build_actions"].get(BuildConstants.ROAD, 0.7)
                best_road_option_details = {"from_node": best_scored_road_option["from_node"], "to_node": best_scored_road_option["to_node"]}

            # INICIO DE MODIFICACIÓN: Lógica de fallback para carreteras subóptimas
            min_road_score_thresh = self.chromosome["build_actions"].get("min_road_score_for_deterministic_build", 1.5)
            actual_heuristic_road_score = max_road_score / self.chromosome["build_actions"].get(BuildConstants.ROAD, 0.7) if best_road_option_details else -float('inf')

            if best_road_option_details and actual_heuristic_road_score < min_road_score_thresh:
                # La mejor carretera determinista es subóptima
                fallback_prob = self.chromosome["road_heuristics"].get("fallback_suboptimal_road_build_probability", 0.4)
                if random.random() < fallback_prob:
                    # Decidimos construir una carretera aleatoria válida en lugar de la subóptima o ninguna
                    if valid_roads: # Asegurarnos de que hay opciones para elegir aleatoriamente
                        chosen_random_road = random.choice(valid_roads)
                        fallback_road_score = self.chromosome["road_heuristics"].get("fallback_suboptimal_road_action_score", 0.5)
                        possible_actions.append({
                            "type": BuildConstants.ROAD,
                            "score": fallback_road_score, # Usar el score de fallback configurado
                            "details": {"from_node": chosen_random_road['starting_node'], "to_node": chosen_random_road['finishing_node']},
                            "cost": cost_road
                        })
                    # Si no hay valid_roads, no se añade nada (ya se manejó que scored_road_options estaría vacío)
                else:
                    # No se activa el fallback aleatorio, pero aún podríamos añadir la carretera subóptima si su score es competitivo
                    # La añadimos con su score original para que compita.
                     possible_actions.append({
                        "type": BuildConstants.ROAD,
                        "score": max_road_score, 
                        "details": best_road_option_details,
                        "cost": cost_road
                    })
            elif best_road_option_details: # Carretera determinista es buena o no hay fallback
                 possible_actions.append({
                    "type": BuildConstants.ROAD,
                    "score": max_road_score, 
                    "details": best_road_option_details,
                    "cost": cost_road
                })
            # FIN DE MODIFICACIÓN
        
        # 3. Evaluar Construir Poblado
        cost_town = Materials.from_iterable(BuildMaterialsConstants[BuildConstants.TOWN])
        num_settlements = len([n for n in self.board.nodes if n['player'] == self.id and not n['has_city']])
        if self.hand.resources.has_more(cost_town) and num_settlements < 5:
            valid_nodes_for_town = self.board.valid_town_nodes(self.id) 
            for node_id in valid_nodes_for_town:
                heuristic_val = self._heuristic_settlement_location(node_id)
                score = heuristic_val * self.chromosome["build_actions"].get(BuildConstants.TOWN, 1.0) # Usar .get con default
                possible_actions.append({
                    "type": BuildConstants.TOWN,
                    "score": score,
                    "details": {"node_id": node_id},
                    "cost": cost_town
                })

        # 4. Evaluar Construir Ciudad
        cost_city = Materials.from_iterable(BuildMaterialsConstants[BuildConstants.CITY])
        num_cities = len([n for n in self.board.nodes if n['player'] == self.id and n['has_city']])
        if self.hand.resources.has_more(cost_city) and num_cities < 4:
            valid_nodes_for_city_upgrade = self.board.valid_city_nodes(self.id) 
            for node_id in valid_nodes_for_city_upgrade: 
                heuristic_val = self._heuristic_city_location(node_id)
                score = heuristic_val * self.chromosome["build_actions"].get(BuildConstants.CITY, 0.9) # Usar .get con default
                possible_actions.append({
                    "type": BuildConstants.CITY,
                    "score": score,
                    "details": {"node_id": node_id},
                    "cost": cost_city
                })

        if not possible_actions:
            return None

        # INICIO DE MODIFICACIÓN: Ajuste de scores basado en PVs y selección final.
        player_structural_vps = 0
        # Intentamos obtener los PV estructurales del agente. Esta es una estimación.
        # Idealmente, el agente tendría un método robusto self.get_victory_points().
        for n_data in self.board.nodes:
            if n_data['player'] == self.id:
                player_structural_vps += 1 # 1 VP por poblado
                if n_data['has_city']:
                    player_structural_vps +=1 # 1 VP adicional por ciudad
        
        vps_threshold = self.chromosome["build_actions"].get("late_game_vps_threshold", 7)
        late_game_pv_bonus_city = self.chromosome["build_actions"].get("late_game_pv_bonus_city", 2.0)
        late_game_pv_card_multiplier = self.chromosome["build_actions"].get("late_game_pv_card_multiplier", 1.2)

        adjusted_actions = []
        for action in possible_actions:
            adjusted_score = action["score"] 

            if player_structural_vps >= vps_threshold:
                if action["type"] == BuildConstants.CITY:
                    adjusted_score += late_game_pv_bonus_city
                elif action["type"] == BuildConstants.CARD:
                    adjusted_score *= late_game_pv_card_multiplier
            
            # INICIO DE MODIFICACIÓN: Aplicar bonus si el inicio fue subóptimo
            if self.had_suboptimal_start and \
               hasattr(self.board, 'turn_number') and \
               self.board.turn_number < self.chromosome["build_actions"].get("suboptimal_start_bonus_decay_turn", 15):
                
                if action["type"] == BuildConstants.CARD:
                    adjusted_score += self.chromosome["build_actions"].get("suboptimal_start_card_buy_bonus", 0.3)
                elif action["type"] == BuildConstants.TOWN:
                    adjusted_score += self.chromosome["build_actions"].get("suboptimal_start_town_build_bonus", 0.2)
            # FIN DE MODIFICACIÓN

            adjusted_actions.append({**action, "adjusted_score": adjusted_score})

        if not adjusted_actions:
            return None

        # INICIO DE MODIFICACIÓN: Lógica de priorización en "Recuperación Temprana"
        if self.had_suboptimal_start and \
           hasattr(self.board, 'turn_number') and \
           self.board.turn_number < self.chromosome["build_actions"].get("suboptimal_start_bonus_decay_turn", 15):
            
            # Aplicar los bonus de recuperación directamente a las acciones correspondientes
            # Estos bonus son significativos para alterar las prioridades.
            for action_data in adjusted_actions:
                if action_data["type"] == BuildConstants.TOWN:
                    action_data["adjusted_score"] += self.chromosome["build_actions"].get("suboptimal_start_town_build_bonus", 2.0)
                elif action_data["type"] == BuildConstants.CARD:
                    action_data["adjusted_score"] += self.chromosome["build_actions"].get("suboptimal_start_card_buy_bonus", 1.5)
                elif action_data["type"] == BuildConstants.ROAD:
                    action_data["adjusted_score"] += self.chromosome["build_actions"].get("suboptimal_start_road_build_bonus", 0.5)
            # Nota: La lógica anterior que aplicaba bonus más pequeños en esta sección ha sido reemplazada / subsumida por esta. 
            # Los bonus por late_game_pv_bonus_city etc., seguirán aplicándose antes de este bloque si procede.
        # FIN DE MODIFICACIÓN

        best_action_data = max(adjusted_actions, key=lambda x: x["adjusted_score"])
        
        min_score_threshold = self.chromosome["build_actions"].get("min_overall_score_threshold", 0.1)
        if best_action_data["adjusted_score"] < min_score_threshold:
             return None
            
        # Devolvemos un diccionario con la información de la acción original, no la que tiene "adjusted_score".
        # Creamos una copia de la acción para no modificar la lista original y eliminamos "adjusted_score" si no es necesario fuera.
        final_action_to_return = {k: v for k, v in best_action_data.items() if k != 'adjusted_score'}
        return final_action_to_return
        # FIN DE MODIFICACIÓN

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
        high_probability_numbers_count = 0 # Contador para terrenos con números de alta probabilidad
        high_prob_numbers = {5, 6, 8, 9} # Definir números de alta probabilidad

        for terrain_idx in contacting_terrain_indices:
            terrain = self.board.terrain[terrain_idx]
            if not self._is_terrain_desert(terrain): 
                resource_type = terrain.get('terrain_type')
                terrain_number = terrain.get('probability') 

                if terrain_number is not None and terrain_number != 7: 
                    prob_dots = dice_roll_to_dots.get(terrain_number, 0)
                    prob_real = prob_dots / 36.0
                    
                    resource_weight = city_chrom_heuristics["resource_priority"].get(resource_type, 0.1)
                    exponent = city_chrom_heuristics["production_probability_exponent"]
                    
                    production_from_terrain = 2 * (prob_real ** exponent) * resource_weight
                    node_resource_production_value += production_from_terrain

                    if terrain_number in high_prob_numbers:
                        high_probability_numbers_count += 1
        
        heuristic_score = node_resource_production_value * city_chrom_heuristics["resource_value_base"]

        # INICIO DE MODIFICACIÓN: Bonus por múltiples números de alta probabilidad
        if high_probability_numbers_count >= 2: # Si hay al menos dos terrenos adyacentes con números altos
            heuristic_score += city_chrom_heuristics.get("multiple_high_prob_numbers_bonus", 2.0)
        # FIN DE MODIFICACIÓN
        
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

        resource_produced = terrain_data['terrain_type']
        block_priority_map = robber_heuristics.get("block_specific_resource_priority", {})
        heuristic_score += block_priority_map.get(resource_produced, 0.0)

        if has_my_node:
            heuristic_score += robber_heuristics.get("avoid_own_nodes_penalty", -5.0)
        
        # INICIO DE MODIFICACIÓN: Lógica avanzada para targetear oponentes líderes y recursos clave
        player_vps = {} # Almacena PVs estimados de jugadores
        if hasattr(self.board, 'get_player_structural_victory_points'): # Ideal
            for n_data_vp_check in self.board.nodes:
                p_id = n_data_vp_check['player']
                if p_id != -1 and p_id != self.id and p_id not in player_vps:
                    player_vps[p_id] = self.board.get_player_structural_victory_points(p_id)
        else: # Fallback a conteo manual
            for n_data_vp_check in self.board.nodes:
                p_id = n_data_vp_check['player']
                if p_id != -1 and p_id != self.id:
                    player_vps[p_id] = player_vps.get(p_id, 0) + (2 if n_data_vp_check['has_city'] else 1)

        my_estimated_vps = player_vps.get(self.id, 0) # Obtener mis propios PVs si se calcularon
        if not hasattr(self.board, 'get_player_structural_victory_points'): # Si hicimos conteo manual, calcular los míos también
            my_own_vps_temp = 0
            for n_data_vp_check in self.board.nodes:
                 if n_data_vp_check['player'] == self.id:
                    my_own_vps_temp += (2 if n_data_vp_check['has_city'] else 1)
            my_estimated_vps = my_own_vps_temp
        
        leader_vps_adv_thresh = robber_heuristics.get("leader_vps_advantage_threshold_for_targeting", 2)
        target_leader_bonus = robber_heuristics.get("target_leader_high_production_resource_bonus", 1.5)
        target_needed_bonus = robber_heuristics.get("target_needed_resource_on_opponent_bonus", 1.0)

        for node_id in terrain_data["contacting_nodes"]:
            node_player_id = self.board.nodes[node_id]['player']
            if node_player_id != -1 and node_player_id != self.id:
                opponent_vps = player_vps.get(node_player_id, 0)
                # Es un líder digno de targetear?
                if opponent_vps >= my_estimated_vps + leader_vps_adv_thresh:
                    heuristic_score += target_leader_bonus
                
                # Este terreno produce un recurso que necesito y este oponente lo tiene?
                # (Simplificación: asumimos que si el oponente está en el nodo, se beneficia del recurso)
                # Necesitaríamos una lista de `self.get_needed_resources()` para ser más precisos.
                # Por ahora, si el recurso producido es CEREAL o MINERAL (generalmente valiosos y necesitados):
                if resource_produced == MaterialConstants.CEREAL or resource_produced == MaterialConstants.MINERAL:
                    heuristic_score += target_needed_bonus * 0.5 # Ponderar un poco menos sin saber necesidad exacta
        # FIN DE MODIFICACIÓN

        if opponent_nodes_count == 0 and not has_my_node: 
            heuristic_score -= 2.0 

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
            # INICIO DE MODIFICACIÓN: Selección estratégica del jugador a robar.
            robbable_players_details = []
            unique_opponent_ids_on_terrain = list(set(players_on_chosen_terrain))

            for p_id in unique_opponent_ids_on_terrain:
                p_vps = 0
                # Estimación de PVs estructurales. Un método self.board.get_player_structural_victory_points(p_id) sería ideal.
                if hasattr(self.board, 'get_player_structural_victory_points'):
                    p_vps = self.board.get_player_structural_victory_points(p_id)
                else: # Fallback a conteo manual
                    for n_data in self.board.nodes:
                        if n_data['player'] == p_id:
                            p_vps += 1
                            if n_data['has_city']: p_vps +=1
                robbable_players_details.append({'id': p_id, 'vps': p_vps})

            if robbable_players_details:
                # Ordenar jugadores por PVs (descendente) para priorizar al líder.
                robbable_players_details.sort(key=lambda x: x['vps'], reverse=True)
                
                # El cromosoma ya tiene `target_opponent_with_most_vps_bias`.
                # Usaremos este bias para decidir si siempre robar al de más PVs o introducir aleatoriedad.
                # Una implementación simple: si el bias es alto (e.g., > 0.5), robar al líder. Sino, más aleatorio.
                # Por ahora, si hay algún bias positivo, se prioriza al líder. Si no, aleatorio.
                # Esto podría refinarse con una lógica probabilística basada en el valor del bias.
                bias_value = self.chromosome.get("robber_placement_heuristics", {}).get("target_opponent_with_most_vps_bias", 0.0)

                if bias_value > 0.25 and robbable_players_details: # Umbral pequeño para activar el sesgo
                    player_to_rob_id = robbable_players_details[0]['id'] # Robar al de más PVs
                else:
                    # Si no hay sesgo o es bajo, o no hay detalles de PV, elección aleatoria entre los presentes.
                    player_to_rob_id = random.choice([p['id'] for p in robbable_players_details])
            
            elif unique_opponent_ids_on_terrain: # Fallback si no se pudieron obtener PVs pero hay jugadores
                 player_to_rob_id = random.choice(unique_opponent_ids_on_terrain)
            # FIN DE MODIFICACIÓN
        
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