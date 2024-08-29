import math
import random

from Classes.Constants import DevelopmentCardConstants as Dcc


# Debido a como funciona el juego, en caso de querer lanzar una carta de desarrollo debería de lanzarse siempre que
# un jugador devuelva una carta como parte de su on_... Si devuelve una carta, el GameManager resuelve su efecto y
# cuenta cualquier otra carta que intente lanzar como un paso de fase.
class DevelopmentDeck:
    # Puedes construir cualquier cantidad de cartas de desarrollo PERO solo puedes jugar una.
    # Puedes jugar cualquier cantidad de cartas de desarrollo que otorguen puntos de victoria.
    # Las cartas que dan puntos de victoria (idealmente) se mantienen en secreto hasta que se pueda ganar con ellas
    # NO se puede jugar una carta que se acaba de comprar SALVO que sea una que te lleve a 10 puntos de victoria
    # Se pueden jugar en cualquier momento de una ronda, incluso antes de tirar el dado (en cualquier on_... del agente)
    current_index = 0  # La carta que se va a robar si alguien construye una

    def __init__(self):
        # cuidado, [objeto] * n crea n referencias al mismo objeto
        self.deck = []
        self.deck += [DevelopmentCard(0, Dcc.KNIGHT, Dcc.KNIGHT_EFFECT) for i in range(14)] # Soldados
        self.deck += [DevelopmentCard(0, Dcc.VICTORY_POINT, Dcc.VICTORY_POINT_EFFECT) for i in range(5)] # Puntos de victoria
        self.deck += [DevelopmentCard(0, Dcc.PROGRESS_CARD, Dcc.ROAD_BUILDING_EFFECT) for i in range(2)] # Cartas de progreso
        self.deck += [DevelopmentCard(0, Dcc.PROGRESS_CARD, Dcc.YEAR_OF_PLENTY_EFFECT) for i in range(2)]
        self.deck += [DevelopmentCard(0, Dcc.PROGRESS_CARD, Dcc.MONOPOLY_EFFECT) for i in range(2)]

        for i in range(len(self.deck)):
            self.deck[i].id = i


    def shuffle_deck(self): # En que momento se ha decidido implementar shuffle. Lo dejo así porque rompe test de intetgración
        current_index = len(self.deck)
        while current_index != 0:
            random_index = math.floor(random.random() * current_index) # randint par quien?
            current_index -= 1
            (self.deck[current_index], self.deck[random_index]) = (self.deck[random_index], self.deck[current_index])

    def draw_card(self):
        if len(self.deck):
            return self.deck.pop(0)

    def __str__(self):
        string = '[ \n' 
        for card in self.deck:
            string += f"{card.__str__()}, \n"
        string += ']'

        return string


class DevelopmentCard:
    """
    Carta de desarrollo
    :param id: Número que identifica la carta.
    :param type: Punto de victoria, soldado, o carta de progreso (monopolio, año de la cosecha,
    construir 2 carreteras gratis).
    :param effect: En función del número que tiene, hace una cosa u otra.
    """

    def __init__(self, id=0, type='', effect=0):
        self.id = id
        self.type = type
        self.effect = effect
        return

    def __str__(self):
        return "{'id': " + str(self.id) + ", 'type': " + str(self.type) + ", 'effect': " + str(self.effect) + "}"

    def __to_object__(self):
        return {'id': self.id, 'type': self.type, 'effect': self.effect}


class DevelopmentCardsHand:
    """
    Clase que interactúa con la mano del jugador. Cada jugador solo puede ver su propia mano salvo que se use una carta,
    en cuyo caso los demás jugadores saben la carta usada.
    """
    def __init__(self):
        self.hand = []

    def add_card(self, card: DevelopmentCard):
        self.hand.append(card)

    def check_hand(self): #TODO: por que no de volver el objeto carta y ya?
        """
        Devuelve la mano que tiene el jugador, por si quiere por su cuenta comprobar qué cartas posee para gastar.
        :return: [{'id': int, 'type': string, 'effect': int}...]
        """
        return [{'id': card.id, 'type': card.type, 'effect': card.effect} for card in self.hand]

    def select_card_by_id(self, id):
        """
        Seleccionas la carta con el ID que se le pase, la pasa al gameManager, la juega y la borra de la mano.
        :param id: (int) Número indicativo de la carta.
        """
        # return next((card for card in self.hand if card.id == id), None) # alternativa
        for card in self.hand:
            if card.id == id:
                return card

    def delete_card(self, id):
        """
        Borra la carta con la ID que se le pase.
        :param id: (int) Número indicativo de la carta.
        """
        self.hand = list(filter(lambda card: card.id != id, self.hand))
