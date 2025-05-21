from Agents.RandomAgent import RandomAgent as ra
from Agents.AdrianHerasAgent import AdrianHerasAgent as aha
from Agents.AlexPastorAgent import AlexPastorAgent as apa
from Agents.AlexPelochoJaimeAgent import AlexPelochoJaimeAgent as apja
from Agents.CarlesZaidaAgent import CarlesZaidaAgent as cza
from Agents.CrabisaAgent import CrabisaAgent as ca
from Agents.EdoAgent import EdoAgent as ea
from Agents.PabloAleixAlexAgent import PabloAleixAlexAgent as paaa
from Agents.SigmaAgent import SigmaAgent as sa
from Agents.TristanAgent import TristanAgent as ta
from Agents.GeneticAgent import GeneticAgent as ga

from Managers.GameDirector import GameDirector
AGENTS = [ra, aha, apa, ga]

def main():
    """
    Función principal para ejecutar una simulación del juego Catan y calcular una métrica de fitness.

    Esta función configura y ejecuta una partida utilizando los agentes definidos globalmente,
    evaluando el rendimiento de un agente específico ('chosen_agent').
    El fitness se determina actualmente por si el 'chosen_agent' gana la partida.
    """
    all_agents = AGENTS  # Lista de todos los agentes participantes en la partida.
    chosen_agent = ga    # Agente específico cuyo rendimiento se está evaluando (GeneticAgent por defecto).

    # Ejemplo de ejecuciÃ³n
    try:
        game_director = GameDirector(agents=all_agents, max_rounds=200, store_trace=False)
        game_trace = game_director.game_start(print_outcome=False)
    except Exception as e:
        print(f"Error: {e}")
        return 0

    # AnÃ¡lisis de resultados
    last_round = max(game_trace["game"].keys(), key=lambda r: int(r.split("_")[-1]))
    last_turn = max(game_trace["game"][last_round].keys(), key=lambda t: int(t.split("_")[-1].lstrip("P")))
    victory_points = game_trace["game"][last_round][last_turn]["end_turn"]["victory_points"]
   
    winner = max(victory_points, key=lambda player: int(victory_points[player]))
    fitness = 0
    if all_agents.index(chosen_agent) == int(winner.lstrip("J")):  
        fitness += 1
    
    print(f"Puntuación de fitness calculada para el agente {chosen_agent.__name__}: {fitness}")
    return fitness

if __name__ == "__main__":
    print("Iniciando ejecución del script de simulación de Catan...")
    resultado_fitness = main()
    
    if resultado_fitness is not None:
        print(f"Ejecución completada. Fitness final obtenido: {resultado_fitness}")
    else:
        print("La ejecución de main() no produjo un resultado de fitness cuantificable o finalizó prematuramente debido a un error.")