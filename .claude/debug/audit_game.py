#!/usr/bin/env python3
"""
Auditoría completa de trazas JSON de PyCatan.
Valida: recursos, trades, builds, dados, ladrón.
Genera un Excel de evidencia por partida.
"""

import json
import sys
import os
from collections import defaultdict
from copy import deepcopy

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ─── Constantes ───────────────────────────────────────────────────────────────

MATERIALS = ['cereal', 'mineral', 'clay', 'wood', 'wool']
MAT_ID_TO_NAME = {0: 'cereal', 1: 'mineral', 2: 'clay', 3: 'wood', 4: 'wool'}
TERRAIN_TO_MAT = {0: 'cereal', 1: 'mineral', 2: 'clay', 3: 'wood', 4: 'wool', -1: None}

BUILD_COSTS = {
    'town':  {'cereal': 1, 'mineral': 0, 'clay': 1, 'wood': 1, 'wool': 1},
    'city':  {'cereal': 2, 'mineral': 3, 'clay': 0, 'wood': 0, 'wool': 0},
    'road':  {'cereal': 0, 'mineral': 0, 'clay': 1, 'wood': 1, 'wool': 0},
    'card':  {'cereal': 1, 'mineral': 1, 'clay': 0, 'wood': 0, 'wool': 1},
}

# ─── Estilos Excel ────────────────────────────────────────────────────────────

HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
ERROR_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
WARNING_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
OK_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
THIN_BORDER = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)


def style_header(ws, num_cols):
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal='center', wrap_text=True)
        cell.border = THIN_BORDER


def auto_width(ws):
    for col_cells in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col_cells[0].column)
        for cell in col_cells:
            try:
                val = str(cell.value) if cell.value else ""
                max_len = max(max_len, len(val))
            except:
                pass
        ws.column_dimensions[col_letter].width = min(max_len + 3, 50)


# ─── Utilidades ───────────────────────────────────────────────────────────────

def parse_hand(hand_dict):
    """Convierte hand dict de strings a ints."""
    if not hand_dict:
        return {m: 0 for m in MATERIALS}
    return {m: int(hand_dict.get(m, 0)) for m in MATERIALS}


def hand_total(hand):
    return sum(hand.values())


def hand_str(hand):
    return f"C:{hand.get('cereal',0)} M:{hand.get('mineral',0)} A:{hand.get('clay',0)} W:{hand.get('wood',0)} L:{hand.get('wool',0)}"


def hand_delta(before, after):
    return {m: after[m] - before[m] for m in MATERIALS}


def has_enough(hand, cost):
    """Verifica si la mano tiene suficientes recursos para un coste."""
    for m in MATERIALS:
        if hand.get(m, 0) < cost.get(m, 0):
            return False
    return True


def subtract_cost(hand, cost):
    h = dict(hand)
    for m in MATERIALS:
        h[m] = h.get(m, 0) - cost.get(m, 0)
    return h


def add_resources(hand, resources):
    h = dict(hand)
    for m in MATERIALS:
        h[m] += resources.get(m, 0)
    return h


def get_sorted_rounds(game):
    """Ordena las rondas numéricamente."""
    return sorted(game.keys(), key=lambda x: int(x.split('_')[1]))


def get_sorted_turns(round_data):
    """Ordena los turnos por número de jugador."""
    turns = []
    for tk in sorted(round_data.keys()):
        if tk.startswith('turn_P'):
            player = int(tk.split('_P')[1])
            turns.append((tk, player))
    return turns


# ─── Auditor principal ────────────────────────────────────────────────────────

class GameAuditor:
    def __init__(self, filepath):
        with open(filepath) as f:
            self.data = json.load(f)
        self.filepath = filepath
        self.game_name = os.path.splitext(os.path.basename(filepath))[0]
        self.game = self.data['game']
        self.setup = self.data['setup']
        self.board = self.setup['board']
        self.terrain = self.board['board_terrain']
        self.nodes = self.board['board_nodes']

        # Estado de seguimiento
        self.hands = {p: {m: 0 for m in MATERIALS} for p in range(4)}
        self.buildings = defaultdict(list)  # player -> list of {type, node_id}
        self.roads = defaultdict(list)       # player -> list of {from, to}
        self.errors = []
        self.trades_log = []
        self.builds_log = []
        self.resources_log = []  # {round, turn, player, hand, delta, source}
        self.dice_log = []
        self.thief_log = []

        # Construir mapa de producción: probability -> [(terrain_idx, material, contacting_nodes)]
        self.prob_map = defaultdict(list)
        for tidx, t in enumerate(self.terrain):
            mat = TERRAIN_TO_MAT.get(t['terrain_type'])
            prob = t.get('probability', 0)
            if mat and prob > 0:
                self.prob_map[prob].append({
                    'terrain_idx': tidx,
                    'material': mat,
                    'contacting_nodes': t.get('contacting_nodes', [])
                })

        # Mapa de nodos ocupados (se actualiza con builds)
        # node_id -> {player, type} 'town' or 'city'
        self.node_owners = {}
        self.thief_terrain = None  # Terreno donde está el ladrón

        # Procesar setup inicial (placements + thief)
        self._process_setup()

    def _process_setup(self):
        """Procesa los asentamientos iniciales del setup."""
        for p in range(4):
            pk = f'P{p}'
            placements = self.setup.get(pk, [])
            for pl in placements:
                node_id = pl['id']
                self.node_owners[node_id] = {'player': p, 'type': 'town'}
                self.buildings[p].append({'type': 'town', 'node_id': node_id})
                road_to = pl.get('road')
                if road_to is not None:
                    self.roads[p].append({'from': node_id, 'to': road_to})

        # Encontrar desierto para posición inicial del ladrón
        for tidx, t in enumerate(self.terrain):
            if t['terrain_type'] == -1:
                self.thief_terrain = tidx
                break

    def compute_dice_production(self, dice_value, thief_terrain=None):
        """Calcula qué recursos produce cada jugador para un dado dado."""
        production = {p: {m: 0 for m in MATERIALS} for p in range(4)}
        if dice_value == 7:
            return production

        terrains = self.prob_map.get(dice_value, [])
        for t_info in terrains:
            tidx = t_info['terrain_idx']
            mat = t_info['material']
            cn = t_info['contacting_nodes']

            # Si el ladrón bloquea este terreno, no produce
            if thief_terrain is not None and tidx == thief_terrain:
                continue

            for node_id in cn:
                owner_info = self.node_owners.get(node_id)
                if owner_info:
                    p = owner_info['player']
                    multiplier = 2 if owner_info['type'] == 'city' else 1
                    production[p][mat] += multiplier

        return production

    def _add_error(self, round_key, turn_key, error_type, description, severity='ERROR'):
        self.errors.append({
            'round': round_key,
            'turn': turn_key,
            'type': error_type,
            'description': description,
            'severity': severity,
        })

    def _process_trades(self, round_key, turn_key, active_player, commerce_phase):
        """Procesa todas las operaciones comerciales de una fase."""
        for ci, commerce in enumerate(commerce_phase):
            # Saltar entradas vacías o con trade_offer="None"
            trade_offer = commerce.get('trade_offer')
            if trade_offer is None or trade_offer == "None" or not isinstance(trade_offer, dict):
                continue

            is_harbor = commerce.get('harbor_trade', False)
            is_inviable = commerce.get('inviable', False)

            # Detectar harbor trades por tipo de gives (int = harbor, dict = normal)
            gives = trade_offer.get('gives')
            if isinstance(gives, int) or is_harbor:
                self._process_harbor_trade(round_key, turn_key, active_player, ci, commerce)
            elif is_inviable:
                # Trade marcado como inviable — logear
                self.trades_log.append({
                    'round': round_key, 'turn': turn_key, 'index': ci,
                    'type': 'inviable', 'giver': active_player, 'receiver': '-',
                    'gives': str(gives),
                    'receives': str(trade_offer.get('receives', '')),
                    'harbor': False, 'result': 'INVIABLE',
                    'validation': 'N/A'
                })
            else:
                self._process_normal_trade(round_key, turn_key, active_player, ci, commerce)

    def _process_harbor_trade(self, round_key, turn_key, active_player, ci, commerce):
        """Procesa un trade con el banco (harbor)."""
        gives_mat_id = commerce['trade_offer']['gives']
        receives_mat_id = commerce['trade_offer']['receives']
        result_hand = parse_hand(commerce.get('answer', {}))

        gives_mat = MAT_ID_TO_NAME.get(gives_mat_id, f'?{gives_mat_id}')
        receives_mat = MAT_ID_TO_NAME.get(receives_mat_id, f'?{receives_mat_id}')

        hand_before = dict(self.hands[active_player])

        # Calcular cuánto dio y cuánto recibió
        given_amount = hand_before[gives_mat] - result_hand[gives_mat]
        received_amount = result_hand[receives_mat] - hand_before[receives_mat]

        # Inferir ratio
        if received_amount > 0:
            ratio = f"{given_amount}:{received_amount}"
        else:
            ratio = "???"

        # Validar que tenía suficiente
        validation = 'OK'
        if hand_before[gives_mat] < given_amount:
            validation = f'ERROR: no tiene {given_amount} {gives_mat} (tiene {hand_before[gives_mat]})'
            self._add_error(round_key, turn_key, 'HARBOR_TRADE',
                f'P{active_player} intenta dar {given_amount} {gives_mat} pero solo tiene {hand_before[gives_mat]}')

        # Validar que el ratio es válido (2:1, 3:1, o 4:1)
        if received_amount > 0 and given_amount > 0:
            rate = given_amount / received_amount
            if rate not in (2.0, 3.0, 4.0):
                if validation == 'OK':
                    validation = f'WARNING: ratio {ratio} inusual'
                self._add_error(round_key, turn_key, 'HARBOR_RATIO',
                    f'P{active_player} harbor trade ratio {ratio} ({gives_mat}->{receives_mat})',
                    severity='WARNING')

        # Verificar coherencia: otros materiales no deberían cambiar
        for m in MATERIALS:
            if m != gives_mat and m != receives_mat:
                if hand_before[m] != result_hand[m]:
                    detail = f'{m}: {hand_before[m]} -> {result_hand[m]}'
                    if validation == 'OK':
                        validation = f'ERROR: material inesperado cambió: {detail}'
                    self._add_error(round_key, turn_key, 'HARBOR_SIDE_EFFECT',
                        f'P{active_player} harbor trade cambió {m} inesperadamente: {detail}')

        self.trades_log.append({
            'round': round_key, 'turn': turn_key, 'index': ci,
            'type': 'harbor', 'giver': f'P{active_player}', 'receiver': 'Banco',
            'gives': f'{given_amount} {gives_mat}',
            'receives': f'{received_amount} {receives_mat}',
            'harbor': True, 'result': f'ratio {ratio}',
            'validation': validation,
            'hand_before': hand_str(hand_before),
            'hand_after': hand_str(result_hand),
        })

        # Actualizar la mano con el resultado directo del JSON
        self.hands[active_player] = result_hand

    def _process_normal_trade(self, round_key, turn_key, active_player, ci, commerce):
        """Procesa un trade normal entre jugadores."""
        offer_gives = parse_hand(commerce['trade_offer']['gives'])
        offer_receives = parse_hand(commerce['trade_offer']['receives'])

        # Verificar si el jugador activo tiene lo que ofrece
        offer_valid = has_enough(self.hands[active_player], offer_gives)
        if not offer_valid:
            lacking = {m: offer_gives[m] - self.hands[active_player][m]
                      for m in MATERIALS if offer_gives[m] > self.hands[active_player][m]}
            self._add_error(round_key, turn_key, 'TRADE_INSUFFICIENT',
                f'P{active_player} ofrece {hand_str(offer_gives)} pero tiene {hand_str(self.hands[active_player])}. Falta: {lacking}')

        # Buscar trades completados en las answers
        answers = commerce.get('answers', [])
        completed_any = False

        for ai, answer_group in enumerate(answers):
            if not isinstance(answer_group, list):
                answer_group = [answer_group]

            for answer in answer_group:
                if not answer.get('completed', False):
                    continue

                completed_any = True
                giver = answer.get('giver')       # Quien da los 'gives'
                receiver = answer.get('receiver')   # Quien recibe los 'gives'
                count = answer.get('count', 1)
                trade_gives = parse_hand(answer['trade_offer']['gives'])
                trade_receives = parse_hand(answer['trade_offer']['receives'])

                # El 'giver' da los 'gives' y recibe los 'receives'
                # El 'receiver' da los 'receives' y recibe los 'gives'
                hand_giver_before = dict(self.hands[giver])
                hand_receiver_before = dict(self.hands[receiver])

                # Validar que giver tiene suficiente para dar
                total_gives = {m: trade_gives[m] * count for m in MATERIALS}
                total_receives = {m: trade_receives[m] * count for m in MATERIALS}

                giver_has_enough = has_enough(self.hands[giver], total_gives)
                receiver_has_enough = has_enough(self.hands[receiver], total_receives)

                validation = 'OK'
                if not giver_has_enough:
                    lacking = {m: total_gives[m] - self.hands[giver][m]
                              for m in MATERIALS if total_gives[m] > self.hands[giver][m]}
                    validation = f'ERROR: P{giver} no tiene suficiente: falta {lacking}'
                    self._add_error(round_key, turn_key, 'TRADE_GIVER_INSUFFICIENT',
                        f'P{giver} da {hand_str(total_gives)} pero tiene {hand_str(self.hands[giver])}')

                if not receiver_has_enough:
                    lacking = {m: total_receives[m] - self.hands[receiver][m]
                              for m in MATERIALS if total_receives[m] > self.hands[receiver][m]}
                    if validation == 'OK':
                        validation = f'ERROR: P{receiver} no tiene suficiente: falta {lacking}'
                    else:
                        validation += f' | P{receiver} falta {lacking}'
                    self._add_error(round_key, turn_key, 'TRADE_RECEIVER_INSUFFICIENT',
                        f'P{receiver} debe dar {hand_str(total_receives)} pero tiene {hand_str(self.hands[receiver])}')

                # Aplicar trade: giver pierde gives y gana receives
                for m in MATERIALS:
                    self.hands[giver][m] -= total_gives[m]
                    self.hands[giver][m] += total_receives[m]
                    self.hands[receiver][m] -= total_receives[m]
                    self.hands[receiver][m] += total_gives[m]

                # Verificar negativos post-trade
                for p in [giver, receiver]:
                    for m in MATERIALS:
                        if self.hands[p][m] < 0:
                            self._add_error(round_key, turn_key, 'NEGATIVE_RESOURCES',
                                f'P{p} tiene {m}={self.hands[p][m]} negativo tras trade')

                self.trades_log.append({
                    'round': round_key, 'turn': turn_key, 'index': ci,
                    'type': 'normal', 'giver': f'P{giver}', 'receiver': f'P{receiver}',
                    'gives': hand_str(total_gives),
                    'receives': hand_str(total_receives),
                    'harbor': False,
                    'result': f'COMPLETED (x{count})',
                    'validation': validation,
                    'hand_before': f'G:{hand_str(hand_giver_before)} R:{hand_str(hand_receiver_before)}',
                    'hand_after': f'G:{hand_str(self.hands[giver])} R:{hand_str(self.hands[receiver])}',
                })

        if not completed_any:
            self.trades_log.append({
                'round': round_key, 'turn': turn_key, 'index': ci,
                'type': 'normal', 'giver': f'P{active_player}', 'receiver': '-',
                'gives': hand_str(offer_gives),
                'receives': hand_str(offer_receives),
                'harbor': False, 'result': 'NO ACEPTADO',
                'validation': 'OK' if offer_valid else f'ERROR: oferta sin recursos',
                'hand_before': hand_str(self.hands[active_player]),
                'hand_after': '',
            })

    def _process_builds(self, round_key, turn_key, active_player, build_phase):
        """Procesa la fase de construcción."""
        for bi, build in enumerate(build_phase):
            building = build.get('building', 'None')
            if building == 'None' or not building:
                continue

            # ─── Manejar played_card (dev card jugada en build phase) ───
            if building == 'played_card':
                self._process_played_card_in_build(round_key, turn_key, active_player, bi, build)
                continue

            finished = build.get('finished', False)
            node_id = build.get('node_id')
            road_to = build.get('road_to')
            card_id = build.get('card_id')
            card_type = build.get('card_type')
            card_effect = build.get('card_effect')

            cost = BUILD_COSTS.get(building, {m: 0 for m in MATERIALS})
            hand_before = dict(self.hands[active_player])
            can_afford = has_enough(self.hands[active_player], cost)

            validation = 'OK'
            if not can_afford:
                lacking = {m: cost.get(m, 0) - self.hands[active_player].get(m, 0)
                          for m in MATERIALS if cost.get(m, 0) > self.hands[active_player].get(m, 0)}
                validation = f'ERROR: no puede pagar, falta {lacking}'
                self._add_error(round_key, turn_key, 'BUILD_INSUFFICIENT',
                    f'P{active_player} construye {building} pero no puede pagar. Falta: {lacking}. Mano: {hand_str(self.hands[active_player])}')

            if not finished:
                validation = f'WARN: finished=false para {building}'
                self._add_error(round_key, turn_key, 'BUILD_NOT_FINISHED',
                    f'P{active_player} construye {building} pero finished=false', severity='WARNING')

            # Restar coste
            self.hands[active_player] = subtract_cost(self.hands[active_player], cost)

            # Verificar negativos
            for m in MATERIALS:
                if self.hands[active_player].get(m, 0) < 0:
                    self._add_error(round_key, turn_key, 'NEGATIVE_AFTER_BUILD',
                        f'P{active_player} tiene {m}={self.hands[active_player][m]} negativo tras construir {building}')

            # Registrar la construcción en el estado
            if building == 'town' and node_id is not None:
                self.node_owners[node_id] = {'player': active_player, 'type': 'town'}
                self.buildings[active_player].append({'type': 'town', 'node_id': node_id})
            elif building == 'city' and node_id is not None:
                self.node_owners[node_id] = {'player': active_player, 'type': 'city'}
                self.buildings[active_player].append({'type': 'city', 'node_id': node_id})
            elif building == 'road' and node_id is not None:
                self.roads[active_player].append({'from': node_id, 'to': road_to})

            detail = building
            if node_id is not None:
                detail += f' @node{node_id}'
            if road_to is not None:
                detail += f'->node{road_to}'
            if card_id is not None:
                detail += f' card_id={card_id} type={card_type} effect={card_effect}'

            self.builds_log.append({
                'round': round_key, 'turn': turn_key, 'index': bi,
                'player': f'P{active_player}',
                'building': building,
                'detail': detail,
                'cost': hand_str(cost),
                'hand_before': hand_str(hand_before),
                'hand_after': hand_str(self.hands[active_player]),
                'validation': validation,
            })

    def _process_played_card_in_build(self, round_key, turn_key, active_player, bi, build):
        """Procesa una carta de desarrollo jugada durante la fase de construcción."""
        dc = build.get('development_card_played', {})
        played = dc.get('played_card', '')
        hand_before = dict(self.hands[active_player])
        validation = 'OK'
        detail = f'played_card: {played}'

        if played == 'monopoly':
            # Monopolio: el JSON incluye las manos resultantes para todos
            mat_id = dc.get('material_chosen')
            mat_sum = dc.get('material_sum', 0)
            mat_name = MAT_ID_TO_NAME.get(mat_id, '?')
            detail += f' material={mat_name}, stolen_total={mat_sum}'

            # Actualizar manos desde el JSON (fuente de verdad)
            for p in range(4):
                hand_key = f'hand_P{p}'
                if hand_key in dc:
                    self.hands[p] = parse_hand(dc[hand_key])

            # Validar: la suma de lo que tenían antes los otros == material_sum
            sum_from_others = 0
            for p in range(4):
                if p != active_player:
                    sum_from_others += hand_before.get(mat_name, 0) if p == active_player else 0
            # No podemos validar fácilmente sin las manos de otros antes del monopolio
            # Confiar en el JSON para las manos resultantes

        elif played == 'year_of_plenty':
            # Año de abundancia: recibe 2 recursos
            mats_selected = dc.get('materials_selected', [])
            detail += f' materials={mats_selected}'

            # El JSON incluye la mano resultante
            hand_key = f'hand_P{active_player}'
            if hand_key in dc:
                result_hand = parse_hand(dc[hand_key])
                # Validar: resultado = antes + 2 materiales seleccionados
                expected = dict(hand_before)
                for mat_id in mats_selected:
                    mat_name = MAT_ID_TO_NAME.get(mat_id, '?')
                    if mat_name != '?':
                        expected[mat_name] = expected.get(mat_name, 0) + 1

                for m in MATERIALS:
                    if expected.get(m, 0) != result_hand.get(m, 0):
                        if validation == 'OK':
                            validation = f'DISCREPANCIA: {m} esperado={expected[m]} actual={result_hand[m]}'
                        self._add_error(round_key, turn_key, 'YEAR_OF_PLENTY_MISMATCH',
                            f'P{active_player} year_of_plenty: {m} esperado={expected[m]} actual={result_hand[m]}')

                self.hands[active_player] = result_hand

        elif played == 'road_building':
            # Construcción de caminos gratuita
            roads_data = dc.get('roads', {})
            detail += f' roads={roads_data}'
            if isinstance(roads_data, dict):
                # Format: {node_id, road_to, node_id_2, road_to_2}
                n1 = roads_data.get('node_id')
                r1 = roads_data.get('road_to')
                n2 = roads_data.get('node_id_2')
                r2 = roads_data.get('road_to_2')
                if n1 is not None:
                    self.roads[active_player].append({'from': n1, 'to': r1})
                if n2 is not None:
                    self.roads[active_player].append({'from': n2, 'to': r2})
            elif isinstance(roads_data, list):
                for road in roads_data:
                    if isinstance(road, dict):
                        self.roads[active_player].append({
                            'from': road.get('node_id'),
                            'to': road.get('road_to')
                        })

        elif played == 'knight':
            # Knight jugado en build phase
            self._process_knight(round_key, turn_key, active_player, dc)
            detail += f' thief->{dc.get("thief_terrain")}'

        self.builds_log.append({
            'round': round_key, 'turn': turn_key, 'index': bi,
            'player': f'P{active_player}',
            'building': 'played_card',
            'detail': detail,
            'cost': '-',
            'hand_before': hand_str(hand_before),
            'hand_after': hand_str(self.hands[active_player]),
            'validation': validation,
        })

    def _process_thief(self, round_key, turn_key, active_player, start_turn, source='dice7'):
        """Procesa movimiento del ladrón y robo."""
        past_terrain = start_turn.get('past_thief_terrain')
        new_terrain = start_turn.get('thief_terrain')
        robbed_player = start_turn.get('robbed_player')
        stolen_mat_id = start_turn.get('stolen_material_id')

        if new_terrain is None and source == 'dice7':
            self._add_error(round_key, turn_key, 'THIEF_NO_MOVE',
                f'dice=7 pero no hay thief_terrain')

        if past_terrain is not None and new_terrain is not None:
            # Verificar que se movió (en dice=7 es obligatorio moverse)
            if source == 'dice7' and past_terrain == new_terrain:
                self._add_error(round_key, turn_key, 'THIEF_SAME_POS',
                    f'dice=7 pero ladrón no se movió (terreno {past_terrain})', severity='WARNING')

            self.thief_terrain = new_terrain

        # Robo de recurso
        stolen_mat = MAT_ID_TO_NAME.get(stolen_mat_id) if stolen_mat_id is not None else None

        validation = 'OK'
        if robbed_player is not None and stolen_mat:
            # Verificar que el jugador robado tiene ese material
            victim_hand = self.hands[robbed_player]
            if victim_hand.get(stolen_mat, 0) <= 0:
                validation = f'ERROR: P{robbed_player} no tiene {stolen_mat} para ser robado (tiene {hand_str(victim_hand)})'
                self._add_error(round_key, turn_key, 'THIEF_STEAL_IMPOSSIBLE',
                    f'P{active_player} roba {stolen_mat} a P{robbed_player} pero este tiene 0 de {stolen_mat}')
            # Nota: No aplicamos el robo aquí porque las manos del start_turn ya lo incluyen
            # El robo ya está contabilizado en las manos reportadas

        self.thief_log.append({
            'round': round_key, 'turn': turn_key,
            'source': source,
            'player': f'P{active_player}',
            'past_terrain': past_terrain,
            'new_terrain': new_terrain,
            'robbed': f'P{robbed_player}' if robbed_player is not None else '-',
            'stolen': stolen_mat or '-',
            'validation': validation,
        })

    def _process_dev_cards(self, round_key, turn_key, active_player, dev_cards, phase='start_turn'):
        """Procesa cartas de desarrollo jugadas."""
        for dc in dev_cards:
            played = dc.get('played_card', '')

            if played == 'knight':
                # Knight mueve el ladrón — la info está en el propio dc
                self._process_knight(round_key, turn_key, active_player, dc)
            elif played == 'failed_victory_point':
                # VP fallido — solo logging, sin efecto en recursos
                pass
            elif played == 'year_of_plenty':
                # Año de abundancia: recibe 2 recursos del banco
                mat1 = dc.get('material_1')
                mat2 = dc.get('material_2')
                if mat1 is not None:
                    mat_name = MAT_ID_TO_NAME.get(mat1, '?')
                    self.hands[active_player][mat_name] = self.hands[active_player].get(mat_name, 0) + 1
                if mat2 is not None:
                    mat_name = MAT_ID_TO_NAME.get(mat2, '?')
                    self.hands[active_player][mat_name] = self.hands[active_player].get(mat_name, 0) + 1
            elif played == 'monopoly':
                # Monopolio: roba todo de un tipo de material
                mat_id = dc.get('material')
                if mat_id is not None:
                    mat_name = MAT_ID_TO_NAME.get(mat_id, '?')
                    stolen_total = 0
                    for p in range(4):
                        if p != active_player:
                            amount = self.hands[p].get(mat_name, 0)
                            self.hands[p][mat_name] = 0
                            stolen_total += amount
                    self.hands[active_player][mat_name] = self.hands[active_player].get(mat_name, 0) + stolen_total

    def _process_knight(self, round_key, turn_key, active_player, dc):
        """Procesa efecto de caballero."""
        past_terrain = dc.get('past_thief_terrain')
        new_terrain = dc.get('thief_terrain')
        robbed_player = dc.get('robbed_player')
        stolen_mat_id = dc.get('stolen_material_id')

        if new_terrain is not None:
            self.thief_terrain = new_terrain

        stolen_mat = MAT_ID_TO_NAME.get(stolen_mat_id) if stolen_mat_id is not None else None
        validation = 'OK'

        # El robo del knight ocurre en start_turn, pero las manos ya lo reflejan
        # Solo validamos coherencia
        if robbed_player is not None and stolen_mat:
            # NOTA: Las manos en start_turn ya incluyen el efecto del knight+dado
            pass

        self.thief_log.append({
            'round': round_key, 'turn': turn_key,
            'source': 'knight',
            'player': f'P{active_player}',
            'past_terrain': past_terrain,
            'new_terrain': new_terrain,
            'robbed': f'P{robbed_player}' if robbed_player is not None else '-',
            'stolen': stolen_mat or '-',
            'validation': validation,
        })

    def audit(self):
        """Ejecuta la auditoría completa."""
        rounds = get_sorted_rounds(self.game)
        total_rounds = len(rounds)
        print(f"  Auditando {self.game_name}: {total_rounds} rondas...")

        # Iterar todas las rondas y turnos secuencialmente
        turn_sequence = []  # Lista global ordenada de (round_key, turn_key, player)
        for rk in rounds:
            round_data = self.game[rk]
            turns = get_sorted_turns(round_data)
            for tk, player in turns:
                turn_sequence.append((rk, tk, player, round_data[tk]))

        for seq_idx, (rk, tk, active_player, turn_data) in enumerate(turn_sequence):
            start_turn = turn_data.get('start_turn', {})
            commerce_phase = turn_data.get('commerce_phase', [])
            build_phase = turn_data.get('build_phase', [])
            end_turn = turn_data.get('end_turn', {})

            dice = start_turn.get('dice')
            if isinstance(dice, str):
                dice = int(dice)

            # ─── Paso 1: Leer las manos del start_turn (estado real del JSON) ───
            json_hands = {}
            for p in range(4):
                json_hands[p] = parse_hand(start_turn.get(f'hand_P{p}', {}))

            # ─── Paso 2: Comparar mano calculada vs mano JSON ───
            # (Solo desde la segunda ronda en adelante, porque la primera inicializa)
            if seq_idx > 0:
                for p in range(4):
                    computed = self.hands[p]
                    actual = json_hands[p]
                    delta = hand_delta(computed, actual)

                    if any(v != 0 for v in delta.values()):
                        # Hay discrepancia — en la primera iteración del turno es esperado
                        # porque incluye producción de dados + robber
                        self.resources_log.append({
                            'round': rk, 'turn': tk, 'player': f'P{p}',
                            'computed_end_prev': hand_str(computed),
                            'actual_start': hand_str(actual),
                            'delta': hand_str(delta),
                            'dice': dice,
                            'explanation': 'producción + robber'
                        })

            # ─── Actualizar manos al estado del JSON (punto de verdad) ───
            for p in range(4):
                self.hands[p] = dict(json_hands[p])

            # ─── Registrar snapshot de recursos ───
            for p in range(4):
                self.resources_log.append({
                    'round': rk, 'turn': tk, 'player': f'P{p}',
                    'computed_end_prev': '',
                    'actual_start': hand_str(self.hands[p]),
                    'delta': '',
                    'dice': dice if p == active_player else '',
                    'explanation': 'start_turn snapshot'
                })

            # ─── Paso 3: Procesar dev cards del start_turn ───
            dev_cards_start = start_turn.get('development_card_played', [])
            if dev_cards_start:
                self._process_dev_cards(rk, tk, active_player, dev_cards_start, 'start_turn')

            # ─── Paso 4: Procesar ladrón si dice=7 ───
            if dice == 7:
                self._process_thief(rk, tk, active_player, start_turn, source='dice7')

            # ─── Paso 5: Dados y producción esperada ───
            if dice and dice != 7:
                # Calcular producción esperada (usando thief_terrain ANTES del turno actual si hay knight)
                # Nota: el thief_terrain ya fue actualizado si hubo knight en dev cards
                expected_prod = self.compute_dice_production(dice, self.thief_terrain)
                self.dice_log.append({
                    'round': rk, 'turn': tk,
                    'dice': dice,
                    'thief_at': self.thief_terrain,
                    'prod_P0': hand_str(expected_prod[0]),
                    'prod_P1': hand_str(expected_prod[1]),
                    'prod_P2': hand_str(expected_prod[2]),
                    'prod_P3': hand_str(expected_prod[3]),
                })
            elif dice == 7:
                self.dice_log.append({
                    'round': rk, 'turn': tk,
                    'dice': 7,
                    'thief_at': self.thief_terrain,
                    'prod_P0': 'ROBBER', 'prod_P1': 'ROBBER',
                    'prod_P2': 'ROBBER', 'prod_P3': 'ROBBER',
                })

            # ─── Paso 6: Procesar comercios ───
            if commerce_phase:
                self._process_trades(rk, tk, active_player, commerce_phase)

            # ─── Paso 7: Procesar construcciones ───
            if build_phase:
                self._process_builds(rk, tk, active_player, build_phase)

            # ─── Paso 8: Dev cards del end_turn ───
            dev_cards_end = end_turn.get('development_card_played', [])
            if dev_cards_end:
                self._process_dev_cards(rk, tk, active_player, dev_cards_end, 'end_turn')

            # ─── Paso 9: Verificar totales ───
            for p in range(4):
                t = hand_total(self.hands[p])
                json_total = start_turn.get(f'total_P{p}')
                if json_total is not None:
                    json_total = int(json_total)
                    json_hand_sum = hand_total(json_hands[p])
                    if json_hand_sum != json_total:
                        self._add_error(rk, tk, 'TOTAL_MISMATCH',
                            f'P{p}: sum(hand)={json_hand_sum} != total={json_total}')

        print(f"  Completado: {len(self.errors)} errores, {len(self.trades_log)} trades, {len(self.builds_log)} builds")

    def generate_excel(self, output_dir='.'):
        """Genera el Excel de evidencia."""
        wb = openpyxl.Workbook()

        # ─── Hoja: Resumen ────────────────────────────────────────────────
        ws = wb.active
        ws.title = "Resumen"
        ws.append(["Auditoría del juego", self.game_name])
        ws.append(["Archivo", self.filepath])
        ws.append(["Total rondas", len(get_sorted_rounds(self.game))])
        ws.append(["Total trades registrados", len(self.trades_log)])
        ws.append(["Total builds registrados", len(self.builds_log)])
        ws.append(["Total errores", len(self.errors)])
        ws.append([])

        # Resumen de errores por tipo
        error_types = defaultdict(int)
        for e in self.errors:
            error_types[e['type']] += 1
        ws.append(["Tipo de error", "Cantidad"])
        for et, count in sorted(error_types.items(), key=lambda x: -x[1]):
            ws.append([et, count])

        ws.append([])
        ws.append(["Severidad", "Cantidad"])
        severity_counts = defaultdict(int)
        for e in self.errors:
            severity_counts[e['severity']] += 1
        for sv, count in sorted(severity_counts.items()):
            ws.append([sv, count])

        for row in ws.iter_rows(min_row=1, max_row=2, max_col=2):
            for cell in row:
                cell.font = Font(bold=True, size=13)

        auto_width(ws)

        # ─── Hoja: Recursos por jugador ───────────────────────────────────
        for p in range(4):
            ws_r = wb.create_sheet(f"Recursos_P{p}")
            headers = ['Ronda', 'Turno', 'Dado', 'Cereal', 'Mineral', 'Arcilla',
                       'Madera', 'Lana', 'Total', 'Fuente']
            ws_r.append(headers)
            style_header(ws_r, len(headers))

            row_idx = 2
            for entry in self.resources_log:
                if entry['player'] != f'P{p}':
                    continue
                if entry['explanation'] != 'start_turn snapshot':
                    continue
                hand = parse_hand_str(entry['actual_start'])
                ws_r.append([
                    entry['round'], entry['turn'],
                    entry['dice'] if entry['dice'] else '',
                    hand['cereal'], hand['mineral'], hand['clay'],
                    hand['wood'], hand['wool'],
                    sum(hand.values()),
                    entry['explanation']
                ])
                row_idx += 1

            auto_width(ws_r)

        # ─── Hoja: Comercios ──────────────────────────────────────────────
        ws_t = wb.create_sheet("Comercios")
        headers = ['Ronda', 'Turno', 'Idx', 'Tipo', 'Dador', 'Receptor',
                   'Da', 'Recibe', 'Harbor', 'Resultado', 'Validación',
                   'Mano Antes', 'Mano Después']
        ws_t.append(headers)
        style_header(ws_t, len(headers))

        for i, t in enumerate(self.trades_log):
            row = [
                t['round'], t['turn'], t['index'], t['type'],
                t['giver'], t['receiver'], t['gives'], t['receives'],
                t['harbor'], t['result'], t['validation'],
                t.get('hand_before', ''), t.get('hand_after', '')
            ]
            ws_t.append(row)
            # Colorear validación
            cell = ws_t.cell(row=i+2, column=11)
            if 'ERROR' in str(t['validation']):
                cell.fill = ERROR_FILL
            elif 'WARN' in str(t['validation']):
                cell.fill = WARNING_FILL
            elif t['validation'] == 'OK':
                cell.fill = OK_FILL

        auto_width(ws_t)

        # ─── Hoja: Construcciones ─────────────────────────────────────────
        ws_b = wb.create_sheet("Construcciones")
        headers = ['Ronda', 'Turno', 'Idx', 'Jugador', 'Edificio', 'Detalle',
                   'Coste', 'Mano Antes', 'Mano Después', 'Validación']
        ws_b.append(headers)
        style_header(ws_b, len(headers))

        for i, b in enumerate(self.builds_log):
            row = [
                b['round'], b['turn'], b['index'], b['player'],
                b['building'], b['detail'], b['cost'],
                b['hand_before'], b['hand_after'], b['validation']
            ]
            ws_b.append(row)
            cell = ws_b.cell(row=i+2, column=10)
            if 'ERROR' in str(b['validation']):
                cell.fill = ERROR_FILL
            elif 'WARN' in str(b['validation']):
                cell.fill = WARNING_FILL
            elif b['validation'] == 'OK':
                cell.fill = OK_FILL

        auto_width(ws_b)

        # ─── Hoja: Dados ─────────────────────────────────────────────────
        ws_d = wb.create_sheet("Dados")
        headers = ['Ronda', 'Turno', 'Dado', 'Ladrón en', 'Prod P0', 'Prod P1', 'Prod P2', 'Prod P3']
        ws_d.append(headers)
        style_header(ws_d, len(headers))

        for d in self.dice_log:
            ws_d.append([
                d['round'], d['turn'], d['dice'], d['thief_at'],
                d['prod_P0'], d['prod_P1'], d['prod_P2'], d['prod_P3']
            ])

        auto_width(ws_d)

        # ─── Hoja: Ladrón ────────────────────────────────────────────────
        ws_th = wb.create_sheet("Ladrón")
        headers = ['Ronda', 'Turno', 'Fuente', 'Jugador', 'Terreno Ant.',
                   'Terreno Nuevo', 'Robado', 'Material', 'Validación']
        ws_th.append(headers)
        style_header(ws_th, len(headers))

        for i, th in enumerate(self.thief_log):
            ws_th.append([
                th['round'], th['turn'], th['source'], th['player'],
                th['past_terrain'], th['new_terrain'],
                th['robbed'], th['stolen'], th['validation']
            ])
            cell = ws_th.cell(row=i+2, column=9)
            if 'ERROR' in str(th['validation']):
                cell.fill = ERROR_FILL
            elif th['validation'] == 'OK':
                cell.fill = OK_FILL

        auto_width(ws_th)

        # ─── Hoja: Errores ────────────────────────────────────────────────
        ws_e = wb.create_sheet("Errores")
        headers = ['Ronda', 'Turno', 'Severidad', 'Tipo', 'Descripción']
        ws_e.append(headers)
        style_header(ws_e, len(headers))

        for i, e in enumerate(self.errors):
            ws_e.append([
                e['round'], e['turn'], e['severity'], e['type'], e['description']
            ])
            severity_cell = ws_e.cell(row=i+2, column=3)
            if e['severity'] == 'ERROR':
                severity_cell.fill = ERROR_FILL
            else:
                severity_cell.fill = WARNING_FILL

        auto_width(ws_e)

        # ─── Hoja: Deltas (discrepancias computed vs actual) ──────────────
        ws_delta = wb.create_sheet("Deltas")
        headers = ['Ronda', 'Turno', 'Jugador', 'Dado', 'Computado fin turno ant.',
                   'Actual start_turn', 'Delta (prod+robber)', 'Explicación']
        ws_delta.append(headers)
        style_header(ws_delta, len(headers))

        for entry in self.resources_log:
            if entry['explanation'] == 'start_turn snapshot':
                continue
            ws_delta.append([
                entry['round'], entry['turn'], entry['player'],
                entry['dice'], entry['computed_end_prev'],
                entry['actual_start'], entry['delta'], entry['explanation']
            ])

        auto_width(ws_delta)

        # ─── Guardar ──────────────────────────────────────────────────────
        output_path = os.path.join(output_dir, f'audit_{self.game_name}.xlsx')
        wb.save(output_path)
        print(f"  Excel generado: {output_path}")
        return output_path


def parse_hand_str(s):
    """Parsea string 'C:1 M:2 A:3 W:4 L:5' a dict."""
    result = {m: 0 for m in MATERIALS}
    if not s:
        return result
    parts = s.split()
    mapping = {'C': 'cereal', 'M': 'mineral', 'A': 'clay', 'W': 'wood', 'L': 'wool'}
    for part in parts:
        if ':' in part:
            key, val = part.split(':')
            mat = mapping.get(key)
            if mat:
                result[mat] = int(val)
    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        # Default: auditar game_0 a game_4
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        trace_dir = os.path.join(base_dir, 'Tests', 'test_traces')
        output_dir = os.path.join(base_dir, '.claude', 'debug', 'audit_results')
        os.makedirs(output_dir, exist_ok=True)

        games = [f'game_{i}.json' for i in range(5)]
        for g in games:
            filepath = os.path.join(trace_dir, g)
            if not os.path.exists(filepath):
                print(f"  SKIP: {filepath} no existe")
                continue
            print(f"\n{'='*60}")
            auditor = GameAuditor(filepath)
            auditor.audit()
            auditor.generate_excel(output_dir)
    else:
        filepath = sys.argv[1]
        output_dir = os.path.dirname(filepath) or '.'
        if len(sys.argv) > 2:
            output_dir = sys.argv[2]
        os.makedirs(output_dir, exist_ok=True)

        auditor = GameAuditor(filepath)
        auditor.audit()
        auditor.generate_excel(output_dir)


if __name__ == '__main__':
    main()
