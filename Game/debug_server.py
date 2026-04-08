#!/usr/bin/env python3
"""
Debug server for Catan Visualizer.
Serves the visualizer on localhost, injects a verification script,
and logs every state transition comparing frontend state vs JSON source of truth.

Usage:
    python Game/debug_server.py [game_trace.json]

Then open http://localhost:8765 in your browser, load a game, and press Play.
The server logs all events and flags discrepancies in the terminal.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# Must be set BEFORE importing websockets
os.environ['WEBSOCKETS_MAX_LINE_LENGTH'] = '65536'

import websockets
import websockets.asyncio.server

# ─── Configuration ───
PORT_HTTP = 8765
PORT_WS = 8766
GAME_DIR = Path(__file__).parent
PROJECT_ROOT = GAME_DIR.parent

# ─── Colors for terminal output ───
class C:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

# ─── Load game trace for verification ───
game_trace = None
trace_path = None

def load_trace(path):
    global game_trace, trace_path
    with open(path) as f:
        game_trace = json.load(f)
    trace_path = path
    print(f"{C.GREEN}Trace loaded: {path}{C.RESET}")
    rounds = len(game_trace.get('game', {}))
    print(f"{C.DIM}  Rounds: {rounds}{C.RESET}")

# ─── Verification logic ───
discrepancy_count = 0
event_count = 0

def verify_hands(event):
    """Compare hands reported by frontend against JSON trace."""
    global discrepancy_count, event_count
    event_count += 1

    round_idx = event.get('round', 0)
    turn_idx = event.get('turn', 0)
    phase = event.get('phase', 0)
    phase_name = event.get('phaseName', '?')
    frontend_hands = event.get('hands', {})

    if not game_trace:
        return

    # Find the corresponding JSON data
    round_key = f'round_{round_idx}'
    turn_key = f'turn_P{turn_idx}'

    game = game_trace.get('game', {})
    rnd = game.get(round_key)
    if not rnd:
        return
    turn = rnd.get(turn_key)
    if not turn:
        return

    # Get expected hands from the JSON based on phase
    expected_hands = {}
    if phase == 0 and turn.get('start_turn'):
        for p in range(4):
            h = turn['start_turn'].get(f'hand_P{p}')
            if h:
                expected_hands[str(p)] = h
    elif phase == 1 and turn.get('commerce_phase'):
        # Use last commerce entry with hands
        for cp in reversed(turn['commerce_phase']):
            if cp.get('hand_P0'):
                for p in range(4):
                    h = cp.get(f'hand_P{p}')
                    if h:
                        expected_hands[str(p)] = h
                break
    elif phase == 2 and turn.get('build_phase'):
        for bp in reversed(turn['build_phase']):
            if bp.get('hand_P0'):
                for p in range(4):
                    h = bp.get(f'hand_P{p}')
                    if h:
                        expected_hands[str(p)] = h
                break
    elif phase == 3 and turn.get('end_turn'):
        for p in range(4):
            h = turn['end_turn'].get(f'hand_P{p}')
            if h:
                expected_hands[str(p)] = h

    if not expected_hands:
        return

    # Compare
    resources = ['cereal', 'mineral', 'clay', 'wood', 'wool']
    mismatches = []

    for p_str, expected in expected_hands.items():
        fe_hand = frontend_hands.get(p_str, {})
        for res in resources:
            exp_val = str(expected.get(res, '0'))
            fe_val = str(fe_hand.get(res, '0'))
            if exp_val != fe_val:
                mismatches.append(f"P{p_str}.{res}: frontend={fe_val} json={exp_val}")

    prefix = f"R{round_idx+1} T{turn_idx+1} {phase_name}"
    if mismatches:
        discrepancy_count += 1
        print(f"{C.RED}{C.BOLD}MISMATCH [{prefix}]{C.RESET}")
        for m in mismatches:
            print(f"  {C.RED}{m}{C.RESET}")
    else:
        print(f"{C.GREEN}  OK [{prefix}] — 4 players verified{C.RESET}")


def verify_event(event):
    """Verify a generic event from the frontend."""
    etype = event.get('type', 'unknown')
    round_idx = event.get('round', 0)
    turn_idx = event.get('turn', 0)
    phase = event.get('phase', 0)
    prefix = f"R{round_idx+1} T{turn_idx+1} P{phase}"

    if etype == 'phase_change':
        phase_name = event.get('phaseName', '?')
        player = event.get('activePlayer', '?')
        print(f"{C.CYAN}[{prefix}] {phase_name} — Jugador activo: {player}{C.RESET}")
        verify_hands(event)

    elif etype == 'trade':
        detail = event.get('detail', '')
        print(f"{C.BLUE}  [{prefix}] TRADE: {detail}{C.RESET}")

    elif etype == 'build':
        detail = event.get('detail', '')
        print(f"{C.YELLOW}  [{prefix}] BUILD: {detail}{C.RESET}")

    elif etype == 'thief':
        detail = event.get('detail', '')
        print(f"{C.RED}  [{prefix}] THIEF: {detail}{C.RESET}")

    elif etype == 'victory':
        detail = event.get('detail', '')
        print(f"{C.GREEN}{C.BOLD}  [{prefix}] VICTORY: {detail}{C.RESET}")

    elif etype == 'game_loaded':
        fname = event.get('filename', '?')
        print(f"\n{C.BOLD}{'='*60}")
        print(f"  GAME LOADED: {fname}")
        print(f"{'='*60}{C.RESET}\n")
        # Try to load the trace if provided
        if trace_path:
            load_trace(trace_path)

    elif etype == 'play_started':
        print(f"\n{C.BOLD}{C.CYAN}>>> PLAY STARTED{C.RESET}")

    elif etype == 'play_stopped':
        print(f"{C.BOLD}{C.CYAN}>>> PLAY STOPPED{C.RESET}")
        print(f"{C.DIM}  Events processed: {event_count}, Discrepancies: {discrepancy_count}{C.RESET}\n")


# ─── WebSocket server ───
async def ws_handler(websocket):
    print(f"{C.GREEN}Debug client connected{C.RESET}")
    try:
        async for message in websocket:
            try:
                event = json.loads(message)
                verify_event(event)
            except json.JSONDecodeError:
                print(f"{C.RED}Invalid JSON from client: {message[:100]}{C.RESET}")
    except websockets.exceptions.ConnectionClosed:
        print(f"{C.YELLOW}Debug client disconnected{C.RESET}")


async def start_ws_server():
    async with websockets.asyncio.server.serve(
        ws_handler, "localhost", PORT_WS,
        max_size=2**20,
    ):
        print(f"{C.GREEN}WebSocket server on ws://localhost:{PORT_WS}{C.RESET}")
        await asyncio.Future()  # run forever


# ─── HTTP server that injects the debug script ───
class DebugHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self):
        # Inject debug script into index.html
        if self.path == '/Game/' or self.path == '/Game/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()

            html_path = GAME_DIR / 'index.html'
            html = html_path.read_text(encoding='utf-8')

            # Inject debug script before </body>
            debug_script = f'''
<script>
// ─── Catan Debug Verification Client ───
(function() {{
    const ws = new WebSocket('ws://localhost:{PORT_WS}');
    let connected = false;

    ws.onopen = () => {{
        connected = true;
        console.log('%c[DEBUG] Connected to verification server', 'color: green; font-weight: bold');
    }};
    ws.onerror = () => console.warn('[DEBUG] Could not connect to verification server');

    function send(data) {{
        if (connected && ws.readyState === WebSocket.OPEN) {{
            ws.send(JSON.stringify(data));
        }}
    }}

    function captureHands() {{
        const hands = {{}};
        for (let p = 0; p < 4; p++) {{
            hands[p] = {{}};
            ['cereal','mineral','clay','wood','wool'].forEach(res => {{
                const el = document.getElementById('res-' + p + '-' + res);
                hands[p][res] = el ? el.textContent : '0';
            }});
        }}
        return hands;
    }}

    // Hook into applyCurrentPhase
    const origApply = window.applyCurrentPhase || (typeof applyCurrentPhase !== 'undefined' ? applyCurrentPhase : null);

    // Patch via MutationObserver on the state-bar to detect phase changes
    const stateBar = document.getElementById('info-phase');
    if (stateBar) {{
        const observer = new MutationObserver(() => {{
            setTimeout(() => {{
                const phaseNames = ['Inicio de Turno', 'Comercio', 'Construccion', 'Fin de Turno'];
                send({{
                    type: 'phase_change',
                    round: typeof currentRound !== 'undefined' ? currentRound : 0,
                    turn: typeof currentTurn !== 'undefined' ? currentTurn : 0,
                    phase: typeof currentPhase !== 'undefined' ? currentPhase : 0,
                    phaseName: stateBar.textContent,
                    activePlayer: document.getElementById('info-active-player')?.textContent || '?',
                    hands: captureHands()
                }});
            }}, 50);  // Small delay to let hands update
        }});
        observer.observe(stateBar, {{ childList: true, characterData: true, subtree: true }});
    }}

    // Hook into game loading
    const fileInput = document.getElementById('file-input');
    if (fileInput) {{
        fileInput.addEventListener('change', () => {{
            setTimeout(() => send({{ type: 'game_loaded', filename: fileInput.files[0]?.name || '?' }}), 500);
        }});
    }}

    // Hook into play/stop
    const playBtn = document.getElementById('btn-play');
    if (playBtn) {{
        playBtn.addEventListener('click', () => {{
            setTimeout(() => {{
                const isPlaying = playBtn.classList.contains('playing');
                send({{ type: isPlaying ? 'play_started' : 'play_stopped' }});
            }}, 100);
        }});
    }}

    // ─── Fast-Forward Button ───
    // Adds a "DEBUG: Fast-Forward" button to the controls bar
    // that advances through ALL phases as fast as possible
    function addFastForwardBtn() {{
        const controls = document.getElementById('controls');
        if (!controls) return;
        const btn = document.createElement('button');
        btn.className = 'ctrl-btn';
        btn.id = 'btn-debug-ff';
        btn.title = 'Debug: recorrer todas las fases a velocidad máxima';
        btn.style.cssText = 'background:#C62828;color:#FFF;font-size:0.6rem;font-weight:800;padding:6px 10px;border-radius:6px;cursor:pointer;border:2px solid #B71C1C;margin-left:8px;';
        btn.textContent = 'FAST-FWD';
        btn.addEventListener('click', runFastForward);
        controls.appendChild(btn);
    }}

    let ffRunning = false;
    async function runFastForward() {{
        if (ffRunning) return;
        if (typeof gameData === 'undefined' || !gameData) {{
            alert('Carga una partida primero');
            return;
        }}
        ffRunning = true;
        const btn = document.getElementById('btn-debug-ff');
        if (btn) btn.textContent = 'RUNNING...';
        send({{ type: 'play_started' }});

        // Total phases: rounds * 4 turns * 4 phases
        const totalPhases = roundKeys.length * 4 * 4;
        let count = 0;

        function step() {{
            if (!ffRunning) return;
            // Check if at the end
            if (currentRound >= roundKeys.length - 1 && currentTurn >= 3 && currentPhase >= 3) {{
                ffRunning = false;
                if (btn) btn.textContent = 'DONE';
                send({{ type: 'play_stopped' }});
                return;
            }}
            nextPhase();
            count++;
            // Use requestAnimationFrame for max speed while letting DOM update
            requestAnimationFrame(step);
        }}

        requestAnimationFrame(step);
    }}

    // Stop fast-forward when navigating manually
    document.addEventListener('keydown', () => {{ ffRunning = false; }});

    addFastForwardBtn();
    console.log('%c[DEBUG] Verification hooks + Fast-Forward installed', 'color: blue');
}})();
</script>
'''
            html = html.replace('</body>', debug_script + '</body>')
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

    def log_message(self, format, *args):
        # Suppress HTTP logs to keep terminal clean
        pass


def start_http_server():
    httpd = HTTPServer(('localhost', PORT_HTTP), DebugHTTPHandler)
    print(f"{C.GREEN}HTTP server on http://localhost:{PORT_HTTP}/Game/{C.RESET}")
    httpd.serve_forever()


# ─── Main ───
def main():
    global trace_path
    if len(sys.argv) > 1:
        trace_path = sys.argv[1]
        if os.path.exists(trace_path):
            load_trace(trace_path)
        else:
            print(f"{C.YELLOW}Trace file not found: {trace_path} (will verify when loaded in browser){C.RESET}")

    print(f"\n{C.BOLD}{'='*60}")
    print(f"  CATAN VISUALIZER - DEBUG SERVER")
    print(f"{'='*60}{C.RESET}")
    print(f"\n  Open: {C.BOLD}http://localhost:{PORT_HTTP}/Game/{C.RESET}")
    print(f"  Load a game trace and press Play to start verification.")
    print(f"  Discrepancies between JSON and frontend will be logged here.\n")

    # Start HTTP server in a thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Start WebSocket server in main thread
    asyncio.run(start_ws_server())


if __name__ == '__main__':
    main()
