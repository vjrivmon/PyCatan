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

    def __init__(self):
        # cuidado, [objeto] * n crea n referencias al mismo objeto
        self.deck = [DevelopmentCard(Dcc.KNIGHT, Dcc.KNIGHT_EFFECT) for i in range(14)] # Soldados
        self.deck += [DevelopmentCard(Dcc.VICTORY_POINT, Dcc.VICTORY_POINT_EFFECT) for i in range(5)] # Puntos de victoria
        self.deck += [DevelopmentCard(Dcc.PROGRESS_CARD, Dcc.ROAD_BUILDING_EFFECT) for i in range(2)] # Cartas de progreso
        self.deck += [DevelopmentCard(Dcc.PROGRESS_CARD, Dcc.YEAR_OF_PLENTY_EFFECT) for i in range(2)]
        self.deck += [DevelopmentCard(Dcc.PROGRESS_CARD, Dcc.MONOPOLY_EFFECT) for i in range(2)]

        random.shuffle(self.deck)


    def draw_card(self):
        if len(self.deck):
            return self.deck.pop(0)


    def __str__(self):
        string = '' 
        for card in self.deck:
            string += f" - {card.__str__()}, \n"

        return string


class DevelopmentCard: # de verdad hace falta type y effect?
    """
    Carta de desarrollo
    :param type: Punto de victoria, soldado, o carta de progreso (monopolio, año de la cosecha,
    construir 2 carreteras gratis).
    :param effect: En función del número que tiene, hace una cosa u otra.
    """

    def __init__(self, type='', effect=0):
        self.type = type
        self.effect = effect
        return

    def __str__(self):
        return f"Type: {self.type}, Effect: {self.effect}"

    def __to_object__(self):
        return {'type': self.type, 'effect': self.effect}


class DevelopmentCardsHand:
    """
    Clase que interactúa con la mano del jugador. Cada jugador solo puede ver su propia mano salvo que se use una carta,
    en cuyo caso los demás jugadores saben la carta usada.
    """
    def __init__(self):
        self.hand = []

    def add_card(self, card: DevelopmentCard):
        self.hand.append(card)

    def select_card(self, idx: int):
        """
        Seleccionas la carta con el índice que se le pase, la pasa al gameManager, la juega y la borra de la mano.
        :param idx: (int) Índice de la carta.
        """
        return self.hand[idx]

    def delete_card(self, card: DevelopmentCard):
        """
        Borra la carta con la ID que se le pase.
        :param id: (int) Número indicativo de la carta.
        """
        self.hand = list(filter(lambda c1: c1 != card, self.hand))

    def find_card_by_effect(self, effect: int):
        """
        Busca una carta en la mano del jugador por su efecto.
        :param effect: (int) Efecto de la carta.
        :return: List(DevelopmentCard) Carta con el efecto buscado.
        """
        return list(filter(lambda c1: c1.effect == effect, self.hand))
