from Classes.Constants import *
from Classes.Materials import Materials
from typing import List, Tuple, Set, FrozenSet
import random
from typing import NamedTuple
from functools import reduce
from Classes.Board import Board
from itertools import chain

class Mat(NamedTuple):
    ce: int
    mi: int
    cl: int
    wd: int
    wl: int
    
    def __str__(self):
        material_icons = ["🥖", "🪨", "🧱", "🪵", "🧶"]
        material_tuples = list(zip(self, material_icons))
        mls = [str(t[0]).rjust(2)+t[1] for t in material_tuples]
        return " ".join(mls)

class Road(NamedTuple):
    vertex: FrozenSet[int]
    owner: int

    def __str__(self):
        return f"{self.owner}: {self.vertex}"

TOWN = BuildConstants.TOWN
CITY = BuildConstants.CITY
ROAD = BuildConstants.ROAD   
CARD = BuildConstants.CARD

CEREAL = MaterialConstants.CEREAL
MINERAL = MaterialConstants.MINERAL
CLAY = MaterialConstants.CLAY
WOOD = MaterialConstants.WOOD
WOOL = MaterialConstants.WOOL



# cereal, mineral, clay, wood, wool
building_costs = {
    TOWN: Mat(1, 0, 1, 1, 1), # {CEREAL: 1, CLAY: 1, WOOD: 1, WOOL: 1},
    CITY: Mat(2, 3, 0, 0, 0), # {CEREAL: 2, MINERAL: 3},
    ROAD: Mat(0, 0, 1, 1, 0), # {CLAY: 1, WOOD: 1},
    CARD: Mat(1, 1, 0, 0, 1), # {CEREAL: 1, WOOL: 1, MINERAL: 1}
}

goals_costs = {
    "build_town": building_costs[TOWN],
    "build_city": building_costs[CITY],
    "build_road": building_costs[ROAD],
    "buy_card": building_costs[CARD]
}

dice_odds = {
    7: 6,
    6: 5, 8: 5,
    5: 4, 9: 4,
    4: 3, 10: 3,
    3: 2, 11: 2,
    2: 1, 12: 1
}


# List helpers

def msub(m1: Mat, m2: Mat) -> Mat: 
    """ Element by element subtraction """ 
    return Mat(*(x - y for x, y in zip(m1, m2)))

def madd(m1: Mat, m2: Mat) -> Mat:
    """ Element by element addition """	
    return Mat(*(x + y for x, y in zip(m1, m2)))

def mpos(m: Mat) -> Mat:
    """ filter non-positive values"""
    return Mat(*(x if x > 0 else 0 for x in m))

def index_to_mat(index: int, value: int = 1) -> Mat:
    """
    Converts an index to a Mat object.
    """
    return Mat(*[value if i == index else 0 for i in range(5)])


# Materials helpers

def materials_to_mat(materials: Materials) -> Mat:
    """ Converts a Materials object to a Mat object. """
    return Mat(materials.cereal, materials.mineral, materials.clay, materials.wood, materials.wool)

def mat_to_materials(mat: Mat) -> Materials:
    """ Converts a Mat object to a Materials object. """
    return Materials(*mat)

def missing_materials(owned: Mat, wanted: Mat) -> Mat:
    """ Calculates the missing materials based on the owned materials and the desired materials. """
    return mpos(msub(wanted, owned))

def excess_materials(owned: Mat, goal_list: List[str]) -> Mat:
    """ Calculates the excess materials based on the owned materials and the desired goals. """
    excess = reduce(msub, [goals_costs[goal] for goal in goal_list], owned)
    return mpos(excess)

def needed_materials(goal_list: List[str]) -> Mat:
    """ Calculates the needed materials based on the desired goals. """	
    wanted = reduce(madd, [goals_costs[goal] for goal in goal_list], Mat(0, 0, 0, 0, 0))
    return wanted


# exchange helpers

def weighted_material_choice(mat: Mat) -> int:
    """ Chooses an index based on the materials. """
    list = [0] * mat[0] + [1] * mat[1] + [2] * mat[2] + [3] * mat[3] + [4] * mat[4]
    return random.choice(list)

def create_exchange(owned: Mat, goal_list: List[str]) -> Tuple[Mat, Mat]:
    """ Creates a trade offer based on the owned materials and the desired goals. """
    excess = excess_materials(owned, goal_list)
    needed = needed_materials(goal_list)
    missing = missing_materials(owned, needed)
    return excess, missing

def goal_distance(owned: Mat, goal_list: List[str]) -> int:
    """ Calculates the distance to the goal based on the owned materials and the desired goals. """
    needed = needed_materials(goal_list)
    missing = missing_materials(owned, needed)
    return sum(missing)


# Road helpers
def get_roads(board: Board, player_id: int) -> Set[FrozenSet[int]]:
    """ Returns a list of all roads on the board. """
    nodes = board.nodes
    roads = set()
    for node in nodes:
        roads.update({frozenset((node["id"], road["node_id"])) for road in node["roads"] if road["player_id"] == player_id})
    return roads

def get_length(roads: Set[FrozenSet[int]], node_id: int) -> int:
    """ Returns the longest road starting from a node. """
    if len(roads) == 0:
        return 0

    next_roads = {road for road in roads if node_id in road}
    if len(next_roads) == 0:
        return 0

    results = []
    for road in next_roads:
        other_node, *_ = road - {node_id}
        new_roads = roads - {road}
        results.append(1 + get_length(new_roads, other_node))
    
    return max(results)

    
def get_road_ends(board: Board, player_id: int) -> List[int]:
    """ Returns an ordered list of all road ends on the board. The order is based on the longest road."""
    roads = get_roads(board, player_id)
    ends = list(set(chain(*roads)))
    ends.sort(key=lambda x: -get_length(roads, x))
    return ends

def get_adjacent_road(board: Board, node_id: int, player_id: int) -> List:
    """ Returns a list of all adjacent nodes to a node. """
    adjacent_nodes = board.__get_adjacent_nodes__(node_id)
    adjacent_roads = [{'starting_node': node_id, 'finishing_node': node} for node in adjacent_nodes]
    adjacent_roads += [{'starting_node': node, 'finishing_node': node_id} for node in adjacent_nodes]
    valid_roads = board.valid_road_nodes(player_id)
    adjacent_valid_roads = [road for road in adjacent_roads if road in valid_roads]
    return adjacent_valid_roads


# Node helpers
def get_free_nodes(board: Board) -> List[int]:
    """ Returns a list of all free nodes on the board. """
    nodes = board.nodes
    free_nodes = [node["id"] for node in nodes if node["player"] == -1]
    return free_nodes

def get_adjacent_terrain(board: Board, node: int) -> List[int]:
    """ Returns a list of all adjacent terrains to a list of nodes. """
    return board.__get_contacting_terrain__(node)

def get_node_resources(board: Board, node: int) -> List[float]:
    """ Returns a list of all resources on a list of nodes. """
    adjacent = get_adjacent_terrain(board, node)
    resources = [terrain['terrain_type'] for terrain in board.terrain if terrain['id'] in adjacent  if terrain['terrain_type'] != TerrainConstants.DESERT]
    dices = [terrain['probability'] for terrain in board.terrain if terrain['id'] in adjacent if terrain['terrain_type'] != TerrainConstants.DESERT]
    # print("adjacent", adjacent, "resources", resources, "dices", dices)
    odds = [dice_odds[dice] for dice in dices]

    terrain = [0., 0., 0., 0., 0.]
    for resource, odd in zip(resources, odds):
        if resource == TerrainConstants.DESERT:
            continue
        terrain[resource] += odd

    return terrain

def get_town_nodes(board: Board, player_id: int) -> List[int]:
    """ Returns a list of all town nodes on the board. """
    nodes = board.nodes
    town_nodes = []
    for node in nodes:
        if node["player"] == player_id:
            town_nodes.append(node["id"])
            if node["has_city"] == True:
                town_nodes.append(node["id"])
    return town_nodes

def get_thief_nodes(board: Board) -> List[int]:
    """ Returns a list of all nodes with the thief on the board. """
    for terrain in board.terrain:
        if terrain["has_thief"] and terrain["terrain_type"] == TerrainConstants.DESERT:
            return terrain["contacting_nodes"]
    return []


# development card helpers

def get_development_card(hand, effect):
    """ Returns the index of the first card of a certain kind in a hand. """
    for i, card in enumerate(hand):
        if card.effect == effect:
            return i
    return None