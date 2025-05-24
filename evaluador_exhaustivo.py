import random
import json
import os
import sys
from datetime import datetime
import time
import csv
import importlib
import concurrent.futures
import gc

# --- Configuración Esencial ---
CHROMOSOMES_DIR = "best_chromosomes"
BEST_CHROMOSOME_FILE = os.path.join(CHROMOSOMES_DIR, "best_chromosome.json")
LOG_FILE_EVAL = "evaluacion_exhaustiva_log.txt"
RESULTS_CSV_FILE = "resultados_evaluacion_exhaustiva.csv"
N_PARTIDAS_POR_POSICION_Y_RIVAL = 10
UMBRAL_VICTORIA_REQUERIDO = 0.25 # 25%

# --- Gestión de Paths y Módulos (similar a entrenador_genetico.py) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from Agents.GeneticAgent import GeneticAgent
    from Agents.RandomAgent import RandomAgent
    from Agents.AdrianHerasAgent import AdrianHerasAgent
    from Agents.EdoAgent import EdoAgent
    from Agents.SigmaAgent import SigmaAgent
    from Agents.AlexPastorAgent import AlexPastorAgent
    from Agents.AlexPelochoJaimeAgent import AlexPelochoJaimeAgent
    from Agents.CarlesZaidaAgent import CarlesZaidaAgent
    from Agents.CrabisaAgent import CrabisaAgent
    from Agents.PabloAleixAlexAgent import PabloAleixAlexAgent
    from Agents.TristanAgent import TristanAgent
    from Managers.GameDirector import GameDirector
except ImportError as e:
    print(f"Error importando módulos: {e}. Asegúrate de que la estructura del proyecto es correcta y que los agentes existen.")
    print(f"Current sys.path: {sys.path}")
    exit(1)

# Lista de agentes oponentes contra los que se evaluará
# Debería ser la misma que en entrenador_genetico.py para consistencia
AGENTES_OPONENTES_TODOS = [
    CrabisaAgent, PabloAleixAlexAgent, CarlesZaidaAgent, SigmaAgent, AlexPelochoJaimeAgent,
    EdoAgent, TristanAgent, RandomAgent, AdrianHerasAgent, AlexPastorAgent
]

# --- Funciones de Logging ---
def log_message_eval(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        with open(LOG_FILE_EVAL, "a", encoding='utf-8') as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"[{timestamp}] [ERROR LOGGING] No se pudo escribir en {LOG_FILE_EVAL}: {e}")

# --- Función para Cargar Cromosoma ---
def cargar_mejor_cromosoma(filepath=BEST_CHROMOSOME_FILE):
    if not os.path.exists(filepath):
        log_message_eval(f"[ERROR CRÍTICO] No se encontró el archivo de cromosoma: {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cromosoma = json.load(f)
        log_message_eval(f"[INFO] Cromosoma cargado exitosamente desde: {filepath} (Hash: {hash(str(cromosoma))%10000:04d})")
        return cromosoma
    except Exception as e:
        log_message_eval(f"[ERROR CRÍTICO] Error al cargar el cromosoma desde {filepath}: {e}")
        return None

# --- Función Principal de Simulación de Partida ---
def simular_partida_eval(genetic_agent_posicion, clase_agente_oponente, cromosoma_genetico):
    """
    Simula una única partida.
    El GeneticAgent usa el cromosoma_genetico.
    Los otros 3 jugadores son instancias de clase_agente_oponente.
    """
    # Configurar GeneticAgent para que use el cromosoma cargado
    GeneticAgent.chromosome_para_entrenamiento_actual = cromosoma_genetico

    agentes_partida = [None] * 4
    for i in range(4):
        if i == genetic_agent_posicion:
            agentes_partida[i] = GeneticAgent
        else:
            agentes_partida[i] = clase_agente_oponente
    
    try:
        game_director = GameDirector(agents=agentes_partida, max_rounds=200, store_trace=True) # store_trace puede ser False si no se necesita
        game_trace = game_director.game_start(print_outcome=False)

        if not game_trace or "game" not in game_trace or not game_trace["game"]:
            # log_message_eval(f"    Partida inválida o sin trace. Oponente: {clase_agente_oponente.__name__}, Pos GA: {genetic_agent_posicion}")
            return 0, 0, 4 # Derrota, 0 puntos, último puesto

        last_round_key = max(game_trace["game"].keys(), key=lambda r_key: int(r_key.split("_")[-1]))
        if not game_trace["game"][last_round_key]:
            # log_message_eval(f"    Última ronda vacía. Oponente: {clase_agente_oponente.__name__}, Pos GA: {genetic_agent_posicion}")
            return 0, 0, 4

        last_turn_key = max(game_trace["game"][last_round_key].keys(), key=lambda t_key: int(t_key.split("_")[-1].lstrip("P")))
        turn_data = game_trace["game"][last_round_key][last_turn_key]

        if "end_turn" not in turn_data or "victory_points" not in turn_data["end_turn"]:
            # log_message_eval(f"    Datos de VP faltantes. Oponente: {clase_agente_oponente.__name__}, Pos GA: {genetic_agent_posicion}")
            return 0, 0, 4
        
        puntos_jugadores_dict = turn_data["end_turn"]["victory_points"]
        parsed_scores = {int(k.lstrip("J")): int(v) for k, v in puntos_jugadores_dict.items()}

        ga_score = parsed_scores.get(genetic_agent_posicion, 0)
        
        # Determinar ganador
        max_score_val = -1
        ganadores_id = []
        for p_id, p_score in parsed_scores.items():
            if p_score > max_score_val:
                max_score_val = p_score
                ganadores_id = [p_id]
            elif p_score == max_score_val:
                ganadores_id.append(p_id)
        
        victoria = 1 if genetic_agent_posicion in ganadores_id else 0

        # Determinar ranking
        ranked_players = sorted(parsed_scores.items(), key=lambda item: item[1], reverse=True)
        puesto_ga = 4 # Por defecto, si no se encuentra (no debería pasar)
        for rank, (player_id, _) in enumerate(ranked_players, start=1):
            if player_id == genetic_agent_posicion:
                puesto_ga = rank
                break
        
        return victoria, ga_score, puesto_ga

    except Exception as e:
        # log_message_eval(f"    ERROR en simular_partida_eval contra {clase_agente_oponente.__name__} (Pos GA: {genetic_agent_posicion}): {e}")
        return 0, 0, 4 # Considerar como derrota en caso de error
    finally:
        if hasattr(GeneticAgent, 'chromosome_para_entrenamiento_actual'):
            del GeneticAgent.chromosome_para_entrenamiento_actual
        if 'game_director' in locals():
            del game_director
        if 'game_trace' in locals():
            del game_trace
        gc.collect()


# --- Función Principal de Evaluación ---
def evaluar_cromosoma_exhaustivo():
    log_message_eval("===================================================")
    log_message_eval("=== INICIO DE EVALUACIÓN EXHAUSTIVA DE CROMOSOMA ===")
    log_message_eval("===================================================")

    cromosoma_a_evaluar = cargar_mejor_cromosoma()
    if cromosoma_a_evaluar is None:
        log_message_eval("[FINAL] No se pudo cargar el cromosoma. Terminando evaluación.")
        return

    # Backup del log anterior y CSV de resultados
    if os.path.exists(LOG_FILE_EVAL):
        try:
            ts_backup = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.rename(LOG_FILE_EVAL, f"{LOG_FILE_EVAL}.{ts_backup}.bak")
        except OSError as e: log_message_eval(f"[Advertencia] No se pudo renombrar log de evaluación antiguo: {e}")
    if os.path.exists(RESULTS_CSV_FILE):
        try:
            ts_backup = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.rename(RESULTS_CSV_FILE, f"{RESULTS_CSV_FILE}.{ts_backup}.bak")
        except OSError as e: log_message_eval(f"[Advertencia] No se pudo renombrar CSV de resultados antiguo: {e}")

    # Preparar archivo CSV para resultados
    csv_headers = ["AgenteOponente", "PosicionGeneticAgent", "PartidasJugadas", "Victorias", 
                   "PorcentajeVictorias", "PuntosTotales", "PuntosPromedio", "PuestoPromedio", "SuperaUmbral"]
    try:
        with open(RESULTS_CSV_FILE, 'w', newline='', encoding='utf-8') as f_csv:
            writer = csv.writer(f_csv)
            writer.writerow(csv_headers)
    except IOError as e:
        log_message_eval(f"[ERROR CRÍTICO] No se pudo abrir/escribir el archivo CSV de resultados: {RESULTS_CSV_FILE}. Error: {e}")
        log_message_eval("[FINAL] Terminando evaluación debido a error con CSV.")
        return


    vulnerabilidades_detectadas = []
    tiempo_inicio_total_eval = time.time()

    # Nuevas variables para el cálculo global
    victorias_globales_totales = 0
    partidas_globales_totales = 0

    num_workers = os.cpu_count() # Usar todos los cores disponibles para evaluación
    log_message_eval(f"[INFO] Utilizando {num_workers} workers para la simulación de partidas.")

    for rival_class in AGENTES_OPONENTES_TODOS:
        nombre_rival = rival_class.__name__
        log_message_eval(f"\n--- Evaluando contra: {nombre_rival} ---")
        
        victorias_totales_vs_rival = 0
        partidas_jugadas_totales_vs_rival = 0
        tiempo_inicio_rival_eval = time.time()

        for pos_ga in range(4): # Posiciones 0, 1, 2, 3
            log_message_eval(f"  Posición del GeneticAgent: {pos_ga+1}/4 (ID interno: {pos_ga})")
            
            victorias_pos = 0
            puntos_totales_pos = 0
            puestos_totales_pos = 0
            
            args_list = [(pos_ga, rival_class, cromosoma_a_evaluar) for _ in range(N_PARTIDAS_POR_POSICION_Y_RIVAL)]

            # Usar ProcessPoolExecutor para paralelizar las partidas
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
                future_to_args = {executor.submit(simular_partida_eval, *args): args for args in args_list}
                
                for i, future in enumerate(concurrent.futures.as_completed(future_to_args)):
                    # args_orig = future_to_args[future] # Si necesitas saber qué argumentos eran
                    try:
                        v, p, r = future.result()
                        victorias_pos += v
                        puntos_totales_pos += p
                        puestos_totales_pos += r
                        # Descomentar para log por partida, puede ser muy verboso:
                        # log_message_eval(f"    Partida {i+1}/{N_PARTIDAS_POR_POSICION_Y_RIVAL} (Pos GA {pos_ga+1} vs {nombre_rival}): {'Victoria' if v else 'Derrota'}, Puntos: {p}, Puesto: {r}")
                    except Exception as exc:
                        log_message_eval(f"      Partida generó una excepción: {exc}. Se cuenta como derrota.")
                        # Ya se maneja en simular_partida_eval, pero por si acaso.
                        puestos_totales_pos += 4 


            porc_victorias_pos = (victorias_pos / N_PARTIDAS_POR_POSICION_Y_RIVAL)
            puntos_promedio_pos = puntos_totales_pos / N_PARTIDAS_POR_POSICION_Y_RIVAL if N_PARTIDAS_POR_POSICION_Y_RIVAL > 0 else 0
            puesto_promedio_pos = puestos_totales_pos / N_PARTIDAS_POR_POSICION_Y_RIVAL if N_PARTIDAS_POR_POSICION_Y_RIVAL > 0 else 4
            supera_umbral_pos = porc_victorias_pos >= UMBRAL_VICTORIA_REQUERIDO

            log_message_eval(f"    Resumen Posición {pos_ga+1} (vs {nombre_rival}):")
            log_message_eval(f"      Victorias: {victorias_pos}/{N_PARTIDAS_POR_POSICION_Y_RIVAL} ({porc_victorias_pos:.2%})")
            log_message_eval(f"      Puntos Promedio: {puntos_promedio_pos:.2f}")
            log_message_eval(f"      Puesto Promedio: {puesto_promedio_pos:.2f}")
            log_message_eval(f"      Supera Umbral ({UMBRAL_VICTORIA_REQUERIDO:.0%})?: {'SÍ' if supera_umbral_pos else 'NO'}")

            # Guardar en CSV
            try:
                with open(RESULTS_CSV_FILE, 'a', newline='', encoding='utf-8') as f_csv:
                    writer = csv.writer(f_csv)
                    writer.writerow([nombre_rival, pos_ga + 1, N_PARTIDAS_POR_POSICION_Y_RIVAL, victorias_pos,
                                     f"{porc_victorias_pos:.4f}", puntos_totales_pos, f"{puntos_promedio_pos:.2f}", 
                                     f"{puesto_promedio_pos:.2f}", 'SI' if supera_umbral_pos else 'NO'])
            except IOError as e:
                 log_message_eval(f"[ERROR] No se pudo escribir la fila en CSV para {nombre_rival}, Pos {pos_ga+1}. Error: {e}")


            victorias_totales_vs_rival += victorias_pos
            partidas_jugadas_totales_vs_rival += N_PARTIDAS_POR_POSICION_Y_RIVAL
            
            # Acumular para el total global
            victorias_globales_totales += victorias_pos
            partidas_globales_totales += N_PARTIDAS_POR_POSICION_Y_RIVAL

            if not supera_umbral_pos:
                vulnerabilidades_detectadas.append({
                    "rival": nombre_rival,
                    "posicion_GA": pos_ga + 1,
                    "win_rate": porc_victorias_pos,
                    "puesto_promedio": puesto_promedio_pos # Añadido para más info
                })
        
        # Resumen final para el rival
        porc_total_victorias_rival = (victorias_totales_vs_rival / partidas_jugadas_totales_vs_rival) if partidas_jugadas_totales_vs_rival > 0 else 0
        supera_umbral_total_rival = porc_total_victorias_rival >= UMBRAL_VICTORIA_REQUERIDO
        
        tiempo_fin_rival_eval = time.time()
        duracion_rival_seg = tiempo_fin_rival_eval - tiempo_inicio_rival_eval
        min_dur_rival, seg_dur_rival = divmod(duracion_rival_seg, 60)

        log_message_eval(f"  Resumen TOTAL para {nombre_rival}:")
        log_message_eval(f"    Victorias Totales: {victorias_totales_vs_rival}/{partidas_jugadas_totales_vs_rival} ({porc_total_victorias_rival:.2%})")
        log_message_eval(f"    Supera Umbral General ({UMBRAL_VICTORIA_REQUERIDO:.0%})?: {'SÍ' if supera_umbral_total_rival else 'NO'}")
        log_message_eval(f"    Tiempo de evaluación contra {nombre_rival}: {int(min_dur_rival)}m {seg_dur_rival:.2f}s")
        log_message_eval(f"--- Fin Evaluación contra: {nombre_rival} ---")

    # Resumen final de toda la evaluación
    log_message_eval("\n===================================================")
    log_message_eval("=== RESUMEN FINAL DE EVALUACIÓN EXHAUSTIVA ===")
    log_message_eval("===================================================")
    
    # Cálculo y muestra del rendimiento global
    if partidas_globales_totales > 0:
        porcentaje_victorias_global = (victorias_globales_totales / partidas_globales_totales)
        supera_umbral_global_final = porcentaje_victorias_global >= UMBRAL_VICTORIA_REQUERIDO
        log_message_eval(f"\n--- RENDIMIENTO GLOBAL GENERAL ---")
        log_message_eval(f"  Victorias Globales Totales: {victorias_globales_totales}")
        log_message_eval(f"  Partidas Globales Totales Jugadas: {partidas_globales_totales}")
        log_message_eval(f"  Porcentaje de Victorias Global: {porcentaje_victorias_global:.2%}")
        log_message_eval(f"  Supera Umbral Global del Profesor ({UMBRAL_VICTORIA_REQUERIDO:.0%})?: {'SÍ' if supera_umbral_global_final else 'NO'}")
    else:
        log_message_eval("\n[INFO] No se jugaron partidas, no se puede calcular el rendimiento global.")

    if vulnerabilidades_detectadas:
        log_message_eval("\n  VULNERABILIDADES DETECTADAS (Rendimiento < Umbral Requerido):")
        for vul in vulnerabilidades_detectadas:
            log_message_eval(f"    - Rival: {vul['rival']}, Posición GA: {vul['posicion_GA']}, Win Rate: {vul['win_rate']:.2%}, Puesto Promedio: {vul['puesto_promedio']:.2f}")
        log_message_eval("\n  SUGERENCIA: Considera re-entrenar focalizando en estos escenarios,")
        log_message_eval("              ajustando los agentes némesis o las generaciones dedicadas en 'entrenador_genetico.py'.")
    else:
        log_message_eval("\n  ¡FELICIDADES! El cromosoma ha superado el umbral de victoria del 25% en todas las posiciones evaluadas contra todos los rivales.")

    tiempo_fin_total_eval = time.time()
    duracion_total_seg = tiempo_fin_total_eval - tiempo_inicio_total_eval
    hr_dur_total, rem_dur_total = divmod(duracion_total_seg, 3600)
    min_dur_total, seg_dur_total = divmod(rem_dur_total, 60)
    log_message_eval(f"\nResultados completos guardados en: {RESULTS_CSV_FILE}")
    log_message_eval(f"Log completo guardado en: {LOG_FILE_EVAL}")
    log_message_eval(f"Tiempo total de evaluación: {int(hr_dur_total)}h {int(min_dur_total)}m {seg_dur_total:.2f}s")
    log_message_eval("===================================================")
    log_message_eval("=== FIN DE EVALUACIÓN EXHAUSTIVA ===")
    log_message_eval("===================================================")


if __name__ == "__main__":
    # Asegurar que GeneticAgent.chromosome_para_entrenamiento_actual se maneje correctamente
    # En este script, se establece y elimina dentro de simular_partida_eval.
    # También se necesita importar gc para la limpieza de memoria explícita.
    if 'GameDirector' not in globals() or not callable(GameDirector):
        print("Error: GameDirector no está definido o no es importable. Verifica imports.")
        exit(1)
    if 'GeneticAgent' not in globals() or not callable(GeneticAgent):
        print("Error: GeneticAgent no está definido o no es importable. Verifica imports.")
        exit(1)
        
    evaluar_cromosoma_exhaustivo() 