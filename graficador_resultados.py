import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os

# --- Configuración ---
RESULTADOS_JSON_FILE = "experimentacion_hiperparametros_resultados.json"
# Por defecto, se graficará el mejor experimento general.
# Puedes cambiar esto a un índice específico (0 para el mejor, 1 para el segundo mejor, etc.)
# o establecer PLOT_SPECIFIC_EXPERIMENT_CSV_FILE al nombre de un archivo CSV directamente.
EXPERIMENTO_A_GRAFICAR_INDICE = 0 # 0 significa el mejor experimento general
PLOT_SPECIFIC_EXPERIMENT_CSV_FILE = None # Ej: "fitness_progress_exp_T50_NG500_...csv"

# Nombre del archivo CSV generado por entrenador_genetico.py
FITNESS_PROGRESS_CSV_FILE = "fitness_por_generacion.csv"
OUTPUT_GRAFICA_FILE = "grafica_fitness_evolucion_global.png" # Nombre para guardar la gráfica

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

def graficar_progreso_fitness_global(csv_filepath):
    """
    Carga los datos de progreso de fitness desde el archivo CSV del entrenamiento genético principal
    y genera una gráfica de la evolución global del fitness, marcando los ciclos.

    Args:
        csv_filepath (str): Ruta al archivo CSV con los datos de fitness.
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
    required_columns = ['GeneracionGlobal', 'MejorFitnessGeneracionVsRivalActual', 'PromedioFitnessGeneracionVsRivalActual', 'RivalActual', 'Ciclo']
    if not all(col in df.columns for col in required_columns):
        print(f"Error: El archivo CSV {csv_filepath} no contiene las columnas requeridas: {required_columns}")
        print(f"Columnas encontradas: {df.columns.tolist()}")
        return

    plt.figure(figsize=(15, 8)) # Aumentar tamaño para mejor visualización
    
    # Plotear las líneas de fitness
    plt.plot(df['GeneracionGlobal'], df['MejorFitnessGeneracionVsRivalActual'], label='Mejor Fitness en Gen (vs Rival Actual)', marker='.', linestyle='-', color='blue', alpha=0.7)
    plt.plot(df['GeneracionGlobal'], df['PromedioFitnessGeneracionVsRivalActual'], label='Fitness Promedio en Gen (vs Rival Actual)', marker='.', linestyle='--', color='green', alpha=0.7)

    # Marcar cambios de ciclo con líneas verticales y/o sombreado
    ciclos = df['Ciclo'].unique()
    num_ciclos = len(ciclos)
    # Usar un colormap para diferenciar ciclos si hay muchos, o alternar colores
    colores_ciclo = plt.cm.get_cmap('viridis', num_ciclos if num_ciclos > 1 else 2) 

    for i, ciclo_val in enumerate(sorted(ciclos)):
        ciclo_data = df[df['Ciclo'] == ciclo_val]
        min_gen_ciclo = ciclo_data['GeneracionGlobal'].min()
        max_gen_ciclo = ciclo_data['GeneracionGlobal'].max()
        
        # Añadir línea vertical al inicio de cada ciclo (excepto el primero si empieza en gen 1)
        if min_gen_ciclo > df['GeneracionGlobal'].min(): # Evitar línea en la gen 0 o 1 si es el inicio
            plt.axvline(x=min_gen_ciclo, color='gray', linestyle=':', linewidth=1.2, label=f'Inicio Ciclo {ciclo_val}' if i == 0 else None) # Solo una etiqueta para la leyenda
        
        # Alternativa: sombrear áreas de ciclos
        # plt.axvspan(min_gen_ciclo, max_gen_ciclo, color=mcolors.to_rgba(colores_ciclo(i), alpha=0.1), label=f'Ciclo {ciclo_val}' if i ==0 else None)

    # Añadir anotaciones para el rival en puntos clave (puede ser muy denso, usar con cuidado)
    # Se podría hacer un muestreo o solo para ciertos eventos.
    # Ejemplo: Marcar el primer enfrentamiento con cada rival en cada ciclo
    # rival_changes = df[df['RivalActual'].ne(df['RivalActual'].shift())]
    # for idx, row in rival_changes.iterrows():
    #     plt.text(row['GeneracionGlobal'], row['MejorFitnessGeneracionVsRivalActual'], 
    #              f"{row['RivalActual'].replace('Agent','')}", rotation=0, ha='left', va='bottom', fontsize=7, alpha=0.6, color='purple')


    plt.title(f'Evolución Global del Fitness del Agente Genético por Generación y Ciclo')
    plt.xlabel('Generación Global')
    plt.ylabel('Fitness (Victorias contra rival actual)')
    
    # Crear una leyenda que no se solape mucho y esté bien ubicada
    handles, labels = plt.gca().get_legend_handles_labels()
    # Filtrar etiquetas duplicadas para axvline si es necesario
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='best')
    
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout() # Ajustar para que todo quepa

    try:
        plt.savefig(OUTPUT_GRAFICA_FILE)
        print(f"Gráfica guardada como: {OUTPUT_GRAFICA_FILE}")
    except Exception as e:
        print(f"Error al guardar la gráfica: {e}")
    
    plt.show()

def main():
    """
    Función principal para generar la gráfica de evolución del fitness global.
    """
    print(f"Intentando graficar el progreso desde: {FITNESS_PROGRESS_CSV_FILE}")
    graficar_progreso_fitness_global(FITNESS_PROGRESS_CSV_FILE)

if __name__ == "__main__":
    # Verificar si pandas y matplotlib están instalados
    try:
        import pandas
        import matplotlib
    except ImportError as e:
        print(f"Error: {e}")
        print("Este script requiere las librerías pandas y matplotlib.")
        print("Por favor, instálalas ejecutando:")
        print("pip install pandas matplotlib")
        # En Colab, puedes usar: !pip install pandas matplotlib
        exit(1)
    
    main() 