import itertools
import entrenador_genetico
import time
import json
from datetime import datetime

# --- Definición de los rangos de hiperparámetros a probar ---
# Define aquí los valores que quieres probar para cada hiperparámetro.
# Puedes añadir o quitar valores de estas listas según necesites.
# ¡Cuidado! Un gran número de combinaciones puede tardar mucho tiempo.

configuraciones_a_probar = {
    'TAMANO_POBLACION': [30, 50], # Ejemplo: [30, 50, 100]
    # 'NUM_GENERACIONES': [50, 100, 250, 500], # Ejemplo: [50, 100, 200],
    'NUM_GENERACIONES': [50, 100, 250, 500], # Ejemplo: [50, 100, 200]
    'PROBABILIDAD_CRUCE': [0.7, 0.8, 0.9], # Ejemplo: [0.7, 0.8, 0.9]
    'PROBABILIDAD_MUTACION_GEN': [0.05, 0.1, 0.15, 0.2], # Ejemplo: [0.05, 0.1, 0.15, 0.2]
    'NUM_PARTIDAS_EVALUACION': [10], # Ejemplo: [10, 15]
    'NUM_ELITES': [3, 5], # Ejemplo: [2, 3, 5]
    # 'MAGNITUD_MUTACION_MAX_PORCENTAJE' se mantiene constante o se añade si se quiere variar.
}

# Archivo para guardar los resultados de la experimentación
resultados_file = "experimentacion_hiperparametros_resultados.json"

def ejecutar_entrenamiento_con_config(config):
    """
    Ejecuta el entrenamiento genético con una configuración de hiperparámetros dada.
    Modifica directamente las variables globales de hiperparámetros en el módulo
    entrenador_genetico antes de llamar a su función main().
    """
    print(f"\n--- Iniciando prueba con configuración: {config} ---")
    
    # Guardar los valores originales para restaurarlos después (buena práctica)
    original_params = {}
    for key in config.keys():
        if hasattr(entrenador_genetico, key):
            original_params[key] = getattr(entrenador_genetico, key)

    # Aplicar la nueva configuración
    for key, value in config.items():
        setattr(entrenador_genetico, key, value)
        print(f"  {key} = {value}")

    # Preparar el nombre del archivo de log para esta ejecución específica
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    config_str_log = "_".join([f"{k.replace('PROBABILIDAD_','P').replace('TAMANO_','T').replace('NUM_','N')}{v}" for k,v in config.items()])
    log_file_specific = f"log_exp_{config_str_log}_{timestamp}.txt"
    original_log_file = entrenador_genetico.LOG_FILE
    entrenador_genetico.LOG_FILE = log_file_specific
    
    # Preparar el nombre del archivo del mejor cromosoma para esta ejecución
    # para que cada experimento guarde su mejor cromosoma por separado y no se sobrescriban.
    best_chromosome_file_specific = f"best_chromosome_exp_{config_str_log}_{timestamp}.json"
    original_best_chromosome_file = entrenador_genetico.BEST_CHROMOSOME_FILE
    entrenador_genetico.BEST_CHROMOSOME_FILE = best_chromosome_file_specific

    # Preparar el nombre del archivo de progreso de fitness para esta ejecución específica
    fitness_progress_file_specific = f"fitness_progress_exp_{config_str_log}_{timestamp}.csv"
    original_fitness_progress_file = None
    if hasattr(entrenador_genetico, 'FITNESS_PROGRESS_FILE'):
        original_fitness_progress_file = entrenador_genetico.FITNESS_PROGRESS_FILE
        entrenador_genetico.FITNESS_PROGRESS_FILE = fitness_progress_file_specific
    else:
        # Si FITNESS_PROGRESS_FILE no existe en entrenador_genetico, no podemos gestionarlo aquí.
        # Esto puede pasar si la modificación para guardarlo no se aplicó o se revirtió.
        print("Advertencia: La variable FITNESS_PROGRESS_FILE no se encontró en entrenador_genetico.py. No se guardará el progreso de fitness por separado para este experimento.")
        fitness_progress_file_specific = None # Indicar que no se gestiona


    # Limpiar el archivo de mejor cromosoma previo si existe para esta config específica,
    # o decidir si se quiere continuar desde un punto previo (más complejo)
    # Por simplicidad, cada ejecución empieza de cero respecto al mejor cromosoma,
    # aunque podría cargar uno si se define una estrategia para ello.
    # Para el experimento, es mejor empezar sin un cromosoma previo cargado para cada config.
    # Esto se puede forzar asegurando que el 'BEST_CHROMOSOME_FILE' específico no exista
    # o modificando la lógica de carga en entrenador_genetico.main() (más invasivo).
    # Una forma sencilla es modificar temporalmente la lógica de carga en entrenador_genetico
    # o simplemente dejar que cada experimento guarde su propio archivo y no cargue.
    # La forma más limpia es pasar un flag a main() para no cargar, pero eso requiere modificar main().
    # Por ahora, al usar nombres de archivo únicos, el cargador no encontrará archivos "previos"
    # para la *nueva* ejecución, lo cual es el comportamiento deseado para una prueba limpia.

    start_time = time.time()
    mejor_fitness = entrenador_genetico.main() # Ejecutar el entrenamiento
    end_time = time.time()
    duracion = end_time - start_time

    print(f"--- Prueba finalizada para: {config} ---")
    print(f"  Mejor Fitness Obtenido: {mejor_fitness}")
    print(f"  Duración: {duracion:.2f} segundos")
    print(f"  Log guardado en: {log_file_specific}")
    print(f"  Mejor cromosoma guardado en: {best_chromosome_file_specific}")

    # Restaurar los valores originales de los hiperparámetros y archivos de log/cromosoma
    for key, value in original_params.items():
        setattr(entrenador_genetico, key, value)
    entrenador_genetico.LOG_FILE = original_log_file
    entrenador_genetico.BEST_CHROMOSOME_FILE = original_best_chromosome_file
    if original_fitness_progress_file is not None and hasattr(entrenador_genetico, 'FITNESS_PROGRESS_FILE'):
        entrenador_genetico.FITNESS_PROGRESS_FILE = original_fitness_progress_file

    resultado_dict = {
        'configuracion': config,
        'mejor_fitness': mejor_fitness,
        'duracion_segundos': duracion,
        'log_file': log_file_specific,
        'best_chromosome_file': best_chromosome_file_specific
    }
    if fitness_progress_file_specific:
        resultado_dict['fitness_progress_file'] = fitness_progress_file_specific
    
    return resultado_dict

def main_experimentador():
    """
    Función principal del script experimentador.
    Genera todas las combinaciones de hiperparámetros y ejecuta el entrenamiento para cada una.
    """
    
    # Obtener todas las claves de los hiperparámetros que se van a variar
    param_names = list(configuraciones_a_probar.keys())
    
    # Obtener todas las listas de valores para cada hiperparámetro
    param_values = [configuraciones_a_probar[key] for key in param_names]
    
    # Generar todas las combinaciones posibles (producto cartesiano)
    combinaciones = list(itertools.product(*param_values))
    
    print(f"Se probarán {len(combinaciones)} combinaciones de hiperparámetros.")
    
    todos_los_resultados = []

    # Cargar resultados previos si existen, para no repetir trabajo (opcional y más complejo)
    # try:
    #     with open(resultados_file, 'r') as f:
    #         todos_los_resultados = json.load(f)
    #     print(f"Resultados previos cargados desde {resultados_file}")
    # except FileNotFoundError:
    #     print("No se encontraron resultados previos.")
    # except json.JSONDecodeError:
    #     print(f"Error al decodificar {resultados_file}. Empezando desde cero.")


    for i, combo_values in enumerate(combinaciones):
        config_actual = dict(zip(param_names, combo_values))
        
        print(f"\n[Experimento {i+1}/{len(combinaciones)}]")
        
        # Aquí podrías añadir lógica para saltar configuraciones ya probadas si las cargas desde archivo
        # if any(res['configuracion'] == config_actual for res in todos_los_resultados):
        #     print(f"Configuración {config_actual} ya probada. Saltando.")
        #     continue

        resultado_ejecucion = ejecutar_entrenamiento_con_config(config_actual)
        todos_los_resultados.append(resultado_ejecucion)
        
        # Guardar resultados progresivamente
        try:
            with open(resultados_file, 'w', encoding='utf-8') as f:
                json.dump(todos_los_resultados, f, indent=4)
            print(f"Resultados actualizados guardados en {resultados_file}")
        except Exception as e:
            print(f"Error guardando resultados: {e}")

    print("\n--- Todos los experimentos finalizados ---")
    
    if not todos_los_resultados:
        print("No se obtuvieron resultados.")
        return

    # Ordenar los resultados por 'mejor_fitness' de mayor a menor
    todos_los_resultados.sort(key=lambda x: x.get('mejor_fitness', -float('inf')), reverse=True)
    
    print("\n--- Mejores Configuraciones Encontradas ---")
    for i, resultado in enumerate(todos_los_resultados[:5]): # Mostrar las 5 mejores
        print(f"  Top {i+1}:")
        print(f"    Configuración: {resultado['configuracion']}")
        print(f"    Mejor Fitness: {resultado['mejor_fitness']}")
        print(f"    Duración: {resultado['duracion_segundos']:.2f}s")
        print(f"    Log: {resultado['log_file']}")
        print(f"    Cromosoma: {resultado['best_chromosome_file']}")
        if 'fitness_progress_file' in resultado and resultado['fitness_progress_file']:
            print(f"    Progreso Fitness: {resultado['fitness_progress_file']}")
        print("-" * 20)
        
    if todos_los_resultados:
        mejor_config_general = todos_los_resultados[0]
        print("\n--- Mejor Configuración General ---")
        print(f"  Configuración: {mejor_config_general['configuracion']}")
        print(f"  Mejor Fitness: {mejor_config_general['mejor_fitness']}")
        print(f"  Duración: {mejor_config_general['duracion_segundos']:.2f}s")
        print(f"  Log: {mejor_config_general['log_file']}")
        print(f"  Cromosoma: {mejor_config_general['best_chromosome_file']}")
        if 'fitness_progress_file' in mejor_config_general and mejor_config_general['fitness_progress_file']:
            print(f"  Progreso Fitness: {mejor_config_general['fitness_progress_file']}")
        print("\n========================================")
        print(f"El mejor cromosoma se puede encontrar en: {mejor_config_general['best_chromosome_file']}")
        print("Puedes usar ese archivo .json para cargar el cromosoma en tu GeneticAgent.")

if __name__ == "__main__":
    # Pequeña verificación para asegurar que el módulo entrenador_genetico es accesible
    # y que su función main está disponible.
    if not hasattr(entrenador_genetico, 'main') or not callable(entrenador_genetico.main):
        print("Error: No se pudo acceder a la función 'main' del módulo 'entrenador_genetico.py'.")
        print("Asegúrate de que el script 'entrenador_genetico.py' está en el mismo directorio o en el PYTHONPATH,")
        print("y que la función 'main' está definida correctamente y devuelve el mejor fitness.")
        exit(1)
        
    # Verificar que los hiperparámetros a modificar existen en el módulo entrenador_genetico
    for param_name_to_check in configuraciones_a_probar.keys():
        if not hasattr(entrenador_genetico, param_name_to_check):
            print(f"Error: El hiperparámetro '{param_name_to_check}' definido en 'configuraciones_a_probar'")
            print(f"       no existe como variable global en 'entrenador_genetico.py'.")
            print("       Por favor, verifica los nombres de los hiperparámetros.")
            exit(1)

    main_experimentador() 