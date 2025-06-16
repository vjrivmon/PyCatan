import random
import json # Para guardar/cargar cromosomas
import os
import sys
from datetime import datetime
import gc # <--- AÑADIDO
import csv
import shutil # Para operaciones de archivos
import concurrent.futures # <--- AÑADIDO PARA PARALELIZAR FITNESS

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
TAMANO_POBLACION = 40
# NUM_GENERACIONES se reemplazará por un esquema de bloques de rivales y ciclos
# PROBABILIDAD_CRUCE y PROBABILIDAD_MUTACION_GEN se volverán dinámicos o servirán de base.
PROBABILIDAD_CRUCE = 0.9
# PROBABILIDAD_MUTACION_GEN ya no será una constante fija global para la mutación
# MAGNITUD_MUTACION_MAX_PORCENTAJE también se volverá dinámico

# Nuevos parámetros para el entrenamiento por bloques de rivales y adaptación dinámica
GENS_POR_RIVAL_BASE = 10 # Número de generaciones base a entrenar contra cada rival
NUM_PARTIDAS_EVALUACION_POR_POSICION = 3 # Partidas por cada una de las 4 posiciones.
NUM_PARTIDAS_EVALUACION = 12 # Total de partidas para evaluar un cromosoma (NUM_PARTIDAS_EVALUACION_POR_POSICION * 4)

# Lista completa de clases de agentes oponentes
AGENTES_OPONENTES_TODOS = [
    # ** PRIORIDAD MÁXIMA BASADA EN ÚLTIMA EVALUACIÓN **
    PabloAleixAlexAgent, # 7.50% win rate en evaluación exhaustiva
    CarlesZaidaAgent,    # 20.00% win rate en evaluación exhaustiva
    CrabisaAgent,        # 22.50% win rate en evaluación exhaustiva
    
    # Resto de agentes némesis originales que aún pueden necesitar atención 
    # o para mantener diversidad en los bloques difíciles.
    # Ordenados de peor a mejor según la evaluación anterior, si aplica, o por intuición.
    SigmaAgent,          # 32.50% (pero con vulnerabilidades por posición)
    AlexPelochoJaimeAgent, # 35.00% (pero con vulnerabilidades por posición)

    # Resto de agentes (generalmente más fáciles según la última eval, pero bueno tenerlos)
    # EdoAgent,            # 42.50%
    # TristanAgent,
    # RandomAgent,
    # AdrianHerasAgent,
    # AlexPastorAgent
]

# === NUEVOS HIPERPARÁMETROS PARA ENTRENAMIENTO AVANZADO ===
NUM_CICLOS_ENTRENAMIENTO = 1  # Aumentamos un ciclo para dar más oportunidad de mejora
AGENTES_NEMESIS = [
    "PabloAleixAlexAgent", 
    "CarlesZaidaAgent", 
    "CrabisaAgent",
    "SigmaAgent", # Sigue siendo bueno mantenerlo como némesis por si acaso
    "AlexPelochoJaimeAgent" # Igual que Sigma
] 
GENS_EXTRA_PARA_NEMESIS = 35 # Aumentamos las generaciones extra para los más difíciles

# Elitismo Inter-Bloque Mejorado
NUM_ELITES_DEL_BLOQUE_ANTERIOR_A_CONSERVAR = 3 # Además del mejor global, cuántos mejores del bloque anterior conservar

# Parámetros para Mutación Adaptativa Reforzada
FACTOR_AJUSTE_MUTACION_PROB_CRITICO = 0.15 # Incremento mayor para probabilidad en estancamiento crítico
FACTOR_AJUSTE_MUTACION_MAGNITUD_CRITICO = 0.15 # Incremento mayor para magnitud en estancamiento crítico
WIN_RATE_CRITICO_UMBRAL = 0.30 # Por debajo de este win_rate (fitness / NUM_PARTIDAS_EVALUACION) se considera crítico

# Parámetros para "Umbral de Pánico" en Mutación
GENERACIONES_BAJO_RENDIMIENTO_PANICO_UMBRAL = 3 # Gens consecutivas con fitness promedio bajo para activar pánico
FITNESS_PROMEDIO_PANICO_UMBRAL = 1.0 # Si el fitness promedio de la población es menor que esto (ej: <1.0 victoria de 4)
DURACION_PANICO_MUTACION_GENS = 3 # Cuántas generaciones dura la mutación de pánico
PROB_MUTACION_PANICO = 0.90 # Probabilidad de mutación durante el pánico
MAGNITUD_MUTACION_PANICO_PORCENTAJE = 0.90 # Magnitud de mutación durante el pánico
# ==========================================================

# === NUEVOS HIPERPARÁMETROS PARA DOMINIO DE NÉMESIS Y LOGGING AVANZADO ===
UMBRAL_DOMINIO_NEMESIS = 0.50  # Win rate mínimo para considerar a un némesis "dominado"
MAX_GENS_POR_NEMESIS_SIN_DOMINIO = 200  # Máx. generaciones si no se alcanza el umbral de dominio
GENERACIONES_PARA_REEVALUAR_DOMINIO = 5 # Cada cuántas generaciones se reevalúa el dominio del mejor cromosoma actual contra el némesis
NUM_PARTIDAS_REEVALUACION_DOMINIO_POR_POSICION = 5 # Partidas por posición para la reevaluación de dominio (Total: 5*4=20)
CHROMOSOMES_NEMESIS_DIR = "best_chromosomes_vs_nemesis" # Directorio para cromosomas que dominan némesis
# =======================================================================

NUM_ELITES = 5 # Elitismo dentro de un bloque de rival (intra-bloque)

# FRACCION_RESET_POBLACION_ENTRE_BLOQUES ya no se usa directamente, se calcula basado en élites.

# Parámetros para la mutación adaptativa (originales, pueden ajustarse sus incrementos)
PROB_MUTACION_INICIAL = 0.15
MAGNITUD_MUTACION_INICIAL_PORCENTAJE = 0.20
PROB_MUTACION_MIN = 0.05
PROB_MUTACION_MAX = 0.60 # Techo normal, pánico puede superarlo temporalmente
MAGNITUD_MUTACION_MIN_PORCENTAJE = 0.05
MAGNITUD_MUTACION_MAX_PORCENTAJE = 0.60 # Igual, pánico puede superarlo
GENERACIONES_SIN_MEJORA_UMBRAL = 3 # Umbral para considerar estancamiento normal
FACTOR_AJUSTE_MUTACION_PROB = 0.05 # Ajuste normal para probabilidad
FACTOR_AJUSTE_MUTACION_MAGNITUD = 0.05 # Ajuste normal para magnitud

# Asegúrate que estas clases de agentes existen y son importables
AGENTES_OPONENTES_CLASES = [ # Esta lista se usará si no hay un rival fijo (comportamiento anterior)
    RandomAgent,
    AdrianHerasAgent,
    EdoAgent,
    SigmaAgent,
    AlexPastorAgent,
    AlexPelochoJaimeAgent
]
# NUM_ELITES = 5 # Definido arriba
LOG_FILE = "genetic_training_log.txt"
BEST_CHROMOSOME_FILE = "best_chromosome.json"
FITNESS_PROGRESS_FILE = "fitness_por_generacion.csv" # Nuevo archivo para el progreso del fitness
# Nuevo: Máximo de rondas por partida para evitar bloqueos
MAX_ROUNDS_PER_GAME = 200
# --- NUEVO: Para paralelizar calcular_fitness ---
MAX_WORKERS_FITNESS_CALC = os.cpu_count()

# Variables globales para la mutación adaptativa (se inicializarán en main)
prob_mutacion_actual = PROB_MUTACION_INICIAL
magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_INICIAL_PORCENTAJE

# Directorio para guardar los cromosomas
CHROMOSOMES_DIR = "best_chromosomes"
BEST_CHROMOSOME_FILE = os.path.join(CHROMOSOMES_DIR, "best_chromosome.json")
FITNESS_PROGRESS_FILE = "fitness_por_generacion.csv" # Nuevo archivo para el progreso del fitness

def log_message(message):
    """Registra un mensaje en la consola y en un archivo de log con timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding='utf-8') as f: # Añadido encoding
            f.write(full_message + "\n")
    except Exception as e:
        # Fallback si el logging a archivo falla, para no detener el script
        print(f"[{timestamp}] [ERROR LOGGING] No se pudo escribir en {LOG_FILE}: {e}")

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
    log_message(f"[INIT] Inicializando población de {TAMANO_POBLACION} individuos.")
    return [inicializar_cromosoma() for _ in range(TAMANO_POBLACION)]

# --- Función auxiliar para simular una partida individual en calcular_fitness (para paralelización) ---
def _simular_partida_para_fitness(args_tupla):
    """
    Simula una única partida para la evaluación del fitness.
    Espera una tupla (cromosoma, clase_rival_fijo, genetic_agent_sim_id)
    Retorna 1 si el GeneticAgent gana, 0 si no.
    """
    cromosoma, clase_rival_fijo, genetic_agent_sim_id = args_tupla
    
    # Configurar GeneticAgent para que use el cromosoma
    # Esto es seguro en ProcessPoolExecutor ya que cada proceso tiene su propia memoria para GeneticAgent.chromosome_para_entrenamiento_actual
    if cromosoma: # Asegurar que el cromosoma no es None
        GeneticAgent.chromosome_para_entrenamiento_actual = cromosoma
    else: # No debería ocurrir si la lógica es correcta, pero es una salvaguarda
        # log_message("Error interno: Cromosoma nulo pasado a _simular_partida_para_fitness") # Podría ser muy verboso
        return 0


    agent_classes_for_director = [None] * 4
    agent_classes_for_director[genetic_agent_sim_id] = GeneticAgent
    
    oponentes_para_partida_clases = []
    if clase_rival_fijo:
        oponentes_para_partida_clases = [clase_rival_fijo, clase_rival_fijo, clase_rival_fijo]
    else:
        possible_opponent_pool = [
            op_class for op_class in AGENTES_OPONENTES_CLASES 
            if op_class != GeneticAgent
        ]
        if not possible_opponent_pool or len(possible_opponent_pool) < 3:
            # log_message("Advertencia: Pool de oponentes (general) insuficiente en _simular_partida. Rellenando con RandomAgent.")
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
                # log_message("Error crítico en asignación de oponentes (fallback) en _simular_partida. Usando RandomAgent.")
                agent_classes_for_director[pos] = RandomAgent
    
    victoria_ga = 0
    game_director = None # Inicializar para finally
    game_trace = None    # Inicializar para finally

    try:
        game_director = GameDirector(agents=agent_classes_for_director, 
                                     max_rounds=MAX_ROUNDS_PER_GAME, 
                                     store_trace=True) # store_trace puede ser False si no se necesita para fitness puro
        game_trace = game_director.game_start(print_outcome=False)
        
        if not game_trace or "game" not in game_trace or not game_trace["game"]:
            # log_message(f"Partida (GA pos {genetic_agent_sim_id} vs {clase_rival_fijo.__name__ if clase_rival_fijo else 'Mix'}) no produjo trace.")
            return 0

        last_round_key = max(game_trace["game"].keys(), key=lambda r_key: int(r_key.split("_")[-1]))
        if not game_trace["game"][last_round_key]:
            # log_message(f"Última ronda vacía (GA pos {genetic_agent_sim_id} vs {clase_rival_fijo.__name__ if clase_rival_fijo else 'Mix'}).")
            return 0

        last_turn_key = max(game_trace["game"][last_round_key].keys(), key=lambda t_key: int(t_key.split("_")[-1].lstrip("P")))
        turn_data = game_trace["game"][last_round_key][last_turn_key]

        if "end_turn" not in turn_data or "victory_points" not in turn_data["end_turn"]:
            # log_message(f"Datos de VP faltantes (GA pos {genetic_agent_sim_id} vs {clase_rival_fijo.__name__ if clase_rival_fijo else 'Mix'}).")
            return 0
        
        puntos_jugadores_dict = turn_data["end_turn"]["victory_points"]
        parsed_scores = {}
        for player_key, score in puntos_jugadores_dict.items():
            try:
                player_idx = int(player_key.lstrip("J"))
                parsed_scores[player_idx] = int(score)
            except ValueError:
                # log_message(f"Advertencia parseo score: '{player_key}', '{score}'")
                parsed_scores[player_idx] = 0 

        if not parsed_scores:
            # log_message(f"No se pudieron determinar scores (GA pos {genetic_agent_sim_id} vs {clase_rival_fijo.__name__ if clase_rival_fijo else 'Mix'}).")
            return 0
        
        max_score_val = -1
        ganadores_id = []
        for p_id, p_score in parsed_scores.items():
            if p_score > max_score_val:
                max_score_val = p_score
                ganadores_id = [p_id]
            elif p_score == max_score_val:
                ganadores_id.append(p_id)
        
        if genetic_agent_sim_id in ganadores_id:
            victoria_ga = 1

    except Exception as e_partida:
        # log_message(f"Error durante _simular_partida_para_fitness: {e_partida}") # Podría ser verboso
        pass # victoria_ga sigue siendo 0
    finally:
        if hasattr(GeneticAgent, 'chromosome_para_entrenamiento_actual'):
            del GeneticAgent.chromosome_para_entrenamiento_actual
        if game_director: del game_director
        if game_trace: del game_trace
        gc.collect() # Limpieza dentro del worker

    return victoria_ga


def calcular_fitness(cromosoma, clase_rival_fijo=None):
    """
    Evalúa un cromosoma jugando partidas y devuelve su fitness (número total de victorias).
    Las partidas se juegan en paralelo usando ProcessPoolExecutor.
    """
    victorias_agente_genetico_total = 0
    
    # Preparar argumentos para las simulaciones en paralelo
    # Cada tupla es (cromosoma, clase_rival_fijo, genetic_agent_sim_id)
    # genetic_agent_sim_id será la posición del agente genético (0, 1, 2, 3)
    args_para_partidas = []
    for i in range(NUM_PARTIDAS_EVALUACION): # NUM_PARTIDAS_EVALUACION es 8, significando 2 partidas por cada una de las 4 posiciones.
        args_para_partidas.append((cromosoma, clase_rival_fijo, i % 4)) # <--- CORREGIDO: Usar i % 4

    # Usar ProcessPoolExecutor para paralelizar las NUM_PARTIDAS_EVALUACION
    # log_message(f"  Calculando fitness para cromosoma (Hash: {hash(str(cromosoma))%10000:04d}) vs {clase_rival_fijo.__name__ if clase_rival_fijo else 'Mix'} usando {MAX_WORKERS_FITNESS_CALC} workers...")
    
    # Envolver la copia del cromosoma aquí puede ser más seguro si hay dudas sobre
    # cómo ProcessPoolExecutor maneja los objetos pasados y si pueden ser modificados
    # por el proceso principal mientras los workers los usan. Para dicts (como el cromosoma),
    # Python suele pasarlos por copia al serializar para otro proceso, pero ser explícito no daña.
    # Sin embargo, si el cromosoma es grande, copiarlo N veces podría tener un coste.
    # Dado que el cromosoma se pasa a _simular_partida_para_fitness y se usa allí,
    # el comportamiento por defecto de pickle al enviar a los workers debería ser suficiente.
    
    resultados_partidas = []
    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS_FITNESS_CALC) as executor:
            # Mapear directamente los argumentos a la función. Los resultados se devolverán en orden.
            # Esto es más simple si no necesitas un manejo complejo de futures.
            # Ojo: si _simular_partida_para_fitness puede tardar mucho y unos acaban antes que otros,
            # as_completed podría ser mejor si necesitas procesar resultados tan pronto lleguen.
            # Para este caso, map es sencillo y efectivo.
            resultados_partidas = list(executor.map(_simular_partida_para_fitness, args_para_partidas, chunksize=1))
        
        victorias_agente_genetico_total = sum(resultados_partidas)
        # log_message(f"    Resultado fitness: {victorias_agente_genetico_total} victorias de {NUM_PARTIDAS_EVALUACION} partidas.")

    except Exception as e_executor:
        log_message(f"  [ERROR FATAL en CALCULATE_FITNESS ProcessPoolExecutor] Individuo (Hash: {hash(str(cromosoma))%10000:04d}) vs {clase_rival_fijo.__name__ if clase_rival_fijo else 'General'}. Error: {e_executor}. Asignando fitness 0.")
        return 0 # Fitness 0 si el pool falla catastróficamente

    # No es necesario borrar GeneticAgent.chromosome_para_entrenamiento_actual aquí,
    # ya que la función _simular_partida_para_fitness lo maneja internamente para cada proceso worker.
    
    # El fitness es el número de victorias.
    return victorias_agente_genetico_total

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
    """
    Guarda un cromosoma en un archivo JSON.
    Si el directorio no existe, lo crea.
    También guarda una copia con timestamp para tener un historial.
    """
    # Asegurarse de que el directorio existe
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            log_message(f"Directorio creado: {directory}")
        except Exception as e:
            log_message(f"Error al crear directorio {directory}: {e}")
            return False
    
    # Guardar el cromosoma
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cromosoma, f, indent=4)
        
        # También guardar una copia con timestamp para tener historial
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        historial_filepath = f"{filepath}.{timestamp}.json"
        with open(historial_filepath, 'w', encoding='utf-8') as f:
            json.dump(cromosoma, f, indent=4)
        
        log_message(f"Cromosoma guardado en: {filepath}")
        log_message(f"Copia histórica guardada en: {historial_filepath}")
        return True
    except Exception as e:
        log_message(f"Error al guardar cromosoma: {e}")
        return False

def cargar_cromosoma(filepath):
    """Carga un cromosoma desde un archivo JSON."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_message(f"Error al cargar cromosoma desde {filepath}: {e}")
            
            # Intenta buscar una copia de respaldo
            directory = os.path.dirname(filepath)
            base_filename = os.path.basename(filepath)
            if directory and os.path.exists(directory):
                backup_files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f != base_filename]
                if backup_files:
                    # Ordenar por fecha y tomar el más reciente
                    backup_files.sort(reverse=True)
                    latest_backup = os.path.join(directory, backup_files[0])
                    log_message(f"Intentando cargar desde backup más reciente: {latest_backup}")
                    try:
                        with open(latest_backup, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except Exception as e_backup:
                        log_message(f"Error al cargar desde backup {latest_backup}: {e_backup}")
            
            return None
    return None

# --- Bucle Principal del AG ---
def main():
    log_message("\n============================================")
    log_message("=== INICIO DEL ENTRENAMIENTO GENÉTICO AVANZADO ===")
    log_message("============================================\n")
    
    global prob_mutacion_actual, magnitud_mutacion_actual_porcentaje # Necesario si se modifican globalmente

    # Inicialización de variables de seguimiento
    mejor_cromosoma_global = None
    mejor_fitness_global = -float('inf')
    progreso_fitness_generaciones_global = [] # Lista de tuplas (gen_global, mejor_fitness_gen_vs_rival, promedio_fitness_gen_vs_rival)
    generacion_global_count = 0

    # Rendimiento por rival para ordenamiento dinámico (almacena el fitness promedio del último ciclo)
    rendimiento_rivales_ciclo_anterior = {rival_class.__name__: -float('inf') for rival_class in AGENTES_OPONENTES_TODOS}

    # Backup del log anterior
    if os.path.exists(LOG_FILE):
        try:
            timestamp_log_backup = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_log_name = f"{LOG_FILE}.{timestamp_log_backup}.bak"
            os.rename(LOG_FILE, backup_log_name)
            log_message(f"[INFO] Log anterior renombrado a: {backup_log_name}")
        except OSError as e_log:
            log_message(f"[Advertencia] No se pudo renombrar el log antiguo '{LOG_FILE}': {e_log}")

    # Asegurarse de que el directorio para cromosomas existe
    if not os.path.exists(CHROMOSOMES_DIR):
        try:
            os.makedirs(CHROMOSOMES_DIR)
            log_message(f"[INFO] Directorio para cromosomas creado: {CHROMOSOMES_DIR}")
        except Exception as e_dir:
            log_message(f"[Advertencia] No se pudo crear el directorio '{CHROMOSOMES_DIR}': {e_dir}")
            log_message("[INFO] Intentando continuar con la ruta actual...")

    # Asegurarse de que el directorio para cromosomas de némesis existe
    if not os.path.exists(CHROMOSOMES_NEMESIS_DIR):
        try:
            os.makedirs(CHROMOSOMES_NEMESIS_DIR)
            log_message(f"[INFO] Directorio para cromosomas de némesis creado: {CHROMOSOMES_NEMESIS_DIR}")
        except Exception as e_dir_nemesis:
            log_message(f"[Advertencia] No se pudo crear el directorio '{CHROMOSOMES_NEMESIS_DIR}': {e_dir_nemesis}")
            # Considerar si esto debe ser un error fatal o no. Por ahora, se registra y continúa.

    # Cargar mejor cromosoma previo si existe
    poblacion = inicializar_poblacion() # Inicializa la población una vez al principio
    if os.path.exists(BEST_CHROMOSOME_FILE):
        log_message(f"[INFO] Intentando cargar mejor cromosoma previo desde {BEST_CHROMOSOME_FILE}...")
        loaded_chromosome = cargar_cromosoma(BEST_CHROMOSOME_FILE)
        if loaded_chromosome:
            log_message(f"[INFO] Mejor cromosoma previo CARGADO (Hash: {hash(str(loaded_chromosome))%10000:04d}). Se integrará en la población inicial.")
            poblacion[0] = loaded_chromosome
            # Opcional: Evaluar este cromosoma para establecer un 'mejor_fitness_global' inicial realista.
            # fitness_inicial_cargado = calcular_fitness(loaded_chromosome, AGENTES_OPONENTES_TODOS[0]) # Evaluar vs primer rival
            # if fitness_inicial_cargado > mejor_fitness_global:
            #    mejor_fitness_global = fitness_inicial_cargado
            #    mejor_cromosoma_global = loaded_chromosome.copy()
            #    log_message(f"[INFO] Fitness inicial del cromosoma cargado (vs {AGENTES_OPONENTES_TODOS[0].__name__}): {fitness_inicial_cargado:.2f}")
        else:
            log_message(f"[Advertencia] No se pudo cargar un cromosoma previo desde {BEST_CHROMOSOME_FILE} o el archivo estaba corrupto.")
    log_message("---")

    # --- Bucle de Ciclos de Entrenamiento ---
    for ciclo_num in range(1, NUM_CICLOS_ENTRENAMIENTO + 1):
        log_message(f"\n ciclo_num [{ciclo_num}/{NUM_CICLOS_ENTRENAMIENTO}] ====================================")
        
        lista_rivales_para_ciclo = list(AGENTES_OPONENTES_TODOS)
        if ciclo_num > 1:
            log_message(f"[Ciclo {ciclo_num}] Reordenando rivales según rendimiento del ciclo anterior...")
            # Ordenar por el fitness promedio del ciclo anterior (ascendente, los peores primero)
            lista_rivales_para_ciclo.sort(key=lambda r_class: rendimiento_rivales_ciclo_anterior.get(r_class.__name__, -float('inf')))
            log_message(f"  Nuevo orden de rivales para Ciclo {ciclo_num}: {[r.__name__ for r in lista_rivales_para_ciclo]}")
        
        rendimiento_actual_del_ciclo_por_rival = {rival_class.__name__: {'sum_fitness': 0.0, 'num_gens': 0} for rival_class in AGENTES_OPONENTES_TODOS}
        poblacion_evaluada_del_bloque_anterior = [] # Para élites inter-bloque

        # --- Bucle de Rivales Dentro de un Ciclo ---
        for rival_idx, rival_class in enumerate(lista_rivales_para_ciclo, start=1):
            log_message(f"\n----------------------------------------------------------------------")
            log_message(f"[Ciclo {ciclo_num} | Rival Block {rival_idx}/{len(lista_rivales_para_ciclo)}] Entrenando vs: {rival_class.__name__}")
            log_message(f"----------------------------------------------------------------------")

            # Determinar generaciones para este rival (más para némesis)
            generaciones_para_este_rival = GENS_POR_RIVAL_BASE
            if rival_class.__name__ in AGENTES_NEMESIS:
                generaciones_para_este_rival += GENS_EXTRA_PARA_NEMESIS
                log_message(f"  [Némesis Detectado] {rival_class.__name__} es un némesis. Entrenando por {generaciones_para_este_rival} generaciones (base {GENS_POR_RIVAL_BASE} + extra {GENS_EXTRA_PARA_NEMESIS}).")
            else:
                log_message(f"  Entrenando por {generaciones_para_este_rival} generaciones contra {rival_class.__name__}.")

            # Gestión de Población para el nuevo bloque de rival
            log_message("  [Gestión Población] Preparando población para este bloque de rival...")
            elites_conservados_para_nuevo_bloque = []
            if mejor_cromosoma_global:
                elites_conservados_para_nuevo_bloque.append(mejor_cromosoma_global.copy())
                log_message(f"    1. Mejor cromosoma GLOBAL (Hash: {hash(str(mejor_cromosoma_global))%10000:04d}, Fitness Global: {mejor_fitness_global:.2f}) conservado.")

            if poblacion_evaluada_del_bloque_anterior: # Si no es el primer rival del ciclo
                # Tomar los N mejores del bloque anterior (excluyendo si ya es el mejor_cromosoma_global)
                num_elites_a_tomar_del_bloque = 0
                for cromo_prev, fit_prev in poblacion_evaluada_del_bloque_anterior:
                    if num_elites_a_tomar_del_bloque >= NUM_ELITES_DEL_BLOQUE_ANTERIOR_A_CONSERVAR:
                        break
                    # Evitar duplicar el mejor global si ya está
                    if mejor_cromosoma_global and hash(str(cromo_prev)) == hash(str(mejor_cromosoma_global)):
                        continue
                    elites_conservados_para_nuevo_bloque.append(cromo_prev.copy())
                    log_message(f"    {len(elites_conservados_para_nuevo_bloque)}. Élite del bloque anterior (vs {lista_rivales_para_ciclo[rival_idx-2].__name__ if rival_idx > 1 else 'N/A'})"
                                f" (Hash: {hash(str(cromo_prev))%10000:04d}, Fitness: {fit_prev:.2f}) conservado.")
                    num_elites_a_tomar_del_bloque +=1
            
            num_nuevos_aleatorios = TAMANO_POBLACION - len(elites_conservados_para_nuevo_bloque)
            if num_nuevos_aleatorios < 0: num_nuevos_aleatorios = 0 # Por si los élites superan el tamaño de población
            
            poblacion_actual_bloque = elites_conservados_para_nuevo_bloque + [inicializar_cromosoma() for _ in range(num_nuevos_aleatorios)]
            poblacion = poblacion_actual_bloque[:TAMANO_POBLACION] # Asegurar tamaño
            log_message(f"    Nueva población para este bloque: {len(elites_conservados_para_nuevo_bloque)} élite(s) + {num_nuevos_aleatorios} nuevos/aleatorios = {len(poblacion)} individuos.")
            
            # Resetear parámetros de mutación para el nuevo bloque de rival
            prob_mutacion_actual = PROB_MUTACION_INICIAL
            magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_INICIAL_PORCENTAJE
            log_message(f"  [Param Reset Bloque] Mutación reseteada para {rival_class.__name__}: Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f}")

            # Variables de seguimiento para el bloque de rival actual
            mejor_fitness_rival_actual_en_este_bloque = -float('inf')
            generaciones_sin_mejora_vs_rival_actual = 0
            generaciones_con_bajo_rendimiento_promedio_consecutivas = 0
            en_modo_panico_mutacion_contador_gens = 0 # Contador de cuántas generaciones de pánico quedan

            # --- Bucle de Generaciones Dentro de un Bloque de Rival ---
            # MODIFICADO: Bucle especial para némesis con criterio de dominio
            if rival_class.__name__ in AGENTES_NEMESIS:
                log_message(f"  [MODO DOMINIO NÉMESIS ACTIVADO] Intentando dominar a {rival_class.__name__} (Umbral: {UMBRAL_DOMINIO_NEMESIS*100:.0f}% WR).")
                gen_rival_block_nemesis_count = 0
                dominio_alcanzado = False
                mejor_cromosoma_actual_para_nemesis = None # El mejor de la población actual

                while not dominio_alcanzado and gen_rival_block_nemesis_count < MAX_GENS_POR_NEMESIS_SIN_DOMINIO:
                    gen_rival_block_nemesis_count += 1
                    generacion_global_count += 1
                    log_message(f"\\n  -- Gen Global {generacion_global_count} | Ciclo {ciclo_num} | Némesis {rival_class.__name__} (Gen Dominio {gen_rival_block_nemesis_count}/{MAX_GENS_POR_NEMESIS_SIN_DOMINIO}) --")

                    # ... (Lógica de mutación de pánico, evaluación de población, actualización de mejor global, mutación adaptativa - COPIADA Y ADAPTADA DE ABAJO)
                    # Lógica de Mutación de Pánico (al inicio de la generación)
                    if en_modo_panico_mutacion_contador_gens > 0:
                        prob_mutacion_actual = PROB_MUTACION_PANICO
                        magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_PANICO_PORCENTAJE
                        log_message(f"    [PANIC MODE ACTIVE] Mutación establecida a: Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f} ({en_modo_panico_mutacion_contador_gens} gens restantes de pánico).")
                        en_modo_panico_mutacion_contador_gens -= 1
                        if en_modo_panico_mutacion_contador_gens == 0:
                             log_message("    [PANIC MODE ENDING] Próxima generación volverá a mutación adaptativa normal.")
                    
                    # Evaluación de la población
                    poblacion_evaluada_generacion_actual = []
                    log_message(f"    Evaluando {len(poblacion)} individuos contra {rival_class.__name__}...")
                    for i, cromo in enumerate(poblacion):
                        try:
                            fitness = calcular_fitness(cromo, clase_rival_fijo=rival_class)
                            poblacion_evaluada_generacion_actual.append((cromo, fitness))
                        except Exception as e_fit:
                            log_message(f"      [ERROR FATAL] Calculando fitness para individuo (Hash: {hash(str(cromo))%10000:04d}): {e_fit}. Asignando fitness muy bajo.")
                            poblacion_evaluada_generacion_actual.append((cromo, -float('inf')))
                    
                    poblacion_evaluada_generacion_actual.sort(key=lambda x: x[1], reverse=True)
                    
                    current_gen_best_fitness_vs_rival = -float('inf')
                    mejor_cromo_gen_actual_vs_rival = None
                    if poblacion_evaluada_generacion_actual and poblacion_evaluada_generacion_actual[0][1] > -float('inf'):
                        current_gen_best_fitness_vs_rival = poblacion_evaluada_generacion_actual[0][1]
                        mejor_cromo_gen_actual_vs_rival = poblacion_evaluada_generacion_actual[0][0]
                        mejor_cromosoma_actual_para_nemesis = mejor_cromo_gen_actual_vs_rival # Guardar el mejor de esta gen
                        log_message(f"    Mejor fitness en esta Gen (vs {rival_class.__name__}): {current_gen_best_fitness_vs_rival:.2f} "
                                    f"(Cromosoma Hash: {hash(str(mejor_cromo_gen_actual_vs_rival))%10000:04d})")
                    else:
                        log_message(f"    [Advertencia Gen] Todos los individuos fallaron o no hubo fitness válido en esta generación contra {rival_class.__name__}.")

                    # Actualizar mejor global
                    if mejor_cromo_gen_actual_vs_rival and current_gen_best_fitness_vs_rival > mejor_fitness_global:
                        mejor_fitness_global = current_gen_best_fitness_vs_rival
                        mejor_cromosoma_global = mejor_cromo_gen_actual_vs_rival.copy()
                        log_message(f"    ¡¡¡ NUEVO MEJOR FITNESS GLOBAL ENCONTRADO !!!: {mejor_fitness_global:.2f}")
                        if not guardar_cromosoma(mejor_cromosoma_global, BEST_CHROMOSOME_FILE):
                            log_message(f"      [ERROR] No se pudo guardar el mejor cromosoma global.")
                            # ... (código de guardado alternativo omitido por brevedad)

                    # Lógica de Mutación Adaptativa (solo si no estamos en modo pánico)
                    if en_modo_panico_mutacion_contador_gens == 0 and not (prob_mutacion_actual == PROB_MUTACION_PANICO):
                        if current_gen_best_fitness_vs_rival > mejor_fitness_rival_actual_en_este_bloque:
                            # ... (lógica de adaptación estándar) ...
                            log_message(f"    [Progreso Bloque Némesis] Mejora contra {rival_class.__name__}. Nuevo mejor fitness en bloque: {current_gen_best_fitness_vs_rival:.2f} (anterior: {mejor_fitness_rival_actual_en_este_bloque:.2f}). Estancamiento reseteado.")
                            mejor_fitness_rival_actual_en_este_bloque = current_gen_best_fitness_vs_rival
                            generaciones_sin_mejora_vs_rival_actual = 0
                            prob_mutacion_actual = max(PROB_MUTACION_MIN, prob_mutacion_actual - FACTOR_AJUSTE_MUTACION_PROB / 2)
                            magnitud_mutacion_actual_porcentaje = max(MAGNITUD_MUTACION_MIN_PORCENTAJE, magnitud_mutacion_actual_porcentaje - FACTOR_AJUSTE_MUTACION_MAGNITUD / 2)
                        else:
                            generaciones_sin_mejora_vs_rival_actual += 1
                            log_message(f"    [Info Bloque Némesis] No hubo mejora contra {rival_class.__name__} ({current_gen_best_fitness_vs_rival:.2f} vs {mejor_fitness_rival_actual_en_este_bloque:.2f}). Gens sin mejora: {generaciones_sin_mejora_vs_rival_actual}.")
                            if generaciones_sin_mejora_vs_rival_actual >= GENERACIONES_SIN_MEJORA_UMBRAL:
                                log_message(f"      [Adaptación Némesis] Estancamiento. Aumentando mutación.")
                                win_rate_actual = current_gen_best_fitness_vs_rival / NUM_PARTIDAS_EVALUACION if NUM_PARTIDAS_EVALUACION > 0 else 0
                                factor_prob_ajuste_actual = FACTOR_AJUSTE_MUTACION_PROB_CRITICO if win_rate_actual < WIN_RATE_CRITICO_UMBRAL else FACTOR_AJUSTE_MUTACION_PROB
                                factor_magnitud_ajuste_actual = FACTOR_AJUSTE_MUTACION_MAGNITUD_CRITICO if win_rate_actual < WIN_RATE_CRITICO_UMBRAL else FACTOR_AJUSTE_MUTACION_MAGNITUD
                                prob_mutacion_actual = min(PROB_MUTACION_MAX, prob_mutacion_actual + factor_prob_ajuste_actual)
                                magnitud_mutacion_actual_porcentaje = min(MAGNITUD_MUTACION_MAX_PORCENTAJE, magnitud_mutacion_actual_porcentaje + factor_magnitud_ajuste_actual)
                        log_message(f"    [Param Adaptativo Némesis] Mutación para siguiente gen: Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f}")
                    
                    # ... (Cálculo de fitness promedio y activación de Pánico) ...
                    valid_fitness_scores_gen = [f for _,f in poblacion_evaluada_generacion_actual if f > -float('inf')]
                    promedio_fitness_gen_rival = sum(valid_fitness_scores_gen) / len(valid_fitness_scores_gen) if valid_fitness_scores_gen else 0.0
                    log_message(f"    Fitness promedio en esta Gen (vs {rival_class.__name__}): {promedio_fitness_gen_rival:.2f}")
                    rendimiento_actual_del_ciclo_por_rival[rival_class.__name__]['sum_fitness'] += promedio_fitness_gen_rival
                    rendimiento_actual_del_ciclo_por_rival[rival_class.__name__]['num_gens'] += 1
                    progreso_fitness_generaciones_global.append((generacion_global_count, current_gen_best_fitness_vs_rival, promedio_fitness_gen_rival, rival_class.__name__, ciclo_num))

                    if en_modo_panico_mutacion_contador_gens == 0 and not (prob_mutacion_actual == PROB_MUTACION_PANICO and magnitud_mutacion_actual_porcentaje == MAGNITUD_MUTACION_PANICO_PORCENTAJE):
                        if promedio_fitness_gen_rival < FITNESS_PROMEDIO_PANICO_UMBRAL and promedio_fitness_gen_rival > -float('inf'):
                            generaciones_con_bajo_rendimiento_promedio_consecutivas += 1
                            log_message(f"    [Alerta Rendimiento Némesis] Fitness promedio ({promedio_fitness_gen_rival:.2f}) < umbral ({FITNESS_PROMEDIO_PANICO_UMBRAL:.2f}) por {generaciones_con_bajo_rendimiento_promedio_consecutivas} gen(s).")
                        else:
                            generaciones_con_bajo_rendimiento_promedio_consecutivas = 0
                        if generaciones_con_bajo_rendimiento_promedio_consecutivas >= GENERACIONES_BAJO_RENDIMIENTO_PANICO_UMBRAL:
                            log_message(f"    ¡¡¡ PÁNICO NÉMESIS ({generaciones_con_bajo_rendimiento_promedio_consecutivas} gens) !!! Activando MODO PÁNICO para {DURACION_PANICO_MUTACION_GENS} gens.")
                            en_modo_panico_mutacion_contador_gens = DURACION_PANICO_MUTACION_GENS
                            generaciones_con_bajo_rendimiento_promedio_consecutivas = 0

                    # Selección y reproducción (igual que antes)
                    # ... (código de selección y reproducción omitido por brevedad pero es el mismo que en el bucle original)
                    nueva_poblacion_para_siguiente_gen = []
                    num_elites_intra_bloque_a_conservar = min(NUM_ELITES, len(poblacion_evaluada_generacion_actual))
                    if num_elites_intra_bloque_a_conservar > 0:
                        # log_message(f"    [Selección Némesis] Conservando {num_elites_intra_bloque_a_conservar} élites...")
                        for i in range(num_elites_intra_bloque_a_conservar):
                            if poblacion_evaluada_generacion_actual[i][1] > -float('inf'):
                                nueva_poblacion_para_siguiente_gen.append(poblacion_evaluada_generacion_actual[i][0])
                    
                    num_hijos_a_generar = TAMANO_POBLACION - len(nueva_poblacion_para_siguiente_gen)
                    if num_hijos_a_generar > 0:
                        # log_message(f"    [Evolución Némesis] Generando {num_hijos_a_generar} hijos...")
                        padres_potenciales_validos = [ind for ind in poblacion_evaluada_generacion_actual if ind[1] > -float('inf')]
                        if not padres_potenciales_validos:
                            for _ in range(num_hijos_a_generar): nueva_poblacion_para_siguiente_gen.append(inicializar_cromosoma())
                        else:
                            for _ in range(num_hijos_a_generar):
                                padre1, padre2 = seleccion_padres(padres_potenciales_validos)
                                hijo = padre1
                                if random.random() < PROBABILIDAD_CRUCE: hijo = cruzar_cromosomas(padre1, padre2)
                                nueva_poblacion_para_siguiente_gen.append(mutar_cromosoma(hijo))
                    
                    num_inmigrantes_final = TAMANO_POBLACION - len(nueva_poblacion_para_siguiente_gen)
                    if num_inmigrantes_final > 0:
                        # log_message(f"    [Diversidad Némesis] Añadiendo {num_inmigrantes_final} inmigrantes.")
                        for _ in range(num_inmigrantes_final): nueva_poblacion_para_siguiente_gen.append(inicializar_cromosoma())
                    poblacion = nueva_poblacion_para_siguiente_gen[:TAMANO_POBLACION]
                    if not poblacion: poblacion = inicializar_poblacion()


                    # Reevaluación de Dominio para Némesis
                    if gen_rival_block_nemesis_count % GENERACIONES_PARA_REEVALUAR_DOMINIO == 0 and mejor_cromosoma_actual_para_nemesis:
                        log_message(f"    [REEVALUACIÓN DOMINIO NÉMESIS] Gen {gen_rival_block_nemesis_count}. Evaluando mejor cromosoma de población actual (Hash: {hash(str(mejor_cromosoma_actual_para_nemesis))%10000:04d}) contra {rival_class.__name__}.")
                        
                        victorias_reevaluacion = 0
                        num_partidas_total_reevaluacion = NUM_PARTIDAS_REEVALUACION_DOMINIO_POR_POSICION * 4
                        
                        # Preparamos argumentos para _simular_partida_para_fitness para la reevaluación
                        args_reevaluacion = []
                        for pos_idx in range(4): # Evaluar en las 4 posiciones
                            for _ in range(NUM_PARTIDAS_REEVALUACION_DOMINIO_POR_POSICION):
                                args_reevaluacion.append((mejor_cromosoma_actual_para_nemesis, rival_class, pos_idx))
                        
                        try:
                            with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS_FITNESS_CALC) as executor:
                                resultados_partidas_reeval = list(executor.map(_simular_partida_para_fitness, args_reevaluacion, chunksize=1))
                            victorias_reevaluacion = sum(resultados_partidas_reeval)
                        except Exception as e_reeval:
                            log_message(f"      [ERROR REEVALUACIÓN] Error durante ProcessPoolExecutor para reevaluación: {e_reeval}")
                            victorias_reevaluacion = 0 # Considerar como 0 victorias si la reevaluación falla

                        win_rate_reevaluacion = victorias_reevaluacion / num_partidas_total_reevaluacion if num_partidas_total_reevaluacion > 0 else 0.0
                        log_message(f"      Resultado Reevaluación vs {rival_class.__name__}: {victorias_reevaluacion}/{num_partidas_total_reevaluacion} victorias (WR: {win_rate_reevaluacion:.2%}).")

                        if win_rate_reevaluacion >= UMBRAL_DOMINIO_NEMESIS:
                            dominio_alcanzado = True
                            log_message(f"      ¡¡¡ DOMINIO ALCANZADO contra {rival_class.__name__} (WR: {win_rate_reevaluacion:.2%}) !!!")
                            nemesis_cromo_filename = f"dominio_{rival_class.__name__}_WR{win_rate_reevaluacion:.2f}_Gen{generacion_global_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            nemesis_cromo_path = os.path.join(CHROMOSOMES_NEMESIS_DIR, nemesis_cromo_filename)
                            if guardar_cromosoma(mejor_cromosoma_actual_para_nemesis, nemesis_cromo_path):
                                log_message(f"        Cromosoma de dominio guardado en: {nemesis_cromo_path}")
                            else:
                                log_message(f"        [ERROR] No se pudo guardar el cromosoma de dominio para {rival_class.__name__}.")
                            # Si este cromosoma también es el mejor global, se guarda como BEST_CHROMOSOME_FILE por la lógica estándar.
                        else:
                            log_message(f"      Dominio aún no alcanzado (WR: {win_rate_reevaluacion:.2%} < {UMBRAL_DOMINIO_NEMESIS:.0%}). Continuando entrenamiento contra {rival_class.__name__}.")
                    
                    gc.collect() # Limpieza de memoria

                if not dominio_alcanzado:
                    log_message(f"  [MODO DOMINIO NÉMESIS FINALIZADO POR LÍMITE] No se alcanzó el umbral de dominio ({UMBRAL_DOMINIO_NEMESIS*100:.0f}%) contra {rival_class.__name__} tras {gen_rival_block_nemesis_count} generaciones (límite {MAX_GENS_POR_NEMESIS_SIN_DOMINIO}).")
                
                # poblacion_evaluada_del_bloque_anterior se actualiza con la última población evaluada en este bloque de némesis
                # (Asumiendo que poblacion_evaluada_generacion_actual es la correcta al final del bucle while)

            else: # --- Bucle de Generaciones NORMAL (para no-némesis) ---
                for gen_rival_block in range(1, generaciones_para_este_rival + 1):
                    generacion_global_count += 1
                    log_message(f"\\n  -- Gen Global {generacion_global_count} | Ciclo {ciclo_num} | Rival {rival_class.__name__} (Gen {gen_rival_block}/{generaciones_para_este_rival}) --")
                    
                    # Lógica de Mutación de Pánico (al inicio de la generación)
                    if en_modo_panico_mutacion_contador_gens > 0:
                        prob_mutacion_actual = PROB_MUTACION_PANICO
                        magnitud_mutacion_actual_porcentaje = MAGNITUD_MUTACION_PANICO_PORCENTAJE
                        log_message(f"    [PANIC MODE ACTIVE] Mutación establecida a: Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f} ({en_modo_panico_mutacion_contador_gens} gens restantes de pánico).")
                        en_modo_panico_mutacion_contador_gens -= 1
                        # Si era la última gen de pánico, la siguiente volverá a adaptación normal (o reset si cambia de rival)
                        if en_modo_panico_mutacion_contador_gens == 0:
                             log_message("    [PANIC MODE ENDING] Próxima generación volverá a mutación adaptativa normal (si no hay cambio de rival).")
                    
                    # Evaluación de la población
                    poblacion_evaluada_generacion_actual = []
                    log_message(f"    Evaluando {len(poblacion)} individuos contra {rival_class.__name__}...")
                    for i, cromo in enumerate(poblacion):
                        # log_message(f"      Evaluando individuo {i+1}/{len(poblacion)} (Hash: {hash(str(cromo))%10000:04d})...")
                        try:
                            fitness = calcular_fitness(cromo, clase_rival_fijo=rival_class)
                            poblacion_evaluada_generacion_actual.append((cromo, fitness))
                            # log_message(f"        Individuo {i+1} Fitness: {fitness:.2f}")
                        except Exception as e_fit:
                            log_message(f"      [ERROR FATAL] Calculando fitness para individuo (Hash: {hash(str(cromo))%10000:04d}): {e_fit}. Asignando fitness muy bajo.")
                            poblacion_evaluada_generacion_actual.append((cromo, -float('inf')))
                    
                    poblacion_evaluada_generacion_actual.sort(key=lambda x: x[1], reverse=True)
                    
                    current_gen_best_fitness_vs_rival = -float('inf')
                    mejor_cromo_gen_actual_vs_rival = None
                    if poblacion_evaluada_generacion_actual and poblacion_evaluada_generacion_actual[0][1] > -float('inf'):
                        current_gen_best_fitness_vs_rival = poblacion_evaluada_generacion_actual[0][1]
                        mejor_cromo_gen_actual_vs_rival = poblacion_evaluada_generacion_actual[0][0]
                        log_message(f"    Mejor fitness en esta Gen (vs {rival_class.__name__}): {current_gen_best_fitness_vs_rival:.2f} "
                                    f"(Cromosoma Hash: {hash(str(mejor_cromo_gen_actual_vs_rival))%10000:04d})")
                    else:
                        log_message(f"    [Advertencia Gen] Todos los individuos fallaron o no hubo fitness válido en esta generación contra {rival_class.__name__}.")

                    # Actualizar mejor global
                    if mejor_cromo_gen_actual_vs_rival and current_gen_best_fitness_vs_rival > mejor_fitness_global:
                        mejor_fitness_global = current_gen_best_fitness_vs_rival
                        mejor_cromosoma_global = mejor_cromo_gen_actual_vs_rival.copy()
                        log_message(f"    ¡¡¡ NUEVO MEJOR FITNESS GLOBAL ENCONTRADO !!!: {mejor_fitness_global:.2f}")
                        log_message(f"      Mejor cromosoma global (Hash: {hash(str(mejor_cromosoma_global))%10000:04d}) GUARDADO en {BEST_CHROMOSOME_FILE} (Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                        # Forzar que se guarde el cromosoma con sync al disco
                        if not guardar_cromosoma(mejor_cromosoma_global, BEST_CHROMOSOME_FILE):
                            log_message(f"      [ERROR] No se pudo guardar el mejor cromosoma global. Intentando guardarlo en la ruta alternativa...")
                            alt_path = f"best_chromosome_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            guardar_cromosoma(mejor_cromosoma_global, alt_path)

                    # Lógica de Mutación Adaptativa (solo si no estamos en modo pánico)
                    if en_modo_panico_mutacion_contador_gens == 0 and not (prob_mutacion_actual == PROB_MUTACION_PANICO): # Asegura que no se ejecute si acabamos de salir de pánico
                        if current_gen_best_fitness_vs_rival > mejor_fitness_rival_actual_en_este_bloque:
                            log_message(f"    [Progreso Bloque] Mejora contra {rival_class.__name__}. Nuevo mejor fitness en bloque: {current_gen_best_fitness_vs_rival:.2f} (anterior: {mejor_fitness_rival_actual_en_este_bloque:.2f}). Estancamiento reseteado.")
                            mejor_fitness_rival_actual_en_este_bloque = current_gen_best_fitness_vs_rival
                            generaciones_sin_mejora_vs_rival_actual = 0
                            # Reducir mutación ligeramente (opcional, o mantener)
                            prob_mutacion_actual = max(PROB_MUTACION_MIN, prob_mutacion_actual - FACTOR_AJUSTE_MUTACION_PROB / 2)
                            magnitud_mutacion_actual_porcentaje = max(MAGNITUD_MUTACION_MIN_PORCENTAJE, magnitud_mutacion_actual_porcentaje - FACTOR_AJUSTE_MUTACION_MAGNITUD / 2)
                        else:
                            generaciones_sin_mejora_vs_rival_actual += 1
                            log_message(f"    [Info Bloque] No hubo mejora contra {rival_class.__name__} en esta gen ({current_gen_best_fitness_vs_rival:.2f} vs mejor bloque {mejor_fitness_rival_actual_en_este_bloque:.2f}). Gens sin mejora (bloque): {generaciones_sin_mejora_vs_rival_actual}.")
                            if generaciones_sin_mejora_vs_rival_actual >= GENERACIONES_SIN_MEJORA_UMBRAL:
                                log_message(f"      [Adaptación] Estancamiento ({generaciones_sin_mejora_vs_rival_actual} gens). Aumentando mutación.")
                                win_rate_actual = current_gen_best_fitness_vs_rival / NUM_PARTIDAS_EVALUACION if NUM_PARTIDAS_EVALUACION > 0 else 0
                                
                                factor_prob_ajuste_actual = FACTOR_AJUSTE_MUTACION_PROB
                                factor_magnitud_ajuste_actual = FACTOR_AJUSTE_MUTACION_MAGNITUD

                                if win_rate_actual < WIN_RATE_CRITICO_UMBRAL and current_gen_best_fitness_vs_rival > -float('inf'): # Solo si el winrate es realmente bajo
                                    log_message(f"        [Estancamiento CRÍTICO] Win rate ({win_rate_actual:.2%}) vs {rival_class.__name__} es < {WIN_RATE_CRITICO_UMBRAL:.0%}. Usando factores de ajuste mayores.")
                                    factor_prob_ajuste_actual = FACTOR_AJUSTE_MUTACION_PROB_CRITICO
                                    factor_magnitud_ajuste_actual = FACTOR_AJUSTE_MUTACION_MAGNITUD_CRITICO
                                
                                prob_mutacion_actual = min(PROB_MUTACION_MAX, prob_mutacion_actual + factor_prob_ajuste_actual)
                                magnitud_mutacion_actual_porcentaje = min(MAGNITUD_MUTACION_MAX_PORCENTAJE, magnitud_mutacion_actual_porcentaje + factor_magnitud_ajuste_actual)
                        log_message(f"    [Param Adaptativo] Mutación para siguiente gen (vs {rival_class.__name__}): Prob={prob_mutacion_actual:.3f}, Magnitud={magnitud_mutacion_actual_porcentaje:.3f}")

                    # Cálculo de fitness promedio y activación de Pánico (si no estamos ya en pánico)
                    valid_fitness_scores_gen = [f for _,f in poblacion_evaluada_generacion_actual if f > -float('inf')]
                    promedio_fitness_gen_rival = sum(valid_fitness_scores_gen) / len(valid_fitness_scores_gen) if valid_fitness_scores_gen else 0.0
                    log_message(f"    Fitness promedio en esta Gen (vs {rival_class.__name__}): {promedio_fitness_gen_rival:.2f}")
                    
                    # Actualizar rendimiento para ordenamiento dinámico
                    rendimiento_actual_del_ciclo_por_rival[rival_class.__name__]['sum_fitness'] += promedio_fitness_gen_rival
                    rendimiento_actual_del_ciclo_por_rival[rival_class.__name__]['num_gens'] += 1

                    progreso_fitness_generaciones_global.append((generacion_global_count, current_gen_best_fitness_vs_rival, promedio_fitness_gen_rival, rival_class.__name__, ciclo_num))

                    # Lógica para activar el modo Pánico (si no estamos ya en él o saliendo de él)
                    if en_modo_panico_mutacion_contador_gens == 0 and not (prob_mutacion_actual == PROB_MUTACION_PANICO and magnitud_mutacion_actual_porcentaje == MAGNITUD_MUTACION_PANICO_PORCENTAJE):
                        if promedio_fitness_gen_rival < FITNESS_PROMEDIO_PANICO_UMBRAL and promedio_fitness_gen_rival > -float('inf'): # Solo si hay un promedio válido pero bajo
                            generaciones_con_bajo_rendimiento_promedio_consecutivas += 1
                            log_message(f"    [Alerta Rendimiento] Fitness promedio ({promedio_fitness_gen_rival:.2f}) < umbral de pánico ({FITNESS_PROMEDIO_PANICO_UMBRAL:.2f}) por {generaciones_con_bajo_rendimiento_promedio_consecutivas} gen(s) consecutivas.")
                        else:
                            if generaciones_con_bajo_rendimiento_promedio_consecutivas > 0:
                                 log_message(f"    [Info Rendimiento] Fitness promedio ({promedio_fitness_gen_rival:.2f}) ha superado el umbral de pánico. Contador de bajo rendimiento reseteado.")
                            generaciones_con_bajo_rendimiento_promedio_consecutivas = 0 # Resetear si el promedio mejora o no es válido

                        if generaciones_con_bajo_rendimiento_promedio_consecutivas >= GENERACIONES_BAJO_RENDIMIENTO_PANICO_UMBRAL:
                            log_message(f"    ¡¡¡ UMBRAL DE PÁNICO ALCANZADO ({generaciones_con_bajo_rendimiento_promedio_consecutivas} gens) !!! Activando MODO PÁNICO de mutación para las próximas {DURACION_PANICO_MUTACION_GENS} generaciones.")
                            en_modo_panico_mutacion_contador_gens = DURACION_PANICO_MUTACION_GENS
                            generaciones_con_bajo_rendimiento_promedio_consecutivas = 0 # Resetear contador de trigger
                            # La mutación se aplicará al inicio de la siguiente generación.
                    
                    # Selección y reproducción para la siguiente generación
                    nueva_poblacion_para_siguiente_gen = []
                    # Elitismo intra-bloque (los N mejores de esta generación contra este rival)
                    num_elites_intra_bloque_a_conservar = min(NUM_ELITES, len(poblacion_evaluada_generacion_actual))
                    if num_elites_intra_bloque_a_conservar > 0:
                        log_message(f"    [Selección Intra-Bloque] Conservando {num_elites_intra_bloque_a_conservar} élites de esta generación (vs {rival_class.__name__})...")
                        for i in range(num_elites_intra_bloque_a_conservar):
                            if poblacion_evaluada_generacion_actual[i][1] > -float('inf'): # Solo conservar élites válidos
                                elite_cromo = poblacion_evaluada_generacion_actual[i][0]
                                nueva_poblacion_para_siguiente_gen.append(elite_cromo)
                                # log_message(f"      Élite Intra-Bloque {i+1} (Hash: {hash(str(elite_cromo))%10000:04d}, Fitness: {poblacion_evaluada_generacion_actual[i][1]:.2f})")
                            else: # Si un "élite" tuvo error, no se añade.
                                log_message(f"      Élite Intra-Bloque {i+1} potencial descartado por fitness inválido.")
                    
                    num_hijos_a_generar = TAMANO_POBLACION - len(nueva_poblacion_para_siguiente_gen)
                    # Podríamos añadir una pequeña fracción de inmigrantes aleatorios aquí también si se desea más diversidad constante.
                    # num_random_immigrants_intra_gen = int(0.05 * TAMANO_POBLACION) 
                    # num_hijos_a_generar -= num_random_immigrants_intra_gen
                    if num_hijos_a_generar < 0: num_hijos_a_generar = 0

                    if num_hijos_a_generar > 0:
                        log_message(f"    [Evolución Intra-Bloque] Generando {num_hijos_a_generar} hijos por cruce y mutación...")
                        # Asegurarse de que hay padres válidos para seleccionar
                        padres_potenciales_validos = [ind for ind in poblacion_evaluada_generacion_actual if ind[1] > -float('inf')]
                        if not padres_potenciales_validos:
                            log_message("      [Advertencia Evolución] No hay padres válidos para selección. Rellenando con individuos aleatorios.")
                            for _ in range(num_hijos_a_generar):
                                 nueva_poblacion_para_siguiente_gen.append(inicializar_cromosoma())
                        else:
                            for _ in range(num_hijos_a_generar):
                                padre1, padre2 = seleccion_padres(padres_potenciales_validos)
                                hijo = padre1 # Por defecto, si no hay cruce
                                if random.random() < PROBABILIDAD_CRUCE:
                                    hijo = cruzar_cromosomas(padre1, padre2)
                                hijo_mutado = mutar_cromosoma(hijo)
                                nueva_poblacion_para_siguiente_gen.append(hijo_mutado)
                    
                    # Rellenar con inmigrantes aleatorios si la población no está llena (debido a élites inválidos o pocos hijos)
                    num_inmigrantes_final = TAMANO_POBLACION - len(nueva_poblacion_para_siguiente_gen)
                    if num_inmigrantes_final > 0:
                        log_message(f"    [Diversidad Intra-Bloque] Añadiendo {num_inmigrantes_final} inmigrantes aleatorios para completar población.")
                        for _ in range(num_inmigrantes_final):
                            nueva_poblacion_para_siguiente_gen.append(inicializar_cromosoma())

                    poblacion = nueva_poblacion_para_siguiente_gen[:TAMANO_POBLACION] # Asegurar tamaño
                    if not poblacion: # Salvaguarda extrema si todo falla
                        log_message("[ERROR CRÍTICO POBLACIÓN] La población quedó vacía. Reinicializando con aleatorios.")
                        poblacion = inicializar_poblacion()

                    gc.collect() # Limpieza de memoria al final de cada generación
                # --- Fin Bucle de Generaciones NORMAL ---
            
            # Asegurar que poblacion_evaluada_del_bloque_anterior tiene los datos de la última evaluación del bloque
            # (sea némesis o no)
            # Esto es crucial para el elitismo inter-bloque
            if 'poblacion_evaluada_generacion_actual' in locals() and poblacion_evaluada_generacion_actual:
                 poblacion_evaluada_del_bloque_anterior = sorted(poblacion_evaluada_generacion_actual, key=lambda x: x[1], reverse=True)
            else: # Si por alguna razón no hubo evaluación (ej. némesis dominado en gen 0, improbable)
                 poblacion_evaluada_del_bloque_anterior = []


            log_message(f"  -- Fin CICLO RIVAL {rival_idx} vs {rival_class.__name__} (Ciclo {ciclo_num}). Mejor fitness en este bloque: {mejor_fitness_rival_actual_en_este_bloque:.2f} -- ")
            # poblacion_evaluada_del_bloque_anterior = sorted(poblacion_evaluada_generacion_actual, key=lambda x: x[1], reverse=True) # Guardar para elitismo inter-bloque # MOVIDO ARRIBA
        # --- Fin Bucle de Rivales ---

        # Actualizar rendimiento_rivales_ciclo_anterior para el próximo ciclo
        log_message(f"[Fin Ciclo {ciclo_num}] Calculando rendimiento promedio por rival para este ciclo...")
        for r_name, data in rendimiento_actual_del_ciclo_por_rival.items():
            if data['num_gens'] > 0:
                avg_fit_for_rival_this_cycle = data['sum_fitness'] / data['num_gens']
                rendimiento_rivales_ciclo_anterior[r_name] = avg_fit_for_rival_this_cycle
                log_message(f"  Rival: {r_name}, Fitness Promedio Ciclo {ciclo_num}: {avg_fit_for_rival_this_cycle:.2f} ({data['num_gens']} gens)")
            else:
                rendimiento_rivales_ciclo_anterior[r_name] = -float('inf') # Si no se entrenó contra él (no debería pasar)
                log_message(f"  Rival: {r_name}, No se entrenó en este ciclo.")
        log_message(f" ciclo_num [{ciclo_num}/{NUM_CICLOS_ENTRENAMIENTO}] FINALIZADO ====================================")
    # --- Fin Bucle de Ciclos ---

    log_message("\n===========================================")
    log_message("=== ENTRENAMIENTO GENÉTICO AVANZADO FINALIZADO ===")
    log_message("===========================================")
    log_message(f"Mejor fitness global alcanzado en TODO el entrenamiento: {mejor_fitness_global:.2f}")
    if mejor_cromosoma_global:
        log_message(f"Mejor cromosoma global (Hash: {hash(str(mejor_cromosoma_global))%10000:04d}) fue guardado en {BEST_CHROMOSOME_FILE}")
        # Guardar una última vez por si acaso.
        guardar_cromosoma(mejor_cromosoma_global, BEST_CHROMOSOME_FILE)
        
        # Crear una copia con el fitness en el nombre para facilitar su identificación
        fitness_copy_path = os.path.join(CHROMOSOMES_DIR, f"best_chromosome_fitness_{mejor_fitness_global:.2f}.json")
        try:
            shutil.copy2(BEST_CHROMOSOME_FILE, fitness_copy_path)
            log_message(f"Copia del mejor cromosoma con fitness en nombre guardada en: {fitness_copy_path}")
        except Exception as e_copy:
            log_message(f"Error al crear copia con fitness en nombre: {e_copy}")
    else:
        log_message("[Resultado Final] No se encontró ningún cromosoma consistentemente exitoso (mejor_fitness_global <= 0 o nulo).")

    try:
        with open(FITNESS_PROGRESS_FILE, 'w', encoding='utf-8', newline='') as f_progress: # Añadido newline='' para CSV
            writer = csv.writer(f_progress)
            writer.writerow(["GeneracionGlobal", "MejorFitnessGeneracionVsRivalActual", "PromedioFitnessGeneracionVsRivalActual", "RivalActual", "Ciclo"])
            for gen_g, best_f_r, avg_f_r, r_name, c_num in progreso_fitness_generaciones_global:
                writer.writerow([gen_g, f"{best_f_r:.2f}", f"{avg_f_r:.2f}", r_name, c_num])
        log_message(f"[INFO] Progreso del fitness global guardado en: {FITNESS_PROGRESS_FILE}")
    except Exception as e_progress:
        log_message(f"[Error] Al guardar el progreso del fitness global en '{FITNESS_PROGRESS_FILE}': {e_progress}")

    log_message("\n[AVISO] La función 'test_calculo_fitness_y_bloque' puede requerir adaptaciones debido a los cambios en 'main' y los nuevos parámetros globales.")
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
    # log_message("[ATENCIÓN TEST] La función de test rápido puede no funcionar correctamente debido a los cambios recientes en 'main' y los parámetros globales. Revisar antes de usar.")
    # test_calculo_fitness_y_bloque() 