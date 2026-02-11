#!/usr/bin/env python3
"""
Validador de coherencia JSON para trazas de PyCatan.
Verifica que:
1. Los valores de hand_P* sean enteros (no strings)
2. build_phase incluya hand_P* después de construcciones
3. commerce_phase incluya hand_P* después de comercios
4. end_turn incluya hand_P*
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

class BackendValidator:
    def __init__(self, trace_path: str):
        self.trace_path = Path(trace_path)
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.stats = {
            'total_hands_checked': 0,
            'hands_with_strings': 0,
            'build_phases_without_hand': 0,
            'commerce_phases_without_hand': 0,
            'end_turns_without_hand': 0,
        }

    def load_trace(self) -> Dict:
        with open(self.trace_path, 'r') as f:
            return json.load(f)

    def check_hand_types(self, hand: Dict, path: str) -> bool:
        """Verifica que todos los valores de recursos sean int."""
        self.stats['total_hands_checked'] += 1
        all_int = True

        for material, value in hand.items():
            if isinstance(value, str):
                self.errors.append({
                    'type': 'STRING_VALUE',
                    'path': f"{path}.{material}",
                    'value': value,
                    'expected': 'int',
                    'got': 'str'
                })
                all_int = False
                self.stats['hands_with_strings'] += 1
                break  # Solo contar una vez por hand

        return all_int

    def check_phase_has_hands(self, phase_obj: Dict, phase_name: str, path: str,
                              actual_player: int = None) -> bool:
        """Verifica que una fase incluya hand_P* actualizado."""
        has_any_hand = False

        for i in range(4):
            hand_key = f'hand_P{i}'
            if hand_key in phase_obj:
                has_any_hand = True
                self.check_hand_types(phase_obj[hand_key], f"{path}.{hand_key}")

        return has_any_hand

    def validate_build_phase(self, build_phases: List[Dict], path: str,
                             actual_player: int) -> None:
        """Valida que build_phase incluya hand_P* después de construcciones exitosas."""
        for idx, build in enumerate(build_phases):
            build_path = f"{path}[{idx}]"

            # Si hubo construcción exitosa, debe tener hand_P*
            if build.get('finished') == True and build.get('building') not in ['None', 'played_card']:
                has_hand = self.check_phase_has_hands(build, 'build_phase', build_path, actual_player)

                if not has_hand:
                    self.errors.append({
                        'type': 'MISSING_HAND_BUILD',
                        'path': build_path,
                        'building': build.get('building'),
                        'message': f"build_phase con construcción exitosa ({build.get('building')}) no incluye hand_P*"
                    })
                    self.stats['build_phases_without_hand'] += 1

    def validate_commerce_phase(self, commerce_phases: List[Dict], path: str,
                                actual_player: int) -> None:
        """Valida que commerce_phase incluya hand_P* después de comercios."""
        for idx, commerce in enumerate(commerce_phases):
            commerce_path = f"{path}[{idx}]"

            # Si hubo comercio exitoso (harbor o jugador), debe tener hand_P*
            trade_offer = commerce.get('trade_offer')
            harbor_trade = commerce.get('harbor_trade')

            # Verificar si hubo comercio real
            had_trade = False
            if trade_offer and trade_offer != 'None' and trade_offer != 'played_card':
                if harbor_trade and commerce.get('answer') and isinstance(commerce.get('answer'), dict):
                    had_trade = True  # Comercio con puerto exitoso
                elif not harbor_trade and commerce.get('answers'):
                    # Verificar si algún jugador aceptó
                    for answer_chain in commerce.get('answers', []):
                        if answer_chain and len(answer_chain) > 0:
                            last_answer = answer_chain[-1]
                            if last_answer.get('completed') == True:
                                had_trade = True
                                break

            if had_trade:
                has_hand = self.check_phase_has_hands(commerce, 'commerce_phase', commerce_path, actual_player)

                if not has_hand:
                    self.errors.append({
                        'type': 'MISSING_HAND_COMMERCE',
                        'path': commerce_path,
                        'message': f"commerce_phase con comercio exitoso no incluye hand_P*"
                    })
                    self.stats['commerce_phases_without_hand'] += 1

    def validate_end_turn(self, end_turn: Dict, path: str, actual_player: int) -> None:
        """Valida que end_turn incluya hand_P*."""
        has_hand = self.check_phase_has_hands(end_turn, 'end_turn', path, actual_player)

        if not has_hand:
            self.warnings.append({
                'type': 'MISSING_HAND_END_TURN',
                'path': path,
                'message': "end_turn no incluye hand_P* (debería incluirlo para consistencia)"
            })
            self.stats['end_turns_without_hand'] += 1

    def validate_turn(self, turn_obj: Dict, path: str, player_num: int) -> None:
        """Valida un turno completo."""
        # Validar start_turn (siempre debe tener hands)
        if 'start_turn' in turn_obj:
            start_turn = turn_obj['start_turn']
            self.check_phase_has_hands(start_turn, 'start_turn', f"{path}.start_turn", player_num)

        # Validar commerce_phase
        if 'commerce_phase' in turn_obj:
            self.validate_commerce_phase(
                turn_obj['commerce_phase'],
                f"{path}.commerce_phase",
                player_num
            )

        # Validar build_phase
        if 'build_phase' in turn_obj:
            self.validate_build_phase(
                turn_obj['build_phase'],
                f"{path}.build_phase",
                player_num
            )

        # Validar end_turn
        if 'end_turn' in turn_obj:
            self.validate_end_turn(
                turn_obj['end_turn'],
                f"{path}.end_turn",
                player_num
            )

    def validate(self) -> Tuple[int, int]:
        """Ejecuta todas las validaciones. Retorna (errores, warnings)."""
        trace = self.load_trace()

        if 'game' not in trace:
            self.errors.append({
                'type': 'MISSING_GAME',
                'path': 'root',
                'message': "Traza no contiene 'game'"
            })
            return len(self.errors), len(self.warnings)

        game = trace['game']

        # Iterar por rondas
        for round_key in sorted([k for k in game.keys() if k.startswith('round_')]):
            round_obj = game[round_key]
            round_path = f"game.{round_key}"

            # Iterar por turnos
            for turn_key in sorted([k for k in round_obj.keys() if k.startswith('turn_P')]):
                player_num = int(turn_key.replace('turn_P', ''))
                turn_obj = round_obj[turn_key]
                turn_path = f"{round_path}.{turn_key}"

                self.validate_turn(turn_obj, turn_path, player_num)

        return len(self.errors), len(self.warnings)

    def print_report(self) -> None:
        """Imprime reporte de validación."""
        print("=" * 60)
        print("REPORTE DE VALIDACIÓN BACKEND")
        print("=" * 60)
        print(f"Archivo: {self.trace_path}")
        print()

        print("ESTADÍSTICAS:")
        print(f"  - Hands revisados: {self.stats['total_hands_checked']}")
        print(f"  - Hands con strings: {self.stats['hands_with_strings']}")
        print(f"  - Build phases sin hand: {self.stats['build_phases_without_hand']}")
        print(f"  - Commerce phases sin hand: {self.stats['commerce_phases_without_hand']}")
        print(f"  - End turns sin hand: {self.stats['end_turns_without_hand']}")
        print()

        if self.errors:
            print(f"ERRORES ({len(self.errors)}):")
            for err in self.errors[:20]:  # Mostrar máximo 20
                print(f"  [{err['type']}] {err.get('path', '')}")
                print(f"    {err.get('message', err)}")
            if len(self.errors) > 20:
                print(f"  ... y {len(self.errors) - 20} errores más")
        else:
            print("ERRORES: 0")

        print()

        if self.warnings:
            print(f"WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings[:10]:
                print(f"  [{warn['type']}] {warn.get('path', '')}")
                print(f"    {warn.get('message', warn)}")
            if len(self.warnings) > 10:
                print(f"  ... y {len(self.warnings) - 10} warnings más")
        else:
            print("WARNINGS: 0")

        print()
        print("=" * 60)
        if self.errors:
            print("RESULTADO: FAILED")
        else:
            print("RESULTADO: PASSED")
        print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Uso: python validate_backend.py <trace.json> [trace2.json ...]")
        sys.exit(1)

    total_errors = 0
    total_warnings = 0

    for trace_path in sys.argv[1:]:
        validator = BackendValidator(trace_path)
        errors, warnings = validator.validate()
        validator.print_report()
        total_errors += errors
        total_warnings += warnings
        print()

    if total_errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
