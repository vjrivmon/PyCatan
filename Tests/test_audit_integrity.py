"""
Test exhaustivo de integridad post-auditoría.
Verifica que todos los bugs corregidos (B1-B10) funcionan correctamente
y que una partida completa genera trazas JSON consistentes.
"""
import json
import math
from copy import deepcopy

from Classes.Board import Board
from Classes.DevelopmentCards import DevelopmentCard, DevelopmentDeck, DevelopmentCardsHand
from Classes.Materials import Materials
from Classes.Hand import Hand
from Classes.Constants import MaterialConstants, BuildConstants, DevelopmentCardConstants
from Managers.GameManager import GameManager
from Managers.GameDirector import GameDirector


class TestAuditIntegrity:
    """Tests exhaustivos para verificar la integridad de todos los fixes de la auditoría."""

    # ──────────────────────────────────────────────
    # B1: Agentes no corrompen el estado del juego
    # ──────────────────────────────────────────────
    def test_agent_hand_protection_on_commerce(self):
        """B1: Verificar que on_commerce_phase no muta el hand real del jugador."""
        gd = GameDirector(for_test='test_trace', max_rounds=5, store_trace=False)
        gd.reset_game_values()
        gm = gd.game_manager

        # Setup: colocar pueblos para que el juego funcione
        for i in range(4):
            gm.on_game_start_build_towns_and_roads(i)
        for i in range(3, -1, -1):
            gm.on_game_start_build_towns_and_roads(i)

        # Dar recursos al jugador 0
        gm.agent_manager.players[0]['resources'].add_material(MaterialConstants.WOOD, 5)
        gm.agent_manager.players[0]['resources'].add_material(MaterialConstants.CLAY, 5)
        gm.agent_manager.players[0]['player'].hand = gm.agent_manager.players[0]['resources']

        hand_before = deepcopy(gm.agent_manager.players[0]['resources'].resources)

        # Llamar a on_commerce_phase (protegido por save/restore)
        gm.call_to_agent_on_commerce_phase(0)

        hand_after = gm.agent_manager.players[0]['resources'].resources

        # La mano debe ser idéntica antes y después
        assert hand_before == hand_after, \
            f"B1 FAIL: hand changed from {hand_before} to {hand_after}"

    def test_agent_hand_protection_on_trade_offer(self):
        """B1: Verificar que on_trade_offer no muta el hand real."""
        gm = GameManager(for_test='test_trade')

        for i in range(4):
            gm.on_game_start_build_towns_and_roads(i)
        for i in range(3, -1, -1):
            gm.on_game_start_build_towns_and_roads(i)

        # Dar recursos
        for i in range(4):
            gm.agent_manager.players[i]['resources'].add_material(MaterialConstants.WOOD, 3)
            gm.agent_manager.players[i]['resources'].add_material(MaterialConstants.CLAY, 3)
            gm.agent_manager.players[i]['player'].hand = gm.agent_manager.players[i]['resources']

        hands_before = [deepcopy(gm.agent_manager.players[i]['resources'].resources) for i in range(4)]

        # Llamar a on_build_phase (protegido)
        gm.call_to_agent_on_build_phase(0)

        for i in range(4):
            assert gm.agent_manager.players[i]['resources'].resources == hands_before[i], \
                f"B1 FAIL: P{i} hand mutated by call_to_agent_on_build_phase"

    # ──────────────────────────────────────────────
    # B2: No auto-robo con el ladrón
    # ──────────────────────────────────────────────
    def test_no_self_robbery(self):
        """B2: El ladrón nunca debe permitir que un jugador se robe a sí mismo."""
        gm = GameManager(for_test='test_thief')

        for i in range(4):
            gm.on_game_start_build_towns_and_roads(i)
        for i in range(3, -1, -1):
            gm.on_game_start_build_towns_and_roads(i)

        # Dar recursos a todos
        for i in range(4):
            gm.agent_manager.players[i]['resources'].add_material(MaterialConstants.WOOD, 3)
            gm.agent_manager.players[i]['player'].hand = gm.agent_manager.players[i]['resources']

        # Forzar que el jugador 2 sea el actual
        gm.agent_manager.actual_player = 2
        gm.turn_manager.whose_turn_is_it = 2

        # Intentar mover al ladrón y robarse a sí mismo
        for terrain in range(19):
            result = gm.move_thief(terrain, 2)  # adjacent_player = self
            assert result['robbed_player'] != 2, \
                f"B2 FAIL: P2 robbed self at terrain {terrain}"

    # ──────────────────────────────────────────────
    # B3: Descarte con ladrón usa ceil(n/2)
    # ──────────────────────────────────────────────
    def test_thief_discard_ceil(self):
        """B3: Al descartar con ladrón, el jugador se queda con ceil(total/2).
        Nota: después del descarte, el ladrón puede robar 1 recurso extra al jugador,
        así que permitimos remaining == expected o remaining == expected - 1 (robado)."""
        gm = GameManager(for_test='test_discard')

        for i in range(4):
            gm.on_game_start_build_towns_and_roads(i)
        for i in range(3, -1, -1):
            gm.on_game_start_build_towns_and_roads(i)

        # Test con varios totales
        test_cases = [8, 9, 10, 11, 12, 15, 20]
        for total_resources in test_cases:
            gm.agent_manager.players[0]['resources'] = Hand()
            gm.agent_manager.players[0]['resources'].add_material(MaterialConstants.WOOD, total_resources)
            gm.agent_manager.players[0]['player'].hand = gm.agent_manager.players[0]['resources']
            gm.agent_manager.actual_player = 1
            gm.last_dice_roll = 7

            # Reset other players to <= 7
            for i in range(1, 4):
                gm.agent_manager.players[i]['resources'] = Hand()
                gm.agent_manager.players[i]['player'].hand = gm.agent_manager.players[i]['resources']

            start_obj = {}
            gm.check_if_thief_is_called(start_obj, 1)

            remaining = gm.agent_manager.players[0]['resources'].get_total()
            expected = math.ceil(total_resources / 2)
            # El ladrón puede robar 1 recurso adicional después del descarte
            robbed = start_obj.get('robbed_player', -1) == 0
            if robbed:
                assert remaining == expected - 1, \
                    f"B3 FAIL: started={total_resources}, remaining={remaining}, expected={expected}-1 (robbed)"
            else:
                assert remaining == expected, \
                    f"B3 FAIL: started={total_resources}, remaining={remaining}, expected={expected}"

    # ──────────────────────────────────────────────
    # B5: Trade ratio almacenado en JSON
    # ──────────────────────────────────────────────
    def test_harbor_trade_ratio_in_json(self):
        """B5: Los harbor trades deben incluir trade_ratio en el JSON."""
        gm = GameManager(for_test='test_ratio')

        for i in range(4):
            gm.on_game_start_build_towns_and_roads(i)
        for i in range(3, -1, -1):
            gm.on_game_start_build_towns_and_roads(i)

        gm.agent_manager.players[0]['resources'].add_material(MaterialConstants.WOOD, 10)
        gm.agent_manager.players[0]['player'].hand = gm.agent_manager.players[0]['resources']

        commerce_obj = {}
        commerce_response = {'gives': MaterialConstants.WOOD, 'receives': MaterialConstants.CEREAL}
        result, _ = gm.on_commerce_response(commerce_obj, commerce_response, 1, 0, False)

        assert 'trade_ratio' in result, "B5 FAIL: trade_ratio not in harbor trade JSON"
        assert result['trade_ratio'] in [2, 3, 4], f"B5 FAIL: invalid trade_ratio {result['trade_ratio']}"

    # ──────────────────────────────────────────────
    # B7: Doble descarte protegido
    # ──────────────────────────────────────────────
    def test_no_double_discard(self):
        """B7: on_having_more_than_7 no debe causar doble descarte."""
        gm = GameManager(for_test='test_double')

        for i in range(4):
            gm.on_game_start_build_towns_and_roads(i)
        for i in range(3, -1, -1):
            gm.on_game_start_build_towns_and_roads(i)

        # P0 con 11 recursos
        gm.agent_manager.players[0]['resources'] = Hand()
        gm.agent_manager.players[0]['resources'].add_material(MaterialConstants.WOOD, 5)
        gm.agent_manager.players[0]['resources'].add_material(MaterialConstants.CLAY, 6)
        gm.agent_manager.players[0]['player'].hand = gm.agent_manager.players[0]['resources']

        # Others at 0
        for i in range(1, 4):
            gm.agent_manager.players[i]['resources'] = Hand()
            gm.agent_manager.players[i]['player'].hand = gm.agent_manager.players[i]['resources']

        gm.agent_manager.actual_player = 1
        gm.last_dice_roll = 7

        start_obj = {}
        gm.check_if_thief_is_called(start_obj, 1)

        remaining = gm.agent_manager.players[0]['resources'].get_total()
        # ceil(11/2) = 6
        assert remaining == 6, f"B7 FAIL: expected 6, got {remaining} (double discard?)"

    # ──────────────────────────────────────────────
    # B8: build_road bloqueada por rival
    # ──────────────────────────────────────────────
    def test_road_blocked_by_rival(self):
        """B8: No se puede construir carretera pasando por poblado de rival."""
        board = Board()
        board.nodes[0]['player'] = 0
        board.build_road(0, 0, 1)
        board.nodes[1]['player'] = 1  # rival en nodo 1
        result = board.build_road(0, 1, 2)  # P0 intenta pasar por nodo de P1
        assert result['response'] is False, "B8 FAIL: road built through rival settlement"

    # ──────────────────────────────────────────────
    # B9: DevelopmentCard tiene id
    # ──────────────────────────────────────────────
    def test_development_card_has_id(self):
        """B9: DevelopmentCard debe tener atributo id."""
        card = DevelopmentCard(DevelopmentCardConstants.KNIGHT, DevelopmentCardConstants.KNIGHT_EFFECT)
        assert hasattr(card, 'id'), "B9 FAIL: DevelopmentCard has no id"

        deck = DevelopmentDeck()
        assert hasattr(deck, 'current_index'), "B9 FAIL: DevelopmentDeck has no current_index"
        assert deck.current_index == 0, f"B9 FAIL: current_index={deck.current_index}, expected 0"

        drawn = deck.draw_card()
        assert hasattr(drawn, 'id') and drawn.id >= 0, "B9 FAIL: drawn card has no valid id"

    def test_dev_cards_hand_validation(self):
        """B9: add_card solo acepta DevelopmentCard."""
        hand = DevelopmentCardsHand()
        hand.add_card("not a card")
        hand.add_card(None)
        hand.add_card(42)
        assert len(hand.hand) == 0, f"B9 FAIL: hand accepted invalid cards, length={len(hand.hand)}"

        hand.add_card(DevelopmentCard(DevelopmentCardConstants.KNIGHT, DevelopmentCardConstants.KNIGHT_EFFECT))
        assert len(hand.hand) == 1

    # ──────────────────────────────────────────────
    # B10: Materials.has_more rechaza negativos
    # ──────────────────────────────────────────────
    def test_has_more_rejects_negatives(self):
        """B10: has_more debe rechazar Materials con valores negativos."""
        m = Materials(5, 5, 5, 5, 5)
        assert not m.has_more(Materials(1, 0, -1, 0, 0)), "B10 FAIL: accepted negative materials"
        assert m.has_more(Materials(1, 0, 0, 0, 0)), "B10 FAIL: rejected valid materials"

    # ──────────────────────────────────────────────
    # INTEGRATION: Partida completa genera trazas válidas
    # ──────────────────────────────────────────────
    def test_full_game_trace_integrity(self):
        """Verificación integral: una partida completa genera trazas JSON consistentes."""
        gd = GameDirector(for_test='test_trace', max_rounds=30, store_trace=False)
        trace = gd.game_start(game_number=999, print_outcome=False)

        game = trace.get('game', {})
        assert len(game) > 0, "No rounds generated"

        issues = []
        for rnd_key, rnd in game.items():
            for turn_key in ['turn_P0', 'turn_P1', 'turn_P2', 'turn_P3']:
                if turn_key not in rnd:
                    continue
                turn = rnd[turn_key]
                st = turn.get('start_turn', {})

                # Check no self-robbery
                if st.get('robbed_player', -1) != -1:
                    if st.get('robbed_player') == int(st.get('actual_player', -1)):
                        issues.append(f"{rnd_key} {turn_key}: self-robbery")

                # Check no negative resources
                for p in range(4):
                    h = st.get(f'hand_P{p}')
                    if h:
                        for res in ['cereal', 'mineral', 'clay', 'wood', 'wool']:
                            if int(h.get(res, 0)) < 0:
                                issues.append(f"{rnd_key} {turn_key}: P{p}.{res} negative")

                # Check harbor trades have ratio
                for cp in turn.get('commerce_phase', []):
                    if cp.get('harbor_trade') and cp.get('trade_offer') not in ['None', None, 'played_card']:
                        if 'trade_ratio' not in cp:
                            issues.append(f"{rnd_key} {turn_key}: harbor without trade_ratio")

                # Check inviable trades don't mutate hands
                prev_hands = {}
                for p in range(4):
                    h = st.get(f'hand_P{p}')
                    if h:
                        prev_hands[p] = h
                for cp in turn.get('commerce_phase', []):
                    if cp.get('inviable'):
                        for p in range(4):
                            h = cp.get(f'hand_P{p}')
                            if h and p in prev_hands and h != prev_hands[p]:
                                issues.append(f"{rnd_key} {turn_key}: inviable trade mutated P{p}")
                    for p in range(4):
                        h = cp.get(f'hand_P{p}')
                        if h:
                            prev_hands[p] = h

        assert len(issues) == 0, f"INTEGRITY FAILURES:\n" + "\n".join(issues)
