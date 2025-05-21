import json
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Configuración ---
RESULTADOS_JSON_FILE = "experimentacion_hiperparametros_resultados.json"
# Por defecto, se graficará el mejor experimento general.
# Puedes cambiar esto a un índice específico (0 para el mejor, 1 para el segundo mejor, etc.)
# o establecer PLOT_SPECIFIC_EXPERIMENT_CSV_FILE al nombre de un archivo CSV directamente.
EXPERIMENTO_A_GRAFICAR_INDICE = 0 # 0 significa el mejor experimento general
PLOT_SPECIFIC_EXPERIMENT_CSV_FILE = None # Ej: "fitness_progress_exp_T50_NG500_...csv"

OUTPUT_GRAFICA_FILE = "grafica_fitness_evolucion.png" # Nombre para guardar la gráfica

def graficar_progreso_fitness(csv_filepath, configuracion_info="Experimento"):
    """
    Carga los datos de progreso de fitness desde un archivo CSV y genera una gráfica.

    Args:
        csv_filepath (str): Ruta al archivo CSV con los datos de fitness.
        configuracion_info (str, optional): Información sobre la configuración para el título.
                                           Defaults to "Experimento".
    """
    if not os.path.exists(csv_filepath):
        print(f"Error: El archivo CSV especificado no se encontró: {csv_filepath}")
        return

    try:
        df = pd.read_csv(csv_filepath)
    except Exception as e:
        print(f"Error al leer el archivo CSV {csv_filepath}: {e}")
        return

    if df.empty:
        print(f"El archivo CSV {csv_filepath} está vacío.")
        return

    # Verificar que las columnas necesarias existen
    required_columns = ['Generacion', 'MejorFitnessGeneracion']
    if not all(col in df.columns for col in required_columns):
        print(f"Error: El archivo CSV {csv_filepath} no contiene las columnas requeridas: {required_columns}")
        print(f"Columnas encontradas: {df.columns.tolist()}")
        return

    plt.figure(figsize=(12, 7))
    
    plt.plot(df['Generacion'], df['MejorFitnessGeneracion'], label='Mejor Fitness por Generación', marker='.', linestyle='-', color='blue')
    
    if 'PromedioFitnessGeneracion' in df.columns:
        plt.plot(df['Generacion'], df['PromedioFitnessGeneracion'], label='Fitness Promedio por Generación', marker='.', linestyle='--', color='green')

    plt.title(f'Evolución del Fitness - {configuracion_info}')
    plt.xlabel('Generación')
    plt.ylabel('Fitness (Victorias)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    try:
        plt.savefig(OUTPUT_GRAFICA_FILE)
        print(f"Gráfica guardada como: {OUTPUT_GRAFICA_FILE}")
    except Exception as e:
        print(f"Error al guardar la gráfica: {e}")
    
    plt.show()

def main():
    """
    Función principal para cargar resultados y generar la gráfica.
    """
    selected_csv_file_to_plot = PLOT_SPECIFIC_EXPERIMENT_CSV_FILE
    config_details_for_title = "Configuración Específica"

    if not selected_csv_file_to_plot:
        if not os.path.exists(RESULTADOS_JSON_FILE):
            print(f"Error: El archivo de resultados JSON '{RESULTADOS_JSON_FILE}' no se encontró.")
            print("Por favor, ejecuta primero experimentador_hiperparametros.py o especifica un archivo CSV directamente.")
            return

        try:
            with open(RESULTADOS_JSON_FILE, 'r', encoding='utf-8') as f:
                todos_los_resultados = json.load(f)
        except Exception as e:
            print(f"Error al leer el archivo JSON de resultados '{RESULTADOS_JSON_FILE}': {e}")
            return

        if not todos_los_resultados:
            print("El archivo de resultados JSON está vacío. No hay experimentos para graficar.")
            return

        # Asumimos que los resultados están ordenados por 'mejor_fitness' descendente en el JSON.
        if EXPERIMENTO_A_GRAFICAR_INDICE >= len(todos_los_resultados):
            print(f"Error: El índice de experimento {EXPERIMENTO_A_GRAFICAR_INDICE} está fuera de rango.")
            print(f"Hay {len(todos_los_resultados)} experimentos en el archivo de resultados.")
            return
        
        experimento_seleccionado = todos_los_resultados[EXPERIMENTO_A_GRAFICAR_INDICE]
        
        if 'fitness_progress_file' not in experimento_seleccionado or not experimento_seleccionado['fitness_progress_file']:
            print(f"Error: El experimento seleccionado (índice {EXPERIMENTO_A_GRAFICAR_INDICE}) no tiene un archivo de progreso de fitness registrado.")
            print(f"Datos del experimento: {experimento_seleccionado.get('configuracion')}")
            return
            
        selected_csv_file_to_plot = experimento_seleccionado['fitness_progress_file']
        config_details_for_title = str(experimento_seleccionado.get('configuracion', 'Mejor Experimento'))
        print(f"Se graficará el progreso del experimento (Top {EXPERIMENTO_A_GRAFICAR_INDICE + 1}): {config_details_for_title}")
        print(f"Usando el archivo CSV: {selected_csv_file_to_plot}")

    if not selected_csv_file_to_plot:
        print("No se ha especificado o encontrado un archivo CSV para graficar.")
        return
        
    graficar_progreso_fitness(selected_csv_file_to_plot, config_details_for_title)

if __name__ == "__main__":
    # Verificar si pandas y matplotlib están instalados
    try:
        import pandas
        import matplotlib
    except ImportError:
        print("Este script requiere las librerías pandas y matplotlib.")
        print("Por favor, instálalas ejecutando:")
        print("pip install pandas matplotlib")
        # En Colab, puedes usar: !pip install pandas matplotlib
        exit(1)

    main() 