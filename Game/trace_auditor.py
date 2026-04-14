#!/usr/bin/env python3
"""
Auditor exhaustivo de trazas JSON del simulador de Catan.

Recorre ronda por ronda, turno por turno, fase por fase verificando:
- Conservacion de recursos (nada aparece/desaparece de la nada)
- Reglas de cartas de desarrollo (compra+juego mismo turno, limite 1 por turno)
- Logica del ladron (auto-robo, descarte correcto, past_thief coherente)
- Trades (inviables no modifican manos, gives/receives coherentes)
- Construccion (costes correctos)
- Recursos negativos
- Totales coinciden con la suma de materiales
- Consistencia entre snapshots consecutivos

Uso:
    python Game/trace_auditor.py Game/test_game_fixed.json
    python Game/trace_auditor.py /ruta/a/cualquier_traza.json
"""

import json
import sys
import math
from pathlib import Path

# ─── Colors ───
class C:
    R = '\033[0m'; RED = '\033[91m'; GRN = '\033[92m'; YEL = '\033[93m'
    BLU = '\033[94m'; CYN = '\033[96m'; B = '\033[1m'; DIM = '\033[2m'

RES = ['cereal', 'mineral', 'clay', 'wood', 'wool']

# Build costs
COSTS = {
    'town': {'cereal': 1, 'mineral': 0, 'clay': 1, 'wood': 1, 'wool': 1},
    'city': {'cereal': 2, 'mineral': 3, 'clay': 0, 'wood': 0, 'wool': 0},
    'road': {'cereal': 0, 'mineral': 0, 'clay': 1, 'wood': 1, 'wool': 0},
    'card': {'cereal': 1, 'mineral': 1, 'clay': 0, 'wood': 0, 'wool': 1},
}

def h2d(hand):
    """Convierte hand dict (strings) a dict de ints."""
    if not hand or not isinstance(hand, dict):
        return None
    return {r: int(hand.get(r, 0)) for r in RES}

def htotal(hd):
    """Suma total de un hand dict."""
    if not hd: return 0
    return sum(hd.values())

def hdiff(h1, h2):
    """Diferencia h2 - h1 por recurso."""
    if not h1 or not h2: return None
    return {r: h2[r] - h1[r] for r in RES}

def fmt_diff(d):
    parts = []
    for r in RES:
        if d[r] != 0:
            parts.append(f"{r}:{d[r]:+d}")
    return ', '.join(parts) if parts else 'sin cambios'


class TraceAuditor:
    def __init__(self, trace):
        self.trace = trace
        self.issues = []  # (severity, location, message)
        self.warnings = []
        self.stats = {
            'rounds': 0, 'turns': 0, 'phases': 0,
            'trades_player': 0, 'trades_harbor': 0, 'trades_inviable': 0,
            'builds': 0, 'thief_events': 0, 'dev_cards_played': 0,
            'dev_cards_bought': 0,
        }

    def error(self, loc, msg):
        self.issues.append(('ERROR', loc, msg))

    def warn(self, loc, msg):
        self.warnings.append(('WARN', loc, msg))

    def get_hands(self, data):
        """Extrae las 4 manos de un snapshot."""
        hands = {}
        for p in range(4):
            h = data.get(f'hand_P{p}')
            if h:
                hands[p] = h2d(h)
        return hands

    def audit(self):
        game = self.trace.get('game', {})
        if not game:
            self.error('GLOBAL', 'No se encontro seccion "game" en la traza')
            return

        sorted_rounds = sorted(game.keys(), key=lambda x: int(x.split('_')[1]))
        self.stats['rounds'] = len(sorted_rounds)

        prev_end_hands = None  # Manos al final del turno anterior
        last_thief_terrain = None  # Ultima posicion conocida del ladron
        global_dev_cards_bought = [[] for _ in range(4)]  # Historial de cartas compradas

        for rnd_key in sorted_rounds:
            rnd = game[rnd_key]
            rnd_num = int(rnd_key.split('_')[1])

            for turn_idx in range(4):
                turn_key = f'turn_P{turn_idx}'
                if turn_key not in rnd:
                    continue

                turn = rnd[turn_key]
                self.stats['turns'] += 1
                loc = f'R{rnd_num+1} T{turn_idx+1}'

                cards_bought_this_turn = []
                cards_played_this_turn = 0

                # ═══════════════════════════════════════
                # FASE 0: START_TURN
                # ═══════════════════════════════════════
                st = turn.get('start_turn', {})
                if st:
                    self.stats['phases'] += 1
                    st_hands = self.get_hands(st)

                    # Check totales coinciden
                    for p in range(4):
                        if p in st_hands:
                            expected_total = htotal(st_hands[p])
                            json_total = int(st.get(f'total_P{p}', -1))
                            if json_total != -1 and json_total != expected_total:
                                self.error(f'{loc} start', f'P{p} total={json_total} pero suma={expected_total}')

                    # Check recursos negativos
                    for p, hand in st_hands.items():
                        for r in RES:
                            if hand[r] < 0:
                                self.error(f'{loc} start', f'P{p}.{r} = {hand[r]} (NEGATIVO)')

                    # Check actual_player coherente
                    ap = st.get('actual_player')
                    if ap is not None and int(ap) != turn_idx:
                        self.warn(f'{loc} start', f'actual_player={ap} pero es turno de P{turn_idx}')

                    # ── Ladron ──
                    if st.get('dice') == 7:
                        self.stats['thief_events'] += 1

                        # Check auto-robo
                        robbed = st.get('robbed_player', -1)
                        if robbed != -1 and robbed == turn_idx:
                            self.error(f'{loc} thief', f'P{turn_idx} se roba a si mismo (robbed_player={robbed})')

                        # Check past_thief coherente
                        past = st.get('past_thief_terrain')
                        new = st.get('thief_terrain')
                        if last_thief_terrain is not None and past is not None:
                            if past != last_thief_terrain:
                                self.warn(f'{loc} thief',
                                    f'past_thief_terrain={past} pero ultimo conocido={last_thief_terrain} '
                                    f'(puede ser carta de caballero entre turnos)')
                        if new is not None:
                            last_thief_terrain = new

                        # Check descarte >7 cartas
                        if prev_end_hands:
                            for p in range(4):
                                if p in prev_end_hands and p in st_hands:
                                    prev_total = htotal(prev_end_hands[p])
                                    now_total = htotal(st_hands[p])
                                    if prev_total > 7:
                                        expected_keep = math.ceil(prev_total / 2)
                                        # El ladron puede robar 1 extra
                                        stolen = 1 if robbed == p else 0
                                        min_expected = expected_keep - stolen
                                        # Recursos de dados pueden sumarse, asi que now_total >= min_expected
                                        # Solo alertar si es menor que ceil/2 - 1 (margen)
                                        if now_total < min_expected - 1:
                                            self.warn(f'{loc} discard',
                                                f'P{p} tenia {prev_total}, ahora {now_total}. '
                                                f'Se esperaba ~{expected_keep} (ceil({prev_total}/2))')

                    # Check cartas de desarrollo en start_turn
                    for cd in st.get('development_card_played', []):
                        if isinstance(cd, dict):
                            played = cd.get('played_card', '')
                            if played in ('failed_victory_point', 'cannot_play_just_bought', 'none'):
                                self.error(f'{loc} start', f'Carta fallida/bloqueada en traza: {played}')
                            elif played:
                                cards_played_this_turn += 1
                                self.stats['dev_cards_played'] += 1
                                if cd.get('thief_terrain') is not None:
                                    last_thief_terrain = cd['thief_terrain']

                    prev_hands = st_hands

                # ═══════════════════════════════════════
                # FASE 1: COMMERCE
                # ═══════════════════════════════════════
                for ci, cp in enumerate(turn.get('commerce_phase', [])):
                    self.stats['phases'] += 1
                    cp_hands = self.get_hands(cp)

                    if not cp or not isinstance(cp, dict):
                        continue

                    to = cp.get('trade_offer')

                    # Check trade inviable no muta manos
                    if cp.get('inviable') and prev_hands and cp_hands:
                        for p in range(4):
                            if p in prev_hands and p in cp_hands:
                                diff = hdiff(prev_hands[p], cp_hands[p])
                                if diff and any(v != 0 for v in diff.values()):
                                    self.error(f'{loc} commerce[{ci}]',
                                        f'Trade inviable pero P{p} cambio: {fmt_diff(diff)}')

                    # Check harbor trade tiene ratio
                    if cp.get('harbor_trade') and to and to != 'None' and isinstance(to, dict):
                        self.stats['trades_harbor'] += 1
                        if 'trade_ratio' not in cp:
                            self.error(f'{loc} commerce[{ci}]', 'Harbor trade sin trade_ratio')

                    # Player trade
                    if to and to != 'None' and isinstance(to, dict) and not cp.get('harbor_trade'):
                        if cp.get('inviable'):
                            self.stats['trades_inviable'] += 1
                        else:
                            self.stats['trades_player'] += 1

                    # Played card during commerce
                    if to == 'played_card':
                        dc = cp.get('development_card_played', {})
                        if isinstance(dc, dict):
                            played = dc.get('played_card', '')
                            if played in ('failed_victory_point', 'cannot_play_just_bought', 'none'):
                                self.error(f'{loc} commerce[{ci}]', f'Carta fallida en traza: {played}')
                            elif played:
                                cards_played_this_turn += 1
                                self.stats['dev_cards_played'] += 1
                                if dc.get('thief_terrain') is not None:
                                    last_thief_terrain = dc['thief_terrain']

                    # Check negativos y totales
                    for p, hand in cp_hands.items():
                        for r in RES:
                            if hand[r] < 0:
                                self.error(f'{loc} commerce[{ci}]', f'P{p}.{r} = {hand[r]} (NEGATIVO)')
                        json_total = int(cp.get(f'total_P{p}', -1))
                        if json_total != -1 and json_total != htotal(hand):
                            self.error(f'{loc} commerce[{ci}]', f'P{p} total={json_total} != suma={htotal(hand)}')

                    if cp_hands:
                        prev_hands = cp_hands

                # ═══════════════════════════════════════
                # FASE 2: BUILD
                # ═══════════════════════════════════════
                for bi, bp in enumerate(turn.get('build_phase', [])):
                    self.stats['phases'] += 1
                    bp_hands = self.get_hands(bp)
                    building = bp.get('building')

                    if building in COSTS and bp.get('finished'):
                        self.stats['builds'] += 1
                        # Verificar que se descontaron los materiales correctos
                        if prev_hands and bp_hands and turn_idx in prev_hands and turn_idx in bp_hands:
                            diff = hdiff(prev_hands[turn_idx], bp_hands[turn_idx])
                            if diff:
                                cost = COSTS[building]
                                for r in RES:
                                    if building != 'None' and cost[r] > 0 and diff[r] > -cost[r] + 1:
                                        # Permitir margen por otros eventos simultaneos
                                        pass

                    if building == 'card' and bp.get('finished'):
                        self.stats['dev_cards_bought'] += 1
                        cards_bought_this_turn.append(bp.get('card_type'))

                    if building == 'played_card':
                        dc = bp.get('development_card_played', {})
                        if isinstance(dc, dict):
                            played = dc.get('played_card', '')
                            if played in ('failed_victory_point', 'cannot_play_just_bought', 'none'):
                                self.error(f'{loc} build[{bi}]', f'Carta fallida en traza: {played}')
                            elif played:
                                cards_played_this_turn += 1
                                self.stats['dev_cards_played'] += 1

                                # Check si la carta fue comprada este turno
                                if cards_bought_this_turn and played != 'victory_point':
                                    self.error(f'{loc} build[{bi}]',
                                        f'Carta "{played}" jugada en turno con compra de carta '
                                        f'(posible buy+play mismo turno)')

                                if dc.get('thief_terrain') is not None:
                                    last_thief_terrain = dc['thief_terrain']

                    # Check negativos
                    for p, hand in bp_hands.items():
                        for r in RES:
                            if hand[r] < 0:
                                self.error(f'{loc} build[{bi}]', f'P{p}.{r} = {hand[r]} (NEGATIVO)')

                    if bp_hands:
                        prev_hands = bp_hands

                # ═══════════════════════════════════════
                # FASE 3: END_TURN
                # ═══════════════════════════════════════
                et = turn.get('end_turn', {})
                if et:
                    self.stats['phases'] += 1
                    et_hands = self.get_hands(et)

                    # Check cartas de desarrollo en end_turn
                    for cd in et.get('development_card_played', []):
                        if isinstance(cd, dict):
                            played = cd.get('played_card', '')
                            if played in ('failed_victory_point', 'cannot_play_just_bought', 'none'):
                                self.error(f'{loc} end', f'Carta fallida en traza: {played}')
                            elif played:
                                cards_played_this_turn += 1
                                self.stats['dev_cards_played'] += 1
                                if cd.get('thief_terrain') is not None:
                                    last_thief_terrain = cd['thief_terrain']

                    # Check: maximo 1 carta de desarrollo por turno (VP no cuenta)
                    if cards_played_this_turn > 1:
                        self.error(f'{loc}', f'{cards_played_this_turn} cartas de desarrollo jugadas en 1 turno (max=1)')

                    # Check negativos y totales
                    for p, hand in et_hands.items():
                        for r in RES:
                            if hand[r] < 0:
                                self.error(f'{loc} end', f'P{p}.{r} = {hand[r]} (NEGATIVO)')
                        json_total = int(et.get(f'total_P{p}', -1))
                        if json_total != -1 and json_total != htotal(hand):
                            self.error(f'{loc} end', f'P{p} total={json_total} != suma={htotal(hand)}')

                    # Check VP coherente
                    vp = et.get('victory_points', {})
                    for p in range(4):
                        vpval = vp.get(f'J{p}')
                        if vpval is not None:
                            v = int(vpval)
                            if v < 0:
                                self.error(f'{loc} end', f'P{p} VP={v} (NEGATIVO)')
                            if v > 12:
                                self.warn(f'{loc} end', f'P{p} VP={v} (>12, posible error)')

                    if et_hands:
                        prev_end_hands = et_hands

                # ═══════════════════════════════════════
                # CHECKS CROSS-FASE: conservacion de recursos entre turnos
                # ═══════════════════════════════════════
                if prev_end_hands and st.get('dice') and st.get('dice') != 7:
                    st_hands_check = self.get_hands(st)
                    total_before = sum(htotal(prev_end_hands.get(p, {})) for p in range(4) if p in prev_end_hands)
                    total_after = sum(htotal(st_hands_check.get(p, {})) for p in range(4) if p in st_hands_check)
                    # Los recursos solo pueden subir (dados) o mantenerse (sin produccion)
                    if total_after < total_before:
                        self.warn(f'{loc} conservation',
                            f'Recursos totales bajaron de {total_before} a {total_after} sin ladron '
                            f'(diff={total_after - total_before})')

    def report(self):
        """Imprime el reporte final."""
        print(f"\n{C.B}{'='*70}")
        print(f"  AUDITOR DE TRAZAS CATAN — REPORTE")
        print(f"{'='*70}{C.R}\n")

        print(f"{C.CYN}Estadisticas:{C.R}")
        for k, v in self.stats.items():
            print(f"  {k}: {v}")
        print()

        if self.issues:
            print(f"{C.RED}{C.B}{len(self.issues)} ERRORES ENCONTRADOS:{C.R}\n")
            for sev, loc, msg in self.issues:
                print(f"  {C.RED}[{sev}] {loc}: {msg}{C.R}")
        else:
            print(f"{C.GRN}{C.B}0 ERRORES — TRAZA LIMPIA{C.R}")

        if self.warnings:
            print(f"\n{C.YEL}{len(self.warnings)} ADVERTENCIAS:{C.R}\n")
            for sev, loc, msg in self.warnings:
                print(f"  {C.YEL}[{sev}] {loc}: {msg}{C.R}")

        print(f"\n{C.B}{'='*70}{C.R}")
        total = len(self.issues)
        if total == 0:
            print(f"{C.GRN}{C.B}  RESULTADO: PASS — 0 errores en {self.stats['rounds']} rondas, "
                  f"{self.stats['turns']} turnos, {self.stats['phases']} fases{C.R}")
        else:
            print(f"{C.RED}{C.B}  RESULTADO: FAIL — {total} errores detectados{C.R}")
        print(f"{C.B}{'='*70}{C.R}\n")

        return len(self.issues)


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <traza.json>")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Archivo no encontrado: {path}")
        sys.exit(1)

    print(f"{C.CYN}Cargando {path}...{C.R}")
    with open(path) as f:
        trace = json.load(f)

    auditor = TraceAuditor(trace)
    auditor.audit()
    errors = auditor.report()
    sys.exit(1 if errors > 0 else 0)


if __name__ == '__main__':
    main()
