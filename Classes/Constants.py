from collections import namedtuple

class MaterialConstants:
    """
    Constantes para facilitar la legibilidad al trabajar con materiales
    """
    CEREAL = 0
    MINERAL = 1
    CLAY = 2
    WOOD = 3
    WOOL = 4

    def __init__(self):
        return


class HarborConstants:
    """
    Constantes para facilitar la legibilidad al trabajar con puertos
    """
    CEREAL = 0
    MINERAL = 1
    CLAY = 2
    WOOD = 3
    WOOL = 4
    ALL = 5
    NONE = -1

    def __init__(self):
        return


class TerrainConstants:
    """
    Constantes para facilitar la legibilidad al trabajar con terrenos
    """
    CEREAL = 0
    MINERAL = 1
    CLAY = 2
    WOOD = 3
    WOOL = 4
    DESERT = -1

    def __init__(self):
        return


class BuildConstants:
    """
    Constantes para facilitar la legibilidad al trabajar con construcciones
    """

    TOWN = 'town'
    CITY = 'city'
    ROAD = 'road'
    CARD = 'card'

    def __init__(self):
        return


class DevelopmentCardConstants:
    """
    Constantes para facilitar la legibilidad al trabajar con cartas de desarrollo
    """

    KNIGHT = 0
    VICTORY_POINT = 1
    PROGRESS_CARD = 2

    KNIGHT_EFFECT = 0
    VICTORY_POINT_EFFECT = 1
    ROAD_BUILDING_EFFECT = 2
    YEAR_OF_PLENTY_EFFECT = 3
    MONOPOLY_EFFECT = 4

    def __init__(self):
        return

BuildMaterialsConstants = {
    BuildConstants.TOWN: (1, 0, 1, 1, 1),
    BuildConstants.CITY: (2, 3, 0, 0, 0),
    BuildConstants.ROAD: (0, 0, 1, 1, 0),
    BuildConstants.CARD: (1, 1, 0, 0, 1)
}