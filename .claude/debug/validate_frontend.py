#!/usr/bin/env python3
"""
Validador Frontend con Playwright para PyCatan Visualizer.
Compara lo que muestra la UI con lo que dice el JSON.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from playwright.sync_api import sync_playwright, Page
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("WARNING: playwright no instalado. Instalar con:")
    print("  pip install playwright")
    print("  playwright install chromium")


class FrontendValidator:
    MATERIALS = ['cereal', 'mineral', 'clay', 'wood', 'wool']

    def __init__(self, base_url: str, trace_path: str):
        self.base_url = base_url.rstrip('/')
        self.trace_path = Path(trace_path)
        self.errors: List[Dict] = []
        self.page: Optional[Page] = None

    def load_trace(self) -> Dict:
        with open(self.trace_path, 'r') as f:
            return json.load(f)

    def get_ui_resources(self, player: int) -> Dict[str, int]:
        """Obtiene recursos mostrados en UI para un jugador."""
        resources = {}
        for mat in self.MATERIALS:
            selector = f'#hand_P{player} .{mat} .{mat}_quantity'
            try:
                element = self.page.query_selector(selector)
                if element:
                    text = element.inner_text()
                    resources[mat] = int(text) if text.strip() else 0
                else:
                    resources[mat] = 0
            except Exception as e:
                print(f"  Error obteniendo {mat} para P{player}: {e}")
                resources[mat] = 0
        return resources

    def parse_json_hand(self, hand: Optional[Dict]) -> Dict[str, int]:
        """Parsea hand del JSON (maneja strings)."""
        if not hand:
            return {m: 0 for m in self.MATERIALS}

        result = {}
        for m in self.MATERIALS:
            val = hand.get(m, 0)
            result[m] = int(val) if isinstance(val, str) else val
        return result

    def compare_resources(self, expected: Dict[str, int], actual: Dict[str, int],
                         player: int, context: str) -> bool:
        """Compara recursos esperados vs actuales."""
        match = True
        for mat in self.MATERIALS:
            exp = expected.get(mat, 0)
            act = actual.get(mat, 0)
            if exp != act:
                self.errors.append({
                    'player': player,
                    'material': mat,
                    'expected': exp,
                    'actual': act,
                    'context': context
                })
                match = False
        return match

    def navigate_to_phase(self, round_num: int, turn: int, phase: str) -> bool:
        """Navega a una fase específica usando los controles del visualizador."""
        try:
            # Seleccionar ronda
            round_selector = self.page.query_selector('#contador_rondas')
            if round_selector:
                round_selector.select_option(f'round_{round_num}')
                time.sleep(0.2)

            # Seleccionar turno
            turn_selector = self.page.query_selector('#contador_turnos')
            if turn_selector:
                turn_selector.select_option(f'P{turn}')
                time.sleep(0.2)

            # Seleccionar fase
            phase_selector = self.page.query_selector('#contador_fases')
            if phase_selector:
                phase_selector.select_option(phase)
                time.sleep(0.3)

            return True
        except Exception as e:
            print(f"  Error navegando a R{round_num}/T{turn}/{phase}: {e}")
            return False

    def validate_phase(self, trace: Dict, round_num: int, turn: int,
                      phase_key: str, phase_data: Dict) -> None:
        """Valida una fase específica."""
        context = f"R{round_num}/P{turn}/{phase_key}"

        # Navegar a la fase
        if not self.navigate_to_phase(round_num, turn, phase_key):
            return

        # Verificar recursos de cada jugador
        for player in range(4):
            hand_key = f'hand_P{player}'
            if hand_key in phase_data:
                expected = self.parse_json_hand(phase_data[hand_key])
                actual = self.get_ui_resources(player)

                if not self.compare_resources(expected, actual, player, context):
                    print(f"  MISMATCH P{player} en {context}:")
                    print(f"    Expected: {expected}")
                    print(f"    Actual:   {actual}")

    def validate(self) -> int:
        """Ejecuta validación completa."""
        if not HAS_PLAYWRIGHT:
            print("ERROR: Playwright requerido")
            return 1

        trace = self.load_trace()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            self.page = browser.new_page()

            # Cargar visualizador
            print(f"Cargando {self.base_url}...")
            self.page.goto(self.base_url)
            time.sleep(2)

            # Cargar traza
            print(f"Cargando traza {self.trace_path}...")
            # Asumiendo que hay un input para cargar JSON
            file_input = self.page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(str(self.trace_path))
                time.sleep(1)

            if 'game' not in trace:
                print("ERROR: Traza sin 'game'")
                return 1

            game = trace['game']

            # Validar primeras 3 rondas como muestra
            rounds_to_check = min(3, len([k for k in game.keys() if k.startswith('round_')]))

            for round_key in sorted([k for k in game.keys() if k.startswith('round_')])[:rounds_to_check]:
                round_num = int(round_key.replace('round_', ''))
                round_obj = game[round_key]
                print(f"\nValidando Ronda {round_num}...")

                for turn_key in sorted([k for k in round_obj.keys() if k.startswith('turn_P')]):
                    turn_num = int(turn_key.replace('turn_P', ''))
                    turn_obj = round_obj[turn_key]

                    # Validar start_turn
                    if 'start_turn' in turn_obj:
                        self.validate_phase(trace, round_num, turn_num,
                                          'start_turn', turn_obj['start_turn'])

                    # Validar end_turn
                    if 'end_turn' in turn_obj:
                        self.validate_phase(trace, round_num, turn_num,
                                          'end_turn', turn_obj['end_turn'])

            browser.close()

        return len(self.errors)

    def print_report(self) -> None:
        """Imprime reporte de validación."""
        print("\n" + "=" * 60)
        print("REPORTE DE VALIDACIÓN FRONTEND")
        print("=" * 60)
        print(f"URL: {self.base_url}")
        print(f"Traza: {self.trace_path}")
        print()

        if self.errors:
            print(f"DISCREPANCIAS ({len(self.errors)}):")
            for err in self.errors[:20]:
                print(f"  P{err['player']} - {err['material']}: "
                      f"expected {err['expected']}, got {err['actual']} "
                      f"({err['context']})")
            if len(self.errors) > 20:
                print(f"  ... y {len(self.errors) - 20} más")
        else:
            print("DISCREPANCIAS: 0")

        print()
        print("=" * 60)
        if self.errors:
            print("RESULTADO: FAILED")
        else:
            print("RESULTADO: PASSED")
        print("=" * 60)


def main():
    if len(sys.argv) < 3:
        print("Uso: python validate_frontend.py <base_url> <trace.json>")
        print("Ejemplo: python validate_frontend.py http://localhost:8000 game_0.json")
        sys.exit(1)

    base_url = sys.argv[1]
    trace_path = sys.argv[2]

    validator = FrontendValidator(base_url, trace_path)
    error_count = validator.validate()
    validator.print_report()

    sys.exit(1 if error_count > 0 else 0)


if __name__ == '__main__':
    main()
