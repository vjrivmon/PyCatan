import sys
sys.path.append('..') # This is to add the parent directory to the path

from Managers.GameDirector import GameDirector
from Agents.RandomAgent import RandomAgent as ra
from Agents.AdrianHerasAgent import AdrianHerasAgent as aha

import random
import json

game_director = GameDirector(agents=(ra, ra, aha, aha), max_rounds=200)
for i in range(100):
    random.seed(i)
    game_trace = game_director.game_start(i, False)
    game_hash = hash(json.dumps(game_trace)) # convert to string because dict is not hashable
    with open(f'./../Tests/test_traces/game_{i}.json', 'r') as f:
        test_hash = hash(f.read())
        if game_hash != test_hash:
            print('Game {i}: ERROR')
            break
        
    print(f'Game {i}: OK')
