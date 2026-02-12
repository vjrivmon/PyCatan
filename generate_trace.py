from Managers.GameDirector import GameDirector
from Agents.AdrianHerasAgent import AdrianHerasAgent
from Agents.AlexPastorAgent import AlexPastorAgent
from Agents.RandomAgent import RandomAgent

gd = GameDirector(agents=(AdrianHerasAgent, AlexPastorAgent, RandomAgent, RandomAgent), max_rounds=200, store_trace=True)
gd.game_start(game_number=999, print_outcome=True)
