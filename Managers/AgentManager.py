from Agents import RandomAgent, AlexPastorAgent
from Interfaces.AgentInterface import AgentInterface as AgIn
from Classes.DevelopmentCards import DevelopmentCardsHand
from Classes.Hand import Hand
import inspect

class AgentManager:
    """
    Clase que se encarga de los agentes. De momento solo los carga en la partida, sin embargo, cabe la posibilidad de
    que sea el agent manager el que se encargue de darle paso a los agentes a hacer sus turnos
    """
    actual_player = 0
    first_agent_class = ''
    second_agent_class = ''
    third_agent_class = ''
    fourth_agent_class = ''

    players = []

    def __init__(self, for_test=False, agents = None):
        if agents:
            if len(agents) != 4:
                raise ValueError('El número de agentes debe ser 4')
            if not all([inspect.isclass(agent) and issubclass(agent, AgIn) for agent in agents]):
                raise ValueError('Los agentes deben de ser clases que hereden de AgentInterface')
            self.first_agent_class = agents[0]
            self.second_agent_class = agents[1]
            self.third_agent_class = agents[2]
            self.fourth_agent_class = agents[3]
        elif not for_test:
            self.first_agent_class = self.import_agent_class_from_input('first')
            self.second_agent_class = self.import_agent_class_from_input('second')
            self.third_agent_class = self.import_agent_class_from_input('third')
            self.fourth_agent_class = self.import_agent_class_from_input('fourth')
        elif for_test == 'test_específico':
            self.first_agent_class = AlexPastorAgent.AlexPastorAgent
            self.second_agent_class = AlexPastorAgent.AlexPastorAgent
            self.third_agent_class = AlexPastorAgent.AlexPastorAgent
            self.fourth_agent_class = AlexPastorAgent.AlexPastorAgent
        else:
            self.first_agent_class = RandomAgent.RandomAgent
            self.second_agent_class = RandomAgent.RandomAgent
            self.third_agent_class = RandomAgent.RandomAgent
            self.fourth_agent_class = RandomAgent.RandomAgent

        self.reset_game_values()
        return

    def set_actual_player(self, player_id=0):
        """
        :param player_id: int
        :return: None
        """
        self.actual_player = player_id
        return

    def reset_game_values(self):
        self.players = [
            {
                'id': 0,
                'victory_points': 0,
                'hidden_victory_points': 0,
                'player': self.first_agent_class(0),
                'resources': Hand(),
                'development_cards': DevelopmentCardsHand(),
                'knights': 0,
                'already_played_development_card': 0,
                'largest_army': 0,
                'longest_road': 0,
            },
            {
                'id': 1,
                'victory_points': 0,
                'hidden_victory_points': 0,
                'player': self.second_agent_class(1),
                'resources': Hand(),
                'development_cards': DevelopmentCardsHand(),
                'knights': 0,
                'already_played_development_card': 0,
                'largest_army': 0,
                'longest_road': 0,
            },
            {
                'id': 2,
                'victory_points': 0,
                'hidden_victory_points': 0,
                'player': self.third_agent_class(2),
                'resources': Hand(),
                'development_cards': DevelopmentCardsHand(),
                'knights': 0,
                'already_played_development_card': 0,
                'largest_army': 0,
                'longest_road': 0,
            },
            {
                'id': 3,
                'victory_points': 0,
                'hidden_victory_points': 0,
                'player': self.fourth_agent_class(3),
                'resources': Hand(),
                'development_cards': DevelopmentCardsHand(),
                'knights': 0,
                'already_played_development_card': 0,
                'largest_army': 0,
                'longest_road': 0,
            }
        ]
        return

    def import_agent_class_from_input(self, name=''):
        module_class = input(
            'Module and class of the ' + name +
            ' agent located in the folder Agents/ (e.g. MyModule.MyClass) (leave blank to use the default): ')
        if module_class == '':
            klass = RandomAgent.RandomAgent
        else:
            components = module_class.split('.')
            module = __import__('Agents.' + components[0], fromlist=[components[1]])
            klass = getattr(module, components[1])

        return klass
