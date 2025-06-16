import os
import time
import importlib
import concurrent.futures
import csv
import json
import glob
import traceback
import sys
import itertools

# --- Dependencias para gráficas (opcional si solo se quiere el JSON) ---
try:
    import matplotlib.pyplot as plt
    import pandas as pd
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
# --- Fin dependencias para gráficas ---

# Asegurarse de que el directorio 'Agents' y 'Managers' están en el path
# Esto es útil si el script se ejecuta desde una ubicación diferente
# o si la estructura del proyecto es más compleja.
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "PyCatan" else script_dir
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if os.path.join(project_root, "PyCatan") not in sys.path and os.path.exists(os.path.join(project_root, "PyCatan")): # Caso común de estructura PyCatan/PyCatan
    sys.path.insert(0, os.path.join(project_root, "PyCatan"))


# Importación dinámica de RandomAgent y GameDirector para evitar problemas de orden
try:
    from Agents.RandomAgent import RandomAgent
    from Managers.GameDirector import GameDirector
except ImportError as e:
    print(f"Error crítico importando módulos base (RandomAgent, GameDirector): {e}")
    print("Asegúrate de que la estructura del proyecto es correcta y PyCatan está en sys.path.")
    print(f"Current sys.path: {sys.path}")
    print(f"Project root considerado: {project_root}")
    exit(1)


# --- Configuración del Benchmark ---
n_matches_por_config = 10  # Número de partidas para CADA configuración específica
porcentaje_workers = 0.95
MAX_ROUNDS_PER_GAME = 200 # Para evitar partidas infinitas

# Lista de agentes principales a evaluar exhaustivamente (rutas de importación)
# Puedes añadir más agentes aquí para una evaluación completa de cada uno.
agentes_principales_a_evaluar_rutas = [
    "Agents.GeneticAgent.GeneticAgent",
    # "Agents.AdrianHerasAgent.AdrianHerasAgent",
    # Añade aquí las rutas de los agentes que quieras evaluar como principales
    # Ejemplo: "Agents.MiAgenteEspecial.MiAgenteEspecial",
]

# --- Funciones Auxiliares ---

def cargar_agente_desde_ruta(ruta_clase_str):
    """Carga una clase de agente desde su ruta de string (e.g., 'Agents.RandomAgent.RandomAgent')."""
    try:
        modulo_str, clase_str = ruta_clase_str.rsplit(".", 1)
        modulo = importlib.import_module(modulo_str)
        return getattr(modulo, clase_str)
    except Exception as e:
        print(f"Error cargando agente desde ruta '{ruta_clase_str}': {e}")
        return None

def listar_rutas_agentes_automatico(directorio_agents="Agents"):
    """
    Escanea el directorio 'Agents' y devuelve una lista de rutas de importación
    para todas las clases de agentes encontradas (archivos *Agent.py con clase homónima).
    Excluye 'RandomAgent' de esta lista si se quiere un trato especial,
    o se pueden filtrar después.
    """
    rutas_agentes = []
    # Asegurar que el path base es correcto. Si el script está en PyCatan/scripts/,
    # directorio_agents debería ser ../Agents
    
    # Intentar encontrar el directorio 'Agents' relativo al script o al proyecto
    path_directorio_agents = os.path.join(project_root, directorio_agents)
    if not os.path.isdir(path_directorio_agents) and project_root.endswith("PyCatan"):
        # Si project_root es PyCatan, y Agents no está en PyCatan/Agents,
        # podría ser que el script esté en una subcarpeta como PyCatan/benchmarks/
        # y Agents esté en PyCatan/Agents/
        path_directorio_agents_alt = os.path.join(os.path.dirname(project_root), directorio_agents)
        if os.path.isdir(path_directorio_agents_alt):
            path_directorio_agents = path_directorio_agents_alt
        else: # Asumimos que está dentro de la carpeta del proyecto PyCatan si no se encuentra
            path_directorio_agents = os.path.join(project_root, "Agents")


    if not os.path.isdir(path_directorio_agents):
        print(f"Directorio de agentes '{path_directorio_agents}' no encontrado. Usando ruta relativa directa '{directorio_agents}'.")
        path_directorio_agents = directorio_agents # Fallback a ruta relativa directa

    if not os.path.isdir(path_directorio_agents):
        print(f"ADVERTENCIA: Directorio de agentes '{path_directorio_agents}' no encontrado. No se cargarán agentes automáticamente.")
        return []

    for filepath in glob.glob(os.path.join(path_directorio_agents, "*Agent.py")):
        filename = os.path.basename(filepath)
        agent_name = filename[:-3]  # Elimina '.py'
        if agent_name == "__init__":
            continue
        # Construye la ruta de importación asumiendo que directorio_agents es el nombre del paquete
        # y está en el nivel superior o accesible vía sys.path
        # Ejemplo: Agents.MiSuperAgent.MiSuperAgent
        # Esto asume que 'Agents' es un paquete directamente importable.
        # Si Agents está dentro de otra carpeta (ej. PyCatan/Agents), ajustar según sea necesario.
        # La lógica de sys.path al inicio debería ayudar con esto.
        # Asumimos que 'Agents' está en el top-level del path de búsqueda o es un subdirectorio del proyecto.
        # Si el script está en PyCatan/scripts/ y Agents en PyCatan/Agents/
        # y PyCatan/ está en sys.path, entonces la importación debe ser "Agents.NombreAgente.NombreAgente"
        # Si la estructura es PyCatan/PyCatan/Agents y PyCatan/PyCatan/ está en sys.path, idem.
        
        # Corrección: Usar el nombre base del directorio_agents como prefijo del paquete.
        package_prefix = os.path.basename(os.path.normpath(directorio_agents))
        ruta_importacion = f"{package_prefix}.{agent_name}.{agent_name}"

        rutas_agentes.append(ruta_importacion)
    
    if not rutas_agentes:
        print(f"No se encontraron archivos *Agent.py en '{path_directorio_agents}'.")
        
    return rutas_agentes


def simular_partida_configurada(agentes_clases_partida, idx_agente_seguimiento):
    """
    Simula una única partida con una configuración de agentes específica.
    Devuelve (victoria, puntos, ranking) para el agente en idx_agente_seguimiento.
    """
    try:
        # GameDirector espera una lista de clases de agentes.
        game_director = GameDirector(agents=list(agentes_clases_partida), 
                                     max_rounds=MAX_ROUNDS_PER_GAME, 
                                     store_trace=False)
        game_trace = game_director.game_start(print_outcome=False)

        if not game_trace or "game" not in game_trace or not game_trace["game"]:
            # print(f"Advertencia: Partida sin trace válido para config: {[ac.__name__ for ac in agentes_clases_partida]}")
            return (0, 0, 4)

        last_round_key = max(game_trace["game"].keys(), key=lambda r_key: int(r_key.split("_")[-1]))
        if not game_trace["game"][last_round_key]:
            # print(f"Advertencia: Última ronda vacía para config: {[ac.__name__ for ac in agentes_clases_partida]}")
            return (0, 0, 4)
            
        last_turn_key = max(game_trace["game"][last_round_key].keys(), key=lambda t_key: int(t_key.split("_")[-1].lstrip("P")))
        
        turn_data = game_trace["game"][last_round_key][last_turn_key]
        if "end_turn" not in turn_data or "victory_points" not in turn_data["end_turn"]:
            # print(f"Advertencia: Datos de fin de turno incompletos para config: {[ac.__name__ for ac in agentes_clases_partida]}")
            return (0, 0, 4)
        
        victory_points_dict = turn_data["end_turn"]["victory_points"]

        agent_id_seguimiento = f"J{idx_agente_seguimiento}"
        
        if agent_id_seguimiento not in victory_points_dict:
             # Esto puede pasar si el agente crashea muy pronto o hay un error en el trace
            # print(f"Advertencia: Agente {agent_id_seguimiento} no encontrado en victory_points: {victory_points_dict}")
            return (0,0,4)

        puntos_agente_seguimiento = int(victory_points_dict[agent_id_seguimiento])
        
        # Determinar ganador
        parsed_scores = {}
        for player_key, score_val in victory_points_dict.items():
            try:
                # player_idx = int(player_key.lstrip("J")) # No necesitamos el índice aquí
                parsed_scores[player_key] = int(score_val)
            except ValueError:
                parsed_scores[player_key] = 0 # Score por defecto si hay error
        
        if not parsed_scores: # Si no hay scores, el agente no ganó.
            return (0, puntos_agente_seguimiento, 4)


        ganador_id_str = max(parsed_scores, key=lambda p_key: parsed_scores[p_key])
        victoria = 1 if ganador_id_str == agent_id_seguimiento else 0

        # Determinar ranking
        # Ordenar por puntos, luego desempatar por ID de jugador (menor ID gana en empate de puntos, arbitrario)
        jugadores_ordenados = sorted(parsed_scores.items(), key=lambda item: (item[1], -int(item[0].lstrip("J"))), reverse=True)
        
        rank_agente_seguimiento = 4 # Default a último
        for idx, (jugador_id_str, _puntos) in enumerate(jugadores_ordenados, start=1):
            if jugador_id_str == agent_id_seguimiento:
                rank_agente_seguimiento = idx
                break
        
        return (victoria, puntos_agente_seguimiento, rank_agente_seguimiento)

    except Exception as e:
        # print(f"Excepción en simular_partida_configurada ({[ac.__name__ for ac in agentes_clases_partida]}): {e}")
        # traceback.print_exc() # Útil para depuración profunda
        return (0, 0, 4) # Considerar como derrota


def ejecutar_configuracion_benchmark(
    agente_principal_clase, 
    posicion_principal, 
    oponentes_config_clases, # Lista de 3 clases de oponentes
    num_partidas, 
    workers_a_utilizar
):
    """
    Ejecuta N partidas para una configuración dada (agente principal en una posición,
    contra una terna de oponentes). Devuelve estadísticas agregadas para el agente principal.
    """
    agentes_partida_final = [None] * 4
    agentes_partida_final[posicion_principal] = agente_principal_clase
    
    idx_oponente = 0
    for i in range(4):
        if agentes_partida_final[i] is None:
            if idx_oponente < len(oponentes_config_clases):
                agentes_partida_final[i] = oponentes_config_clases[idx_oponente]
                idx_oponente += 1
            else: # Debería estar cubierto por la lógica de llamada, pero por si acaso
                agentes_partida_final[i] = RandomAgent 
    
    # Convertir a tupla para que sea hasheable si ProcessPoolExecutor lo necesita internamente
    # o para evitar modificaciones accidentales.
    agentes_partida_final_tuple = tuple(agentes_partida_final)

    total_victorias_principal = 0
    total_puntos_principal = 0
    total_rank_principal = 0
    
    # El ProcessPoolExecutor se crea una vez por llamada a esta función
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers_a_utilizar) as executor:
        futures = [
            executor.submit(simular_partida_configurada, agentes_partida_final_tuple, posicion_principal) 
            for _ in range(num_partidas)
        ]
        for f in concurrent.futures.as_completed(futures):
            try:
                victoria, puntos, rank = f.result()
                total_victorias_principal += victoria
                total_puntos_principal += puntos
                total_rank_principal += rank
            except Exception as exc:
                print(f'Una partida generó una excepción: {exc}')
                # No sumar nada, se considera una partida fallida para las estadísticas
                # O asignar valores de derrota: total_rank_principal += 4

    nombres_agentes_partida = [ag.__name__ for ag in agentes_partida_final_tuple]
    return (total_victorias_principal, total_puntos_principal, total_rank_principal, nombres_agentes_partida)


# --- Funciones de Graficación ---
def generar_graficas(json_filepath="benchmark_resultados_detallados.json"):
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib o Pandas no están disponibles. No se generarán gráficas.")
        print("Puedes instalarla con: pip install matplotlib pandas")
        return

    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Archivo de resultados JSON '{json_filepath}' no encontrado. No se pueden generar gráficas.")
        return
    
    if not data:
        print("El archivo JSON está vacío. No hay datos para graficar.")
        return

    df = pd.DataFrame(data)

    # Convertir a numérico por si acaso
    df['victorias_principal'] = pd.to_numeric(df['victorias_principal'])
    df['puntos_total_principal'] = pd.to_numeric(df['puntos_total_principal'])
    df['rank_total_principal'] = pd.to_numeric(df['rank_total_principal'])
    df['partidas_simuladas_config'] = pd.to_numeric(df['partidas_simuladas_config'])

    df['ratio_victorias'] = df['victorias_principal'] / df['partidas_simuladas_config']
    df['puntos_media'] = df['puntos_total_principal'] / df['partidas_simuladas_config']
    df['rank_media'] = df['rank_total_principal'] / df['partidas_simuladas_config']
    
    # Crear directorio para gráficas si no existe
    graficas_dir = "benchmark_graficas"
    os.makedirs(graficas_dir, exist_ok=True)

    agentes_unicos_principales = df['agente_principal'].unique()

    for agente_nombre in agentes_unicos_principales:
        print(f"\nGenerando gráficas para: {agente_nombre}")
        df_agente = df[df['agente_principal'] == agente_nombre].copy()

        if df_agente.empty:
            print(f"No hay datos para el agente {agente_nombre}.")
            continue

        # 1. Estadísticas por Posición del Agente Principal
        stats_por_posicion = df_agente.groupby('posicion_principal').agg(
            ratio_victorias_mean=('ratio_victorias', 'mean'),
            puntos_media_mean=('puntos_media', 'mean'),
            rank_media_mean=('rank_media', 'mean')
        ).reset_index()
        stats_por_posicion['posicion_principal_display'] = stats_por_posicion['posicion_principal'] + 1

        if not stats_por_posicion.empty:
            # Ratio de Victorias por Posición
            plt.figure(figsize=(10, 6))
            plt.bar(stats_por_posicion['posicion_principal_display'], stats_por_posicion['ratio_victorias_mean'], color='skyblue')
            plt.title(f'Ratio de Victorias Promedio por Posición ({agente_nombre})')
            plt.xlabel('Posición de Inicio del Agente')
            plt.ylabel('Ratio de Victorias Promedio')
            plt.xticks(stats_por_posicion['posicion_principal_display'])
            plt.ylim(0, 1)
            plt.grid(axis='y', linestyle='--')
            plt.savefig(os.path.join(graficas_dir, f"{agente_nombre}_victorias_por_posicion.png"))
            plt.close()

            # Puntos Medios por Posición
            plt.figure(figsize=(10, 6))
            plt.bar(stats_por_posicion['posicion_principal_display'], stats_por_posicion['puntos_media_mean'], color='lightgreen')
            plt.title(f'Puntos Promedio por Posición ({agente_nombre})')
            plt.xlabel('Posición de Inicio del Agente')
            plt.ylabel('Puntos Promedio')
            plt.xticks(stats_por_posicion['posicion_principal_display'])
            plt.grid(axis='y', linestyle='--')
            plt.savefig(os.path.join(graficas_dir, f"{agente_nombre}_puntos_por_posicion.png"))
            plt.close()

            # Ranking Medio por Posición
            plt.figure(figsize=(10, 6))
            plt.bar(stats_por_posicion['posicion_principal_display'], stats_por_posicion['rank_media_mean'], color='lightcoral')
            plt.title(f'Ranking Promedio por Posición ({agente_nombre})')
            plt.xlabel('Posición de Inicio del Agente')
            plt.ylabel('Ranking Promedio (1=mejor, 4=peor)')
            plt.xticks(stats_por_posicion['posicion_principal_display'])
            plt.ylim(1, 4)
            plt.gca().invert_yaxis() # Mejor ranking arriba
            plt.grid(axis='y', linestyle='--')
            plt.savefig(os.path.join(graficas_dir, f"{agente_nombre}_rank_por_posicion.png"))
            plt.close()
            print(f"  Gráficas por posición guardadas para {agente_nombre}.")
        else:
            print(f"  No hay datos suficientes para gráficas por posición para {agente_nombre}.")


        # 2. Estadísticas contra Oponentes Específicos
        # Usaremos la 'descripcion_config' que ahora contiene la terna de oponentes.
        df_agente['oponente_clave'] = df_agente['descripcion_config']
        
        stats_vs_oponente = df_agente.groupby('oponente_clave').agg(
            ratio_victorias_mean=('ratio_victorias', 'mean'),
            puntos_media_mean=('puntos_media', 'mean'),
            rank_media_mean=('rank_media', 'mean'),
            total_partidas_config=('partidas_simuladas_config', 'sum')
        ).reset_index()

        # Ordenar por ratio de victorias para que la gráfica sea más legible si hay muchas ternas
        stats_vs_oponente = stats_vs_oponente.sort_values(by='ratio_victorias_mean', ascending=False)

        if not stats_vs_oponente.empty:
            plt.figure(figsize=(max(12, len(stats_vs_oponente) * 0.5), 7)) # Ajustar ancho dinámicamente
            plt.bar(stats_vs_oponente['oponente_clave'], stats_vs_oponente['ratio_victorias_mean'], color='purple')
            plt.title(f'Ratio de Victorias Promedio vs Ternas de Oponentes ({agente_nombre})')
            plt.xlabel('Terna de Oponentes Configurada')
            plt.ylabel('Ratio de Victorias Promedio')
            plt.xticks(rotation=75, ha="right") # Rotación mayor para nombres largos
            plt.ylim(0, 1)
            plt.tight_layout()
            plt.grid(axis='y', linestyle='--')
            plt.savefig(os.path.join(graficas_dir, f"{agente_nombre}_victorias_vs_ternas_oponentes.png"))
            plt.close()
            print(f"  Gráfica de victorias vs ternas de oponentes guardada para {agente_nombre}.")
        else:
             print(f"  No hay datos suficientes para gráficas vs ternas de oponentes para {agente_nombre}.")


    print(f"\nTodas las gráficas generadas en el directorio: {graficas_dir}")


# --- Bucle Principal del Benchmark ---
if __name__ == '__main__':
    print("Iniciando benchmark detallado...\n")
    if not MATPLOTLIB_AVAILABLE:
        print("ADVERTENCIA: Matplotlib y/o Pandas no están instalados. Las gráficas no se generarán al final.")
        print("             Puedes instalarlos con: pip install matplotlib pandas\n")

    total_workers_cpu = os.cpu_count()
    workers_a_utilizar = max(1, int(total_workers_cpu * porcentaje_workers))
    print(f"CPUs disponibles: {total_workers_cpu}")
    print(f"Workers a utilizar ({porcentaje_workers*100}%): {workers_a_utilizar}\n")

    # Listar todos los agentes disponibles automáticamente, excluyendo RandomAgent por defecto.
    # Los agentes principales vendrán de `agentes_principales_a_evaluar_rutas`.
    print("Listando agentes oponentes disponibles...")
    todas_rutas_agentes_encontradas = listar_rutas_agentes_automatico()
    
    oponentes_especificos_clases = []
    for ruta_str in todas_rutas_agentes_encontradas:
        if "RandomAgent" in ruta_str: # Siempre excluimos RandomAgent de la lista de oponentes "específicos"
            continue
        
        clase_agente = cargar_agente_desde_ruta(ruta_str)
        if clase_agente:
            # Podríamos añadir más filtros, ej. no incluir GeneticAgent si se entrena con él mismo
            oponentes_especificos_clases.append(clase_agente)

    if oponentes_especificos_clases:
        print(f"Oponentes específicos encontrados ({len(oponentes_especificos_clases)}): {', '.join([ag.__name__ for ag in oponentes_especificos_clases])}")
    else:
        print("No se encontraron oponentes específicos automáticos. Solo se usará RandomAgent como oponente.")
    
    resultados_globales_json = []
    tiempo_inicio_total = time.time()

    for ruta_agente_principal_str in agentes_principales_a_evaluar_rutas:
        agente_principal_clase = cargar_agente_desde_ruta(ruta_agente_principal_str)
        if not agente_principal_clase:
            print(f"Saltando evaluación para {ruta_agente_principal_str} (no se pudo cargar).")
            continue

        nombre_agente_principal = agente_principal_clase.__name__
        print(f"\n==== Evaluando Agente Principal: {nombre_agente_principal} ====")
        tiempo_inicio_agente_principal = time.time()

        # Construir la lista de clases de agentes que pueden ser oponentes en las ternas.
        # Esta lista incluirá todos los agentes de `oponentes_especificos_clases` (que son todos los agentes
        # encontrados automáticamente EXCEPTO RandomAgent), y también `RandomAgent`.
        # Luego, filtraremos al propio agente_principal_clase si está en esta lista.
        
        posibles_oponentes_para_producto = []
        for op_clase_cand in oponentes_especificos_clases: # oponentes_especificos_clases ya no tiene RandomAgent
            if op_clase_cand != agente_principal_clase: # No enfrentarse a sí mismo en la terna de oponentes
                posibles_oponentes_para_producto.append(op_clase_cand)
        
        posibles_oponentes_para_producto.append(RandomAgent) # Añadir RandomAgent a la lista de opciones

        # Eliminar duplicados por si RandomAgent ya estaba (aunque la lógica actual lo excluye antes)
        # y para manejar el caso donde oponentes_especificos_clases estaba vacío.
        temp_set = set()
        lista_final_oponentes_para_producto = []
        for item in posibles_oponentes_para_producto:
            if item not in temp_set:
                lista_final_oponentes_para_producto.append(item)
                temp_set.add(item)
        
        if not lista_final_oponentes_para_producto:
            print(f"  Advertencia: No hay oponentes disponibles (ni siquiera RandomAgent) para {nombre_agente_principal}. Usando solo RandomAgent como fallback.")
            lista_final_oponentes_para_producto = [RandomAgent]
        
        print(f"  Oponentes base para ternas: {[op.__name__ for op in lista_final_oponentes_para_producto]}")

        for pos_principal in range(4): # Iterar sobre las 4 posiciones de inicio para el agente principal
            print(f"\n  {nombre_agente_principal} en Posición de Inicio {pos_principal + 1}:")

            # Generar todas las ternas de oponentes usando itertools.product
            # cada elemento de ternas_de_oponentes_clases será una tupla de 3 clases de agentes
            num_configs_por_pos = 0
            for terna_oponentes_clases_tupla in itertools.product(lista_final_oponentes_para_producto, repeat=3):
                num_configs_por_pos +=1
                oponentes_config_actual_lista = list(terna_oponentes_clases_tupla)
                nombres_oponentes_str = ', '.join([op.__name__ for op in oponentes_config_actual_lista])
                
                print(f"    Config {num_configs_por_pos}: vs. [{nombres_oponentes_str}] (x{n_matches_por_config} partidas)")

                victorias, puntos, rank, nombres_cfg_partida = ejecutar_configuracion_benchmark(
                    agente_principal_clase, pos_principal, oponentes_config_actual_lista, 
                    n_matches_por_config, workers_a_utilizar
                )
                
                descripcion_config_str = f"vs [{nombres_oponentes_str}]"
                
                resultados_globales_json.append({
                    "agente_principal": nombre_agente_principal,
                    "posicion_principal": pos_principal,
                    "agentes_en_partida": nombres_cfg_partida, # Lista de los 4 agentes en orden de partida
                    "descripcion_config": descripcion_config_str, # Describe la terna de oponentes
                    "victorias_principal": victorias,
                    "puntos_total_principal": puntos,
                    "rank_total_principal": rank,
                    "partidas_simuladas_config": n_matches_por_config
                })
                print(f"      Resultado ({descripcion_config_str}): {victorias}/{n_matches_por_config} victorias, PtsTot: {puntos}, RankTot: {rank}")
            
            print(f"    Total de {num_configs_por_pos} configuraciones de oponentes probadas para {nombre_agente_principal} en posición {pos_principal+1}.")

        tiempo_fin_agente_principal = time.time()
        horas, resto = divmod(tiempo_fin_agente_principal - tiempo_inicio_agente_principal, 3600)
        minutos, segundos = divmod(resto, 60)
        print(f"\n  Tiempo para {nombre_agente_principal}: {int(horas)}h {int(minutos)}m {int(segundos)}s")

    # Guardar resultados detallados en JSON
    json_filename = "benchmark_resultados_detallados.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as f_json:
            json.dump(resultados_globales_json, f_json, indent=4)
        print(f"\nResultados detallados guardados en: {json_filename}")
    except Exception as e_json:
        print(f"Error al guardar el archivo JSON: {e_json}")

    tiempo_fin_total = time.time()
    horas_tot, resto_tot = divmod(tiempo_fin_total - tiempo_inicio_total, 3600)
    minutos_tot, segundos_tot = divmod(resto_tot, 60)
    print(f"\n--- Benchmark Detallado Completado ---")
    print(f"Tiempo total de ejecución: {int(horas_tot)}h {int(minutos_tot)}m {int(segundos_tot)}s\n")

    # Generar gráficas
    print("Intentando generar gráficas desde el archivo JSON...")
    try:
        generar_graficas(json_filename)
    except Exception as e_graf:
        print(f"Error durante la generación de gráficas: {e_graf}")
        traceback.print_exc()

    print("\n¡Proceso finalizado!")