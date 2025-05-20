import os
import time
import importlib
import concurrent.futures
import csv
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
from Managers.GameDirector import GameDirector

n_matches = 1000
porcentaje_workers = 0.95

agentes_alumnos = [
    "Agents.GeneticAgent.GeneticAgent",
    "Agents.AdrianHerasAgent.AdrianHerasAgent",
    # "Agents.CarlesZaidaAgent.CarlesZaidaAgent",
    # "Agents.EdoAgent.EdoAgent",
    # "Agents.SigmaAgent.SigmaAgent",
    # "Agents.TristanAgent.TristanAgent",
    # "Agents.PabloAleixAlexAgent.PabloAleixAlexAgent",
    # "Agents.CrabisaAgent.CrabisaAgent",
    # "Agents.AlexPelochoJaimeAgent.AlexPelochoJaimeAgent",
    # "Agents.AlexPastorAgent.AlexPastorAgent",
]

def cargar_agente(ruta_clase):
    modulo, clase = ruta_clase.rsplit(".", 1)
    mod = importlib.import_module(modulo)
    return getattr(mod, clase)

def simulate_match(position, agente_alumno):
    try:
        match_agents = [aha, apa, apja]
        match_agents.insert(position, agente_alumno)

        game_director = GameDirector(agents=match_agents, max_rounds=200, store_trace=False)
        game_trace = game_director.game_start(print_outcome=False)

        last_round = max(game_trace["game"].keys(), key=lambda r: int(r.split("_")[-1]))
        last_turn = max(game_trace["game"][last_round].keys(), key=lambda t: int(t.split("_")[-1].lstrip("P")))
        victory_points = game_trace["game"][last_round][last_turn]["end_turn"]["victory_points"]

        agent_id = f"J{position}"
        points = int(victory_points[agent_id])
        winner = max(victory_points, key=lambda player: int(victory_points[player]))
        victory = 1 if winner == agent_id else 0

        ordenados = sorted(victory_points.items(), key=lambda item: int(item[1]), reverse=True)
        for idx, (jugador, _) in enumerate(ordenados, start=1):
            if jugador == agent_id:
                rank = idx
                break

        return (victory, points, rank)
    except Exception:
        return (0, 0, 4)

if __name__ == '__main__':
    total_workers = os.cpu_count()
    workers_a_utilizar = max(1, int(total_workers * porcentaje_workers))
    print(f"Workers a utilizar ({porcentaje_workers*100}%): {workers_a_utilizar}\n")

    start_time = time.time()
    resumen_csv = []

    for ruta_agente in agentes_alumnos:
        agente_alumno = cargar_agente(ruta_agente)
        agent_name = agente_alumno.__name__
        print(f"\n==== Evaluando agente: {agent_name} ====\n")

        partial_start_time = time.time()
        position_results = {pos: 0 for pos in range(4)}
        total_wins = 0
        total_points = 0
        total_rank = 0

        with concurrent.futures.ProcessPoolExecutor(max_workers=workers_a_utilizar) as executor:
            for pos in range(4):
                futures = [executor.submit(simulate_match, pos, agente_alumno) for _ in range(n_matches)]
                for f in concurrent.futures.as_completed(futures):
                    victory, points, rank = f.result()
                    position_results[pos] += victory
                    total_wins += victory
                    total_points += points
                    total_rank += rank

        for pos in range(4):
            wins = position_results[pos]
            percentage = 100 * wins / n_matches
            print(f"- Posición {pos+1}: {wins} victorias de {n_matches} partidas ({percentage:.2f}%)")

        total_partidas = n_matches * 4
        ratio_victorias = total_wins / total_partidas
        media_puntos = total_points / total_partidas
        puesto_medio = total_rank / total_partidas

        print(f"\nTotal para {agent_name}: {total_wins} victorias de {total_partidas} partidas ({ratio_victorias:.2%})")
        print(f"Media de puntos: {media_puntos:.2f}")
        print(f"Puesto medio: {puesto_medio:.2f}")

        resumen_csv.append([agent_name, total_wins, total_points, total_partidas,
                            f"{ratio_victorias:.4f}", f"{media_puntos:.2f}", f"{puesto_medio:.2f}"])

        partial_end_time = time.time()
        horas, resto = divmod(partial_end_time - partial_start_time, 3600)
        minutos, segundos = divmod(resto, 60)
        print(f"Tiempo parcial: {int(horas)}h {int(minutos)}m {int(segundos)}s\n")

    # Guardar CSV
    csv_filename = "benchmark_vs_random_resultados.csv"
    with open(csv_filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Agente", "Victorias", "Puntos", "Partidas", "Ratio Victorias", "Media Puntos", "Puesto Medio"])
        for row in resumen_csv:
            writer.writerow(row)

    print(f"\nResultados guardados en: {csv_filename}")

    end_time = time.time()
    horas, resto = divmod(end_time - start_time, 3600)
    minutos, segundos = divmod(resto, 60)
    print(f"\nTiempo total: {int(horas)}h {int(minutos)}m {int(segundos)}s\n")