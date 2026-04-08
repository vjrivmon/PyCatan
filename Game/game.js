/* ===================================================
   CATÁN VISUALIZADOR - LÓGICA JS PURA (VANILLA)
   ===================================================
   Sin jQuery, sin Bootstrap, sin frameworks.
   =================================================== */

'use strict';

// ============================================================
// CONSTANTES
// ============================================================
const TERRAIN_TYPES = {
    0: { name: 'Cereal', asset: 'hexagono_paja.png' },
    1: { name: 'Mineral', asset: 'hexagono_roca.png' },
    2: { name: 'Arcilla', asset: 'hexagono_arcilla.png' },
    3: { name: 'Madera', asset: 'hexagono_bosque.png' },
    4: { name: 'Lana', asset: 'hexagono_ovejas.png' },
    '-1': { name: 'Desierto', asset: 'hexagono_desierto.png' }
};

const RESOURCE_ICONS = {
    cereal: '🌾',
    mineral: '⛰️',
    clay: '🧱',
    wood: '🌲',
    wool: '🐑'
};

// Imágenes de materiales reales
const RESOURCE_IMG = {
    cereal: 'materiales/paja.png',
    mineral: 'materiales/roca.png',
    clay: 'materiales/arcilla.png',
    wood: 'materiales/madera.png',
    wool: 'materiales/lana.png'
};

const RESOURCE_NAMES = {
    cereal: 'Cereal',
    mineral: 'Mineral',
    clay: 'Arcilla',
    wood: 'Madera',
    wool: 'Lana'
};

const PLAYER_COLORS = ['p0', 'p1', 'p2', 'p3'];
const PLAYER_NAMES = ['J1 (Rojo)', 'J2 (Azul)', 'J3 (Naranja)', 'J4 (Verde)'];
const PLAYER_COLOR_HEX = ['#D32F2F', '#1976D2', '#F57C00', '#388E3C'];

const BUILDING_ASSETS = {
    settlement: [
        'poblados/poblado_rojo.png',
        'poblados/poblado_azul.png',
        'poblados/poblado_naranja.png',
        'poblados/poblado_verde.png'
    ],
    city: [
        'ciudades/ciudad_roja.png',
        'ciudades/ciudad_azul.png',
        'ciudades/ciudad_naranja.png',
        'ciudades/ciudad_verde.png'
    ],
    road: [
        'caminos/camino_rojo.png',
        'caminos/camino_azul.png',
        'caminos/camino_naranja.png',
        'caminos/camino_verde.png'
    ]
};

const HARBOR_LABELS = {
    0: '🌾 2:1',
    1: '⛰️ 2:1',
    2: '🧱 2:1',
    3: '🌲 2:1',
    4: '🐑 2:1',
    5: '? 3:1'
};

// Harbor material images for the badge
const HARBOR_IMG = {
    0: 'materiales/paja.png',        // cereal 2:1
    1: 'materiales/roca.png',        // mineral 2:1
    2: 'materiales/arcilla.png',     // clay 2:1
    3: 'materiales/madera.png',      // wood 2:1
    4: 'materiales/lana.png',        // wool 2:1
};

const HARBOR_RATIO = {
    0: '2:1', 1: '2:1', 2: '2:1', 3: '2:1', 4: '2:1', 5: '3:1'
};

const CARD_TYPES = {
    0: 'Caballero',
    1: 'Punto de Victoria',
    2: 'Monopolio',
    3: 'Dos Caminos',
    4: 'Abundancia'
};

const DEV_CARD_ASSETS = {
    0: 'desarrollo/caballero.png',
    1: 'desarrollo/punto_victoria.png',
    2: 'desarrollo/monopolio.png',
    3: 'desarrollo/dos_caminos.png',
    4: 'desarrollo/abundancia.png',
    'knight': 'desarrollo/caballero.png',
    'victory_point': 'desarrollo/punto_victoria.png',
    'monopoly': 'desarrollo/monopolio.png',
    'road_building': 'desarrollo/dos_caminos.png',
    'year_of_plenty': 'desarrollo/abundancia.png'
};

// Asset base path
const ASSET_BASE = '../nuevos_assets/';

// ============================================================
// HEX GRID COORDINATES (pixel positions for each hex on board)
// Standard Catan board: rows 3-4-5-4-3 = 19 hexagons
// ============================================================
const HEX_W = 130;
const HEX_H = Math.round(HEX_W * 1.1547); // ~150px
const HEX_VERT_STEP = Math.round(HEX_H * 0.75); // ~113px vertical between rows
const HEX_HORIZ_STEP = HEX_W + 5; // horizontal between hex centers

const HEX_POSITIONS = computeHexPositions();

function computeHexPositions() {
    // Rows: 3, 4, 5, 4, 3 hexes
    const rows = [3, 4, 5, 4, 3];
    const positions = [];
    // Auto-calculate board size from hex grid
    const gridWidth = 4 * HEX_HORIZ_STEP + HEX_W; // widest row (5 hexes)
    const gridHeight = 4 * HEX_VERT_STEP + HEX_H;
    const boardPadding = 55;
    const boardCenterX = gridWidth / 2 + boardPadding;
    const startY = boardPadding;

    for (let r = 0; r < rows.length; r++) {
        const count = rows[r];
        // Center each row: offset so middle hex is at boardCenterX
        const rowStartX = boardCenterX - ((count - 1) * HEX_HORIZ_STEP) / 2 - HEX_W / 2;
        for (let c = 0; c < count; c++) {
            positions.push({
                x: rowStartX + c * HEX_HORIZ_STEP,
                y: startY + r * HEX_VERT_STEP
            });
        }
    }
    return positions;
}

// ============================================================
// NODE COORDINATES - computed dynamically from hex positions
// using contacting_terrain data from JSON
// ============================================================
let NODE_POSITIONS = [];

function computeNodePositionsFromData(nodes, terrain) {
    // Each terrain has contacting_nodes[6] whose index maps to hex vertices:
    //   index 0 → top-left vertex
    //   index 1 → top vertex
    //   index 2 → top-right vertex
    //   index 3 → bottom-left vertex
    //   index 4 → bottom vertex
    //   index 5 → bottom-right vertex
    const nodeOffsets = [
        { x: 0,          y: HEX_H * 0.25 },  // [0] top-left
        { x: HEX_W / 2,  y: 0 },              // [1] top
        { x: HEX_W,      y: HEX_H * 0.25 },  // [2] top-right
        { x: 0,          y: HEX_H * 0.75 },   // [3] bottom-left
        { x: HEX_W / 2,  y: HEX_H },          // [4] bottom
        { x: HEX_W,      y: HEX_H * 0.75 }   // [5] bottom-right
    ];

    const positions = new Array(nodes.length).fill(null);

    terrain.forEach((t, tIdx) => {
        const hexPos = HEX_POSITIONS[tIdx];
        if (!hexPos || !t.contacting_nodes) return;

        t.contacting_nodes.forEach((nodeId, idx) => {
            if (idx < 6 && positions[nodeId] === null) {
                positions[nodeId] = {
                    x: hexPos.x + nodeOffsets[idx].x,
                    y: hexPos.y + nodeOffsets[idx].y
                };
            }
        });
    });

    // Safety: fill any remaining nulls (shouldn't happen)
    positions.forEach((p, i) => {
        if (p === null) positions[i] = { x: 0, y: 0 };
    });

    return positions;
}

// ============================================================
// GAME STATE
// ============================================================
let gameData = null;       // Full JSON data
let boardState = null;     // Current board state (nodes, terrain, roads)
let roundKeys = [];        // Sorted round keys
let currentRound = 0;
let currentTurn = 0;       // 0-3 (P0-P3)
let currentPhase = 0;      // 0=start, 1=commerce, 2=build, 3=end
let isPlaying = false;
let playInterval = null;
let playSpeed = 1000;
let previousHands = {};    // Track previous hands for diff highlights

// ============================================================
// DOM REFERENCES
// ============================================================
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    restoreFromSession();
});

function initEventListeners() {
    // File loading
    $('#load-btn').addEventListener('click', () => showModal('upload-modal'));
    $('#file-input').addEventListener('change', handleFileSelect);
    $('#modal-cancel').addEventListener('click', () => hideModal('upload-modal'));
    $('#modal-load').addEventListener('click', loadSelectedFile);
    $('#victory-close').addEventListener('click', () => hideModal('victory-modal'));

    // Drop zone
    const dropZone = $('#drop-zone');
    dropZone.addEventListener('click', () => $('#file-input').click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', handleFileDrop);

    // Modal overlay click to close
    $$('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            e.target.closest('.modal').classList.add('hidden');
        });
    });

    // Navigation controls
    $('#btn-start').addEventListener('click', goToStart);
    $('#btn-end').addEventListener('click', goToEnd);
    $('#btn-prev').addEventListener('click', prevPhase);
    $('#btn-next').addEventListener('click', nextPhase);
    $('#btn-prev-round').addEventListener('click', prevRound);
    $('#btn-next-round').addEventListener('click', nextRound);
    $('#btn-play').addEventListener('click', togglePlay);

    // Speed slider removed — fixed at 1s

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (!gameData) return;
        switch (e.key) {
            case 'ArrowRight': nextPhase(); break;
            case 'ArrowLeft': prevPhase(); break;
            case 'ArrowUp': nextRound(); break;
            case 'ArrowDown': prevRound(); break;
            case ' ':
                e.preventDefault();
                togglePlay();
                break;
        }
    });
}

// ============================================================
// FILE HANDLING
// ============================================================
let selectedFile = null;

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) setSelectedFile(file);
}

function handleFileDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    $('#drop-zone').classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.json')) {
        setSelectedFile(file);
    }
}

function setSelectedFile(file) {
    selectedFile = file;
    $('#file-info').classList.remove('hidden');
    $('#file-name').textContent = file.name;
    $('#modal-load').disabled = false;
}

function loadSelectedFile() {
    if (!selectedFile) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        // Clear any previous corrupt session data before loading
        try { sessionStorage.removeItem('catan_game_data'); } catch (_) {}

        let data;
        try {
            data = JSON.parse(e.target.result);
        } catch (err) {
            alert('Error al parsear JSON: archivo inválido.\n' + err.message);
            return;
        }

        try {
            const fileName = selectedFile.name;
            loadGame(data);
            hideModal('upload-modal');
            $('#game-status').classList.remove('hidden');
            $('#status-text').textContent = fileName;
        } catch (err) {
            console.error('Error al cargar la partida:', err);
            alert('Error al cargar la partida: ' + err.message + '\n\nRevisa la consola (F12) para más detalles.');
            // Reset state on error
            gameData = null;
            boardState = null;
        }
    };
    reader.readAsText(selectedFile);
}

// ============================================================
// GAME LOADING
// ============================================================
function loadGame(data) {
    // Validar estructura JSON antes de procesar
    if (!data || !data.setup || !data.setup.board || !data.setup.board.board_nodes || !data.setup.board.board_terrain || !data.game) {
        console.error('Estructura JSON inválida. Claves encontradas:', data ? Object.keys(data) : 'null');
        if (data && data.setup) console.error('setup keys:', Object.keys(data.setup));
        if (data && data.setup && data.setup.board) console.error('board keys:', Object.keys(data.setup.board));
        throw new Error('El archivo JSON no tiene la estructura esperada. Revisa la consola para detalles.');
    }

    // Validar que terrain tenga terrain_type en cada entrada
    const terrain = data.setup.board.board_terrain;
    for (let i = 0; i < terrain.length; i++) {
        if (terrain[i] && terrain[i].terrain_type === undefined) {
            console.error('Terrain[' + i + '] no tiene terrain_type:', terrain[i]);
            throw new Error('Terrain[' + i + '] no tiene campo terrain_type.');
        }
    }

    gameData = data;

    // Persist to sessionStorage for reload
    try {
        sessionStorage.setItem('catan_game_data', JSON.stringify(data));
    } catch (e) { /* ignore quota errors */ }

    // Initialize board state from setup
    boardState = {
        nodes: JSON.parse(JSON.stringify(data.setup.board.board_nodes)),
        terrain: data.setup.board.board_terrain,
        roads: [],
        playerDevCards: [[], [], [], []]
    };

    // Parse round keys and sort numerically
    roundKeys = Object.keys(data.game)
        .filter(k => k.startsWith('round_'))
        .sort((a, b) => parseInt(a.split('_')[1]) - parseInt(b.split('_')[1]));

    // Reset state
    currentRound = 0;
    currentTurn = 0;
    currentPhase = 0;
    previousHands = {};

    // Compute node positions from hex + terrain data
    NODE_POSITIONS = computeNodePositionsFromData(boardState.nodes, boardState.terrain);

    // Apply setup placements
    applySetup();

    // Render board
    renderBoard();
    renderPlayers();
    clearLogs();

    // Navigate to first state
    applyCurrentPhase();
    updateUI();

    // Show loaded indicator
    const loadBtn = $('#load-btn');
    const indicator = document.createElement('span');
    indicator.id = 'loaded-indicator';
    indicator.textContent = 'Partida cargada';
    indicator.style.cssText = 'font-size:0.75rem;background:rgba(76,175,80,0.8);color:#fff;padding:3px 10px;border-radius:12px;margin-right:8px;';
    const existing = document.getElementById('loaded-indicator');
    if (existing) existing.remove();
    loadBtn.parentNode.insertBefore(indicator, loadBtn);

    addLog('🎮 Partida cargada correctamente — ' + roundKeys.length + ' rondas', 'log-phase');
}

function restoreFromSession() {
    try {
        const saved = sessionStorage.getItem('catan_game_data');
        if (saved) {
            const data = JSON.parse(saved);
            if (data && data.setup && data.setup.board &&
                data.setup.board.board_nodes && data.setup.board.board_terrain &&
                data.game && Object.keys(data.game).length > 0) {
                loadGame(data);
            } else {
                sessionStorage.removeItem('catan_game_data');
                console.warn('Datos de sesión incompletos, eliminados.');
            }
        }
    } catch (e) {
        sessionStorage.removeItem('catan_game_data');
        console.warn('No se pudo restaurar la partida:', e);
    }
}

// ============================================================
// SETUP - Apply initial settlements and roads
// ============================================================
function applySetup() {
    for (let p = 0; p < 4; p++) {
        const placements = gameData.setup['P' + p];
        if (!placements) continue;

        for (const placement of placements) {
            // Place settlement
            const nodeIdx = placement.id;
            if (boardState.nodes[nodeIdx]) {
                boardState.nodes[nodeIdx].player = p;
                boardState.nodes[nodeIdx].has_city = false;
            }

            // Place road
            const roadTo = placement.road;
            boardState.roads.push({ from: nodeIdx, to: roadTo, player: p });
        }
    }

    // Find thief position
    boardState.thiefTerrain = boardState.terrain.findIndex(t => t.has_thief);
    if (boardState.thiefTerrain === -1) {
        // Default to desert
        boardState.thiefTerrain = boardState.terrain.findIndex(t => t.terrain_type === -1);
    }
}

// ============================================================
// BOARD RENDERING
// ============================================================
function renderBoard() {
    // Dynamically size the board div based on hex grid
    const gridWidth = 4 * HEX_HORIZ_STEP + HEX_W;
    const gridHeight = 4 * HEX_VERT_STEP + HEX_H;
    const boardPadding = 55;
    const boardEl = $('#board');
    boardEl.style.width = (gridWidth + boardPadding * 2) + 'px';
    boardEl.style.height = (gridHeight + boardPadding * 2) + 'px';

    renderHexagons();
    renderNumberTokens();
    renderNodes();
    renderHarbors();
    renderRoads();
    renderRobber();
}

function renderHexagons() {
    const container = $('#hex-container');
    container.innerHTML = '';

    boardState.terrain.forEach((terrain, idx) => {
        const pos = HEX_POSITIONS[idx];
        if (!pos) return;

        const tt = terrain ? terrain.terrain_type : -1;
        const terrainInfo = TERRAIN_TYPES[tt] || TERRAIN_TYPES[String(tt)] || TERRAIN_TYPES['-1'] || { name: 'Desconocido', asset: 'hexagono_desierto.png' };
        const div = document.createElement('div');
        div.className = 'hex';
        div.id = 'hex-' + idx;
        div.style.left = pos.x + 'px';
        div.style.top = pos.y + 'px';
        div.title = terrainInfo.name + (terrain.probability > 0 ? ' (' + terrain.probability + ')' : '');

        const img = document.createElement('img');
        img.src = ASSET_BASE + 'hexagonos/' + terrainInfo.asset;
        img.alt = terrainInfo.name;
        img.draggable = false;
        div.appendChild(img);

        container.appendChild(div);
    });
}

function renderNumberTokens() {
    const container = $('#token-container');
    container.innerHTML = '';

    boardState.terrain.forEach((terrain, idx) => {
        if (terrain.probability <= 0 || terrain.terrain_type === -1) return;

        const pos = HEX_POSITIONS[idx];
        if (!pos) return;

        const div = document.createElement('div');
        div.className = 'number-token';
        div.id = 'token-' + idx;
        // Center the token on the hex (token img = 60px, offset = 30)
        div.style.left = (pos.x + HEX_W / 2 - 30) + 'px';
        div.style.top = (pos.y + HEX_H / 2 - 30) + 'px';

        const img = document.createElement('img');
        const num = terrain.probability;
        img.src = ASSET_BASE + 'fichas/ficha_numero_' + num + '.png';
        img.alt = '' + num;
        img.draggable = false;
        div.appendChild(img);

        container.appendChild(div);
    });
}

function renderNodes() {
    const container = $('#node-container');
    container.innerHTML = '';

    boardState.nodes.forEach((node, idx) => {
        const pos = NODE_POSITIONS[idx];
        if (!pos) return;

        const div = document.createElement('div');
        div.className = 'node';
        div.id = 'node-' + idx;
        div.style.left = pos.x + 'px';
        div.style.top = pos.y + 'px';

        if (node.player !== -1) {
            div.classList.add('has-building');
            if (node.has_city) {
                div.classList.add('has-city');
                const img = document.createElement('img');
                img.src = ASSET_BASE + BUILDING_ASSETS.city[node.player];
                img.alt = 'Ciudad J' + (node.player + 1);
                img.draggable = false;
                div.appendChild(img);
            } else {
                const img = document.createElement('img');
                img.src = ASSET_BASE + BUILDING_ASSETS.settlement[node.player];
                img.alt = 'Poblado J' + (node.player + 1);
                img.draggable = false;
                div.appendChild(img);
            }
        } else {
            div.classList.add('empty-node');
        }

        // Harbor nodes tracked for separate rendering
        // (harbors rendered by renderHarbors)

        container.appendChild(div);
    });
}

function renderRoads() {
    const container = $('#road-container');
    container.innerHTML = '';

    boardState.roads.forEach((road, idx) => {
        const fromPos = NODE_POSITIONS[road.from];
        const toPos = NODE_POSITIONS[road.to];
        if (!fromPos || !toPos) return;

        const div = document.createElement('div');
        div.className = 'road built';
        div.id = 'road-' + road.from + '-' + road.to;

        // Calculate road position and rotation
        const dx = toPos.x - fromPos.x;
        const dy = toPos.y - fromPos.y;
        const length = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.atan2(dy, dx) * (180 / Math.PI);

        const roadH = 18;
        div.style.left = fromPos.x + 'px';
        div.style.top = (fromPos.y - roadH / 2) + 'px';
        div.style.width = length + 'px';
        div.style.transformOrigin = '0 50%';
        div.style.transform = 'rotate(' + angle + 'deg)';

        const img = document.createElement('img');
        img.src = ASSET_BASE + BUILDING_ASSETS.road[road.player];
        img.alt = 'Camino J' + (road.player + 1);
        img.draggable = false;
        img.style.width = '100%';
        img.style.height = '18px';
        img.style.objectFit = 'fill';
        div.appendChild(img);

        container.appendChild(div);
    });
}

function renderHarbors() {
    const container = $('#harbor-container');
    container.innerHTML = '';

    // Step 1: Compute board geometric center from all hex positions
    let boardCX = 0, boardCY = 0;
    HEX_POSITIONS.forEach(h => {
        boardCX += h.x + HEX_W / 2;
        boardCY += h.y + HEX_H / 2;
    });
    boardCX /= HEX_POSITIONS.length;
    boardCY /= HEX_POSITIONS.length;

    // Step 2: Group harbor nodes into pairs (each port has 2 adjacent nodes)
    const used = new Set();
    const pairs = [];

    boardState.nodes.forEach((node, idx) => {
        if (node.harbor === -1 || node.harbor === undefined) return;
        if (used.has(idx)) return;

        let pairIdx = -1;
        for (const adj of (node.adjacent || [])) {
            if (!used.has(adj) && boardState.nodes[adj] &&
                boardState.nodes[adj].harbor === node.harbor) {
                pairIdx = adj;
                break;
            }
        }
        used.add(idx);
        if (pairIdx !== -1) used.add(pairIdx);
        pairs.push({ n1: idx, n2: pairIdx, type: node.harbor });
    });

    // Step 3: Render each harbor at the correct vertex position
    pairs.forEach(pair => {
        const p1 = NODE_POSITIONS[pair.n1];
        const p2 = pair.n2 !== -1 ? NODE_POSITIONS[pair.n2] : null;
        if (!p1) return;

        // Pick the vertex that is MOST OUTER (furthest from board center)
        let anchorX, anchorY;
        if (p2) {
            const d1 = (p1.x - boardCX) ** 2 + (p1.y - boardCY) ** 2;
            const d2 = (p2.x - boardCX) ** 2 + (p2.y - boardCY) ** 2;
            if (d1 >= d2) {
                anchorX = p1.x; anchorY = p1.y;
            } else {
                anchorX = p2.x; anchorY = p2.y;
            }
        } else {
            anchorX = p1.x; anchorY = p1.y;
        }

        // Direction outward from board center through this vertex
        let outX = anchorX - boardCX;
        let outY = anchorY - boardCY;
        const len = Math.sqrt(outX * outX + outY * outY) || 1;
        outX /= len;
        outY /= len;

        // Place badge just outside the vertex, touching it
        const offset = 20;
        const badgeX = anchorX + outX * offset;
        const badgeY = anchorY + outY * offset;

        // Create badge element
        const badge = document.createElement('div');
        badge.className = 'harbor-badge';
        badge.style.left = badgeX + 'px';
        badge.style.top = badgeY + 'px';

        const harborType = pair.type;
        if (HARBOR_IMG[harborType]) {
            const himg = document.createElement('img');
            himg.src = ASSET_BASE + HARBOR_IMG[harborType];
            himg.alt = HARBOR_RATIO[harborType] || '3:1';
            himg.draggable = false;
            himg.className = 'harbor-icon';
            badge.appendChild(himg);
        }

        const ratio = document.createElement('span');
        ratio.className = 'harbor-ratio';
        ratio.textContent = HARBOR_RATIO[harborType] || '3:1';
        badge.appendChild(ratio);

        container.appendChild(badge);
    });
}

function renderRobber() {
    const robber = $('#robber');
    const terrainIdx = boardState.thiefTerrain;

    if (terrainIdx >= 0 && terrainIdx < HEX_POSITIONS.length) {
        const pos = HEX_POSITIONS[terrainIdx];
        robber.style.left = (pos.x + HEX_W / 2 - 28) + 'px';
        robber.style.top = (pos.y + HEX_H / 2 - 28) + 'px';
        robber.classList.remove('hidden');
    }
}

// ============================================================
// PLAYER PANEL RENDERING
// ============================================================
function renderPlayers() {
    const container = $('#players-container');
    container.innerHTML = '';

    const resources = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

    for (let p = 0; p < 4; p++) {
        const card = document.createElement('div');
        card.className = 'player-card ' + PLAYER_COLORS[p];
        card.id = 'player-card-' + p;

        let resHTML = '';
        resources.forEach(res => {
            resHTML += `
                <div class="resource-cell res-${res}" title="${RESOURCE_NAMES[res]}">
                    <img class="res-icon-img" src="${ASSET_BASE}${RESOURCE_IMG[res]}" alt="${RESOURCE_NAMES[res]}" draggable="false">
                    <span class="res-count" id="res-${p}-${res}">0</span>
                </div>`;
        });

        card.innerHTML = `
            <div class="player-card-header">
                <span class="player-name">${PLAYER_NAMES[p]}</span>
                <span class="player-vp" id="vp-${p}">⭐ 2</span>
            </div>
            <div class="player-card-body">
                <div class="resources-row">
                    ${resHTML}
                </div>
                <div class="player-footer">
                    <span class="player-total">Total: <span id="total-${p}">0</span></span>
                    <div class="dev-cards-row" id="devcards-${p}"></div>
                </div>
            </div>
        `;

        container.appendChild(card);
    }

    // Initialize dev card tracking
    if (!boardState.playerDevCards) {
        boardState.playerDevCards = [[], [], [], []];
    }
}

/**
 * Updates player hand displays with persistent delta badges.
 * @param {object} turnData - Object with hand_P0..hand_P3 and total_P0..total_P3
 * @param {string} source - 'dice'|'trade'|'build'|'thief'|null — used to color-code delta badges
 */
function updatePlayerHands(turnData, source) {
    for (let p = 0; p < 4; p++) {
        const handKey = 'hand_P' + p;
        const totalKey = 'total_P' + p;
        const hand = turnData[handKey];
        const total = turnData[totalKey];

        if (!hand) continue;

        const resources = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
        const prevHand = previousHands[p] || {};

        resources.forEach(res => {
            const val = parseInt(hand[res]) || 0;
            const prevVal = parseInt(prevHand[res]) || 0;
            const el = $(`#res-${p}-${res}`);
            if (!el) return;

            el.textContent = val;

            // Remove previous delta badges
            const cell = el.closest('.resource-cell');
            if (cell) {
                const oldBadge = cell.querySelector('.res-delta');
                if (oldBadge) oldBadge.remove();
            }

            // Persistent delta badge — stays until next updatePlayerHands call
            el.classList.remove('increased', 'decreased');
            const diff = val - prevVal;
            if (diff > 0) {
                el.classList.add('increased');
                if (cell) {
                    const badge = document.createElement('span');
                    badge.className = 'res-delta res-delta-up' + (source === 'trade' ? ' delta-trade' : '');
                    badge.textContent = '+' + diff;
                    cell.appendChild(badge);
                }
            } else if (diff < 0) {
                el.classList.add('decreased');
                if (cell) {
                    const badge = document.createElement('span');
                    badge.className = 'res-delta res-delta-down';
                    badge.textContent = diff;
                    cell.appendChild(badge);
                }
            }
        });

        if (total !== undefined) {
            const totalEl = $(`#total-${p}`);
            if (totalEl) totalEl.textContent = total;
        }

        // Save for next diff
        previousHands[p] = { ...hand };
    }
}

function updateVictoryPoints(vpData) {
    if (!vpData) return;
    for (let p = 0; p < 4; p++) {
        const key = 'J' + p;
        const vp = vpData[key];
        if (vp !== undefined) {
            const el = $(`#vp-${p}`);
            if (el) el.textContent = '⭐ ' + vp;
        }
    }
}

function renderPlayerDevCards(playerIdx) {
    const container = $(`#devcards-${playerIdx}`);
    if (!container || !boardState.playerDevCards) return;
    container.innerHTML = '';

    const cards = boardState.playerDevCards[playerIdx];
    if (cards.length === 0) return;

    // Group cards by type and count
    const counts = {};
    cards.forEach(cardType => {
        if (cardType === null || cardType === undefined) return;
        const key = String(cardType);
        counts[key] = (counts[key] || 0) + 1;
    });

    // Render one icon per type with multiplier
    Object.entries(counts).forEach(([cardType, count]) => {
        const group = document.createElement('div');
        group.className = 'dev-card-group';

        const img = document.createElement('img');
        img.className = 'dev-card-thumb';
        const asset = DEV_CARD_ASSETS[cardType];
        if (asset) {
            img.src = ASSET_BASE + asset;
        } else {
            img.src = ASSET_BASE + 'desarrollo/caballero.png';
        }
        img.alt = CARD_TYPES[cardType] || DEV_CARD_NAMES[cardType] || '?';
        img.title = CARD_TYPES[cardType] || DEV_CARD_NAMES[cardType] || 'Carta';
        img.draggable = false;
        img.onerror = function() { this.style.display = 'none'; };
        group.appendChild(img);

        if (count > 1) {
            const mult = document.createElement('span');
            mult.className = 'dev-card-count';
            mult.textContent = 'x' + count;
            group.appendChild(mult);
        }

        container.appendChild(group);
    });
}

function renderAllDevCards() {
    if (!boardState.playerDevCards) return;
    for (let p = 0; p < 4; p++) {
        renderPlayerDevCards(p);
    }
}

function highlightActivePlayer(playerIdx) {
    $$('.player-card').forEach(card => card.classList.remove('active-turn'));
    const card = $(`#player-card-${playerIdx}`);
    if (card) card.classList.add('active-turn');

    const infoEl = $('#info-active-player');
    if (infoEl) {
        infoEl.textContent = PLAYER_NAMES[playerIdx];
        infoEl.style.backgroundColor = PLAYER_COLOR_HEX[playerIdx];
        infoEl.style.color = '#FFF';
    }
}

// ============================================================
// NAVIGATION LOGIC
// ============================================================
function getTurnData() {
    if (!gameData || roundKeys.length === 0) return null;
    const roundKey = roundKeys[currentRound];
    if (!roundKey) return null;
    const round = gameData.game[roundKey];
    if (!round) return null;
    const turnKey = 'turn_P' + currentTurn;
    return round[turnKey] || null;
}

function getPhaseNames() {
    return ['Inicio de Turno', 'Comercio', 'Construcción', 'Fin de Turno'];
}

function addTurnSeparator(playerIdx) {
    const container = $('#log-container');
    const empty = container.querySelector('.empty-log');
    if (empty) empty.remove();

    const sep = document.createElement('div');
    sep.className = 'log-turn-separator';
    sep.innerHTML = `Turno de <span class="separator-player pname-${playerIdx}">${PLAYER_NAMES[playerIdx]}</span> — Ronda ${currentRound + 1}`;
    container.appendChild(sep);
    container.scrollTop = container.scrollHeight;

    // Also clear commerce for new turn
    const cc = $('#commerce-container');
    cc.innerHTML = '<div class="empty-log"><p>Los comercios de este turno aparecerán aquí</p></div>';
}

function applyCurrentPhase() {
    const turn = getTurnData();
    if (!turn) return;

    highlightActivePlayer(currentTurn);

    // Insert turn separator at the start of each turn (phase 0)
    if (currentPhase === 0) {
        addTurnSeparator(currentTurn);
    }

    switch (currentPhase) {
        case 0: applyStartTurn(turn.start_turn); break;
        case 1: applyCommerce(turn.commerce_phase); break;
        case 2: applyBuild(turn.build_phase); break;
        case 3: applyEndTurn(turn.end_turn); break;
    }
}


function highlightProducingHexes(diceValue) {
    // Remove previous highlights
    document.querySelectorAll('.hex.hex-producing').forEach(el => {
        el.classList.remove('hex-producing');
    });

    if (!boardState.terrain || !diceValue || diceValue === 7) return;

    boardState.terrain.forEach((terrain, idx) => {
        if (terrain.probability === diceValue && terrain.terrain_type !== -1) {
            const hexEl = document.getElementById('hex-' + idx);
            if (hexEl) {
                hexEl.classList.add('hex-producing');
                setTimeout(() => hexEl.classList.remove('hex-producing'), 2500);
            }
        }
    });
}

function applyStartTurn(data) {
    if (!data) return;

    const dice = data.dice;
    const player = parseInt(data.actual_player);

    // Update dice display with player color
    const diceEl = $('#dice-display');
    diceEl.classList.remove('hidden', 'dice-player-0', 'dice-player-1', 'dice-player-2', 'dice-player-3');
    diceEl.classList.add('dice-player-' + player);
    const diceVal = $('#dice-value');
    diceVal.textContent = dice;
    diceVal.classList.toggle('dice-seven', dice === 7);

    // Highlight hexes that produce resources for this dice roll
    highlightProducingHexes(dice);

    // Update hands (source: dice for resource distribution)
    updatePlayerHands(data, 'dice');

    // Log dice roll
    addLog(
        `🎲 <span class="pname-${player}">${PLAYER_NAMES[player]}</span> lanza los dados: <strong>${dice}</strong>`,
        dice === 7 ? 'log-thief' : 'log-dice'
    );

    // Development cards played at start of turn
    if (data.development_card_played && data.development_card_played.length > 0) {
        data.development_card_played.forEach(cardInfo => {
            handleDevCardPlayed(cardInfo, player);
        });
    }

    // Thief movement
    if (dice === 7 || data.thief_terrain !== undefined) {
        if (data.past_thief_terrain !== undefined && data.thief_terrain !== undefined) {
            boardState.thiefTerrain = data.thief_terrain;
            renderRobber();

            addLog(
                `🥷 Ladrón movido del terreno ${data.past_thief_terrain} al terreno ${data.thief_terrain}`,
                'log-thief'
            );

            if (data.robbed_player !== undefined && data.robbed_player !== -1) {
                const stolen = data.stolen_material_id;
                const stolenName = stolen >= 0 ? Object.values(RESOURCE_NAMES)[stolen] : 'nada';
                addLog(
                    `🥷 <span class="pname-${player}">${PLAYER_NAMES[player]}</span> roba <strong>${stolenName}</strong> a <span class="pname-${data.robbed_player}">${PLAYER_NAMES[data.robbed_player]}</span>`,
                    'log-thief'
                );
            }
        }
    }
}

function applyCommerce(data) {
    if (!data || data.length === 0) return;

    const commerceContainer = $('#commerce-container');
    commerceContainer.innerHTML = '';
    const activePlayer = currentTurn;

    data.forEach((trade, idx) => {
        // Update hands from every commerce entry
        if (trade['hand_P0']) {
            updatePlayerHands(trade, 'trade');
        }

        // Skip null/None/empty/played_card trade offers for logging purposes
        if (!trade.trade_offer || trade.trade_offer === 'None' || trade.trade_offer === null) {
            addLog(`${resIcon('wood')} Sin comercio en esta fase`, 'log-trade');
            return;
        }
        if (trade.trade_offer === 'played_card') {
            return;
        }
        if (typeof trade.trade_offer !== 'object') {
            return;
        }

        if (trade.harbor_trade || typeof trade.trade_offer.gives === 'number') {
            // Harbor/bank trade — show quantities
            const ratio = trade.trade_ratio || 4;
            const givesStr = formatTradeOffer(trade.trade_offer.gives, ratio);
            const recvStr = formatTradeOffer(trade.trade_offer.receives, 1);
            addLog(
                `<span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span> comercia con ${ratio === 4 ? 'banca (4:1)' : ratio === 3 ? 'puerto (3:1)' : 'puerto especial (2:1)'} — Da: ${givesStr} → Recibe: ${recvStr}`,
                'log-trade'
            );
            addCommerceLog(
                `<span class="commerce-header">Comercio ${ratio}:1</span><br>` +
                `<span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span> da ${givesStr} y recibe ${recvStr}`
            );
        } else {
            // Player trade
            const gives = formatTradeResources(trade.trade_offer.gives);
            const receives = formatTradeResources(trade.trade_offer.receives);

            if (trade.inviable) {
                addLog(
                    `<span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span> intenta ofrecer: ${gives} a cambio de: ${receives} — <em class="trade-inviable">Inviable (no tiene recursos suficientes)</em>`,
                    'log-trade log-warning'
                );
                addCommerceLog(
                    `<span class="commerce-header">Oferta inviable</span><br>` +
                    `<span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span> no puede ofrecer ${gives}`
                );
            } else {
                addLog(
                    `<span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span> ofrece: ${gives} | Pide: ${receives}`,
                    'log-trade'
                );

                addCommerceLog(
                    `<span class="commerce-header">Oferta de <span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span></span><br>` +
                    `Da: ${gives} &nbsp;|&nbsp; Pide: ${receives}`
                );
            }

            // Process answers
            if (trade.answers) {
                trade.answers.forEach((playerAnswers) => {
                    if (!Array.isArray(playerAnswers) || playerAnswers.length === 0) return;

                    const respondent = playerAnswers[0].receiver;
                    const last = playerAnswers[playerAnswers.length - 1];
                    const completed = last.completed === true;
                    const accepted = last.response === true;
                    const hadCounterOffers = playerAnswers.length > 1;

                    let status, statusClass;
                    if (completed) {
                        status = 'Acepta y se realiza el intercambio';
                        statusClass = 'trade-accepted';
                    } else if (accepted && !completed) {
                        status = 'Acepta pero recursos insuficientes para ejecutar';
                        statusClass = 'trade-warning';
                    } else if (hadCounterOffers) {
                        status = 'Rechaza (hubo contra-ofertas sin acuerdo)';
                        statusClass = 'trade-rejected';
                    } else {
                        status = 'Rechaza la oferta';
                        statusClass = 'trade-rejected';
                    }

                    addCommerceLog(
                        `<span class="pname-${respondent}">${PLAYER_NAMES[respondent] || 'J?'}</span> → <span class="${statusClass}">${status}</span>`
                    );
                });
            }
        }
    });
}

function applyBuild(data) {
    if (!data || data.length === 0) return;

    data.forEach(build => {
        if (build.building === 'None') {
            addLog(`🔨 Sin construcciones en esta fase`, 'log-build');
            return;
        }

        switch (build.building) {
            case 'town': {
                const nodeIdx = build.node_id;
                if (boardState.nodes[nodeIdx]) {
                    boardState.nodes[nodeIdx].player = currentTurn;
                    boardState.nodes[nodeIdx].has_city = false;
                }
                addLog(
                    `🏠 <span class="pname-${currentTurn}">${PLAYER_NAMES[currentTurn]}</span> construye <strong>poblado</strong> en nodo ${nodeIdx}`,
                    'log-build'
                );
                break;
            }
            case 'city': {
                const nodeIdx = build.node_id;
                if (boardState.nodes[nodeIdx]) {
                    boardState.nodes[nodeIdx].has_city = true;
                }
                addLog(
                    `🏰 <span class="pname-${currentTurn}">${PLAYER_NAMES[currentTurn]}</span> mejora a <strong>ciudad</strong> en nodo ${nodeIdx}`,
                    'log-build'
                );
                break;
            }
            case 'road': {
                const from = build.node_id;
                const to = build.road_to;
                boardState.roads.push({ from, to, player: currentTurn });
                addLog(
                    `🛤️ <span class="pname-${currentTurn}">${PLAYER_NAMES[currentTurn]}</span> construye <strong>camino</strong> ${from} → ${to}`,
                    'log-build'
                );
                break;
            }
            case 'card': {
                if (!build.finished) {
                    addLog(`🃏 <span class="pname-${currentTurn}">${PLAYER_NAMES[currentTurn]}</span> intenta comprar carta pero no puede`, 'log-card');
                    break;
                }
                const cardType = CARD_TYPES[build.card_type] || 'Desconocida';
                addLog(
                    `🃏 <span class="pname-${currentTurn}">${PLAYER_NAMES[currentTurn]}</span> compra carta de desarrollo: <strong>${cardType}</strong>`,
                    'log-card'
                );
                // Track dev card for player (only if valid card_type)
                if (boardState.playerDevCards && build.card_type !== null && build.card_type !== undefined) {
                    boardState.playerDevCards[currentTurn].push(build.card_type);
                    renderPlayerDevCards(currentTurn);
                }
                break;
            }
            case 'played_card': {
                const cardData = build.development_card_played || {};
                handleBuildPhaseCard(cardData, currentTurn);
                break;
            }
            default:
                addLog(`🔨 Acción: ${build.building}`, 'log-build');
        }
    });

    // Update hands after builds (from backend hand snapshots)
    if (data.length > 0) {
        // Use the last build entry that has hand data
        for (let i = data.length - 1; i >= 0; i--) {
            if (data[i]['hand_P0']) {
                updatePlayerHands(data[i], 'build');
                break;
            }
        }
    }

    // Re-render board elements that changed
    renderNodes();
    renderRoads();
}

function applyEndTurn(data) {
    if (!data) return;

    // Update victory points
    if (data.victory_points) {
        updateVictoryPoints(data.victory_points);

        // Check for winner
        for (let p = 0; p < 4; p++) {
            const vp = parseInt(data.victory_points['J' + p]);
            if (vp >= 10) {
                addLog(
                    `🏆 ¡<span class="pname-${p}">${PLAYER_NAMES[p]}</span> GANA con ${vp} puntos de victoria!`,
                    'log-victory'
                );
                showVictory(p, vp);
            }
        }
    }

    // Update final hands
    if (data['hand_P0']) {
        updatePlayerHands(data, null);
    }

    // Development cards played at end of turn
    if (data.development_card_played && data.development_card_played.length > 0) {
        data.development_card_played.forEach(cardInfo => {
            // Filter out failed_victory_point spam from the log
            if (cardInfo && cardInfo.played_card === 'failed_victory_point') return;
            // Use the proper handler that supports both objects and numbers
            handleDevCardPlayed(cardInfo, currentTurn);
        });
    }

    addLog(`✅ Fin del turno de <span class="pname-${currentTurn}">${PLAYER_NAMES[currentTurn]}</span>`, 'log-phase');
}

// ============================================================
// DEVELOPMENT CARD HANDLERS
// ============================================================
const DEV_CARD_NAMES = {
    knight: '⚔️ Caballero',
    road_building: '🛤️ Construcción de Caminos',
    year_of_plenty: '🌾 Año de Abundancia',
    monopoly: '💰 Monopolio',
    victory_point: '⭐ Punto de Victoria',
    failed_victory_point: '❌ Punto de Victoria (fallido)'
};

function handleDevCardPlayed(cardInfo, player) {
    if (typeof cardInfo === 'number') {
        addLog(
            `🃏 <span class="pname-${player}">${PLAYER_NAMES[player]}</span> juega carta: <strong>${CARD_TYPES[cardInfo] || 'Desconocida'}</strong>`,
            'log-card'
        );
        return;
    }

    const cardName = DEV_CARD_NAMES[cardInfo.played_card] || cardInfo.played_card || 'Desconocida';
    const pName = `<span class="pname-${player}">${PLAYER_NAMES[player]}</span>`;

    switch (cardInfo.played_card) {
        case 'knight':
            addLog(`🃏 ${pName} juega ${cardName} (total: ${cardInfo.total_knights || '?'})`, 'log-card');
            if (cardInfo.thief_terrain !== undefined) {
                boardState.thiefTerrain = cardInfo.thief_terrain;
                renderRobber();
                addLog(`🥷 Ladrón movido al terreno ${cardInfo.thief_terrain}`, 'log-thief');
                if (cardInfo.robbed_player !== undefined && cardInfo.robbed_player !== -1) {
                    const stolen = cardInfo.stolen_material_id;
                    const stolenName = stolen >= 0 ? Object.values(RESOURCE_NAMES)[stolen] : 'nada';
                    addLog(`🥷 Roba <strong>${stolenName}</strong> a ${PLAYER_NAMES[cardInfo.robbed_player]}`, 'log-thief');
                }
            }
            break;
        case 'failed_victory_point':
            addLog(`🃏 ${pName} intenta jugar ${cardName}`, 'log-card');
            break;
        default:
            addLog(`🃏 ${pName} juega <strong>${cardName}</strong>`, 'log-card');
    }
}

function handleBuildPhaseCard(cardData, player) {
    const cardName = DEV_CARD_NAMES[cardData.played_card] || cardData.played_card || 'Carta';
    const pName = `<span class="pname-${player}">${PLAYER_NAMES[player]}</span>`;

    switch (cardData.played_card) {
        case 'road_building':
            addLog(`🃏 ${pName} juega <strong>${cardName}</strong>`, 'log-card');
            if (cardData.roads) {
                const r = cardData.roads;
                if (r.node_id !== undefined && r.road_to !== undefined) {
                    boardState.roads.push({ from: r.node_id, to: r.road_to, player });
                    addLog(`🛤️ Camino gratis: ${r.node_id} → ${r.road_to}`, 'log-build');
                }
                if (r.node_id_2 !== undefined && r.road_to_2 !== undefined) {
                    boardState.roads.push({ from: r.node_id_2, to: r.road_to_2, player });
                    addLog(`🛤️ Camino gratis: ${r.node_id_2} → ${r.road_to_2}`, 'log-build');
                }
            }
            break;
        case 'year_of_plenty':
            addLog(`🃏 ${pName} juega <strong>${cardName}</strong>`, 'log-card');
            if (cardData.materials_selected) {
                const m1 = Object.values(RESOURCE_NAMES)[cardData.materials_selected.material] || '?';
                const m2 = Object.values(RESOURCE_NAMES)[cardData.materials_selected.material_2] || '?';
                addLog(`🌾 Recibe: ${m1} + ${m2}`, 'log-resource');
            }
            break;
        case 'monopoly':
            addLog(`🃏 ${pName} juega <strong>${cardName}</strong>`, 'log-card');
            break;
        case 'knight':
            handleDevCardPlayed(cardData, player);
            break;
        case 'failed_victory_point':
            addLog(`🃏 ${pName} intenta jugar Punto de Victoria (fallido)`, 'log-card');
            break;
        default:
            addLog(`🃏 ${pName} juega carta: <strong>${cardName}</strong>`, 'log-card');
    }
}

// ============================================================
// NAVIGATION CONTROLS
// ============================================================
function nextPhase() {
    if (!gameData) return;

    currentPhase++;
    if (currentPhase > 3) {
        currentPhase = 0;
        currentTurn++;
        if (currentTurn > 3) {
            currentTurn = 0;
            currentRound++;
            if (currentRound >= roundKeys.length) {
                currentRound = roundKeys.length - 1;
                currentTurn = 3;
                currentPhase = 3;
                stopPlay();
                addLog('🏁 Fin de la partida', 'log-victory');
                return;
            }
        }
        // Check if turn exists, skip if not
        const turn = getTurnData();
        if (!turn) {
            nextPhase();
            return;
        }
    }

    applyCurrentPhase();
    updateUI();
}

function prevPhase() {
    if (!gameData) return;

    currentPhase--;
    if (currentPhase < 0) {
        currentPhase = 3;
        currentTurn--;
        if (currentTurn < 0) {
            currentTurn = 3;
            currentRound--;
            if (currentRound < 0) {
                currentRound = 0;
                currentTurn = 0;
                currentPhase = 0;
                clearEventLog();
                rebuildState();
                replayLogUpToCurrent();
                applyCurrentPhase();
                updateUI();
                return;
            }
        }
    }

    // Rebuild state from scratch for this position
    clearEventLog();
    rebuildState();
    replayLogUpToCurrent();
    applyCurrentPhase();
    updateUI();
}


function replayLogUpToCurrent() {
    // Replay all log events from the start up to (but NOT including) the current phase.
    // The current phase is handled by applyCurrentPhase() to avoid duplication.
    if (!gameData) return;

    for (let r = 0; r <= currentRound; r++) {
        const roundKey = roundKeys[r];
        if (!roundKey) continue;
        const round = gameData.game[roundKey];
        if (!round) continue;

        const maxTurn = (r === currentRound) ? currentTurn : 3;

        for (let t = 0; t <= maxTurn; t++) {
            const turn = round['turn_P' + t];
            if (!turn) continue;

            const maxPhase = (r === currentRound && t === currentTurn) ? currentPhase - 1 : 3;

            // Save/restore globals so addLog timestamps are correct
            const savedRound = currentRound;
            const savedTurn = currentTurn;
            const savedPhase = currentPhase;
            currentRound = r;
            currentTurn = t;

            // Add turn separator for every replayed turn
            if (maxPhase >= 0) {
                addTurnSeparator(t);
            }

            // Phase 0: start_turn
            if (maxPhase >= 0 && turn.start_turn) {
                currentPhase = 0;
                applyStartTurnLog(turn.start_turn, t);
            }

            // Phase 1: commerce
            if (maxPhase >= 1 && turn.commerce_phase) {
                currentPhase = 1;
                applyCommerceLog(turn.commerce_phase);
            }

            // Phase 2: build
            if (maxPhase >= 2 && turn.build_phase) {
                currentPhase = 2;
                applyBuildLog(turn.build_phase, t);
            }

            // Phase 3: end_turn
            if (maxPhase >= 3 && turn.end_turn) {
                currentPhase = 3;
                applyEndTurnLog(turn.end_turn, t);
            }

            currentRound = savedRound;
            currentTurn = savedTurn;
            currentPhase = savedPhase;
        }
    }
}

function applyStartTurnLog(data, player) {
    if (!data || !data.dice) return;
    const dice = data.dice;
    addLog(
        `🎲 <span class="pname-${player}">${PLAYER_NAMES[player]}</span> lanza los dados: <strong>${dice}</strong>`,
        dice === 7 ? 'log-thief' : 'log-dice'
    );
    if (data.development_card_played && data.development_card_played.length > 0) {
        data.development_card_played.forEach(cardInfo => {
            handleDevCardPlayedLog(cardInfo, player);
        });
    }
    if (data.past_thief_terrain !== undefined && data.thief_terrain !== undefined) {
        addLog(`🥷 Ladrón movido del terreno ${data.past_thief_terrain} al terreno ${data.thief_terrain}`, 'log-thief');
        if (data.robbed_player !== undefined && data.robbed_player !== -1) {
            const stolen = data.stolen_material_id;
            const stolenName = stolen >= 0 ? Object.values(RESOURCE_NAMES)[stolen] : 'nada';
            addLog(`🥷 <span class="pname-${player}">${PLAYER_NAMES[player]}</span> roba <strong>${stolenName}</strong> a <span class="pname-${data.robbed_player}">${PLAYER_NAMES[data.robbed_player]}</span>`, 'log-thief');
        }
    }
}

function handleDevCardPlayedLog(cardInfo, player) {
    if (typeof cardInfo === 'number') {
        addLog(`🃏 <span class="pname-${player}">${PLAYER_NAMES[player]}</span> juega carta: <strong>${CARD_TYPES[cardInfo] || 'Desconocida'}</strong>`, 'log-card');
        return;
    }
    if (cardInfo && cardInfo.played_card === 'failed_victory_point') return;
    const cardName = DEV_CARD_NAMES[cardInfo.played_card] || cardInfo.played_card || 'Desconocida';
    const pName = `<span class="pname-${player}">${PLAYER_NAMES[player]}</span>`;
    if (cardInfo.played_card === 'knight') {
        addLog(`🃏 ${pName} juega ${cardName} (total: ${cardInfo.total_knights || '?'})`, 'log-card');
        if (cardInfo.thief_terrain !== undefined) {
            addLog(`🥷 Ladrón movido al terreno ${cardInfo.thief_terrain}`, 'log-thief');
            if (cardInfo.robbed_player !== undefined && cardInfo.robbed_player !== -1) {
                const stolen = cardInfo.stolen_material_id;
                const stolenName = stolen >= 0 ? Object.values(RESOURCE_NAMES)[stolen] : 'nada';
                addLog(`🥷 Roba <strong>${stolenName}</strong> a ${PLAYER_NAMES[cardInfo.robbed_player]}`, 'log-thief');
            }
        }
    } else {
        addLog(`🃏 ${pName} juega <strong>${cardName}</strong>`, 'log-card');
    }
}

function applyCommerceLog(data) {
    if (!data || data.length === 0) return;
    const activePlayer = currentTurn;
    data.forEach(trade => {
        if (!trade.trade_offer || trade.trade_offer === 'None' || trade.trade_offer === null) return;
        if (trade.trade_offer === 'played_card') return;
        if (typeof trade.trade_offer !== 'object') return;
        if (trade.harbor_trade || typeof trade.trade_offer.gives === 'number') {
            const ratio = trade.trade_ratio || 4;
            addLog(`<span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span> comercia con ${ratio === 4 ? 'banca' : 'puerto'} (${ratio}:1) — Da: ${formatTradeOffer(trade.trade_offer.gives, ratio)} → Recibe: ${formatTradeOffer(trade.trade_offer.receives, 1)}`, 'log-trade');
        } else {
            const gives = formatTradeResources(trade.trade_offer.gives);
            const receives = formatTradeResources(trade.trade_offer.receives);
            if (trade.inviable) {
                addLog(`<span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span> intenta ofrecer: ${gives} a cambio de: ${receives} — <em class="trade-inviable">Inviable</em>`, 'log-trade log-warning');
            } else {
                addLog(`<span class="pname-${activePlayer}">${PLAYER_NAMES[activePlayer]}</span> ofrece: ${gives} | Pide: ${receives}`, 'log-trade');
            }
        }
    });
}

function applyBuildLog(data, player) {
    if (!data || data.length === 0) return;
    data.forEach(build => {
        if (build.building === 'None') return;
        const pName = `<span class="pname-${player}">${PLAYER_NAMES[player]}</span>`;
        switch (build.building) {
            case 'town': addLog(`🏠 ${pName} construye <strong>poblado</strong> en nodo ${build.node_id}`, 'log-build'); break;
            case 'city': addLog(`🏰 ${pName} mejora a <strong>ciudad</strong> en nodo ${build.node_id}`, 'log-build'); break;
            case 'road': addLog(`🛤️ ${pName} construye <strong>camino</strong> ${build.node_id} → ${build.road_to}`, 'log-build'); break;
            case 'card':
                if (build.finished) {
                    const cardType = CARD_TYPES[build.card_type] || 'Desconocida';
                    addLog(`🃏 ${pName} compra carta de desarrollo: <strong>${cardType}</strong>`, 'log-card');
                }
                break;
            case 'played_card':
                if (build.development_card_played) {
                    handleDevCardPlayedLog(build.development_card_played, player);
                }
                break;
        }
    });
}

function applyEndTurnLog(data, player) {
    if (!data) return;
    if (data.development_card_played && data.development_card_played.length > 0) {
        data.development_card_played.forEach(cardInfo => {
            if (cardInfo && cardInfo.played_card === 'failed_victory_point') return;
            handleDevCardPlayedLog(cardInfo, player);
        });
    }
    addLog(`✅ Fin del turno de <span class="pname-${player}">${PLAYER_NAMES[player]}</span>`, 'log-phase');
}

function nextRound() {
    if (!gameData) return;
    if (currentRound < roundKeys.length - 1) {
        currentRound++;
        currentTurn = 0;
        currentPhase = 0;
        clearEventLog();
        rebuildState();
        replayLogUpToCurrent();
        applyCurrentPhase();
        updateUI();
    }
}

function prevRound() {
    if (!gameData) return;
    if (currentRound > 0) {
        currentRound--;
        currentTurn = 0;
        currentPhase = 0;
        clearEventLog();
        rebuildState();
        replayLogUpToCurrent();
        applyCurrentPhase();
        updateUI();
    }
}

function goToStart() {
    if (!gameData) return;
    currentRound = 0;
    currentTurn = 0;
    currentPhase = 0;
    clearEventLog();
    rebuildState();
    replayLogUpToCurrent();
    applyCurrentPhase();
    updateUI();
    stopPlay();
}

function goToEnd() {
    if (!gameData) return;
    // Find the actual last available turn/phase
    currentRound = roundKeys.length - 1;
    const lastRound = gameData.game[roundKeys[currentRound]];
    if (!lastRound) return;

    // Find last available turn
    currentTurn = 3;
    while (currentTurn >= 0 && !lastRound['turn_P' + currentTurn]) {
        currentTurn--;
    }
    if (currentTurn < 0) { currentTurn = 0; }

    currentPhase = 3;
    clearEventLog();
    rebuildState();
    replayLogUpToCurrent();
    applyCurrentPhase();
    updateUI();
    stopPlay();
}

function togglePlay() {
    if (isPlaying) {
        stopPlay();
    } else {
        startPlay();
    }
}

function startPlay() {
    isPlaying = true;
    $('#btn-play').classList.add('playing');
    $('#play-icon').src = '../nuevos_assets/ui/boton_pause.png';
    playInterval = setInterval(nextPhase, playSpeed);
}

function stopPlay() {
    isPlaying = false;
    $('#btn-play').classList.remove('playing');
    $('#play-icon').src = '../nuevos_assets/ui/boton_play.png';
    if (playInterval) {
        clearInterval(playInterval);
        playInterval = null;
    }
}

// ============================================================
// STATE REBUILD (for going backwards)
// ============================================================
function rebuildState() {
    // Reset board to setup state
    boardState.nodes = JSON.parse(JSON.stringify(gameData.setup.board.board_nodes));
    boardState.roads = [];
    boardState.playerDevCards = [[], [], [], []];

    // Re-apply setup
    for (let p = 0; p < 4; p++) {
        const placements = gameData.setup['P' + p];
        if (!placements) continue;
        for (const placement of placements) {
            if (boardState.nodes[placement.id]) {
                boardState.nodes[placement.id].player = p;
                boardState.nodes[placement.id].has_city = false;
            }
            boardState.roads.push({ from: placement.id, to: placement.road, player: p });
        }
    }

    // Reset thief
    boardState.thiefTerrain = boardState.terrain.findIndex(t => t.has_thief);
    if (boardState.thiefTerrain === -1) {
        boardState.thiefTerrain = boardState.terrain.findIndex(t => t.terrain_type === -1);
    }

    // Track the latest hand and VP data as we replay
    let latestHands = {};
    let latestVP = {};

    // Replay all phases up to current position
    for (let r = 0; r <= currentRound; r++) {
        const roundKey = roundKeys[r];
        if (!roundKey) continue;
        const round = gameData.game[roundKey];
        if (!round) continue;

        const maxTurn = (r === currentRound) ? currentTurn : 3;

        for (let t = 0; t <= maxTurn; t++) {
            const turnKey = 'turn_P' + t;
            const turn = round[turnKey];
            if (!turn) continue;

            const maxPhase = (r === currentRound && t === currentTurn) ? currentPhase - 1 : 3;

            // Apply start_turn for thief + hands + dev cards
            if (maxPhase >= 0 && turn.start_turn) {
                if (turn.start_turn.thief_terrain !== undefined) {
                    boardState.thiefTerrain = turn.start_turn.thief_terrain;
                }
                // Handle dev cards played at start (e.g., knight)
                if (turn.start_turn.development_card_played) {
                    turn.start_turn.development_card_played.forEach(cd => {
                        if (cd.thief_terrain !== undefined) {
                            boardState.thiefTerrain = cd.thief_terrain;
                        }
                    });
                }
                // Capture latest hands
                for (let p = 0; p < 4; p++) {
                    if (turn.start_turn['hand_P' + p]) {
                        latestHands['hand_P' + p] = turn.start_turn['hand_P' + p];
                        latestHands['total_P' + p] = turn.start_turn['total_P' + p];
                    }
                }
            }

            // Apply commerce phase hands
            if (maxPhase >= 1 && turn.commerce_phase) {
                turn.commerce_phase.forEach(trade => {
                    for (let p = 0; p < 4; p++) {
                        if (trade['hand_P' + p]) {
                            latestHands['hand_P' + p] = trade['hand_P' + p];
                            latestHands['total_P' + p] = trade['total_P' + p];
                        }
                    }
                });
            }

            // Apply builds + capture hand snapshots
            if (maxPhase >= 2 && turn.build_phase) {
                turn.build_phase.forEach(build => {
                    // Capture hand snapshots from build phase
                    for (let p = 0; p < 4; p++) {
                        if (build['hand_P' + p]) {
                            latestHands['hand_P' + p] = build['hand_P' + p];
                            latestHands['total_P' + p] = build['total_P' + p];
                        }
                    }
                    if (build.building === 'None') return;
                    if (build.building === 'town') {
                        if (boardState.nodes[build.node_id]) {
                            boardState.nodes[build.node_id].player = t;
                            boardState.nodes[build.node_id].has_city = false;
                        }
                    } else if (build.building === 'city') {
                        if (boardState.nodes[build.node_id]) {
                            boardState.nodes[build.node_id].has_city = true;
                        }
                    } else if (build.building === 'road') {
                        boardState.roads.push({ from: build.node_id, to: build.road_to, player: t });
                    } else if (build.building === 'card' && build.finished && build.card_type !== null && build.card_type !== undefined) {
                        boardState.playerDevCards[t].push(build.card_type);
                    } else if (build.building === 'played_card') {
                        // Handle road_building dev card
                        const cd = build.development_card_played;
                        if (cd && cd.played_card === 'road_building' && cd.roads) {
                            const r = cd.roads;
                            if (r.node_id !== undefined && r.road_to !== undefined) {
                                boardState.roads.push({ from: r.node_id, to: r.road_to, player: t });
                            }
                            if (r.node_id_2 !== undefined && r.road_to_2 !== undefined) {
                                boardState.roads.push({ from: r.node_id_2, to: r.road_to_2, player: t });
                            }
                        }
                        // Handle knight card thief movement
                        if (cd && cd.played_card === 'knight' && cd.thief_terrain !== undefined) {
                            boardState.thiefTerrain = cd.thief_terrain;
                        }
                    }
                });
            }

            // Apply end_turn VP + hands
            if (maxPhase >= 3 && turn.end_turn) {
                if (turn.end_turn.victory_points) {
                    latestVP = turn.end_turn.victory_points;
                }
                for (let p = 0; p < 4; p++) {
                    if (turn.end_turn['hand_P' + p]) {
                        latestHands['hand_P' + p] = turn.end_turn['hand_P' + p];
                        latestHands['total_P' + p] = turn.end_turn['total_P' + p];
                    }
                }
            }
        }
    }

    // Apply latest hands and VP to the UI
    if (Object.keys(latestHands).length > 0) {
        previousHands = {}; // Don't show diff animations on rebuild
        updatePlayerHands(latestHands);
    }
    if (Object.keys(latestVP).length > 0) {
        updateVictoryPoints(latestVP);
    }

    // Re-render board + dev cards
    renderNodes();
    renderHarbors();
    renderRoads();
    renderRobber();
    renderAllDevCards();
}

// ============================================================
// UI UPDATE
// ============================================================
function updateUI() {
    // Round info
    $('#info-round').textContent = (currentRound + 1);
    $('#info-round-max').textContent = '/ ' + roundKeys.length;
    $('#info-turn').textContent = 'J' + (currentTurn + 1);
    $('#info-phase').textContent = getPhaseNames()[currentPhase];

    // Disable buttons at bounds
    $('#btn-prev').disabled = (currentRound === 0 && currentTurn === 0 && currentPhase === 0);
    $('#btn-prev-round').disabled = (currentRound === 0);
    $('#btn-next').disabled = (currentRound >= roundKeys.length - 1 && currentTurn >= 3 && currentPhase >= 3);
    $('#btn-next-round').disabled = (currentRound >= roundKeys.length - 1);
}

// ============================================================
// LOGGING
// ============================================================
function addLog(message, className) {
    const container = $('#log-container');

    // Remove empty state
    const empty = container.querySelector('.empty-log');
    if (empty) empty.remove();

    const entry = document.createElement('div');
    entry.className = 'log-entry ' + (className || '');

    const time = document.createElement('span');
    time.className = 'log-time';
    time.textContent = `R${currentRound + 1} T${currentTurn + 1}`;

    entry.appendChild(time);

    const content = document.createElement('span');
    content.innerHTML = ' ' + message;
    entry.appendChild(content);

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function addCommerceLog(message) {
    const container = $('#commerce-container');

    const empty = container.querySelector('.empty-log');
    if (empty) empty.remove();

    const entry = document.createElement('div');
    entry.className = 'log-entry log-trade';
    entry.innerHTML = message;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function clearLogs() {
    $('#log-container').innerHTML = '<div class="empty-log"><p>📜 Carga una partida para ver los eventos</p></div>';
    $('#commerce-container').innerHTML = '<div class="empty-log"><p>🤝 Los comercios aparecerán aquí</p></div>';
}


function clearEventLog() {
    const container = $('#log-container');
    // Remove all entries AND separators
    container.querySelectorAll('.log-entry, .log-turn-separator').forEach(e => e.remove());

    // Also clear commerce container and restore placeholder
    const cc = $('#commerce-container');
    cc.innerHTML = '<div class="empty-log"><p>Los comercios de este turno aparecerán aquí</p></div>';
}



// ============================================================
// FORMATTING HELPERS
// ============================================================
function resIcon(resName) {
    // Returns an inline <img> tag for the resource, replacing emojis
    if (RESOURCE_IMG[resName]) {
        return `<img class="res-icon-inline" src="${ASSET_BASE}${RESOURCE_IMG[resName]}" alt="${RESOURCE_NAMES[resName]}" title="${RESOURCE_NAMES[resName]}">`;
    }
    return RESOURCE_ICONS[resName] || resName;
}

function formatTradeResources(offer) {
    if (!offer || typeof offer !== 'object') return String(offer);
    const parts = [];
    const resources = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
    resources.forEach(res => {
        const val = parseInt(offer[res]) || 0;
        if (val > 0) {
            parts.push(`${resIcon(res)}<span class="res-qty">${val}</span>`);
        }
    });
    return parts.length > 0 ? parts.join(' ') : 'nada';
}

const MAT_ID_TO_NAME = {0: 'cereal', 1: 'mineral', 2: 'clay', 3: 'wood', 4: 'wool'};

function formatTradeOffer(offer, ratio) {
    if (typeof offer === 'number') {
        const matName = MAT_ID_TO_NAME[offer];
        if (matName) {
            const qty = ratio ? `x${ratio}` : '';
            return `${resIcon(matName)} ${RESOURCE_NAMES[matName]}${qty ? ' ' + qty : ''}`;
        }
        return String(offer);
    }
    return formatTradeResources(offer);
}

// ============================================================
// VICTORY
// ============================================================
function showVictory(playerIdx, points) {
    const modal = $('#victory-modal');
    const text = $('#winner-text');
    text.innerHTML = `<span class="pname-${playerIdx}" style="font-size: 1.5rem;">${PLAYER_NAMES[playerIdx]}</span> gana con <strong>${points}</strong> puntos de victoria`;
    modal.classList.remove('hidden');
    stopPlay();
}

// ============================================================
// MODAL HELPERS
// ============================================================
function showModal(id) {
    $('#' + id).classList.remove('hidden');
}

function hideModal(id) {
    $('#' + id).classList.add('hidden');
    // Reset file input
    if (id === 'upload-modal') {
        $('#file-input').value = '';
        selectedFile = null;
        $('#file-info').classList.add('hidden');
        $('#modal-load').disabled = true;
    }
}
