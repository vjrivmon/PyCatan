import random
import json # Para guardar/cargar cromosomas
import os
import sys
from datetime import datetime

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
# NOTA: Considerar experimentar con NUM_GENERACIONES más altas (ej. 200, 500) 
# y diferentes valores para PROBABILIDAD_MUTACION_GEN y PROBABILIDAD_CRUCE 
# según las recomendaciones para una exploración más exhaustiva.
PROBABILIDAD_CRUCE = 0.9
PROBABILIDAD_MUTACION_GEN = 0.15
MAGNITUD_MUTACION_MAX_PORCENTAJE = 0.2
NUM_PARTIDAS_EVALUACION = 10 
# Asegúrate que estas clases de agentes existen y son importables
AGENTES_OPONENTES_CLASES = [
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

def calcular_fitness(cromosoma, oponentes_fijos=True):
    """
    Evalúa un cromosoma jugando partidas y devuelve su fitness.
    El fitness se define como el número total de partidas ganadas.
    El GeneticAgent rotará su posición de inicio.
    Los 3 oponentes se seleccionarán aleatoriamente de AGENTES_OPONENTES_CLASES.
    """
    victorias_agente_genetico = 0
    # Eliminadas variables de puntos_totales_agente_genetico y puestos_sum ya que no se usarán para el fitness.
    partidas_jugadas_validas = 0

    GeneticAgent.chromosome_para_entrenamiento_actual = cromosoma

    # Pool de oponentes para seleccionar (excluyendo GeneticAgent si estuviera por error)
    possible_opponent_pool = [
        op_class for op_class in AGENTES_OPONENTES_CLASES 
        if op_class != GeneticAgent
    ]

    if not possible_opponent_pool or len(possible_opponent_pool) < 3:
        log_message("Advertencia: El pool de oponentes es insuficiente (necesita al menos 3 distintos de GeneticAgent). Rellenando con RandomAgent o usando los disponibles.")
        # Asegurar que tenemos al menos 3 opciones, incluso si son repetidas de RandomAgent
        # Esta es una medida de contingencia; idealmente AGENTES_OPONENTES_CLASES es diverso.
        while len(possible_opponent_pool) < 3:
            possible_opponent_pool.append(RandomAgent)


    for i in range(NUM_PARTIDAS_EVALUACION):
        genetic_agent_sim_id = i % 4 

        # Seleccionar 3 oponentes aleatorios del pool
        # Nos aseguramos de que, si el pool es pequeño, tomamos muestras con reemplazo o lo que esté disponible.
        if len(possible_opponent_pool) >= 3:
            oponentes_para_partida_clases = random.sample(possible_opponent_pool, 3)
        else: # Si no hay suficientes oponentes únicos, tomar lo que hay y completar con RandomAgent (o el último disponible)
            oponentes_para_partida_clases = list(possible_opponent_pool) # Tomar todos los disponibles
            while len(oponentes_para_partida_clases) < 3:
                oponentes_para_partida_clases.append(RandomAgent) # O el último de possible_opponent_pool si es más seguro
            oponentes_para_partida_clases = oponentes_para_partida_clases[:3] # Asegurar que solo son 3

        agent_classes_for_director = [None] * 4
        agent_classes_for_director[genetic_agent_sim_id] = GeneticAgent
        
        idx_opponent_list = 0
        for pos in range(4):
            if agent_classes_for_director[pos] is None:
                if idx_opponent_list < len(oponentes_para_partida_clases):
                    agent_classes_for_director[pos] = oponentes_para_partida_clases[idx_opponent_list]
                    idx_opponent_list += 1
                else:
                    log_message("Error crítico en asignación de oponentes. Usando RandomAgent.")
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
                continue

            last_round_key = max(game_trace["game"].keys(), key=lambda r_key: int(r_key.split("_")[-1]))
            
            if not game_trace["game"][last_round_key]:
                log_message(f"    Partida {i+1}, última ronda ({last_round_key}) vacía. Saltando.")
                continue

            last_turn_key = max(game_trace["game"][last_round_key].keys(), key=lambda t_key: int(t_key.split("_")[-1].lstrip("P")))
            
            turn_data = game_trace["game"][last_round_key][last_turn_key]
            if "end_turn" not in turn_data or "victory_points" not in turn_data["end_turn"]:
                log_message(f"    Partida {i+1} no tiene datos de 'victory_points' en el último turno. Saltando.")
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

    if hasattr(GeneticAgent, 'chromosome_para_entrenamiento_actual'):
        del GeneticAgent.chromosome_para_entrenamiento_actual
    
    if partidas_jugadas_validas == 0:
        log_message("  No se completaron partidas válidas para este individuo. Fitness = 0.")
        return 0 # Fitness es el número de victorias, si no hay partidas válidas, es 0.

    # El fitness es simplemente el número de victorias.
    fitness = victorias_agente_genetico
    
    log_message(f"  Individuo evaluado ({partidas_jugadas_validas} partidas válidas): {victorias_agente_genetico} victorias -> Fitness: {fitness}")
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
            if random.random() < PROBABILIDAD_MUTACION_GEN:
                original_value = item
                if isinstance(item, float) and 0 <= item <= 1: 
                    variacion = random.uniform(-MAGNITUD_MUTACION_MAX_PORCENTAJE * item, MAGNITUD_MUTACION_MAX_PORCENTAJE * item) if item != 0 else random.uniform(-0.1,0.1)
                    nuevo_valor = max(0.0, min(1.0, item + variacion))
                elif item >= 0: 
                    variacion = item * random.uniform(-MAGNITUD_MUTACION_MAX_PORCENTAJE, MAGNITUD_MUTACION_MAX_PORCENTAJE) if item !=0 else random.uniform(0, 0.2) 
                    nuevo_valor = max(0.0, item + variacion)
                    nuevo_valor = round(nuevo_valor) if isinstance(item, int) else nuevo_valor
                else: 
                    variacion = abs(item) * random.uniform(-MAGNITUD_MUTACION_MAX_PORCENTAJE, MAGNITUD_MUTACION_MAX_PORCENTAJE) if item !=0 else random.uniform(-0.2,0.2)
                    nuevo_valor = item + variacion
                    nuevo_valor = round(nuevo_valor) if isinstance(item, int) else nuevo_valor
                return nuevo_valor
            return item
        elif isinstance(item, bool):
            if random.random() < PROBABILIDAD_MUTACION_GEN:
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
    log_message("Inicio del entrenamiento genético.")
    
    poblacion = inicializar_poblacion()
    mejor_cromosoma_global = None
    mejor_fitness_global = -float('inf') 
    progreso_fitness_generaciones = [] # Lista para guardar (generacion, fitness_mejor_de_gen, fitness_promedio_de_gen)

    if os.path.exists(LOG_FILE): # Limpiar log antiguo o renombrar
        try:
            os.rename(LOG_FILE, LOG_FILE + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        except OSError as e_log:
            log_message(f"Advertencia: No se pudo renombrar el log antiguo: {e_log}")


    if os.path.exists(BEST_CHROMOSOME_FILE):
        log_message(f"Intentando cargar el mejor cromosoma previo desde {BEST_CHROMOSOME_FILE}")
        loaded_chromosome = cargar_cromosoma(BEST_CHROMOSOME_FILE)
        if loaded_chromosome:
            log_message("Mejor cromosoma previo cargado. Se usará como base para el primer individuo y se re-evaluará.")
            # Calcular su fitness actual para tener una línea base para mejor_fitness_global
            try:
                initial_best_fitness = calcular_fitness(loaded_chromosome)
                if initial_best_fitness > mejor_fitness_global:
                    mejor_fitness_global = initial_best_fitness
                    mejor_cromosoma_global = loaded_chromosome.copy()
                    log_message(f"Fitness del cromosoma cargado: {initial_best_fitness}. Establecido como mejor global inicial.")
            except Exception as e_init_fit:
                 log_message(f"Error calculando fitness para cromosoma cargado: {e_init_fit}. Se ignora.")

            poblacion[0] = loaded_chromosome # Reemplazar el primer individuo aleatorio

    for generacion in range(NUM_GENERACIONES):
        log_message(f"--- Generación {generacion + 1}/{NUM_GENERACIONES} ---")
        
        poblacion_evaluada = []
        for i, cromo in enumerate(poblacion):
            log_message(f" Evaluando individuo {i+1}/{TAMANO_POBLACION} (Gen {generacion+1})...")
            try:
                fitness = calcular_fitness(cromo)
                poblacion_evaluada.append((cromo, fitness))
            except Exception as e:
                log_message(f"Error al calcular fitness para individuo {i+1}: {e}. Se asigna fitness muy bajo.")
                poblacion_evaluada.append((cromo, -float('inf'))) 

        poblacion_evaluada.sort(key=lambda x: x[1], reverse=True)
        
        if not poblacion_evaluada or poblacion_evaluada[0][1] == -float('inf') and mejor_fitness_global == -float('inf') : # Modificado para considerar si todos fallan y no hay mejor global previo
            log_message("Todos los individuos fallaron en la evaluación esta generación y no hay un mejor global previo. Saltando cruce/mutación.")
            # Podríamos reintentar con una nueva población aleatoria o detener.
            # Por ahora, si todos fallan, la población no cambiará mucho más que por elitismo (que también falló).
            # Re-inicializar una parte de la población podría ser una estrategia.
            poblacion = [inicializar_cromosoma() for _ in range(TAMANO_POBLACION)] # Reiniciar si todo falla
            continue


        current_gen_best_fitness = poblacion_evaluada[0][1] if poblacion_evaluada else -float('inf') # Manejar caso de lista vacía
        if current_gen_best_fitness > mejor_fitness_global:
            mejor_fitness_global = current_gen_best_fitness
            mejor_cromosoma_global = poblacion_evaluada[0][0].copy() 
            log_message(f"¡Nuevo mejor fitness global encontrado!: {mejor_fitness_global}")
            guardar_cromosoma(mejor_cromosoma_global, BEST_CHROMOSOME_FILE)
            
        log_message(f"Mejor fitness de la Gen {generacion + 1}: {current_gen_best_fitness}")
        
        valid_fitness_scores = [f for _,f in poblacion_evaluada if f != -float('inf')] # No cambia, ya que el fitness ahora es numérico (0 o más)
        if valid_fitness_scores:
            promedio_fitness_gen = sum(valid_fitness_scores) / len(valid_fitness_scores)
            log_message(f"Fitness promedio de la Gen {generacion + 1} (válidos): {promedio_fitness_gen:.2f}")
            progreso_fitness_generaciones.append((generacion + 1, current_gen_best_fitness, promedio_fitness_gen))
        else:
            log_message(f"Fitness promedio de la Gen {generacion + 1}: N/A (todos fallaron o no hubo partidas válidas)")
            progreso_fitness_generaciones.append((generacion + 1, current_gen_best_fitness, 0.0)) # O None para promedio


        nueva_poblacion = []
        
        for i in range(NUM_ELITES):
            if i < len(poblacion_evaluada) and poblacion_evaluada[i][1] > -float('inf') : # Se mantiene la guarda por si acaso, aunque el fitness es >= 0
                nueva_poblacion.append(poblacion_evaluada[i][0])
        
        num_random_immigrants = int(0.1 * TAMANO_POBLACION) # Introducir 10% de inmigrantes aleatorios

        while len(nueva_poblacion) < TAMANO_POBLACION - num_random_immigrants:
            if not poblacion_evaluada or not [ind for ind in poblacion_evaluada if ind[1] > -float('inf')]: # Si no hay individuos válidos para seleccionar
                log_message("Población evaluada sin individuos válidos para selección, rellenando aleatoriamente.")
                nueva_poblacion.append(inicializar_cromosoma())
                continue
            
            # Seleccionar padres de la porción válida de la población evaluada
            valid_evaluated_population = [ind for ind in poblacion_evaluada if ind[1] > -float('inf')]
            if not valid_evaluated_population: # Doble check, aunque el anterior debería cubrirlo
                 log_message("Fallback: No hay población válida para selección. Rellenando aleatoriamente.")
                 nueva_poblacion.append(inicializar_cromosoma())
                 continue

            padre1, padre2 = seleccion_padres(valid_evaluated_population)
            
            hijo = padre1 
            if random.random() < PROBABILIDAD_CRUCE:
                hijo = cruzar_cromosomas(padre1, padre2)
                
            hijo_mutado = mutar_cromosoma(hijo)
            nueva_poblacion.append(hijo_mutado)
        
        # Añadir inmigrantes aleatorios para mantener diversidad
        for _ in range(num_random_immigrants):
            if len(nueva_poblacion) < TAMANO_POBLACION:
                nueva_poblacion.append(inicializar_cromosoma())
            
        poblacion = nueva_poblacion

    log_message("--- Entrenamiento Finalizado ---")
    log_message(f"Mejor fitness global alcanzado: {mejor_fitness_global}")
    log_message(f"Mejor cromosoma guardado en {BEST_CHROMOSOME_FILE}")

    # Guardar el progreso del fitness
    try:
        with open(FITNESS_PROGRESS_FILE, 'w', encoding='utf-8') as f_progress:
            f_progress.write("Generacion,MejorFitnessGeneracion,PromedioFitnessGeneracion\n")
            for gen_num, best_f, avg_f in progreso_fitness_generaciones:
                f_progress.write(f"{gen_num},{best_f},{avg_f}\n")
        log_message(f"Progreso del fitness guardado en: {FITNESS_PROGRESS_FILE}")
    except Exception as e_progress:
        log_message(f"Error al guardar el progreso del fitness: {e_progress}")

    return mejor_fitness_global

if __name__ == "__main__":
    if 'GameDirector' not in globals() or not callable(GameDirector):
        log_message("Error: GameDirector no está definido o no es importable correctamente.")
        log_message("Por favor, verifica el import en la parte superior del script.")
        exit(1)
    else:
        log_message("GameDirector parece estar importado. Procediendo con el entrenamiento.")
    
    # Pequeña modificación en GeneticAgent.__init__ es necesaria:
    log_message("RECORDATORIO: Asegúrate de que GeneticAgent.__init__ puede usar 'GeneticAgent.chromosome_para_entrenamiento_actual'")

    main() 