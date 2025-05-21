import random
import json # Para guardar/cargar cromosomas
import os
import sys
from datetime import datetime
import gc # <--- AÑADIDO

# Necesitamos añadir la ruta de PyCatan al sys.path para que los imports funcionen
# si ejecutas este script desde fuera del directorio PyCatan.
# Si está en la raíz de PyCatan, esto podría no ser estrictamente necesario,
# pero es una buena práctica para asegurar que los módulos se encuentren.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # Asumiendo que entrenador_genetico.py está en PyCatan/
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ahora intentamos los imports sabiendo que PyCatan está en el path
try:
    from Agents.GeneticAgent import GeneticAgent
    from Agents.RandomAgent import RandomAgent
    from Agents.AdrianHerasAgent import AdrianHerasAgent
    # Importa otros agentes que quieras usar como oponentes
    from Agents.EdoAgent import EdoAgent
    from Agents.SigmaAgent import SigmaAgent
    from Agents.AlexPastorAgent import AlexPastorAgent
    from Agents.AlexPelochoJaimeAgent import AlexPelochoJaimeAgent
    # Imports de agentes adicionales para la lista extendida de oponentes
    from Agents.CarlesZaidaAgent import CarlesZaidaAgent
    from Agents.CrabisaAgent import CrabisaAgent
    from Agents.PabloAleixAlexAgent import PabloAleixAlexAgent
    from Agents.TristanAgent import TristanAgent
    # Importa el GameDirector
    from Managers.GameDirector import GameDirector # MODIFICADO: Usar GameDirector
    # Board ya no es necesario aquí directamente, GameDirector lo maneja.
    
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que la estructura de tu proyecto y los nombres de los módulos son correctos.")
    print(f"Current sys.path: {sys.path}")
    exit(1)


# --- Hiperparámetros del AG ---
TAMANO_POBLACION = 30 
NUM_GENERACIONES = 500  
# NOTA: NUM_GENERACIONES se reemplazará por un esquema de bloques de rivales
# PROBABILIDAD_CRUCE y PROBABILIDAD_MUTACION_GEN se volverán dinámicos o servirán de base.
PROBABILIDAD_CRUCE = 0.9
# PROBABILIDAD_MUTACION_GEN ya no será una constante fija global para la mutación
# MAGNITUD_MUTACION_MAX_PORCENTAJE también se volverá dinámico

# Nuevos parámetros para el entrenamiento por bloques de rivales y adaptación dinámica
GENS_POR_RIVAL = 10 # Número de generaciones a entrenar contra cada rival
NUM_PARTIDAS_EVALUACION_POR_POSICION = 1 # Partidas por cada una de las 4 posiciones. Total 4 partidas.
                                         # El fitness será la suma de victorias en estas 4 partidas.
NUM_PARTIDAS_EVALUACION = 4 # Total de partidas para evaluar un cromosoma (1 por cada posición)

# Lista completa de clases de agentes oponentes
# NOTA: El usuario mencionó 11 rivales. Actualmente hay 10. Revisar y completar si es necesario.
AGENTES_OPONENTES_TODOS = [
    RandomAgent, 
    AdrianHerasAgent, 
    EdoAgent, 
    SigmaAgent,
    AlexPastorAgent,
    AlexPelochoJaimeAgent,
    CarlesZaidaAgent,
    CrabisaAgent,
    PabloAleixAlexAgent,
    TristanAgent
    # Añadir más agentes aquí si es necesario para llegar a 11
]

NUM_ELITES = 5 # Elitismo dentro de un bloque de rival
NUM_ELITES_ENTRE_BLOQUES = 2 # Número de élites a conservar al cambiar de rival
FRACCION_RESET_POBLACION_ENTRE_BLOQUES = 0.8 # Fracción de la población a reemplazar con nuevos individuos aleatorios al cambiar de rival (conservando NUM_ELITES_ENTRE_BLOQUES)

# Parámetros para la mutación adaptativa
PROB_MUTACION_INICIAL = 0.15
MAGNITUD_MUTACION_INICIAL_PORCENTAJE = 0.20
PROB_MUTACION_MIN = 0.05
PROB_MUTACION_MAX = 0.50
MAGNITUD_MUTACION_MIN_PORCENTAJE = 0.05
MAGNITUD_MUTACION_MAX_PORCENTAJE = 0.50
GENERACIONES_SIN_MEJORA_UMBRAL = 3 # Número de generaciones sin mejora para incrementar mutación
FACTOR_AJUSTE_MUTACION_PROB = 0.05 # Cuánto aumentar/disminuir la probabilidad de mutación
FACTOR_AJUSTE_MUTACION_MAGNITUD = 0.05 # Cuánto aumentar/disminuir la magnitud de mutación

# Asegúrate que estas clases de agentes existen y son importables
AGENTES_OPONENTES_CLASES = [ # Esta lista se usará si no hay un rival fijo (comportamiento anterior)
    RandomAgent, 
    AdrianHerasAgent, 
    EdoAgent, 
    SigmaAgent,
    AlexPastorAgent,
    AlexPelochoJaimeAgent
] 
NUM_ELITES = 5 
LOG_FILE = "genetic_training_log.txt"
BEST_CHROMOSOME_FILE = "best_chromosome.json"
FITNESS_PROGRESS_FILE = "fitness_por_generacion.csv" # Nuevo archivo para el progreso del fitness
# Nuevo: Máximo de rondas por partida para evitar bloqueos
MAX_ROUNDS_PER_GAME = 200 

# Variables globales para la mutación adaptativa (se inicializarán en main)
prob_mutacion_actual = PROB_MUTACION_INICIAL
magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_INICIAL_PORCENTAJE


def log_message(message):
    """Registra un mensaje en la consola y en un archivo de log."""
    print(message)
    with open(LOG_FILE, "a", encoding='utf-8') as f: # Añadido encoding
        f.write(f"{datetime.now()}: {message}\\n")

def inicializar_cromosoma():
    """Genera un cromosoma inicial (diccionario de pesos)."""
    # El ID del agente es temporal, no se usará realmente en la creación del cromosoma base.
    cromosoma_base = GeneticAgent(agent_id=-1)._initialize_default_chromosome() 

    def perturbar_recursivo(item):
        if isinstance(item, dict):
            return {k: perturbar_recursivo(v) for k, v in item.items()}
        elif isinstance(item, (float, int)):
            variacion = item * random.uniform(-0.5, 0.5) if item != 0 else random.uniform(-0.5, 0.5)
            nuevo_valor = item + variacion
            if isinstance(item, float) and 0 <= cromosoma_base.get(list(cromosoma_base.keys())[0] if cromosoma_base else "", {}).get("suboptimal_start_bonus_decay_turn", 0) <=1 : # heuristica para probabilidad
                 return max(0.0, min(1.0, nuevo_valor))
            if item >= 0: 
                 return max(0.0, nuevo_valor)
            return nuevo_valor
        return item

    return perturbar_recursivo(cromosoma_base)

def inicializar_poblacion():
    """Crea la población inicial de cromosomas."""
    return [inicializar_cromosoma() for _ in range(TAMANO_POBLACION)]

def calcular_fitness(cromosoma, clase_rival_fijo=None):
    """
    Evalúa un cromosoma jugando partidas y devuelve su fitness.
    El fitness se define como el número total de partidas ganadas.
    El GeneticAgent rotará su posición de inicio (0, 1, 2, 3).
    Si clase_rival_fijo se proporciona, los 3 oponentes serán de esa clase.
    De lo contrario, se seleccionarán 3 oponentes aleatoriamente de AGENTES_OPONENTES_CLASES.
    """
    victorias_agente_genetico = 0
    partidas_jugadas_validas = 0

    GeneticAgent.chromosome_para_entrenamiento_actual = cromosoma

    for i in range(NUM_PARTIDAS_EVALUACION): # NUM_PARTIDAS_EVALUACION ahora es 4
        genetic_agent_sim_id = i # Esto directamente asigna la posición 0, 1, 2, 3

        agent_classes_for_director = [None] * 4
        agent_classes_for_director[genetic_agent_sim_id] = GeneticAgent
        
        oponentes_para_partida_clases = []
        if clase_rival_fijo:
            oponentes_para_partida_clases = [clase_rival_fijo, clase_rival_fijo, clase_rival_fijo]
        else:
            # Comportamiento anterior: seleccionar oponentes aleatorios del pool general
            possible_opponent_pool = [
                op_class for op_class in AGENTES_OPONENTES_CLASES 
                if op_class != GeneticAgent
            ]
            if not possible_opponent_pool or len(possible_opponent_pool) < 3:
                log_message("Advertencia: El pool de oponentes (general) es insuficiente. Rellenando con RandomAgent.")
                while len(possible_opponent_pool) < 3:
                    possible_opponent_pool.append(RandomAgent)
            
            if len(possible_opponent_pool) >= 3:
                oponentes_para_partida_clases = random.sample(possible_opponent_pool, 3)
            else: 
                oponentes_para_partida_clases = list(possible_opponent_pool)
                while len(oponentes_para_partida_clases) < 3:
                    oponentes_para_partida_clases.append(RandomAgent)
                oponentes_para_partida_clases = oponentes_para_partida_clases[:3]

        idx_opponent_list = 0
        for pos in range(4):
            if agent_classes_for_director[pos] is None:
                if idx_opponent_list < len(oponentes_para_partida_clases):
                    agent_classes_for_director[pos] = oponentes_para_partida_clases[idx_opponent_list]
                    idx_opponent_list += 1
                else:
                    # Esto no debería ocurrir si la lógica de oponentes es correcta
                    log_message("Error crítico en asignación de oponentes (fallback). Usando RandomAgent.")
                    agent_classes_for_director[pos] = RandomAgent
        
        try:
            game_director = GameDirector(agents=agent_classes_for_director, 
                                         max_rounds=MAX_ROUNDS_PER_GAME, 
                                         store_trace=True)
            game_trace = game_director.game_start(print_outcome=False)
            
            partidas_jugadas_validas +=1

            if not game_trace or "game" not in game_trace or not game_trace["game"]:
                log_message(f"    Partida {i+1} no produjo un trace válido. Saltando.")
                # No se suma victoria, se considera una partida no concluyente para el fitness.
                # Liberar memoria del trace y director si la partida falla pronto
                if 'game_director' in locals(): del game_director
                if 'game_trace' in locals(): del game_trace
                # gc.collect() # Podría ser muy frecuente aquí
                continue

            last_round_key = max(game_trace["game"].keys(), key=lambda r_key: int(r_key.split("_")[-1]))
            
            if not game_trace["game"][last_round_key]:
                log_message(f"    Partida {i+1}, última ronda ({last_round_key}) vacía. Saltando.")
                # Liberar memoria
                if 'game_director' in locals(): del game_director
                if 'game_trace' in locals(): del game_trace
                # gc.collect()
                continue

            last_turn_key = max(game_trace["game"][last_round_key].keys(), key=lambda t_key: int(t_key.split("_")[-1].lstrip("P")))
            
            turn_data = game_trace["game"][last_round_key][last_turn_key]
            if "end_turn" not in turn_data or "victory_points" not in turn_data["end_turn"]:
                log_message(f"    Partida {i+1} no tiene datos de 'victory_points' en el último turno. Saltando.")
                # Liberar memoria
                if 'game_director' in locals(): del game_director
                if 'game_trace' in locals(): del game_trace
                # gc.collect()
                continue
            else:
                puntos_jugadores_dict = turn_data["end_turn"]["victory_points"]
            
            parsed_scores = {}
            for player_key, score in puntos_jugadores_dict.items():
                try:
                    player_idx = int(player_key.lstrip("J"))
                    parsed_scores[player_idx] = int(score)
                except ValueError:
                    log_message(f"Advertencia: No se pudo parsear la clave de jugador '{player_key}' o el score '{score}'")
                    parsed_scores[player_idx] = 0 

            if not parsed_scores:
                log_message(f"    Partida {i+1}: No se pudieron determinar los scores.")
                continue
            
            ranked_players = sorted(parsed_scores.items(), key=lambda item: item[1], reverse=True)
            
            winner_id_numeric = -1
            if ranked_players:
                # Comprobar si hay empate en el primer puesto
                max_score = ranked_players[0][1]
                winners = [p_id for p_id, p_score in ranked_players if p_score == max_score]
                # Si el agente genético es uno de los ganadores (incluso en empate), cuenta como victoria.
                # O, si se prefiere una victoria única estricta:
                # if len(winners) == 1 and winners[0] == genetic_agent_sim_id:
                if genetic_agent_sim_id in winners: # Contar como victoria si está entre los que tienen puntuación máxima
                     victorias_agente_genetico += 1
                     winner_id_numeric = genetic_agent_sim_id # Para el log, si es relevante
                elif winners: # Si hay ganadores pero no es el genético
                    winner_id_numeric = winners[0] # Tomar el primero para el log

        except Exception as e_partida:
            log_message(f"    Error durante la partida {i+1}: {e_partida}. Partida no contabilizada para fitness.")
            # No se incrementa partidas_jugadas_validas si la partida crashea antes de finalizar y registrar scores.
            # O si se incrementó antes, aquí no se contabiliza la victoria.
            # La lógica actual incrementa partidas_jugadas_validas al inicio del try.
            # Si hay error, no se suma victoria.
        finally:
            # Asegurarse de limpiar game_director y game_trace después de cada partida
            if 'game_director' in locals():
                del game_director
            if 'game_trace' in locals():
                del game_trace
            # gc.collect() # Llamar gc.collect() después de cada partida puede ser costoso.
                           # Hacerlo al final de la evaluación del individuo podría ser un compromiso.

    if hasattr(GeneticAgent, 'chromosome_para_entrenamiento_actual'):
        del GeneticAgent.chromosome_para_entrenamiento_actual
    
    if partidas_jugadas_validas == 0:
        log_message("  No se completaron partidas válidas para este individuo. Fitness = 0.")
        return 0 # Fitness es el número de victorias, si no hay partidas válidas, es 0.

    # El fitness es simplemente el número de victorias.
    fitness = victorias_agente_genetico
    
    log_message(f"  Individuo evaluado ({partidas_jugadas_validas} partidas válidas de {NUM_PARTIDAS_EVALUACION}): {victorias_agente_genetico} victorias -> Fitness: {fitness}")
    return fitness

def seleccion_padres(poblacion_evaluada):
    """Selecciona dos padres de la población evaluada (lista de tuplas (cromosoma, fitness))."""
    padres = []
    for _ in range(2):
        # Selección por torneo de tamaño 3
        # Asegurarse de que hay suficientes individuos para el torneo
        sample_size = min(3, len(poblacion_evaluada))
        if sample_size < 1: # No hay nadie para seleccionar
             # Esto no debería ocurrir si la población se maneja bien, pero es una salvaguarda.
             # Devolver dos individuos aleatorios o los mejores si solo hay 1 o 2.
             if len(poblacion_evaluada) >=1:
                padres.append(poblacion_evaluada[0][0]) # Tomar el mejor
                if len(poblacion_evaluada) >=2 and len(padres) < 2:
                    padres.append(poblacion_evaluada[1][0])
                elif len(padres) < 2: # Si solo hay uno, duplicarlo
                    padres.append(poblacion_evaluada[0][0])

             else: #Poblacion vacía, crear nuevos (esto es una recuperación de error)
                log_message("Advertencia: Población evaluada vacía o muy pequeña en seleccion_padres. Creando cromosoma aleatorio.")
                padres.append(inicializar_cromosoma())
                if len(padres) < 2: padres.append(inicializar_cromosoma())

             # Salir del bucle for si ya hemos llenado los padres o no podemos hacer más.
             if len(padres) == 2: break
             else: continue # Intentar llenar el resto si es posible (aunque unlikely con este error)

        participantes_torneo = random.sample(poblacion_evaluada, sample_size)
        participantes_torneo.sort(key=lambda x: x[1], reverse=True) # El mejor fitness gana
        padres.append(participantes_torneo[0][0]) # Se selecciona el cromosoma del ganador
    
    # Si por alguna razón no se seleccionaron 2 padres (ej. población muy pequeña al inicio del bucle)
    while len(padres) < 2:
        log_message("Advertencia: No se pudieron seleccionar 2 padres por torneo, usando el mejor disponible o aleatorio.")
        if poblacion_evaluada and poblacion_evaluada[0][1] > -float('inf'): # Asegurarse que el mejor no falló catastróficamente
            padres.append(poblacion_evaluada[0][0]) # Añadir el mejor de nuevo
        else: # Si todos fallaron o la población está vacía
            padres.append(inicializar_cromosoma()) # Añadir uno aleatorio si la población está vacía.

    return padres[0], padres[1]

def cruzar_cromosomas(padre1_cromo, padre2_cromo):
    """Realiza el cruce entre dos cromosomas padres para producir un hijo."""
    # hijo_cromo = {} # Se define al final de la función interna

    def _recursive_crossover(p1_item, p2_item, key_path=""):
        # Case 1: Both items are dictionaries
        if isinstance(p1_item, dict) and isinstance(p2_item, dict):
            child_dict = {}
            
            # Normalize keys and determine preferred type (int if possible for numeric-like keys)
            # The structure will be: str_key -> {'v1': value_from_p1, 'v2': value_from_p2, 'type': preferred_type_for_child_key}
            processed_keys_data = {}

            # Process p1_item
            for k, v_p1 in p1_item.items():
                sk = str(k) # Key normalized to string for internal processing
                # Determine preferred type for this key: if k was int, prefer int. Else, original type of k.
                pref_type = int if isinstance(k, int) else type(k)
                processed_keys_data[sk] = {'v1': v_p1, 'v2': None, 'type': pref_type}

            # Process p2_item, update v2 in processed_keys_data and potentially upgrade preferred_type
            for k, v_p2 in p2_item.items():
                sk = str(k) # Key normalized to string
                current_pref_type_p2 = int if isinstance(k, int) else type(k)
                if sk in processed_keys_data:
                    processed_keys_data[sk]['v2'] = v_p2
                    # If p1's original key type was str and p2's is int for the same stringified key,
                    # upgrade the preferred type to int.
                    if processed_keys_data[sk]['type'] is str and current_pref_type_p2 is int:
                        processed_keys_data[sk]['type'] = int
                else: # Key was only in p2
                    processed_keys_data[sk] = {'v1': None, 'v2': v_p2, 'type': current_pref_type_p2}
            
            all_string_keys_to_process = processed_keys_data.keys()

            for str_k_for_processing in all_string_keys_to_process:
                data_for_key = processed_keys_data[str_k_for_processing]
                val_from_p1, val_from_p2, preferred_final_type = data_for_key['v1'], data_for_key['v2'], data_for_key['type']

                # current_kp is for debugging path or deeper recursion, uses the stringified key. This resolves the TypeError.
                current_recursive_key_path = key_path + "." + str_k_for_processing if key_path else str_k_for_processing

                # Determine the actual key to use for the child dictionary (e.g., int for MaterialConstants)
                final_key_for_child_dict = str_k_for_processing # Default to string
                if preferred_final_type is int:
                    try:
                        final_key_for_child_dict = int(str_k_for_processing)
                    except ValueError: 
                        # This case should ideally not be reached if preferred_final_type is int,
                        # as it implies str_k_for_processing was a valid integer string.
                        # If it does, it means a non-integer string key was marked to prefer int type,
                        # which indicates an issue in type preference logic. Fallback to string key.
                        final_key_for_child_dict = str_k_for_processing 
                
                if val_from_p1 is None: # Key was only in p2_item
                    child_dict[final_key_for_child_dict] = val_from_p2
                elif val_from_p2 is None: # Key was only in p1_item
                    child_dict[final_key_for_child_dict] = val_from_p1
                else: # Key in both items, recurse
                    child_dict[final_key_for_child_dict] = _recursive_crossover(val_from_p1, val_from_p2, current_recursive_key_path)
            return child_dict

        # Case 2: Both items are numeric (int or float) - Blending
        elif isinstance(p1_item, (int, float)) and isinstance(p2_item, (int, float)):
            alpha = random.uniform(0.3, 0.7) # Blend factor
            blended_value = alpha * p1_item + (1 - alpha) * p2_item
            # Preserve int type if both parents were int
            if isinstance(p1_item, int) and isinstance(p2_item, int):
                return round(blended_value)
            return blended_value

        # Case 3: Both items are boolean - Random choice
        elif isinstance(p1_item, bool) and isinstance(p2_item, bool):
            return random.choice([p1_item, p2_item])

        # Fallback Case: Types differ significantly (e.g., dict vs int),
        # or one of the items is of an unhandled type for paired processing.
        # Choose one parent's value randomly. This matches the original implicit fallback.
        else:
            return random.choice([p1_item, p2_item])

    hijo_cromo = _recursive_crossover(padre1_cromo, padre2_cromo)
    return hijo_cromo

def mutar_cromosoma(cromosoma):
    """Aplica mutación a un cromosoma."""
    
    def _recursive_mutation(item, key_path=""): 
        if isinstance(item, dict):
            return {k: _recursive_mutation(v, key_path + "." + str(k) if key_path else str(k)) for k, v in item.items()}
        elif isinstance(item, (float, int)):
            if random.random() < prob_mutacion_actual:
                original_value = item
                if isinstance(item, float) and 0 <= item <= 1: 
                    variacion = random.uniform(-magnitud_mutacion_actual_porcentaje * item, magnitud_mutacion_actual_porcentaje * item) if item != 0 else random.uniform(-0.1,0.1)
                    nuevo_valor = max(0.0, min(1.0, item + variacion))
                elif item >= 0: 
                    variacion = item * random.uniform(-magnitud_mutacion_actual_porcentaje, magnitud_mutacion_actual_porcentaje) if item !=0 else random.uniform(0, 0.2) 
                    nuevo_valor = max(0.0, item + variacion)
                    nuevo_valor = round(nuevo_valor) if isinstance(item, int) else nuevo_valor
                else: 
                    variacion = abs(item) * random.uniform(-magnitud_mutacion_actual_porcentaje, magnitud_mutacion_actual_porcentaje) if item !=0 else random.uniform(-0.2,0.2)
                    nuevo_valor = item + variacion
                    nuevo_valor = round(nuevo_valor) if isinstance(item, int) else nuevo_valor
                return nuevo_valor
            return item
        elif isinstance(item, bool):
            if random.random() < prob_mutacion_actual:
                return not item
            return item
        return item

    return _recursive_mutation(cromosoma)

def guardar_cromosoma(cromosoma, filepath):
    """Guarda un cromosoma en un archivo JSON."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f: # Añadido encoding
            json.dump(cromosoma, f, indent=4)
        log_message(f"Cromosoma guardado en: {filepath}")
    except Exception as e:
        log_message(f"Error al guardar cromosoma: {e}")

def cargar_cromosoma(filepath):
    """Carga un cromosoma desde un archivo JSON."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: # Añadido encoding
                return json.load(f)
        except Exception as e:
            log_message(f"Error al cargar cromosoma desde {filepath}: {e}")
            return None
    return None

# --- Bucle Principal del AG ---
def main():
    log_message("\n============================================")
    log_message("=== INICIO DEL ENTRENAMIENTO GENÉTICO ===")
    log_message("============================================\n")
    
    global prob_mutacion_actual, magnitud_mutacion_actual_porcentaje
    prob_mutacion_actual = PROB_MUTACION_INICIAL
    magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_INICIAL_PORCENTAJE
    log_message(f"[Param Inicial] Mutación: Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f}")

    poblacion = inicializar_poblacion()
    mejor_cromosoma_global = None
    mejor_fitness_global = -float('inf') 
    progreso_fitness_generaciones_global = []
    generacion_global_count = 0

    if os.path.exists(LOG_FILE):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.rename(LOG_FILE, f"{LOG_FILE}.bak_{timestamp}")
            log_message(f"[INFO] Log anterior renombrado a: {LOG_FILE}.bak_{timestamp}")
        except OSError as e_log:
            log_message(f"[Advertencia] No se pudo renombrar el log antiguo: {e_log}")

    if os.path.exists(BEST_CHROMOSOME_FILE):
        log_message(f"[INFO] Intentando cargar mejor cromosoma previo desde {BEST_CHROMOSOME_FILE}...")
        loaded_chromosome = cargar_cromosoma(BEST_CHROMOSOME_FILE)
        if loaded_chromosome:
            log_message("[INFO] Mejor cromosoma previo CARGADO. Se integrará en la población inicial.")
            poblacion[0] = loaded_chromosome 
            # Considerar evaluar este cromosoma cargado para establecer un `mejor_fitness_global` inicial.
            # Esto podría hacerse con una evaluación general o contra el primer rival.
            # Por simplicidad, se evaluará normalmente dentro del primer ciclo de rival.
            log_message(f"  Cromosoma cargado (Hash simplificado): {hash(str(poblacion[0])) % 10000:04d}")
        else:
            log_message("[INFO] No se pudo cargar un cromosoma previo o el archivo no existe.")
    log_message("---")
    
    for rival_idx, rival_class in enumerate(AGENTES_OPONENTES_TODOS, start=1):
        log_message(f"\n----------------------------------------------------------------------")
        log_message(f"[CICLO DE RIVAL {rival_idx}/{len(AGENTES_OPONENTES_TODOS)}] Entrenando vs: {rival_class.__name__}")
        log_message(f"----------------------------------------------------------------------")

        if rival_idx > 1:
            log_message("  [Gestión Población] Cambiando de rival. Reintroduciendo diversidad.")
            elites_conservados = []
            if mejor_cromosoma_global:
                elites_conservados.append(mejor_cromosoma_global.copy())
                log_message(f"    Mejor cromosoma global (Hash: {hash(str(mejor_cromosoma_global)) % 10000:04d}, Fitness: {mejor_fitness_global:.2f}) conservado como élite.")
            
            # Añadir más élites del bloque anterior si NUM_ELITES_ENTRE_BLOQUES lo permite y tenemos una `poblacion` ordenada
            # Esta parte es una simplificación: actualmente solo el mejor_cromosoma_global se pasa explícitamente.
            # Para pasar más élites del bloque anterior, necesitaríamos tener la `poblacion_evaluada_rival_actual` del final del bloque anterior.
            # Considerar refinar esto si se requiere un elitismo inter-bloque más sofisticado.

            num_aleatorios_a_generar = TAMANO_POBLACION - len(elites_conservados)
            if num_aleatorios_a_generar < 0: num_aleatorios_a_generar = 0
            
            poblacion_nueva_para_bloque = elites_conservados + [inicializar_cromosoma() for _ in range(num_aleatorios_a_generar)]
            poblacion = poblacion_nueva_para_bloque[:TAMANO_POBLACION] # Asegurar tamaño correcto
            log_message(f"    Nueva población para este bloque: {len(elites_conservados)} élite(s) + {num_aleatorios_a_generar} nuevos/aleatorios = {len(poblacion)} individuos.")
            
            prob_mutacion_actual = PROB_MUTACION_INICIAL
            magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_INICIAL_PORCENTAJE
            log_message(f"  [Param Reset] Mutación reseteada para nuevo rival: Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f}")

        mejor_fitness_rival_actual_en_bloque = -float('inf') 
        generaciones_sin_mejora_rival_actual = 0

        for gen_rival_block in range(1, GENS_POR_RIVAL + 1):
            generacion_global_count += 1
            log_message(f"\n  -- Gen Global {generacion_global_count} | Ciclo Rival {rival_idx} (Gen {gen_rival_block}/{GENS_POR_RIVAL} vs {rival_class.__name__}) --")
            
            poblacion_evaluada_rival_actual = []
            log_message(f"    Evaluando {len(poblacion)} individuos contra {rival_class.__name__}...")
            for i, cromo in enumerate(poblacion):
                try:
                    fitness = calcular_fitness(cromo, clase_rival_fijo=rival_class)
                    poblacion_evaluada_rival_actual.append((cromo, fitness))
                except Exception as e:
                    log_message(f"      ERROR al calcular fitness para individuo (Hash: {hash(str(cromo))%10000:04d}): {e}. Fitness muy bajo.")
                    poblacion_evaluada_rival_actual.append((cromo, -float('inf'))) 

            poblacion_evaluada_rival_actual.sort(key=lambda x: x[1], reverse=True)
            
            current_gen_best_fitness_vs_rival = -float('inf')
            if poblacion_evaluada_rival_actual and poblacion_evaluada_rival_actual[0][1] > -float('inf'):
                current_gen_best_fitness_vs_rival = poblacion_evaluada_rival_actual[0][1]
                mejor_cromo_gen_actual_vs_rival = poblacion_evaluada_rival_actual[0][0]
                log_message(f"    Mejor fitness en esta Gen (vs {rival_class.__name__}): {current_gen_best_fitness_vs_rival:.2f} "
                            f"(Cromosoma Hash: {hash(str(mejor_cromo_gen_actual_vs_rival))%10000:04d})")
            else:
                log_message(f"    [Advertencia] Todos los individuos fallaron o no hubo fitness válido en esta generación.")
            
            if current_gen_best_fitness_vs_rival > mejor_fitness_global:
                mejor_fitness_global = current_gen_best_fitness_vs_rival
                mejor_cromosoma_global = poblacion_evaluada_rival_actual[0][0].copy() 
                log_message(f"    ¡¡NUEVO MEJOR FITNESS GLOBAL ENCONTRADO!!: {mejor_fitness_global:.2f}")
                log_message(f"      Mejor cromosoma global (Hash: {hash(str(mejor_cromosoma_global))%10000:04d}) GUARDADO en {BEST_CHROMOSOME_FILE}")
                guardar_cromosoma(mejor_cromosoma_global, BEST_CHROMOSOME_FILE)
            
            if current_gen_best_fitness_vs_rival > mejor_fitness_rival_actual_en_bloque:
                mejor_fitness_rival_actual_en_bloque = current_gen_best_fitness_vs_rival
                generaciones_sin_mejora_rival_actual = 0
                log_message(f"    [Progreso] Mejora contra {rival_class.__name__}. Nuevo mejor fitness en bloque: {mejor_fitness_rival_actual_en_bloque:.2f}. Estancamiento reseteado.")
                prob_mutacion_actual = max(PROB_MUTACION_MIN, prob_mutacion_actual - FACTOR_AJUSTE_MUTACION_PROB / 2)
                magnitud_mutacion_actual_porcentaje = max(MAGNITUD_MUTACION_MIN_PORCENTAJE, magnitud_mutacion_actual_porcentaje - FACTOR_AJUSTE_MUTACION_MAGNITUD / 2)
            else:
                generaciones_sin_mejora_rival_actual += 1
                log_message(f"    [Info] No hubo mejora contra {rival_class.__name__} en esta gen. Gens sin mejora (bloque): {generaciones_sin_mejora_rival_actual}.")
                if generaciones_sin_mejora_rival_actual >= GENERACIONES_SIN_MEJORA_UMBRAL:
                    log_message(f"      [Adaptación] Estancamiento ({generaciones_sin_mejora_rival_actual} gens). Aumentando mutación.")
                    prob_mutacion_actual = min(PROB_MUTACION_MAX, prob_mutacion_actual + FACTOR_AJUSTE_MUTACION_PROB)
                    magnitud_mutacion_actual_porcentaje = min(MAGNITUD_MUTACION_MAX_PORCENTAJE, magnitud_mutacion_actual_porcentaje + FACTOR_AJUSTE_MUTACION_MAGNITUD)
            log_message(f"    [Param Adaptativo] Mutación para siguiente gen: Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f}")

            valid_fitness_scores_rival = [f for _,f in poblacion_evaluada_rival_actual if f > -float('inf')]
            promedio_fitness_gen_rival = sum(valid_fitness_scores_rival) / len(valid_fitness_scores_rival) if valid_fitness_scores_rival else 0
            log_message(f"    Fitness promedio en esta Gen (vs {rival_class.__name__}): {promedio_fitness_gen_rival:.2f}")
            progreso_fitness_generaciones_global.append((generacion_global_count, current_gen_best_fitness_vs_rival, promedio_fitness_gen_rival))

            nueva_poblacion_bloque = []
            valid_eval_pop_block = [ind for ind in poblacion_evaluada_rival_actual if ind[1] > -float('inf')]

            if not valid_eval_pop_block:
                log_message("      [Advertencia] No hay individuos válidos para selección. Generando población completamente aleatoria.")
                nueva_poblacion_bloque = [inicializar_cromosoma() for _ in range(TAMANO_POBLACION)]
            else:
                num_elites_intra_bloque = NUM_ELITES
                log_message(f"    [Selección] Conservando {min(num_elites_intra_bloque, len(valid_eval_pop_block))} élites para este bloque...")
                for i in range(min(num_elites_intra_bloque, len(valid_eval_pop_block))):
                    elite_cromo = valid_eval_pop_block[i][0]
                    nueva_poblacion_bloque.append(elite_cromo)
                    # log_message(f"      Élite {i+1} (Hash: {hash(str(elite_cromo))%10000:04d}, Fitness: {valid_eval_pop_block[i][1]:.2f}) conservado.")
            
                num_random_immigrants_block = int(0.1 * TAMANO_POBLACION)
                num_hijos_a_generar = TAMANO_POBLACION - len(nueva_poblacion_bloque) - num_random_immigrants_block
                if num_hijos_a_generar < 0: num_hijos_a_generar = 0

                log_message(f"    [Evolución] Generando {num_hijos_a_generar} hijos por cruce y mutación...")
                for _ in range(num_hijos_a_generar):
                    padre1, padre2 = seleccion_padres(valid_eval_pop_block)
                    hijo = padre1 
                    if random.random() < PROBABILIDAD_CRUCE:
                        hijo = cruzar_cromosomas(padre1, padre2)
                    hijo_mutado = mutar_cromosoma(hijo) 
                    nueva_poblacion_bloque.append(hijo_mutado)
            
                log_message(f"    [Diversidad] Añadiendo {num_random_immigrants_block} inmigrantes aleatorios...")
                for _ in range(num_random_immigrants_block):
                    if len(nueva_poblacion_bloque) < TAMANO_POBLACION:
                        nueva_poblacion_bloque.append(inicializar_cromosoma())
                
            poblacion = nueva_poblacion_bloque[:TAMANO_POBLACION] # Asegurar tamaño correcto
            gc.collect()
        log_message(f"  -- Fin CICLO RIVAL {rival_idx} vs {rival_class.__name__}. Mejor fitness en bloque: {mejor_fitness_rival_actual_en_bloque:.2f} -- ")
    
    log_message("\n===========================================")
    log_message("=== ENTRENAMIENTO GENÉTICO FINALIZADO ===")
    log_message("===========================================")
    log_message(f"Mejor fitness global alcanzado en TODO el entrenamiento: {mejor_fitness_global:.2f}")
    if mejor_cromosoma_global:
        log_message(f"Mejor cromosoma global (Hash: {hash(str(mejor_cromosoma_global))%10000:04d}) fue guardado en {BEST_CHROMOSOME_FILE}")
        # Guardar una última vez por si acaso, aunque ya se guarda cuando se encuentra.
        # guardar_cromosoma(mejor_cromosoma_global, BEST_CHROMOSOME_FILE) 
    else:
        log_message("[Resultado] No se encontró ningún cromosoma consistentemente exitoso (mejor_fitness_global <= 0).")

    try:
        with open(FITNESS_PROGRESS_FILE, 'w', encoding='utf-8') as f_progress:
            f_progress.write("GeneracionGlobal,MejorFitnessGeneracionVsRivalActual,PromedioFitnessGeneracionVsRivalActual\n")
            for gen_g, best_f_r, avg_f_r in progreso_fitness_generaciones_global:
                f_progress.write(f"{gen_g},{best_f_r:.2f},{avg_f_r:.2f}\n")
        log_message(f"[INFO] Progreso del fitness global guardado en: {FITNESS_PROGRESS_FILE}")
    except Exception as e_progress:
        log_message(f"[Error] Al guardar el progreso del fitness global: {e_progress}")

    return mejor_fitness_global

def test_calculo_fitness_y_bloque():
    log_message("\n=======================================")
    log_message("===   INICIO DEL TEST RÁPIDO DE AG  ===")
    log_message("=======================================\n")
    global prob_mutacion_actual, magnitud_mutacion_actual_porcentaje
    prob_mutacion_actual = PROB_MUTACION_INICIAL
    magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_INICIAL_PORCENTAJE

    TAMANO_POBLACION_TEST = 3
    GENS_POR_RIVAL_TEST = 2
    AGENTES_RIVALES_TEST = [AGENTES_OPONENTES_TODOS[0], AGENTES_OPONENTES_TODOS[1]] 
    
    log_message(f"[INFO] Configuración del Test:")
    log_message(f"  - Tamaño Población: {TAMANO_POBLACION_TEST}")
    log_message(f"  - Generaciones por Rival: {GENS_POR_RIVAL_TEST}")
    log_message(f"  - Rivales en Test: {[r.__name__ for r in AGENTES_RIVALES_TEST]}\n")

    poblacion_test = [inicializar_cromosoma() for _ in range(TAMANO_POBLACION_TEST)]
    mejor_cromosoma_test_global = None
    mejor_fitness_test_global = -float('inf')

    log_message("[INIT] Población inicial generada.")
    for idx, cromo in enumerate(poblacion_test):
        log_message(f"  Cromosoma Test ID-{idx} (inicial) - Hash simplificado: {hash(str(cromo)) % 10000:04d}")
        # log_message(f"    Muestra (primeras claves): { {k: str(v)[:60]+"..." if len(str(v)) > 60 else v for k,v in list(cromo.items())[:2]} }")
    log_message("---")

    for rival_idx_test, rival_class_test in enumerate(AGENTES_RIVALES_TEST, start=1):
        log_message(f"\n----------------------------------------------------------------------")
        log_message(f"[BLOQUE {rival_idx_test}/{len(AGENTES_RIVALES_TEST)}] Entrenamiento TEST vs: {rival_class_test.__name__}")
        log_message(f"----------------------------------------------------------------------")
        prob_mutacion_actual = PROB_MUTACION_INICIAL 
        magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_INICIAL_PORCENTAJE
        log_message(f"  [Param] Mutación para bloque: Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f}")
        mejor_fitness_bloque_test = -float('inf')

        for gen_test in range(1, GENS_POR_RIVAL_TEST + 1):
            log_message(f"\n  -- Generación TEST {gen_test}/{GENS_POR_RIVAL_TEST} (vs {rival_class_test.__name__}) --")
            
            poblacion_evaluada_test = []
            log_message(f"    Evaluando {len(poblacion_test)} individuos...")
            for i, cromo_test in enumerate(poblacion_test):
                log_message(f"      Individuo ID-{i} (Hash: {hash(str(cromo_test)) % 10000:04d}) vs {rival_class_test.__name__}...")
                try:
                    fitness_test = calcular_fitness(cromo_test, clase_rival_fijo=rival_class_test)
                    poblacion_evaluada_test.append((cromo_test, fitness_test))
                    log_message(f"        Resultado: Fitness = {fitness_test}")
                    if fitness_test > mejor_fitness_test_global:
                        mejor_fitness_test_global = fitness_test
                        mejor_cromosoma_test_global = cromo_test.copy()
                        log_message(f"        ¡NUEVO MEJOR FITNESS GLOBAL (TEST): {mejor_fitness_test_global}! (Cromosoma ID-{i} "
                                    f"Hash: {hash(str(mejor_cromosoma_test_global)) % 10000:04d}) - SIMULANDO GUARDADO.")
                    if fitness_test > mejor_fitness_bloque_test:
                        mejor_fitness_bloque_test = fitness_test

                except Exception as e_test_fit:
                    log_message(f"        ERROR al calcular fitness: {e_test_fit}")
                    poblacion_evaluada_test.append((cromo_test, -float('inf')))
            
            poblacion_evaluada_test.sort(key=lambda x: x[1], reverse=True)
            if poblacion_evaluada_test and poblacion_evaluada_test[0][1] > -float('inf'):
                 log_message(f"    Mejor fitness en Gen Test {gen_test} (vs {rival_class_test.__name__}): {poblacion_evaluada_test[0][1]}")
            else:
                log_message(f"    Todos los individuos fallaron o no hubo mejora en Gen Test {gen_test}.")

            nueva_poblacion_test = []
            if not [ind for ind in poblacion_evaluada_test if ind[1] > -float('inf')]:
                log_message("      [Advertencia] Todos los individuos de test fallaron. Rellenando con nuevos aleatorios.")
                nueva_poblacion_test = [inicializar_cromosoma() for _ in range(TAMANO_POBLACION_TEST)]
            else:
                valid_evaluated_population_test = [ind for ind in poblacion_evaluada_test if ind[1] > -float('inf')]
                
                # Elitismo simple: Conservar el mejor del bloque actual
                if valid_evaluated_population_test:
                    elite_cromo = valid_evaluated_population_test[0][0]
                    nueva_poblacion_test.append(elite_cromo)
                    log_message(f"      [Selección] Élite (ID-{poblacion_test.index(elite_cromo) if elite_cromo in poblacion_test else 'N/A'}, "
                                f"Hash: {hash(str(elite_cromo)) % 10000:04d}, Fitness: {valid_evaluated_population_test[0][1]}) conservado.")

                log_message(f"      Generando {TAMANO_POBLACION_TEST - len(nueva_poblacion_test)} nuevos individuos por Cruce y Mutación...")
                while len(nueva_poblacion_test) < TAMANO_POBLACION_TEST:
                    padre1_cromo, padre2_cromo = seleccion_padres(valid_evaluated_population_test)
                    
                    hijo_original_cromo = padre1_cromo.copy() # Para comparación
                    hijo_post_cruce_cromo = padre1_cromo.copy()

                    # CRUCE
                    if random.random() < PROBABILIDAD_CRUCE:
                        hijo_post_cruce_cromo = cruzar_cromosomas(padre1_cromo, padre2_cromo)
                    
                    # MUTACIÓN
                    hijo_mutado_cromo = mutar_cromosoma(hijo_post_cruce_cromo.copy()) # Mutar una copia
                    
                    nueva_poblacion_test.append(hijo_mutado_cromo)
                    
                    # Log de cambios (para el primer hijo generado en cada generación)
                    if len(nueva_poblacion_test) == (1 if valid_evaluated_population_test and nueva_poblacion_test[0] == elite_cromo else 0) + 1:
                        log_message(f"        Ejemplo de Evolución de Cromosoma (nuevo individuo {len(nueva_poblacion_test)-1}):")
                        log_message(f"          Padre 1 Hash: {hash(str(padre1_cromo)) % 10000:04d}")
                        log_message(f"          Padre 2 Hash: {hash(str(padre2_cromo)) % 10000:04d}")
                        
                        cambio_cruce = "Sí" if hijo_post_cruce_cromo != padre1_cromo else "No (o P1 elegido)"
                        log_message(f"          Post-Cruce Hash: {hash(str(hijo_post_cruce_cromo)) % 10000:04d} (¿Cambió respecto a Padre1?: {cambio_cruce})")
                        
                        cambio_mutacion = "Sí" if hijo_mutado_cromo != hijo_post_cruce_cromo else "No"
                        log_message(f"          Post-Mutación Hash: {hash(str(hijo_mutado_cromo)) % 10000:04d} (¿Cambió respecto a Post-Cruce?: {cambio_mutacion})")
            
            poblacion_test = nueva_poblacion_test
            log_message(f"    Fin Gen Test {gen_test}. {len(poblacion_test)} individuos en la nueva población.")
            if poblacion_test:
                log_message(f"      Muestra nuevo Cromosoma Test ID-0 (Hash simplificado): {hash(str(poblacion_test[0])) % 10000:04d}")
            gc.collect()
        log_message(f"  -- Fin Bloque TEST vs {rival_class_test.__name__}. Mejor fitness en bloque: {mejor_fitness_bloque_test} -- ") 

    log_message("\n=======================================")
    log_message("===    FIN DEL TEST RÁPIDO DE AG    ===")
    log_message(f"Mejor fitness global alcanzado en TEST: {mejor_fitness_test_global}")
    if mejor_cromosoma_test_global:
        log_message(f"Mejor cromosoma (TEST) Hash simplificado: {hash(str(mejor_cromosoma_test_global)) % 10000:04d}")
        log_message("(Nota: En un entrenamiento real, este cromosoma se guardaría en best_chromosome.json)")
    log_message("=======================================\n")

if __name__ == "__main__":
    if 'GameDirector' not in globals() or not callable(GameDirector):
        log_message("Error: GameDirector no está definido o no es importable correctamente.")
        log_message("Por favor, verifica el import en la parte superior del script.")
        exit(1)
    else:
        log_message("[INFO] GameDirector parece estar importado.")
    
    log_message("[INFO] RECORDATORIO: Asegúrate de que GeneticAgent.__init__ puede usar 'GeneticAgent.chromosome_para_entrenamiento_actual'")

    # --- Para ejecutar el entrenamiento completo, DESCOMENTA main() y COMENTA test_calculo_fitness_y_bloque() ---
    log_message("[INFO] Ejecutando ENTRENAMIENTO COMPLETO (main). Para test, modifica if __name__ == '__main__'.")
    main()
    # --- Para ejecutar el test rápido, COMENTA main() y DESCOMENTA la siguiente línea ---
    # log_message("[INFO] Ejecutando TEST RÁPIDO en lugar de main(). Comenta/cambia esta línea para ejecutar el entrenamiento completo.")
    # test_calculo_fitness_y_bloque() 