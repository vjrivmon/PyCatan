#!/usr/bin/env python3
"""
Exportador de recursos a Excel para análisis de trazas PyCatan.
Genera:
- Hoja "Totales": Recursos totales por jugador por ronda + gráfico
- Hojas "P0-P3": Detalle por recurso + delta entre rondas
- Hoja "Errores": Discrepancias detectadas
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from openpyxl import Workbook
    from openpyxl.chart import LineChart, Reference
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    Workbook = None  # Placeholder para type hints
    print("WARNING: openpyxl no instalado. Instalar con: pip install openpyxl")


class ResourceTracker:
    MATERIALS = ['cereal', 'mineral', 'clay', 'wood', 'wool']
    MATERIAL_EMOJIS = {'cereal': '🌾', 'mineral': '�ite', 'clay': '🧱', 'wood': '🪵', 'wool': '🐑'}

    def __init__(self, trace_path: str):
        self.trace_path = Path(trace_path)
        self.data: Dict = {}
        self.rounds_data: List[Dict] = []
        self.errors: List[Dict] = []

    def load_trace(self) -> None:
        with open(self.trace_path, 'r') as f:
            self.data = json.load(f)

    def parse_hand(self, hand: Optional[Dict]) -> Dict[str, int]:
        """Convierte hand a dict con int (maneja strings)."""
        if not hand:
            return {m: 0 for m in self.MATERIALS}

        result = {}
        for m in self.MATERIALS:
            val = hand.get(m, 0)
            if isinstance(val, str):
                result[m] = int(val)
            else:
                result[m] = val
        return result

    def extract_resources(self) -> None:
        """Extrae recursos de cada ronda/turno/fase."""
        if 'game' not in self.data:
            return

        game = self.data['game']

        for round_key in sorted([k for k in game.keys() if k.startswith('round_')]):
            round_num = int(round_key.replace('round_', ''))
            round_obj = game[round_key]

            round_data = {
                'round': round_num,
                'players': {i: {'phases': []} for i in range(4)}
            }

            for turn_key in sorted([k for k in round_obj.keys() if k.startswith('turn_P')]):
                player_num = int(turn_key.replace('turn_P', ''))
                turn_obj = round_obj[turn_key]

                # Extraer de start_turn
                if 'start_turn' in turn_obj:
                    st = turn_obj['start_turn']
                    for i in range(4):
                        hand_key = f'hand_P{i}'
                        if hand_key in st:
                            round_data['players'][i]['phases'].append({
                                'phase': f'start_turn_P{player_num}',
                                'hand': self.parse_hand(st[hand_key])
                            })

                # Extraer de commerce_phase
                if 'commerce_phase' in turn_obj:
                    for cp_idx, cp in enumerate(turn_obj['commerce_phase']):
                        for i in range(4):
                            hand_key = f'hand_P{i}'
                            if hand_key in cp:
                                round_data['players'][i]['phases'].append({
                                    'phase': f'commerce_{player_num}_{cp_idx}',
                                    'hand': self.parse_hand(cp[hand_key])
                                })

                # Extraer de build_phase
                if 'build_phase' in turn_obj:
                    for bp_idx, bp in enumerate(turn_obj['build_phase']):
                        for i in range(4):
                            hand_key = f'hand_P{i}'
                            if hand_key in bp:
                                round_data['players'][i]['phases'].append({
                                    'phase': f'build_{player_num}_{bp_idx}',
                                    'hand': self.parse_hand(bp[hand_key])
                                })

                # Extraer de end_turn
                if 'end_turn' in turn_obj:
                    et = turn_obj['end_turn']
                    for i in range(4):
                        hand_key = f'hand_P{i}'
                        if hand_key in et:
                            round_data['players'][i]['phases'].append({
                                'phase': f'end_turn_P{player_num}',
                                'hand': self.parse_hand(et[hand_key])
                            })

            self.rounds_data.append(round_data)

    def get_last_hand_per_round(self, player: int, round_idx: int) -> Dict[str, int]:
        """Obtiene la última mano conocida de un jugador en una ronda."""
        if round_idx >= len(self.rounds_data):
            return {m: 0 for m in self.MATERIALS}

        phases = self.rounds_data[round_idx]['players'][player]['phases']
        if phases:
            return phases[-1]['hand']
        return {m: 0 for m in self.MATERIALS}

    def get_total_resources(self, hand: Dict[str, int]) -> int:
        """Suma total de recursos."""
        return sum(hand.values())

    def export_to_excel(self, output_path: str) -> None:
        """Exporta los datos a Excel."""
        if not HAS_OPENPYXL:
            print("ERROR: openpyxl requerido para exportar a Excel")
            return

        wb = Workbook()

        # Hoja de Totales
        self._create_totals_sheet(wb)

        # Hojas por jugador
        for player in range(4):
            self._create_player_sheet(wb, player)

        # Hoja de Errores
        self._create_errors_sheet(wb)

        # Guardar
        wb.save(output_path)
        print(f"Excel exportado a: {output_path}")

    def _create_totals_sheet(self, wb: Workbook) -> None:
        """Crea hoja con totales por ronda."""
        ws = wb.active
        ws.title = "Totales"

        # Encabezados
        headers = ['Ronda', 'P0 Total', 'P1 Total', 'P2 Total', 'P3 Total']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")

        # Datos
        for row_idx, round_data in enumerate(self.rounds_data, 2):
            ws.cell(row=row_idx, column=1, value=round_data['round'])
            for player in range(4):
                hand = self.get_last_hand_per_round(player, row_idx - 2)
                total = self.get_total_resources(hand)
                ws.cell(row=row_idx, column=player + 2, value=total)

        # Gráfico
        if len(self.rounds_data) > 1:
            chart = LineChart()
            chart.title = "Recursos Totales por Jugador"
            chart.y_axis.title = "Total Recursos"
            chart.x_axis.title = "Ronda"

            data = Reference(ws, min_col=2, min_row=1, max_col=5, max_row=len(self.rounds_data) + 1)
            cats = Reference(ws, min_col=1, min_row=2, max_row=len(self.rounds_data) + 1)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)

            ws.add_chart(chart, "G2")

    def _create_player_sheet(self, wb: Workbook, player: int) -> None:
        """Crea hoja con detalle por jugador."""
        ws = wb.create_sheet(f"P{player}")

        # Encabezados
        headers = ['Ronda'] + self.MATERIALS + ['Total', 'Delta']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            colors = {0: "4472C4", 1: "ED7D31", 2: "A5A5A5", 3: "FFC000"}
            cell.fill = PatternFill(start_color=colors[player], end_color=colors[player], fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")

        prev_total = 0
        for row_idx, round_data in enumerate(self.rounds_data, 2):
            ws.cell(row=row_idx, column=1, value=round_data['round'])
            hand = self.get_last_hand_per_round(player, row_idx - 2)

            for col, mat in enumerate(self.MATERIALS, 2):
                ws.cell(row=row_idx, column=col, value=hand.get(mat, 0))

            total = self.get_total_resources(hand)
            ws.cell(row=row_idx, column=len(self.MATERIALS) + 2, value=total)

            delta = total - prev_total
            delta_cell = ws.cell(row=row_idx, column=len(self.MATERIALS) + 3, value=delta)
            if delta > 0:
                delta_cell.font = Font(color="008000")
            elif delta < 0:
                delta_cell.font = Font(color="FF0000")

            prev_total = total

    def _create_errors_sheet(self, wb: Workbook) -> None:
        """Crea hoja con errores/discrepancias."""
        ws = wb.create_sheet("Errores")

        headers = ['Ronda', 'Jugador', 'Fase', 'Tipo', 'Descripción']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")

        if not self.errors:
            ws.cell(row=2, column=1, value="Sin errores detectados")
        else:
            for row_idx, error in enumerate(self.errors, 2):
                ws.cell(row=row_idx, column=1, value=error.get('round', ''))
                ws.cell(row=row_idx, column=2, value=error.get('player', ''))
                ws.cell(row=row_idx, column=3, value=error.get('phase', ''))
                ws.cell(row=row_idx, column=4, value=error.get('type', ''))
                ws.cell(row=row_idx, column=5, value=error.get('description', ''))

    def print_summary(self) -> None:
        """Imprime resumen en consola."""
        print("=" * 60)
        print("RESUMEN DE RECURSOS")
        print("=" * 60)
        print(f"Archivo: {self.trace_path}")
        print(f"Rondas: {len(self.rounds_data)}")
        print()

        print("RECURSOS FINALES:")
        if self.rounds_data:
            last_round = len(self.rounds_data) - 1
            for player in range(4):
                hand = self.get_last_hand_per_round(player, last_round)
                total = self.get_total_resources(hand)
                print(f"  P{player}: {hand} = {total}")
        print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Uso: python resource_tracker.py <trace.json> [output.xlsx]")
        sys.exit(1)

    trace_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "recursos.xlsx"

    tracker = ResourceTracker(trace_path)
    tracker.load_trace()
    tracker.extract_resources()
    tracker.print_summary()

    if HAS_OPENPYXL:
        tracker.export_to_excel(output_path)
    else:
        print("Instala openpyxl para exportar a Excel: pip install openpyxl")


if __name__ == '__main__':
    main()
