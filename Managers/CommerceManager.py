class CommerceManager:
    """
     Clase que se encarga del comercio entre jugadores.
    """
    offerReceiver = int
    maxCounterOffers = 2
    maxOfferPropositions = 2

    def __init__(self):
        return

    def trade_without_harbor(self, player_hand, gives, receives):
        """
        Sustituye 4 del material pasado por 1 del deseado.
        :param player_hand: (Hand()) materiales que tiene el jugador.
        :param gives: (int) ID del material que quiere cambiar con el puerto.
        :param receives: (int) ID del material que quiere recibir a cambio.
        :return: bool
        """
        if player_hand.get_from_id(gives) >= 4:
            player_hand.remove_material(gives, 4)
            player_hand.add_material(receives, 1)
            return player_hand
        else:
            return False

    def trade_through_harbor(self, player_hand, gives, receives):
        """
        Sustituye 3 del material pasado por 1 del deseado.
        :param player_hand: (Hand()) materiales que tiene el jugador.
        :param gives: (int) ID del material que quiere cambiar con el puerto.
        :param receives: (int) ID del material que quiere recibir a cambio.
        :return: bool
        """
        if player_hand.get_from_id(gives) >= 3:
            player_hand.remove_material(gives, 3)
            player_hand.add_material(receives, 1)
            return player_hand
        else:
            return False

    def trade_through_special_harbor(self, player_hand, gives, receives):
        """
        Sustituye 2 del material pasado por 1 del deseado.
        :param player_hand: (Hand()) materiales que tiene el jugador.
        :param gives: (int) ID del material que quiere cambiar con el puerto.
        :param receives: (int) ID del material que quiere recibir a cambio.
        :return: bool
        """
        if player_hand.get_from_id(gives) >= 2:
            player_hand.remove_material(gives, 2)
            player_hand.add_material(receives, 1)
            return player_hand
        else:
            return False
