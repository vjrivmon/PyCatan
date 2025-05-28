let game_obj = {};
let round_obj = {};
let turn_obj = {};
let phase_obj = {};

let game_direction = 'forward'; // or "backward"
let autoPlayInterval = null;
let isPlaying = false;


function init_events() {
    let input = jQuery('#get_file');
    let load_game = jQuery('#load_game');
    
    // Inicializar controles de auto-play
    initAutoPlayControls();
    
    // Modificar el comportamiento del botón para abrir el modal en lugar del selector de archivos
    load_game.on('click', function (e) {
        $('#uploadModal').modal('show');
    });

    // Inicializar el área de arrastrar y soltar
    const dropArea = document.getElementById('drop-area');
    const fileSelector = document.getElementById('file-selector');
    const selectedFileDisplay = document.getElementById('selected-file');
    const loadSelectedFileBtn = document.getElementById('load-selected-file');
    let selectedFile = null;

    // Evitar comportamiento predeterminado de arrastrar y soltar
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Resaltar el área al arrastrar un archivo
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('highlight');
    }

    function unhighlight() {
        dropArea.classList.remove('highlight');
    }

    // Manejar el archivo soltado
    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Manejar selección de archivo con el selector
    fileSelector.addEventListener('change', function(e) {
        handleFiles(this.files);
    });

    // Procesar archivos seleccionados
    function handleFiles(files) {
        console.log('[DEBUG] handleFiles llamado. Archivos:', files); 
        if (files.length) {
            selectedFile = files[0];
            console.log('[DEBUG] Archivo seleccionado:', selectedFile.name, 'Tipo:', selectedFile.type, 'Tamaño:', selectedFile.size);
            
            const isJsonType = selectedFile.type === 'application/json';
            const isJsonExtension = selectedFile.name.endsWith('.json');
            console.log('[DEBUG] Verificación de tipo: esJsonType =', isJsonType, ', esJsonExtension =', isJsonExtension);

            if (isJsonType || isJsonExtension) {
                console.log('[DEBUG] El archivo es JSON.');
                loadSelectedFileBtn.disabled = false;
                console.log('[DEBUG] Botón Cargar HABILITADO.');
            } else {
                console.warn('[DEBUG] El archivo NO es JSON. Tipo detectado:', selectedFile.type, 'Nombre:', selectedFile.name);
                loadSelectedFileBtn.disabled = true;
                selectedFile = null; 
                console.log('[DEBUG] Botón Cargar DESHABILITADO y selectedFile limpiado.');
            }
        } else {
            console.log('[DEBUG] No se seleccionaron archivos (files.length es 0).');
            loadSelectedFileBtn.disabled = true; 
            selectedFile = null;
        }
    }

    // Cargar el archivo seleccionado cuando se hace clic en el botón "Cargar"
    loadSelectedFileBtn.addEventListener('click', function() {
        console.log('[DEBUG] Botón "Cargar" del modal clickeado.'); // DEBUG
        if (selectedFile) {
            console.log('[DEBUG] selectedFile existe. Procediendo a leer:', selectedFile.name); // DEBUG
            // Leer y procesar el archivo
            let reader = new FileReader();
            reader.readAsText(selectedFile, "UTF-8");
            console.log('[DEBUG] FileReader.readAsText llamado.'); // DEBUG

            reader.onload = function (evt) {
                console.log('[DEBUG] FileReader.onload disparado.'); // DEBUG
                console.log('[DEBUG] Contenido crudo del archivo:', evt.target.result.substring(0, 500) + '...'); // Muestra los primeros 500 chars
                
                try {
                    game_obj = JSON.parse(evt.target.result);
                    console.log('[DEBUG] JSON parseado correctamente. game_obj:', game_obj); // DEBUG
                } catch (e) {
                    console.error('[DEBUG] Error al parsear JSON:', e); // DEBUG
                    alert('Error: El archivo JSON no es válido.');
                    // Limpiar selección en caso de error de parseo
                    selectedFile = null;
                    loadSelectedFileBtn.disabled = true;
                    $('#uploadModal').modal('hide'); // Opcional: cerrar modal en error
                    return;
                }
                
                console.log('[DEBUG] Antes de resetear tablero y contadores.'); // DEBUG
                // Resetear el tablero
                jQuery('.node').add('.road').add('.vertical_road').css('background', 'none').css('border', 'none').text('');
                $('#contador_rondas').val('').change();
                $('#contador_turnos').val('').change();
                $('#contador_fases').val('').change();
                console.log('[DEBUG] Tablero y contadores reseteados.'); // DEBUG
                
                // Detener la reproducción automática si está activa
                console.log('[DEBUG] Antes de stopAutoPlay().'); // DEBUG
                stopAutoPlay();
                console.log('[DEBUG] Después de stopAutoPlay().'); // DEBUG

                // Primero ejecutar setup para dibujar el tablero base y luego inicializar eventos con el juego
                console.log('[DEBUG] Antes de setup().'); // DEBUG
                setup(); 
                console.log('[DEBUG] Después de setup().'); // DEBUG
                
                // Inicializar juego con el objeto cargado
                console.log('[DEBUG] Antes de init_events_with_game_obj(). game_obj:', JSON.parse(JSON.stringify(game_obj))); // DEBUG
                init_events_with_game_obj();
                console.log('[DEBUG] Después de init_events_with_game_obj().'); // DEBUG

                console.log('[DEBUG] Antes de addLogFromJSON().'); // DEBUG
                addLogFromJSON();
                console.log('[DEBUG] Después de addLogFromJSON().'); // DEBUG

                console.log('[DEBUG] Antes de reset_game().'); // DEBUG
                reset_game(); // Resetear información de jugadores, etc.
                console.log('[DEBUG] Después de reset_game().'); // DEBUG
                
                // Actualizar UI con datos del JSON (esto repoblará info de jugadores, recursos, etc.)
                updateUIDataFromGameObj(game_obj); 
                console.log('[DEBUG] Después de updateUIDataFromGameObj().'); // DEBUG
                
                // Cerrar el modal
                $('#uploadModal').modal('hide');
                console.log('[DEBUG] Modal cerrado. Carga de partida completada.'); // DEBUG
                
                // Limpiar selección
                selectedFile = null;
                loadSelectedFileBtn.disabled = true;

                // Iniciar juego automáticamente si el botón play está presente y no deshabilitado
                // Esto asume que `initAutoPlayControls` ya ha sido llamado (ej. en `setup`)
                // y que el botón play/stop ya existe.
                if ($('#play_btn').length && !$('#play_btn').prop('disabled')) {
                     // Comprobamos si el juego tiene datos antes de intentar iniciar.
                    if (Object.keys(game_obj).length > 0) {
                        console.log('[DEBUG] Intentando iniciar reproducción automática después de cargar partida.');
                        // startAutoPlay(); // Descomentar si se desea que inicie solo al cargar.
                                          // Por ahora, el usuario debe dar al play.
                    } else {
                        console.warn('[DEBUG] game_obj está vacío, no se iniciará la reproducción automática.');
                    }
                }
            }
            reader.onerror = function (evt) {
                console.error('[DEBUG] FileReader.onerror disparado. Error:', evt); // DEBUG
                alert('Error al leer el archivo.');
            }
        } else {
            console.warn('[DEBUG] Botón "Cargar" clickeado, pero selectedFile es null.'); // DEBUG
        }
    });

    // Mantener la compatibilidad con el input original
    input.on('change', function (e) {
        let file = document.getElementById("get_file").files[0];
        if (file) {
            let reader = new FileReader();
            reader.readAsText(file, "UTF-8");
            reader.onload = function (evt) {
                game_obj = JSON.parse(evt.target.result);

                // TODO: Mejora a futuro: falta añadir "mayor ejercito" / "carretera más larga"
                init_events_with_game_obj();
                addLogFromJSON();
                setup();
                reset_game();
                // Renderizar perfiles de jugador y actualizar con datos del JSON
                // renderPlayerProfiles(); // ELIMINAR: Ya se llama dentro de setup()
                updateUIDataFromGameObj(game_obj); // Nueva función para poblar datos
            }
            reader.onerror = function (evt) {
                console.log('Error al cargar el archivo');
            }
        }

        for (let i = 1; i < 5; i++) {
            let textarea = $('#buildings_P' + i);
            textarea.text('');
        }
        game_obj = {};
        round_obj = {};
        turn_obj = {};
        phase_obj = {};
    });


    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
    
    // Inicializar el botón de play/stop
    initAutoPlayControls();
}

function reset_game() {
    // Limpiar completamente el tablero
    jQuery('.node').empty().removeAttr('style').removeClass('player-red player-blue player-green player-yellow');
    jQuery('.road').empty().removeAttr('style').removeClass('player-red player-blue player-green player-yellow');
    jQuery('.vertical_road').empty().removeAttr('style').removeClass('player-red player-blue player-green player-yellow');
    
    // Resetear estilos de los nodos y carreteras
    jQuery('.node').css({
        'background-color': '',
        'border': '',
        'border-radius': '',
        'transform': '',
        'z-index': ''
    });
    
    jQuery('.road, .vertical_road').css({
        'background-color': '',
        'border': '',
        'transform': '',
        'z-index': ''
    });
    
    // Limpiar logs
    jQuery('#commerce_log_text').html('');
    jQuery('#other_useful_info_text').html('');
    
    // Resetear puntos de victoria y recursos de todos los jugadores
    for (let i = 1; i <= 4; i++) {
        $('#puntos_victoria_J' + i).text('0');
        
        // Resetear recursos
        const resourceTypes = ['cereal', 'clay', 'wool', 'wood', 'mineral'];
        resourceTypes.forEach(resource => {
            $(`#hand_P${i-1} .resources-grid .${resource} .${resource}_quantity`).text('0');
        });
        
        // Resetear cartas de desarrollo
        const devCardTypes = ['knight', 'victory_point', 'road_building', 'year_of_plenty', 'monopoly'];
        devCardTypes.forEach(card => {
            $(`#hand_P${i-1} .dev-cards-grid .${card} .${card}_quantity`).text('0');
        });
        
        // Ocultar badges especiales
        $(`#largest_army_P${i-1}`).hide();
        $(`#longest_road_P${i-1}`).hide();
        
        // Remover clases de ganador
        $(`#player-card-${i-1}`).removeClass('winner-glow');
        
        // Resetear bordes de los paneles de jugadores
        $(`#hand_P${i-1}`).css('border', '');
    }
    
    // Resetear contadores
    jQuery('#contador_rondas').val('').empty();
    jQuery('#contador_turnos').val('').empty();
    jQuery('#contador_fases').val('').empty();
    
    // Resetear display de contadores
    jQuery('#contador_rondas_display').text('1');
    jQuery('#contador_turnos_display').text('1');
    jQuery('#contador_fases_display').text('1');
    jQuery('#rondas_maximas').text('');
    
    // Cerrar modal de victoria si está abierto
    $('#victory-modal').modal('hide');
    
    // Limpiar variables globales
    round_obj = {};
    turn_obj = {};
    phase_obj = {};
    
    // Limpiar animaciones y efectos
    $('.animate__animated').removeClass('animate__animated animate__bounceIn animate__pulse animate__fadeIn');
    $('.auto-play-indicator').remove();
    
    console.log('[DEBUG] Juego reseteado completamente');
}

function addLogFromJSON() {
    // Los inputs ocultos #contador_rondas, #contador_turnos, y #contador_fases
    // son inicializados y sus eventos 'change' son disparados por init_events_with_game_obj()
    // cuando la primera ronda es cargada. No es necesario (y es problemático)
    // re-establecerlos a '1' aquí y disparar 'change()' de nuevo.

    // Solo se asegura que los contadores visibles (spans) reflejen los valores
    // actuales de los inputs ocultos.
    updateVisibleCounters(); 

    // Establece el número máximo de rondas en la UI.
    if (game_obj && game_obj.game && Object.keys(game_obj.game).length > 0) {
        $('#rondas_maximas').text(Object.keys(game_obj.game).length);
    } else {
        // Si no hay juego o rondas, muestra '0' o 'N/A'
        $('#rondas_maximas').text('0'); 
        console.warn("[DEBUG] addLogFromJSON: game_obj.game no está definido o está vacío al intentar establecer rondas_maximas.");
    }
}

// Función para actualizar los contadores visibles (spans)
function updateVisibleCounters() {
    $('#contador_rondas_display').text($('#contador_rondas').val() || '1');
    $('#contador_turnos_display').text($('#contador_turnos').val() || '1');
    $('#contador_fases_display').text($('#contador_fases').val() || '1');
}

function addSetupBuildings() {
    setup_obj = game_obj['setup'];

    for (let i = 0; i < 4; i++) {
        let textarea = $('#buildings_P' + (i + 1))
        for (let j = 0; j < setup_obj['P' + i].length; j++) {
            let node = jQuery('#node_' + setup_obj['P' + i][j]['id']);
            let road = '';
            if (setup_obj['P' + i][j]['id'] < setup_obj['P' + i][j]['road']) {
                road = jQuery('#road_' + setup_obj['P' + i][j]['id'] + '_' + setup_obj['P' + i][j]['road']);
            } else {
                road = jQuery('#road_' + setup_obj['P' + i][j]['road'] + '_' + setup_obj['P' + i][j]['id']);
            }

            let str = 'node: ' + setup_obj['P' + i][j]['id'] + ' | ' + 'type: ' + 'T' + '\r\n';
            str += 'node: ' + setup_obj['P' + i][j]['id'] + ' | ' + 'road_to: ' + setup_obj['P' + i][j]['road'] + ' | ' + 'type: ' + 'R' + '\r\n';

            textarea.text(textarea.text() + str);

            paint_it_player_color(i, node);
            paint_it_player_color(i, road);

            // Agregar emoticonos para poblados y caminos iniciales
            let playerEmoji = getPlayerEmoji(i);
            let settlementEmoji = getBuildingEmoji('settlement');
            let roadEmoji = getBuildingEmoji('road');
            
            node.html('<i class="fa-solid fa-house"></i><span class="player-emoji">' + playerEmoji + '</span><span class="building-emoji">' + settlementEmoji + '</span>');
            road.html('<span class="player-emoji">' + playerEmoji + '</span><span class="building-emoji">' + roadEmoji + '</span>');
        }
    }
}

function terrainSetup() {
    terrain = game_obj['setup']['board']['board_terrain'];

    for (let i = 0; i < terrain.length; i++) {
        let terrain_div = jQuery('#terrain_' + i);
        let terrain_number = jQuery('#terrain_' + i + ' .terrain_number');

        html = '';
        if (terrain[i]['probability'] != 0) {
            if (terrain[i]['probability'] == 6 || terrain[i]['probability'] == 8) {
                html += '<span style="color: red;">';
            } else {
                html += '<span>';
            }
            html += terrain[i]['probability'] + '</span>';
        } else {
            html += '<i class="fa-solid fa-user-ninja fa-2x" data-toggle="tooltip" data-placement="top" title="Ladrón"></i>'
        }

        terrain_number.html(html);
        terrain_div.removeClass('terrain_cereal terrain_mineral terrain_clay terrain_wood terrain_wool terrain_desert')
        terrain_div.addClass(getTerrainTypeClass(terrain[i]['terrain_type']));
        //                terrain_div.text(terrain_div.text() + '');
    }
}

// Función mejorada para la visualización de puertos
function fromHarborNumberToMaterials(harborNumber) {
    switch (harborNumber) {
        case 0:
            return '<div class="harbor-content harbor-cereal"><i class="fa-solid fa-wheat-awn"></i><span>2:1</span></div>';
        case 1:
            return '<div class="harbor-content harbor-mineral"><i class="fa-solid fa-mountain-sun"></i><span>2:1</span></div>';
        case 2:
            return '<div class="harbor-content harbor-clay"><i class="fa-solid fa-trowel-bricks"></i><span>2:1</span></div>';
        case 3:
            return '<div class="harbor-content harbor-wood"><i class="fa-solid fa-wand-sparkles"></i><span>2:1</span></div>';
        case 4:
            return '<div class="harbor-content harbor-wool"><i class="fa-brands fa-cotton-bureau"></i><span>2:1</span></div>';
        case 5:
            return '<div class="harbor-content"><span>3:1</span></div>';
        case -1:
            return '';
        default:
            return '';
    }
}

// Función mejorada para configurar los nodos y sus puertos
function nodeSetup() {
    nodes = game_obj['setup']['board']['board_nodes'];

    for (let i = 0; i < nodes.length; i++) {
        let node = jQuery('#node_' + i);
        
        // Si el nodo tiene un valor de puerto, añadirlo
        if (nodes[i]['harbor'] !== -1) {
            node.addClass('is-harbor');
            node.attr('data-bs-toggle', 'tooltip');
            
            // Establecer título según el tipo de puerto
            let tooltipTitle = '';
            switch (nodes[i]['harbor']) {
                case 0:
                    tooltipTitle = 'Puerto de Cereal 2:1';
                    break;
                case 1:
                    tooltipTitle = 'Puerto de Mineral 2:1';
                    break;
                case 2:
                    tooltipTitle = 'Puerto de Ladrillo 2:1';
                    break;
                case 3:
                    tooltipTitle = 'Puerto de Madera 2:1';
                    break;
                case 4:
                    tooltipTitle = 'Puerto de Lana 2:1';
                    break;
                case 5:
                    tooltipTitle = 'Puerto 3:1';
                    break;
            }
            node.attr('title', tooltipTitle);
            
            // Añadir animación sutil al puerto
            gsap.to(node, {
                duration: 2,
                repeat: -1,
                yoyo: true,
                boxShadow: '0 0 15px rgba(52, 152, 219, 0.7)',
                ease: "sine.inOut"
            });
        }
        
        // Añadir contenido al nodo
        node.html(fromHarborNumberToMaterials(nodes[i]['harbor']));
    }
    
    // Inicializar tooltips para los puertos
    $('[data-bs-toggle="tooltip"]').tooltip();
}

function getTerrainTypeClass(terrainType) {
    switch (terrainType) {
        case 0:
            return 'terrain_cereal';
        case 1:
            return 'terrain_mineral';
        case 2:
            return 'terrain_clay';
        case 3:
            return 'terrain_wood';
        case 4:
            return 'terrain_wool';
        case -1:
            return 'terrain_desert';
        default:
            //            alert('Caso ilegal de terreno');
            break;
    }
}

function setup() {
    // Limpiar cualquier contenido previo del tablero para asegurar un estado limpio
    jQuery('.node').empty().removeAttr('style').removeClass('player-red player-blue player-green player-yellow');
    jQuery('.road').empty().removeAttr('style').removeClass('player-red player-blue player-green player-yellow');
    jQuery('.vertical_road').empty().removeAttr('style').removeClass('player-red player-blue player-green player-yellow');
    jQuery('.terrain .terrain_number').empty(); // Limpiar números de terreno
    jQuery('.fa-user-ninja').remove(); // Remover ladrón si existe

    // Renderizar el tablero base (terrenos, números, ladrón inicial y puertos)
    // Es importante que game_obj esté disponible aquí si se quiere cargar el estado del tablero desde el JSON
    if (game_obj && game_obj.setup && game_obj.setup.board) {
        terrainSetup(); // Dibuja terrenos, números de probabilidad y ladrón inicial
        nodeSetup();    // Dibuja los puertos en los nodos
        addSetupBuildings(); // Dibuja los edificios y carreteras iniciales
    } else {
        console.warn("[DEBUG] setup: game_obj.setup.board no está disponible. No se puede renderizar el tablero completamente.");
        // Podríamos llamar a una función de renderizado de tablero por defecto si es necesario
        // o simplemente dejar el tablero vacío si se espera que el JSON siempre lo provea.
    }
    
    // Aplicar animaciones y mejoras visuales
    if (typeof initAnimations === 'function') {
        initAnimations();
    }
    renderPlayerProfiles(); // Renderizar perfiles de jugadores
    enhanceHarborNodes(); // Estilizar nodos de puerto (ahora deberían existir)
    enhanceDiceRoll(); // Mejorar animación de dados
    applyWaterEffects(); // Aplicar efectos de agua

    // Inicializar controles de reproducción automática (Play/Stop)
    initAutoPlayControls();
}

function init_events_with_game_obj() {
    let contador_rondas = jQuery('#contador_rondas');
    let contador_turnos = jQuery('#contador_turnos');
    let contador_fases = jQuery('#contador_fases');

    let ronda_previa_btn = jQuery('#ronda_previa_btn');
    let ronda_siguiente_btn = jQuery('#ronda_siguiente_btn');

    let turno_previo_btn = jQuery('#turno_previo_btn');
    let turno_siguiente_btn = jQuery('#turno_siguiente_btn');

    let fase_previa_btn = jQuery('#fase_previa_btn');
    let fase_siguiente_btn = jQuery('#fase_siguiente_btn');

    let millis_for_play = jQuery('#millis_for_play');
    let play_btn = jQuery('#play_btn');

    // Asegurarse de que los contadores visibles se actualicen al cambiar los ocultos
    contador_rondas.add(contador_turnos).add(contador_fases).on('change', function() {
        updateVisibleCounters();
    });

    // CONTENIDO PRINCIPAL DE LA FUNCIÓN DESCOMENTADO
    contador_rondas.off('change').on('change', function (e) {
        updateVisibleCounters(); // Actualizar display
        let _this = $(this);
        
        // Verificar que game_obj y game_obj.game existen
        if (!game_obj || !game_obj.game) {
            console.warn("[DEBUG] game_obj o game_obj.game no está definido en contador_rondas change");
            return;
        }
        
        let currentGameData = game_obj.game[_this.val()];
        if (!currentGameData) {
            console.warn("[DEBUG] No se encontraron datos para la ronda:", _this.val());
            return;
        }
        
        let turnos = Object.keys(currentGameData);
        let num_turnos_en_ronda = turnos.length;

        contador_turnos.empty();
        for (let i = 0; i < num_turnos_en_ronda; i++) {
            contador_turnos.append($("<option></option>").attr("value", turnos[i]).text(turnos[i]));
        }

        if (game_direction == 'forward') {
            contador_turnos.val(turnos[0]).change();
        } else {
            contador_turnos.val(turnos[num_turnos_en_ronda - 1]).change();
        }

        // Actualizar display de rondas máximas (si no se hizo ya en addLogFromJSON)
        if ($('#rondas_maximas').text() === '' || $('#rondas_maximas').text() === '0') {
             $('#rondas_maximas').text(Object.keys(game_obj.game).length);
        }
    });

    contador_turnos.off('change').on('change', function (e) {
        updateVisibleCounters(); // Actualizar display
        let _this = $(this);
        
        // Verificar que round_obj existe
        if (!game_obj || !game_obj.game || !game_obj.game[contador_rondas.val()]) {
            console.warn("[DEBUG] No se pueden obtener datos de la ronda en contador_turnos change");
            return;
        }
        
        round_obj = game_obj.game[contador_rondas.val()];
        
        let currentTurnData = round_obj[contador_turnos.val()];
        if (!currentTurnData) {
            console.warn("[DEBUG] No se encontraron datos para el turno:", contador_turnos.val());
            return;
        }
        
        let fases = Object.keys(currentTurnData);
        let num_fases_en_turno = fases.length;

        contador_fases.empty();
        for (let i = 0; i < num_fases_en_turno; i++) {
            contador_fases.append($("<option></option>").attr("value", fases[i]).text(fases[i]));
        }

        if (game_direction == 'forward') {
            contador_fases.val(fases[0]).change();
        } else {
            contador_fases.val(fases[num_fases_en_turno - 1]).change();
        }
    });

    contador_fases.off('change').on('change', function (e) {
        updateVisibleCounters(); // Actualizar display
        // Limpiar logs e información anterior
        jQuery('#commerce_log_text').html('');
        jQuery('#other_useful_info_text').html('');
        deleteCaretStyling();

        let _this = $(this);
        turn_obj = round_obj[contador_turnos.val()];
        phase_obj = turn_obj[contador_fases.val()];

        // Lógica para procesar cada fase y actualizar la UI y los logs
        // Esta es la parte más compleja y donde se deberían añadir iconos y mejorar los logs.
        // Por ahora, solo se restaura la lógica original.

        if (phase_obj["phase_type"] == "start_turn") {
            // ... (lógica original de start_turn)
            $('#hand_P' + phase_obj['player']).css('border', 'solid 3px black');
            if (phase_obj['dice'] !== undefined) {
                updateDiceRoll(phase_obj['dice']); // Asegura que la animación de dados se llame
                // Añadir log de tirada de dados
                let html = `<div class="log-entry dice-roll mb-2">
                    <i class="fas fa-dice text-primary me-2"></i>
                    <strong>Jugador ${phase_obj['player']}</strong> tiró los dados: 
                    <span class="badge bg-primary">${phase_obj['dice']}</span>
                </div>`;
                jQuery('#other_useful_info_text').append(html);
                autoScrollLog('other_useful_info_text');
            }
        } else {
             $('#hand_P' + phase_obj['player']).css('border', 'solid 0px black');
        }

        if (phase_obj["phase_type"] == "rob_player" || phase_obj["phase_type"] == "move_bandit") {
            move_thief(phase_obj['past_thief_terrain'], phase_obj['thief_terrain'], phase_obj['robbed_player'], phase_obj['stolen_material_id'], false);
            
            // Añadir log del movimiento del ladrón
            let html = `<div class="log-entry thief-move mb-2">
                <i class="fas fa-user-ninja text-danger me-2"></i>
                <strong>Jugador ${phase_obj['player']}</strong> movió el ladrón`;
            if (phase_obj['robbed_player'] !== undefined && phase_obj['robbed_player'] !== -1) {
                html += ` y robó al <strong>Jugador ${phase_obj['robbed_player']}</strong>`;
            }
            html += `</div>`;
            jQuery('#other_useful_info_text').append(html);
            autoScrollLog('other_useful_info_text');
        }

        if (phase_obj["phase_type"] == "trade_bank") {
            // ... (lógica original de trade_bank)
            let giveIcon = getResourceIcon(phase_obj['give']);
            let receiveIcon = getResourceIcon(phase_obj['receive']);
            let html = `<div class="log-entry trade-bank mb-2">
                <i class="fas fa-university text-success me-2"></i>
                <strong>Jugador ${phase_obj['player']}</strong> comerció con el banco:
                <br><small class="ms-4">
                    Dio: ${giveIcon} <span class="text-danger">-${getResourceQuantity(phase_obj['give'])}</span> 
                    | Recibió: ${receiveIcon} <span class="text-success">+${getResourceQuantity(phase_obj['receive'])}</span>
                </small>
            </div>`;
            jQuery('#commerce_log_text').append(html);
        }

        if (phase_obj["phase_type"] == "trade_players") {
            // ... (lógica original de trade_players)
            let html = `<div class="log-entry trade-players mb-2">
                <i class="fas fa-handshake text-info me-2"></i>
                <strong>Jugador ${phase_obj['player_id_send']}</strong> comerció con 
                <strong>Jugador ${phase_obj['player_id_receive']}</strong>
                <br><small class="ms-4">Oferta: ${JSON.stringify(phase_obj['offer'])}</small>
            </div>`;
            jQuery('#commerce_log_text').append(html);
        }

        if (phase_obj["phase_type"] == "build") {
            // ... (lógica original de build)
            let building = phase_obj['what_build'];
            let node_id = phase_obj['node_id'];
            let road_to = phase_obj['road_to'];
            let player = phase_obj['player'];
            
            let buildingIcon = getBuildingIcon(building);
            let buildingName = getBuildingName(building);
            
            let html = `<div class="log-entry build mb-2">
                ${buildingIcon}
                <strong>Jugador ${player}</strong> construyó ${buildingName}`;
            if (node_id !== undefined) html += ` en nodo ${node_id}`;
            if (road_to !== undefined) html += ` hacia ${road_to}`;
            html += `</div>`;
            jQuery('#other_useful_info_text').append(html);

            // Aplicar cambios visuales con soporte para todas las variantes
            if (building === 'S舎' || building === 'settlement' || building === 'town') {
                animateBuilding(node_id, building, player);
            } else if (building === 'C都市' || building === 'city') {
                animateBuilding(node_id, building, player);
            } else if (building === 'R道' || building === 'road') {
                let road_id_str = node_id < road_to ? `road_${node_id}_${road_to}` : `road_${road_to}_${node_id}`;
                animateRoadBuilding(road_id_str, player);
            }
        }
        
        if (phase_obj["phase_type"] == "buy_card") {
            // Mejorar el log de compra de cartas
            let html = `<div class="log-entry buy-card mb-2">
                <i class="fas fa-shopping-cart text-warning me-2"></i>
                <strong>Jugador ${phase_obj['player']}</strong> compró una carta de desarrollo 🃏
            </div>`;
            jQuery('#other_useful_info_text').append(html);
            autoScrollLog('other_useful_info_text');
        }

        if (phase_obj["phase_type"] == "play_card") {
            on_development_card_played(phase_obj);
        }

        if (phase_obj["phase_type"] == "give_cards") {
            // Mejorar el log de distribución de recursos
            let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
            let resourceIcons = ['🌾', '⛰️', '🧱', '🪵', '🐑'];
            
            let html = `<div class="log-entry give-cards mb-2">
                <i class="fas fa-gift text-success me-2"></i>
                <strong>Distribución de recursos por dados (${phase_obj['dice'] || 'N/A'})</strong>
                <br><small class="ms-4">`;
            
            let playersGotResources = false;
            for (let i = 0; i < 4; i++) {
                if (phase_obj['given_to_P' + i]) {
                    playersGotResources = true;
                    html += `Jugador ${i}: `;
                    for (let j = 0; j < materials.length; j++) {
                        if (phase_obj['given_to_P' + i][materials[j]] > 0) {
                            html += `${resourceIcons[j]} +${phase_obj['given_to_P' + i][materials[j]]} `;
                        }
                    }
                    html += '<br>';
                }
            }
            
            if (!playersGotResources) {
                html += 'Ningún jugador recibió recursos';
            }
            
            html += '</small></div>';
            jQuery('#other_useful_info_text').append(html);
            autoScrollLog('other_useful_info_text');
            
            // Animar recursos ganados
            for (let i = 0; i < 4; i++) {
                if (phase_obj['given_to_P' + i]) {
                    for (let j = 0; j < materials.length; j++) {
                        if (phase_obj['given_to_P' + i][materials[j]] > 0) {
                            animateResourceGain(i, materials[j], phase_obj['given_to_P' + i][materials[j]]);
                        }
                    }
                }
            }
        }

        if (phase_obj["phase_type"] == "discard_cards") {
            // Mejorar el log de descarte de cartas
            let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
            let resourceIcons = ['🌾', '⛰️', '🧱', '🪵', '🐑'];
            
            let html = `<div class="log-entry discard-cards mb-2">
                <i class="fas fa-trash text-danger me-2"></i>
                <strong>Jugador ${phase_obj['player']}</strong> descartó cartas por ladrón (7) 🎲
                <br><small class="ms-4">Descartó: `;
            
            if (phase_obj['discarded']) {
                for (let j = 0; j < materials.length; j++) {
                    if (phase_obj['discarded'][materials[j]] > 0) {
                        html += `${resourceIcons[j]} -${phase_obj['discarded'][materials[j]]} `;
                    }
                }
            }
            
            html += '</small></div>';
            jQuery('#other_useful_info_text').append(html);
            autoScrollLog('other_useful_info_text');
        }

        // Actualizar mano del jugador para la fase actual con mejor tracking
        if (phase_obj['hand_P' + phase_obj['player']] !== undefined) {
            changeHandObject(phase_obj['player'], phase_obj['hand_P' + phase_obj['player']]);
        }

        // Actualizar todas las manos si están disponibles (para casos como monopolio)
        for (let i = 0; i < 4; i++) {
            if (phase_obj['hand_P' + i] !== undefined) {
                changeHandObject(i, phase_obj['hand_P' + i]);
            }
        }

        // Actualizar puntos de victoria si están disponibles
        if (phase_obj['victory_points']) {
            for (let i = 0; i < 4; i++) {
                if (phase_obj['victory_points']['J' + i] !== undefined) {
                    $('#puntos_victoria_J' + (i + 1)).text(phase_obj['victory_points']['J' + i]);
                    
                    // Animar cambio de puntos de victoria
                    $('#puntos_victoria_J' + (i + 1)).addClass('animate__animated animate__bounceIn');
                    setTimeout(() => {
                        $('#puntos_victoria_J' + (i + 1)).removeClass('animate__animated animate__bounceIn');
                    }, 1000);
                }
            }
        }

        // Verificar victoria después de cada fase
        setTimeout(() => {
            checkVictory();
        }, 500);

        // Actualizar cartas de desarrollo si están disponibles
        if (phase_obj['development_cards_P' + phase_obj['player']]) {
            let devCards = phase_obj['development_cards_P' + phase_obj['player']];
            updateDevCards(phase_obj['player'], devCards);
        }

        // Activar/desactivar botones de navegación
        if (game_obj && game_obj.game && round_obj && turn_obj) {
            ronda_previa_btn.prop('disabled', contador_rondas.val() == Object.keys(game_obj.game)[0] && contador_turnos.val() == Object.keys(round_obj)[0] && contador_fases.val() == Object.keys(turn_obj)[0]);
            ronda_siguiente_btn.prop('disabled', contador_rondas.val() == Object.keys(game_obj.game)[Object.keys(game_obj.game).length - 1] && contador_turnos.val() == Object.keys(round_obj)[Object.keys(round_obj).length - 1] && contador_fases.val() == Object.keys(turn_obj)[Object.keys(turn_obj).length - 1]);
            turno_previo_btn.prop('disabled', contador_turnos.val() == Object.keys(round_obj)[0] && contador_fases.val() == Object.keys(turn_obj)[0]);
            turno_siguiente_btn.prop('disabled', contador_turnos.val() == Object.keys(round_obj)[Object.keys(round_obj).length - 1] && contador_fases.val() == Object.keys(turn_obj)[Object.keys(turn_obj).length - 1]);
            fase_previa_btn.prop('disabled', contador_fases.val() == Object.keys(turn_obj)[0]);
            fase_siguiente_btn.prop('disabled', contador_fases.val() == Object.keys(turn_obj)[Object.keys(turn_obj).length - 1]);
        } else {
            console.warn("[DEBUG] No se pueden habilitar/deshabilitar botones: objetos game/round/turn no están definidos");
            // Deshabilitar todos los botones si no hay datos
            ronda_previa_btn.prop('disabled', true);
            ronda_siguiente_btn.prop('disabled', true);
            turno_previo_btn.prop('disabled', true);
            turno_siguiente_btn.prop('disabled', true);
            fase_previa_btn.prop('disabled', true);
            fase_siguiente_btn.prop('disabled', true);
        }

    });

    ronda_previa_btn.off('click').on('click', function (e) {
        game_direction = 'backward';
        
        // Verificar que game_obj existe
        if (!game_obj || !game_obj.game) {
            console.warn("[DEBUG] game_obj no está definido en ronda_previa_btn");
            return;
        }
        
        let rounds = Object.keys(game_obj.game);
        let current_round_index = rounds.indexOf(contador_rondas.val());
        if (current_round_index > 0) {
            contador_rondas.val(rounds[current_round_index - 1]).change();
        }
    });
    
    ronda_siguiente_btn.off('click').on('click', function (e) {
        game_direction = 'forward';
        
        // Verificar que game_obj existe
        if (!game_obj || !game_obj.game) {
            console.warn("[DEBUG] game_obj no está definido en ronda_siguiente_btn");
            return;
        }
        
        let rounds = Object.keys(game_obj.game);
        let current_round_index = rounds.indexOf(contador_rondas.val());
        if (current_round_index < rounds.length - 1) {
            contador_rondas.val(rounds[current_round_index + 1]).change();
        }
    });

    turno_previo_btn.off('click').on('click', function (e) {
        game_direction = 'backward';
        
        // Verificar que round_obj existe
        if (!round_obj) {
            console.warn("[DEBUG] round_obj no está definido en turno_previo_btn");
            return;
        }
        
        let turns = Object.keys(round_obj);
        let current_turn_index = turns.indexOf(contador_turnos.val());
        if (current_turn_index > 0) {
            contador_turnos.val(turns[current_turn_index - 1]).change();
        } else { // Ir a la ronda anterior, último turno
            ronda_previa_btn.click();
        }
    });
    
    turno_siguiente_btn.off('click').on('click', function (e) {
        game_direction = 'forward';
        
        // Verificar que round_obj existe
        if (!round_obj) {
            console.warn("[DEBUG] round_obj no está definido en turno_siguiente_btn");
            return;
        }
        
        let turns = Object.keys(round_obj);
        let current_turn_index = turns.indexOf(contador_turnos.val());
        if (current_turn_index < turns.length - 1) {
            contador_turnos.val(turns[current_turn_index + 1]).change();
        } else { // Ir a la siguiente ronda, primer turno
            ronda_siguiente_btn.click();
        }
    });

    fase_previa_btn.off('click').on('click', function (e) {
        game_direction = 'backward';
        
        // Verificar que turn_obj existe
        if (!turn_obj) {
            console.warn("[DEBUG] turn_obj no está definido en fase_previa_btn");
            return;
        }
        
        let phases = Object.keys(turn_obj);
        let current_phase_index = phases.indexOf(contador_fases.val());
        if (current_phase_index > 0) {
            contador_fases.val(phases[current_phase_index - 1]).change();
        } else { // Ir al turno anterior, última fase
            turno_previo_btn.click();
        }
    });
    
    fase_siguiente_btn.off('click').on('click', function (e) {
        game_direction = 'forward';
        
        // Verificar que turn_obj existe
        if (!turn_obj) {
            console.warn("[DEBUG] turn_obj no está definido en fase_siguiente_btn");
            return;
        }
        
        let phases = Object.keys(turn_obj);
        let current_phase_index = phases.indexOf(contador_fases.val());
        if (current_phase_index < phases.length - 1) {
            contador_fases.val(phases[current_phase_index + 1]).change();
        } else { // Ir al siguiente turno, primera fase
            turno_siguiente_btn.click();
        }
    });

    // Lógica del botón Play/Stop (ya existe en initAutoPlayControls, pero aquí estaba la original)
    // Se puede mantener la llamada a initAutoPlayControls() que se hace en setup() o al final de init_events().
    // Por ahora, se asume que initAutoPlayControls() maneja el play_btn.

    // Inicializar el primer estado
    if (Object.keys(game_obj).length > 0 && game_obj.game) {
        let rounds = Object.keys(game_obj.game);
        if (rounds.length > 0) {
            contador_rondas.val(rounds[0]).change(); 
        }
    } else {
        console.warn("[DEBUG] init_events_with_game_obj: game_obj no tiene la estructura esperada para iniciar la reproducción.");
    }
}

// Función para mostrar confeti de victoria
function showVictoryConfetti(playerIndex) {
    // Obtener los colores según el jugador
    let colors = getPlayerColors(playerIndex);
    
    // Mostrar el modal de victoria
    $('#winner-name').text('¡Jugador ' + (playerIndex + 1) + ' ha ganado!');
    $('#victory-modal').modal('show');
    
    // Disparar confeti
    let duration = 5 * 1000;
    let animationEnd = Date.now() + duration;
    let defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    let interval = setInterval(function() {
        let timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        let particleCount = 50 * (timeLeft / duration);
        
        // Disparar confeti desde posiciones aleatorias
        confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
            colors: colors
        });
        confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
            colors: colors
        });
    }, 250);
}

// Función para obtener colores según el jugador
function getPlayerColors(playerIndex) {
    switch(playerIndex) {
        case 0: return ['#e74c3c', '#c0392b', '#f5b7b1']; // Rojo
        case 1: return ['#3498db', '#2980b9', '#aed6f1']; // Azul
        case 2: return ['#2ecc71', '#27ae60', '#abebc6']; // Verde
        case 3: return ['#f39c12', '#d35400', '#fad7a0']; // Amarillo
        default: return ['#e74c3c', '#3498db', '#2ecc71', '#f39c12'];
    }
}

// Función para animar adquisición de recursos
function animateResourceGain(playerIndex, resourceType, quantity) {
    // Crear animación de ganancia de recursos
    const resourceElement = $(`#hand_P${playerIndex} .resources-grid .${resourceType} .${resourceType}_quantity`);
    
    if (resourceElement.length) {
        // Animar el incremento
        resourceElement.addClass('animate__animated animate__pulse text-success');
        
        // Crear un indicador de ganancia
        const gainIndicator = $(`<span class="gain-indicator">+${quantity}</span>`);
        gainIndicator.css({
            position: 'absolute',
            color: '#28a745',
            fontWeight: 'bold',
            fontSize: '12px',
            zIndex: 1000,
            animation: 'fadeInUp 1s ease-out forwards'
        });
        
        resourceElement.parent().css('position', 'relative').append(gainIndicator);
        
        // Limpiar después de la animación
        setTimeout(() => {
            resourceElement.removeClass('animate__animated animate__pulse text-success');
            gainIndicator.remove();
        }, 1500);
    }
    
    console.log(`[DEBUG] Jugador ${playerIndex} ganó ${quantity} de ${resourceType}`);
}

function getPlayerEmoji(playerIndex) {
    switch (playerIndex) {
        case 0:
            return '🔴'; // P1 - Rojo
        case 1:
            return '🔵'; // P2 - Azul
        case 2:
            return '🟢'; // P3 - Verde
        case 3:
            return '🟡'; // P4 - Amarillo
        default:
            return '⚪'; // Por defecto
    }
}

function getBuildingEmoji(buildingType) {
    switch (buildingType) {
        case 'settlement':
        case 'town':
        case 'S舎':
            return '🏠'; // Poblado
        case 'city':
        case 'C都市':
            return '🏛️'; // Ciudad
        case 'road':
        case 'R道':
            return '🛣️'; // Camino
        default:
            return '🏗️'; // Construcción genérica
    }
}

// Función para animar construcciones
function animateBuilding(nodeId, buildingType, playerIndex) {
    const nodeElement = $('#node_' + nodeId);
    const colors = getPlayerColors(playerIndex);
    const playerMainColor = colors[0]; // Color principal del jugador
    
    if (nodeElement.length) {
        // Limpiar cualquier contenido anterior
        nodeElement.empty();
        
        // Aplicar estilo de jugador
        nodeElement.css({
            'background-color': playerMainColor,
            'border': `3px solid ${colors[1]}`,
            'border-radius': buildingType === 'city' || buildingType === 'C都市' ? '8px' : '50%',
            'transform': 'scale(1)',
            'z-index': '10'
        });
        
        // Añadir emoji según el tipo de construcción
        let emoji = '';
        if (buildingType === 'settlement' || buildingType === 'S舎') {
            emoji = '🏠';
        } else if (buildingType === 'city' || buildingType === 'C都市') {
            emoji = '🏛️';
        }
        
        if (emoji) {
            nodeElement.html(`<span style="font-size: 16px; line-height: 1;">${emoji}</span>`);
        }
        
        // Animación de aparición
        nodeElement.addClass('animate__animated animate__bounceIn');
        
        // Efecto de construcción
        createConstructionEffect(nodeElement.offset().left, nodeElement.offset().top);
        
        setTimeout(() => {
            nodeElement.removeClass('animate__animated animate__bounceIn');
        }, 1000);
        
        console.log(`[DEBUG] Construido ${buildingType} para Jugador ${playerIndex} en nodo ${nodeId}`);
    }
}

// Función para animar la construcción de carreteras
function animateRoadBuilding(roadId, playerIndex) {
    const roadElement = $('#' + roadId);
    const colors = getPlayerColors(playerIndex);
    const playerMainColor = colors[0];
    
    if (roadElement.length) {
        // Aplicar color del jugador a la carretera
        roadElement.css({
            'background-color': playerMainColor,
            'border': `2px solid ${colors[1]}`,
            'transform': 'scale(1)',
            'z-index': '5'
        });
        
        // Añadir emoji de carretera
        roadElement.html(`<span style="font-size: 12px; color: white;">🛤️</span>`);
        
        // Animación de construcción
        roadElement.addClass('animate__animated animate__fadeIn');
        
        setTimeout(() => {
            roadElement.removeClass('animate__animated animate__fadeIn');
        }, 1000);
        
        console.log(`[DEBUG] Construida carretera para Jugador ${playerIndex}: ${roadId}`);
    }
}

// Función para animar el movimiento del ladrón
function animateThiefMovement(fromTerrainId, toTerrainId) {
    // Obtener las posiciones iniciales y finales
    let fromTerrain = $('#terrain_' + fromTerrainId);
    let toTerrain = $('#terrain_' + toTerrainId);
    
    // Animar el ladrón
    let thief = $('.fa-user-ninja');
    
    gsap.to(thief, {
        duration: 1,
        y: 50,
        opacity: 0,
        scale: 0.5,
        ease: "power2.in",
        onComplete: function() {
            // Mover el ladrón al nuevo terreno
            fromTerrain.find('.terrain_number').html('');
            thief.appendTo(toTerrain.find('.terrain_number'));
            
            // Animar la aparición en el nuevo terreno
            gsap.fromTo(thief, 
                { y: -50, opacity: 0, scale: 0.5 },
                { duration: 1, y: 0, opacity: 1, scale: 1, ease: "bounce.out" }
            );
        }
    });
}

// Función para animar jugada de carta de desarrollo
function animateCardPlay(playerIndex, cardType) {
    // Seleccionar el elemento de la carta
    let card = $('#hand_P' + playerIndex + ' .' + cardType);
    
    // Animar la carta jugada
    gsap.to(card, {
        duration: 0.5,
        y: -20,
        opacity: 0.5,
        ease: "power1.out",
        onComplete: function() {
            gsap.to(card, {
                duration: 0.5,
                y: 0,
                opacity: 1,
                ease: "power1.in"
            });
            
            // Actualizar contador
            let quantityElement = card.find('.' + cardType + '_quantity');
            let currentValue = parseInt(quantityElement.text());
            quantityElement.text(currentValue - 1);
        }
    });
}

// Función para animar comercio entre jugadores
function animateTrade(fromPlayerIndex, toPlayerIndex, givenResources, receivedResources) {
    // Crear elementos visuales para el comercio
    let tradeAnimation = $('<div class="trade-animation"></div>');
    $('body').append(tradeAnimation);
    
    // Posicionar la animación entre los dos jugadores
    let fromPlayer = $('#P' + fromPlayerIndex);
    let toPlayer = $('#P' + toPlayerIndex);
    
    // Animar intercambio
    gsap.from(tradeAnimation, {
        duration: 1,
        x: fromPlayer.offset().left,
        y: fromPlayer.offset().top,
        ease: "power2.out",
        onComplete: function() {
            gsap.to(tradeAnimation, {
                duration: 1,
                x: toPlayer.offset().left,
                y: toPlayer.offset().top,
                ease: "power2.in",
                onComplete: function() {
                    tradeAnimation.remove();
                }
            });
        }
    });
}

// Mejora de la función existente
function paint_it_player_color(player, object_to_paint) {
    let colorClass;
    
    switch (player) {
        case 0:
            colorClass = 'player-red';
            object_to_paint.css('background', '#e74c3c');
            object_to_paint.css('border', '2px solid #c0392b');
            break;
        case 1:
            colorClass = 'player-blue';
            object_to_paint.css('background', '#3498db');
            object_to_paint.css('border', '2px solid #2980b9');
            break;
        case 2:
            colorClass = 'player-green';
            object_to_paint.css('background', '#2ecc71');
            object_to_paint.css('border', '2px solid #27ae60');
            break;
        case 3:
            colorClass = 'player-yellow';
            object_to_paint.css('background', '#f39c12');
            object_to_paint.css('border', '2px solid #d35400');
            break;
    }
    
    // Añadir clase para futuras referencias
    object_to_paint.addClass(colorClass);
    
    // Añadir efecto de iluminación
    object_to_paint.css('box-shadow', '0 0 10px ' + object_to_paint.css('background-color'));
    
    // Animar la aparición
    gsap.from(object_to_paint, {
        duration: 0.5,
        opacity: 0,
        ease: "power1.out"
    });
}

// Modificar función de tirar dados para incluir animación
let originalDiceroll = $('#diceroll').text();
function updateDiceRoll(value) {
    // Animar el dado
    animateDiceRoll(value);
}

// Función para comprobar victoria
function checkVictory() {
    // Verificar si algún jugador ha ganado (10 puntos de victoria)
    for (let i = 1; i <= 4; i++) {
        const victoryPoints = parseInt($('#puntos_victoria_J' + i).text()) || 0;
        if (victoryPoints >= 10) {
            // Detener autoplay si está activo
            if (isPlaying) {
                stopAutoPlay();
            }
            
            // Mostrar efectos de victoria después de un breve delay
            setTimeout(() => {
                showVictoryConfetti(i - 1);
                
                // Log de victoria
                let html = `<div class="log-entry victory mb-2">
                    <i class="fas fa-crown text-warning me-2"></i>
                    <strong class="text-warning">🎉 ¡JUGADOR ${i} HA GANADO! 🎉</strong>
                    <br><small class="ms-4">Victoria con ${victoryPoints} puntos</small>
                </div>`;
                jQuery('#other_useful_info_text').append(html);
                autoScrollLog('other_useful_info_text');
                
                // Resaltar el jugador ganador
                $(`#player-card-${i-1}`).addClass('winner-glow');
                
            }, 500);
            
            return true; // Victoria detectada
        }
    }
    return false; // No hay victoria
}

// Funciones para animaciones y efectos especiales
function initAnimations() {
    // Configuración de animaciones
    $('.terrain').each(function(index) {
        // Añadimos un pequeño retraso a la animación de cada terreno para crear un efecto cascada
        if (typeof gsap !== 'undefined') {
            gsap.from(this, {
                duration: 0.8,
                delay: index * 0.05,
                y: -50,
                opacity: 0,
                ease: "power2.out"
            });
        }
    });

    // Animación de los nodos
    if (typeof gsap !== 'undefined') {
        gsap.from('.node', {
            duration: 0.5,
            delay: 0.8,
            scale: 0,
            opacity: 0,
            stagger: 0.01,
            ease: "back.out(1.7)"
        });

        // Animación de las carreteras
        gsap.from('.road', {
            duration: 0.5,
            delay: 1,
            scaleX: 0,
            opacity: 0,
            stagger: 0.01,
            ease: "power1.out"
        });
    }
}

// Función para renderizar perfiles de jugadores
function renderPlayerProfiles() {
    const playerColorsGoogle = [ // Paleta de Google
        { bg: '#e57373', text: '#ffffff', border: '#d32f2f' },  // Rojo claro
        { bg: '#64b5f6', text: '#ffffff', border: '#1976d2' },  // Azul claro
        { bg: '#81c784', text: '#ffffff', border: '#388e3c' },  // Verde claro
        { bg: '#fff176', text: '#424242', border: '#fbc02d' }   // Amarillo claro (texto oscuro para contraste)
    ];
    
    let playersContainer = $('#players-container');
    playersContainer.empty();
    
    // Iconos para recursos y cartas (FontAwesome)
    const resourceIcons = {
        cereal: 'fa-solid fa-wheat-awn',
        clay: 'fa-solid fa-trowel-bricks', // O fa-solid fa-cubes
        wool: 'fa-brands fa-cotton-bureau', // O fa-solid fa-sheep
        wood: 'fa-solid fa-tree', // O fa-solid fa-seedling
        mineral: 'fa-solid fa-mountain-sun' // O fa-solid fa-gem
    };

    const devCardIcons = {
        knight: 'fa-solid fa-chess-knight',
        victory_point: 'fa-solid fa-award', // Diferente al de PV general
        road_building: 'fa-solid fa-road-bridge',
        year_of_plenty: 'fa-solid fa-gifts',
        monopoly: 'fa-solid fa-bullhorn' // O fa-solid fa-sack-dollar
    };
    
    for (let i = 0; i < 4; i++) {
        const playerColor = playerColorsGoogle[i];
        let playerHtml = `
            <div class="col-md-6 mb-3 player-profile-column">
                <div class="player-card" id="player-card-${i}" style="border-top: 5px solid ${playerColor.border};">
                    <div class="player-header" style="background-color: ${playerColor.bg}; color: ${playerColor.text};">
                        <div class="player-name-vp">
                            <span class="player-title"><i class="fas fa-user me-2"></i>Jugador ${i + 1}</span>
                            <span class="player-vp" title="Puntos de Victoria"><i class="fas fa-trophy me-1"></i><span id="puntos_victoria_J${i + 1}">0</span></span>
                        </div>
                        <div class="player-awards mt-1">
                            <span class="largest-army-badge" id="largest_army_P${i}" style="display:none;" title="Mayor Ejército"><i class="fas fa-shield-alt"></i></span>
                            <span class="longest-road-badge" id="longest_road_P${i}" style="display:none;" title="Ruta Más Larga"><i class="fas fa-road"></i></span>
                        </div>
                    </div>
                    <div class="player-body" id="hand_P${i}">
                        <div class="player-resources" id="hand_P${i}_resources">
                            <h5>Recursos:</h5>
                            <div class="resources-grid">
                                <div class="resource-item cereal" title="Cereal">
                                    <i class="${resourceIcons.cereal}"></i>
                                    <span class="resource-quantity cereal_quantity">0</span>
                                </div>
                                <div class="resource-item clay" title="Arcilla">
                                    <i class="${resourceIcons.clay}"></i>
                                    <span class="resource-quantity clay_quantity">0</span>
                                </div>
                                <div class="resource-item wool" title="Lana">
                                    <i class="${resourceIcons.wool}"></i>
                                    <span class="resource-quantity wool_quantity">0</span>
                                </div>
                                <div class="resource-item wood" title="Madera">
                                    <i class="${resourceIcons.wood}"></i>
                                    <span class="resource-quantity wood_quantity">0</span>
                                </div>
                                <div class="resource-item mineral" title="Mineral">
                                    <i class="${resourceIcons.mineral}"></i>
                                    <span class="resource-quantity mineral_quantity">0</span>
                                </div>
                            </div>
                        </div>
                        <hr class="my-2">
                        <div class="player-dev-cards" id="hand_P${i}_dev_cards">
                            <h5>Cartas de Desarrollo:</h5>
                            <div class="dev-cards-grid">
                                <div class="dev-card-item knight" data-id="knight" title="Caballero">
                                    <i class="${devCardIcons.knight}"></i>
                                    <span class="dev-card-quantity knight_quantity">0</span>
                                </div>
                                <div class="dev-card-item victory_point" data-id="victory_point" title="Punto de Victoria">
                                    <i class="${devCardIcons.victory_point}"></i>
                                    <span class="dev-card-quantity victory_point_quantity">0</span>
                                </div>
                                <div class="dev-card-item road_building" data-id="road_building" title="Construcción de Carreteras">
                                    <i class="${devCardIcons.road_building}"></i>
                                    <span class="dev-card-quantity road_building_quantity">0</span>
                                </div>
                                <div class="dev-card-item year_of_plenty" data-id="year_of_plenty" title="Año de la Abundancia">
                                    <i class="${devCardIcons.year_of_plenty}"></i>
                                    <span class="dev-card-quantity year_of_plenty_quantity">0</span>
                                </div>
                                <div class="dev-card-item monopoly" data-id="monopoly" title="Monopolio">
                                    <i class="${devCardIcons.monopoly}"></i>
                                    <span class="dev-card-quantity monopoly_quantity">0</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        playersContainer.append(playerHtml);
    }
    
    // Aplicar animación de entrada (ya existente)
    /* Comentado para depuración
    gsap.from('.player-card', {
        duration: 0.8,
        y: 50,
        opacity: 0,
        stagger: 0.2,
        ease: "power2.out"
    });
    */
    // Forzar visibilidad para depuración
    jQuery('.player-card').css('opacity', 1).css('transform', 'translate(0px, 0px)');

}

// Función para mejorar visualmente los nodos de puerto
function enhanceHarborNodes() {
    // Esperar un segundo para asegurarse de que todo esté cargado
    setTimeout(function() {
        $('.is-harbor').each(function() {
            // Añadir un efecto de brillo para destacar los puertos
            $(this).css('box-shadow', '0 0 15px rgba(52, 152, 219, 0.5)');
            
            // Agregar animación de pulsación
            gsap.to(this, {
                duration: 2,
                repeat: -1,
                yoyo: true,
                scale: 1.1,
                ease: "sine.inOut"
            });
        });
    }, 1000);
}

// Interceptar las llamadas al método de cambio de fase para animar tiradas de dados
let originalCounterFasesChange = null;

// Después de iniciar el juego
function enhanceDiceRoll() {
    // Capturar la función original si aún no se ha hecho
    if (!originalCounterFasesChange) {
        const contador_fases_jq = jQuery('#contador_fases');
        const contadorFasesElement = contador_fases_jq.get(0);

        if (contadorFasesElement) {
            // Guardar la función onchange original si existe y es una función
            if (typeof contadorFasesElement.onchange === 'function') {
                originalCounterFasesChange = contadorFasesElement.onchange;
            }
            
            // Desvincular cualquier manejador 'change' previo y vincular el nuestro
            contador_fases_jq.off('change').on('change', function(e) {
                if (contador_fases_jq.val() === '') {
                    console.log('[DEBUG] enhanceDiceRoll: contador_fases está vacío, retornando.');
                    // Si había una función original y el valor es vacío, quizás queramos llamarla
                    if (originalCounterFasesChange) {
                        originalCounterFasesChange.call(this, e);
                    }
                    return;
                }
                
                // let actual_player_json = parseInt(jQuery('#contador_turnos').val()) - 1; // No parece usarse
                
                // Si estamos en la fase 0 (representada por valor 1 en el input) y avanzando
                if (parseInt(contador_fases_jq.val()) === 1 && game_direction === 'forward') {
                    console.log('[DEBUG] enhanceDiceRoll: Fase 1 y forward detectado.');
                    const phase_obj = turn_obj ? turn_obj['start_turn'] : undefined;
                    
                    if (phase_obj && phase_obj['dice']) {
                        console.log('[DEBUG] enhanceDiceRoll: Animando dados con valor:', phase_obj['dice']);
                        animateDiceRoll(phase_obj['dice']);
                        
                        setTimeout(function() {
                            if (originalCounterFasesChange) {
                                console.log('[DEBUG] enhanceDiceRoll: Llamando a originalCounterFasesChange después de animación.');
                                originalCounterFasesChange.call(contadorFasesElement, e);
                            } else {
                                console.log('[DEBUG] enhanceDiceRoll: No hay originalCounterFasesChange para llamar después de animación.');
                            }
                        }, 3500); 
                        return;
                    } else {
                        console.log('[DEBUG] enhanceDiceRoll: No hay phase_obj o phase_obj.dice para animar.');
                    }
                }
                
                // Para otros casos, llamar a la función original directamente si existe
                if (originalCounterFasesChange) {
                    console.log('[DEBUG] enhanceDiceRoll: Llamando a originalCounterFasesChange (caso general).');
                    originalCounterFasesChange.call(this, e);
                } else {
                    console.log('[DEBUG] enhanceDiceRoll: No hay originalCounterFasesChange (caso general).');
                }
            });
        } else {
            console.warn("[DEBUG] El elemento #contador_fases no fue encontrado. enhanceDiceRoll no se activará.");
        }
    }
}

// Función para generar texturas de olas dinámicamente
function createWaveTexture() {
    // Crear un canvas para la textura
    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 400;
    const ctx = canvas.getContext('2d');
    
    // Limpiar el canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Configurar el estilo
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 2;
    
    // Dibujar ondas
    for (let y = 0; y < canvas.height; y += 20) {
        ctx.beginPath();
        for (let x = 0; x < canvas.width; x += 5) {
            const waveHeight = 5 * Math.sin((x / 20) + (y / 30));
            
            if (x === 0) {
                ctx.moveTo(x, y + waveHeight);
            } else {
                ctx.lineTo(x, y + waveHeight);
            }
        }
        ctx.stroke();
    }
    
    // Crear una imagen a partir del canvas
    const image = new Image();
    image.src = canvas.toDataURL();
    
    // Aplicar la textura como fondo
    document.documentElement.style.setProperty('--wave-texture', `url(${image.src})`);
    
    return image.src;
}

// Función para aplicar efectos adicionales de agua
function applyWaterEffects() {
    // Generar la textura de olas
    const waveTexture = createWaveTexture();
    
    // Crear estilos para las olas y añadirlos al documento
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        #gamefield_external::before, .terrain_water::after {
            background-image: var(--wave-texture) !important;
        }
        
        @keyframes ripple {
            0% { transform: scale(0); opacity: 0.8; }
            100% { transform: scale(2); opacity: 0; }
        }
        
        .water-drop {
            position: absolute;
            width: 15px;
            height: 15px;
            background: radial-gradient(circle, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0) 70%);
            border-radius: 50%;
            z-index: 10;
            pointer-events: none;
            animation: ripple 2s ease-out forwards;
        }
    `;
    document.head.appendChild(styleElement);
    
    // Añadir gotas de agua aleatorias en el océano
    const gamefieldExternal = document.getElementById('gamefield_external');
    
    setInterval(() => {
        if (Math.random() > 0.7) { // 30% de probabilidad
            createWaterDrop(gamefieldExternal);
        }
    }, 3000);
    
    // Añadir efecto de ondulación al océano
    animateOceanWaves();
}

// Función para crear una gota de agua
function createWaterDrop(container) {
    const drop = document.createElement('div');
    drop.className = 'water-drop';
    
    // Posición aleatoria
    const x = Math.random() * container.offsetWidth;
    const y = Math.random() * container.offsetHeight;
    
    // Aplicar estilos
    drop.style.left = `${x}px`;
    drop.style.top = `${y}px`;
    drop.style.animationDuration = `${0.5 + Math.random()}s`;
    
    // Añadir al contenedor
    container.appendChild(drop);
    
    // Eliminar después de la animación
    setTimeout(() => {
        drop.remove();
    }, 2000);
}

// Función para animar las olas del océano
function animateOceanWaves() {
    // Seleccionar todos los elementos de terreno de agua
    const waterTerrains = document.querySelectorAll('.terrain_water, .top_terrain, .bottom_terrain');
    
    // Añadir animación con GSAP
    waterTerrains.forEach((terrain, index) => {
        // Crear una animación ligeramente diferente para cada terreno
        gsap.to(terrain, {
            y: "+=3",
            duration: 2 + (index % 3),
            ease: "sine.inOut",
            repeat: -1,
            yoyo: true,
            delay: index * 0.1
        });
    });
    
    // Animar el brillo del agua
    const gamefieldExternal = document.getElementById('gamefield_external');
    gsap.to(gamefieldExternal, {
        backgroundPosition: "+=50px +=30px",
        duration: 20,
        ease: "none",
        repeat: -1,
        yoyo: true
    });
}

// Función para probar la animación de dados
function testDiceAnimation() {
    // Obtener un número aleatorio entre 1 y 6
    const randomValue = Math.floor(Math.random() * 6) + 1;
    console.log("Probando animación de dados con valor: " + randomValue);
    
    // Ejecutar la animación
    animateDiceRoll(randomValue);
}

// Añadir evento para probar la animación al cargar la página
jQuery(document).ready(function($) {
    console.log("Documento listo, añadiendo botón de prueba de dados");
    
    // Botón para probar manualmente
    $('#load_game').after('<button id="test_dice" class="btn btn-secondary ms-2"><i class="fas fa-dice me-2"></i>Probar dados</button>');
    
    // Evento de prueba
    $(document).on('click', '#test_dice', function() {
        console.log("Botón de prueba de dados clickeado");
        testDiceAnimation();
    });
    
    // Verificar que el overlay existe
    const overlay = document.getElementById('dice-overlay');
    if (!overlay) {
        console.error("Error: Elemento 'dice-overlay' no encontrado");
    } else {
        console.log("Overlay de dados encontrado correctamente");
    }
    
    // Verificar que el dado existe
    const dice = document.querySelector('.dice');
    if (!dice) {
        console.error("Error: Elemento '.dice' no encontrado");
    } else {
        console.log("Elemento dado encontrado correctamente");
    }
});

// Función para crear efectos de cursor personalizados
function initCursorEffects() {
    // Crear el elemento seguidor del cursor
    const cursorFollower = document.createElement('div');
    cursorFollower.className = 'cursor-follower';
    document.body.appendChild(cursorFollower);
    
    // Seguimiento del cursor principal
    document.addEventListener('mousemove', function(e) {
        // Actualizar posición del seguidor
        cursorFollower.style.left = e.clientX + 'px';
        cursorFollower.style.top = e.clientY + 'px';
        
        // Crear efecto de estela
        if (Math.random() > 0.7) { // Solo crear partículas ocasionalmente
            createCursorTrail(e.clientX, e.clientY);
        }
    });
    
    // Efecto al hacer clic
    document.addEventListener('mousedown', function(e) {
        cursorFollower.style.transform = 'translate(-50%, -50%) scale(0.8)';
        // Crear efecto de "construcción"
        createConstructionEffect(e.clientX, e.clientY);
    });
    
    document.addEventListener('mouseup', function() {
        cursorFollower.style.transform = 'translate(-50%, -50%) scale(1)';
    });
    
    // Cambiar el cursor según el tipo de terreno
    const terrains = document.querySelectorAll('.terrain');
    terrains.forEach(terrain => {
        terrain.addEventListener('mouseenter', function() {
            // Cambiar el icono según el tipo de terreno
            if (terrain.classList.contains('terrain_cereal')) {
                cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%23ffd700" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L20 7v10l-8 5-8-5V7l8-5z"/></svg>\')';
            } else if (terrain.classList.contains('terrain_clay')) {
                cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%23a5673f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L20 7v10l-8 5-8-5V7l8-5z"/></svg>\')';
            } else if (terrain.classList.contains('terrain_wood')) {
                cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%232ecc71" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L20 7v10l-8 5-8-5V7l8-5z"/></svg>\')';
            } else if (terrain.classList.contains('terrain_wool')) {
                cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%23c3e59a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L20 7v10l-8 5-8-5V7l8-5z"/></svg>\')';
            } else if (terrain.classList.contains('terrain_mineral')) {
                cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%238d8d8d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L20 7v10l-8 5-8-5V7l8-5z"/></svg>\')';
            } else {
                // Restaurar a imagen por defecto para otros terrenos
                cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%233498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>\')';
            }
        });
        
        terrain.addEventListener('mouseleave', function() {
            // Restaurar a la imagen por defecto
            cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%233498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>\')';
        });
    });
    
    // Cambiar el cursor al pasar sobre nodos
    const nodes = document.querySelectorAll('.node');
    nodes.forEach(node => {
        node.addEventListener('mouseenter', function() {
            cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%23e74c3c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>\')';
        });
        
        node.addEventListener('mouseleave', function() {
            cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%233498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>\')';
        });
    });
    
    // Cambiar el cursor al pasar sobre carreteras
    const roads = document.querySelectorAll('.road');
    roads.forEach(road => {
        road.addEventListener('mouseenter', function() {
            cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%23f39c12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l18 18"/></svg>\')';
        });
        
        road.addEventListener('mouseleave', function() {
            cursorFollower.style.backgroundImage = 'url(\'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%233498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>\')';
        });
    });
}

// Función para crear el efecto de estela del cursor
function createCursorTrail(x, y) {
    const trail = document.createElement('div');
    trail.className = 'cursor-trail';
    trail.style.left = x + 'px';
    trail.style.top = y + 'px';
    document.body.appendChild(trail);
    
    // Eliminar después de la animación
    setTimeout(() => {
        trail.remove();
    }, 1000);
}

// Función para crear efecto de construcción al hacer clic
function createConstructionEffect(x, y) {
    // Crear círculo de "construcción"
    const constructEffect = document.createElement('div');
    constructEffect.className = 'cursor-trail';
    constructEffect.style.left = x + 'px';
    constructEffect.style.top = y + 'px';
    constructEffect.style.background = 'rgba(231, 76, 60, 0.5)';
    constructEffect.style.width = '6px';
    constructEffect.style.height = '6px';
    document.body.appendChild(constructEffect);
    
    // Animar y eliminar
    gsap.to(constructEffect, {
        duration: 0.5,
        width: '40px',
        height: '40px',
        opacity: 0,
        onComplete: function() {
            constructEffect.remove();
        }
    });
    
    // Sonido de construcción (opcional)
    // Podríamos agregar un sonido aquí si el juego tiene audio
}

// Función para inicializar los controles de reproducción automática
function initAutoPlayControls() {
    const playBtn = $('#play_btn');
    const playText = $('#play-text');
    
    // Asegurarse de que no se dupliquen los eventos
    playBtn.off('click').on('click', function() {
        if (isPlaying) {
            stopAutoPlay();
        } else {
            startAutoPlay();
        }
    });
}

// Función para iniciar la reproducción automática
function startAutoPlay() {
    if (isPlaying) return;
    
    // Verificar que el juego está cargado
    if (Object.keys(game_obj).length === 0) {
        alert('Debes cargar una partida primero');
        // Adicionalmente, asegurar que el botón de play no quede en estado "playing"
        const playBtn = $('#play_btn');
        const playText = $('#play-text');
        playBtn.removeClass('playing');
        playText.text('Play');
        playBtn.find('i').removeClass('fa-stop').addClass('fa-play');
        return;
    }
    
    // Cambiar el estado y apariencia del botón
    isPlaying = true;
    const playBtn = $('#play_btn');
    const playText = $('#play-text');
    
    playBtn.addClass('playing');
    playText.text('Stop');
    playBtn.find('i').removeClass('fa-play').addClass('fa-stop');
    
    // Velocidad fija para la reproducción automática (en milisegundos)
    const speed = 800;
    
    // Iniciar el intervalo para avanzar automáticamente
    autoPlayInterval = setInterval(function() {
        // Intentar avanzar a la siguiente fase
        const faseBtn = $('#fase_siguiente_btn');
        if (!faseBtn.prop('disabled')) {
            highlightActiveButton('#fase_siguiente_btn');
            faseBtn.click();
        } else {
            // Si no se puede avanzar de fase, intentar avanzar al siguiente turno
            const turnoBtn = $('#turno_siguiente_btn');
            if (!turnoBtn.prop('disabled')) {
                highlightActiveButton('#turno_siguiente_btn');
                turnoBtn.click();
            } else {
                // Si no se puede avanzar de turno, intentar avanzar a la siguiente ronda
                const rondaBtn = $('#ronda_siguiente_btn');
                if (!rondaBtn.prop('disabled')) {
                    highlightActiveButton('#ronda_siguiente_btn');
                    rondaBtn.click();
                } else {
                    // Si llegamos al final del juego, detener la reproducción
                    stopAutoPlay();
                    
                    // Verificar si hay un ganador
                    checkVictory();
                    
                    // Mostrar un mensaje de que el juego ha terminado
                    alert('¡La partida ha terminado!');
                }
            }
        }
    }, speed);
    
    // Añadir animación de "jugando" al tablero
    $('#gamefield').addClass('playing-mode');
    
    // Añadir indicador de reproducción automática
    $('<div class="auto-play-indicator">Reproducción automática</div>')
        .appendTo('#gamefield_external')
        .css({
            position: 'absolute',
            top: '10px',
            right: '10px',
            background: 'rgba(39, 174, 96, 0.7)',
            color: 'white',
            padding: '5px 10px',
            borderRadius: '5px',
            fontWeight: 'bold',
            zIndex: 100,
            boxShadow: '0 2px 5px rgba(0, 0, 0, 0.2)'
        })
        .hide()
        .fadeIn(500);
    
    console.log('Reproducción automática iniciada');
}

// Función para detener la reproducción automática
function stopAutoPlay() {
    if (!isPlaying) return;
    
    // Cambiar el estado y apariencia del botón
    isPlaying = false;
    const playBtn = $('#play_btn');
    const playText = $('#play-text');
    
    playBtn.removeClass('playing');
    playText.text('Play');
    playBtn.find('i').removeClass('fa-stop').addClass('fa-play');
    
    // Quitar resaltado de botones
    $('#controles .btn').removeClass('active-button');
    
    // Detener el intervalo
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
    }
    
    // Quitar animación del tablero
    $('#gamefield').removeClass('playing-mode');
    
    // Quitar indicador de reproducción automática
    $('.auto-play-indicator').fadeOut(500, function() {
        $(this).remove();
    });
    
    console.log('Reproducción automática detenida');
}

// Añadir esta función al objeto window para poder probarla desde la consola
window.testDiceAnimation = testDiceAnimation;

// Función para marcar visualmente el botón activo durante la reproducción automática
function highlightActiveButton(buttonId) {
    // Primero quitar la clase de todos los botones
    $('#controles .btn').removeClass('active-button');
    
    // Añadir la clase al botón activo
    $(buttonId).addClass('active-button');
    
    // Aplicar animación al botón
    $(buttonId).addClass('animate__animated animate__pulse');
    setTimeout(function() {
        $(buttonId).removeClass('animate__animated animate__pulse');
    }, 500);
}

// Nueva función para actualizar la UI con datos del game_obj cargado
function updateUIDataFromGameObj(game_data) {
    console.log("[DEBUG] updateUIDataFromGameObj llamado con:", JSON.parse(JSON.stringify(game_data)));

    if (!game_data || !game_data.game) {
        console.error("[DEBUG] game_data o game_data.game no está definido.");
        return;
    }

    const DEV_CARD_TYPE_MAP = {
        0: 'knight',       // KNIGHT_EFFECT (asumiendo type 0 es Knight)
        1: 'victory_point',// VICTORY_POINT_EFFECT (asumiendo type 1 es VP)
        2: 'road_building',
        3: 'year_of_plenty',
        4: 'monopoly'
    };
    // Mapeo de constantes de tipo de carta desde Python
    const PYTHON_KNIGHT_CARD_TYPE = 0;
    const PYTHON_VICTORY_POINT_CARD_TYPE = 1;
    const PYTHON_PROGRESS_CARD_TYPE = 2;

    // Mapeo de constantes de efecto de carta desde Python
    // const PYTHON_KNIGHT_EFFECT = 0; // Coincide con DEV_CARD_TYPE_MAP[0]
    // const PYTHON_VICTORY_POINT_EFFECT = 1; // Coincide con DEV_CARD_TYPE_MAP[1]
    const PYTHON_ROAD_BUILDING_EFFECT = 2;
    const PYTHON_YEAR_OF_PLENTY_EFFECT = 3;
    const PYTHON_MONOPOLY_EFFECT = 4;

    let lastRoundKey = 'round_0';
    if (game_data.game && Object.keys(game_data.game).length > 0) {
        lastRoundKey = Object.keys(game_data.game).sort((a, b) => parseInt(b.split('_')[1]) - parseInt(a.split('_')[1]))[0];
    }
    const lastRoundData = game_data.game[lastRoundKey];
    if (!lastRoundData) {
        console.error("[DEBUG] No se encontraron datos para la última ronda (", lastRoundKey, ")");
        return;
    }

    let lastTurnKey = 'P0'; // Asumimos un jugador por defecto si no hay turnos
    if (lastRoundData && Object.keys(lastRoundData).length > 0) {
         // Los turnos son como P0, P1, P2, P3 o turn_P0, turn_P1 etc.
         // Necesitamos encontrar el último turno procesado que tenga end_turn y start_turn.
         // Las claves de turno podrían ser "turn_P0", "P0", etc.
         // Vamos a buscar el índice de jugador más alto en las claves.
        let playerIndexes = Object.keys(lastRoundData).map(key => {
            const match = key.match(/(?:turn_P|P)(\d+)/);
            return match ? parseInt(match[1]) : -1;
        }).filter(idx => idx !== -1);

        if (playerIndexes.length > 0) {
            const maxPlayerIndex = Math.max(...playerIndexes);
            // Intentar encontrar la clave de turno que contiene la información más completa (end_turn)
            // Las claves pueden ser P0, P1... o start_turn, end_turn, etc. o turn_P0.
            // Daremos prioridad a las claves que representen un turno de jugador (ej. P0, turn_P0)
            const potentialTurnKeys = Object.keys(lastRoundData).filter(key => key.includes('P' + maxPlayerIndex));
            if (potentialTurnKeys.length > 0) {
                 // Idealmente, la traza debería tener una estructura consistente para el último estado.
                 // Por ahora, tomaremos la primera clave que coincida con el jugador más alto.
                 // Esto podría necesitar ajuste si la estructura de la traza varía mucho.
                lastTurnKey = potentialTurnKeys.sort().pop(); // Tomar la última alfabéticamente, heurística.
            } else {
                 // Si no encontramos una clave específica de jugador, buscamos una general 'end_turn' o 'start_turn'
                 // Esto es menos ideal, ya que el JSON podría no tener todos los datos en una sola de estas claves
                 // para todos los jugadores al mismo tiempo.
                if (lastRoundData['end_turn']) lastTurnKey = 'end_turn';
                else if (lastRoundData['start_turn']) lastTurnKey = 'start_turn';
                // Si no, se queda con P0 por defecto, lo cual es problemático.
                console.warn("[DEBUG] No se encontró una clave de turno específica para el jugador", maxPlayerIndex, "en la ronda", lastRoundKey, ". Usando", lastTurnKey);
            }
        }
    }
    
    const turnData = lastRoundData[lastTurnKey];
    // Si turnData no existe o está vacío, intentamos con el objeto de ronda directamente
    // ya que a veces la información de 'hand_P*' y 'victory_points' puede estar allí.
    const currentTurnState = (turnData && Object.keys(turnData).length > 0) ? turnData : lastRoundData;

    if (!currentTurnState) {
        console.error("[DEBUG] No se encontraron datos para el último turno (", lastTurnKey, ") en la ronda (", lastRoundKey, ")");
        return;
    }

    console.log("[DEBUG] Datos del último turno (", lastTurnKey, ") a usar:", JSON.parse(JSON.stringify(currentTurnState)));

    const resourcesOrder = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

    for (let i = 0; i < 4; i++) {
        // 1. Actualizar Puntos de Victoria
        let victoryPoints = 0;
        if (currentTurnState.victory_points && currentTurnState.victory_points['J' + i]) {
            victoryPoints = parseInt(currentTurnState.victory_points['J' + i]) || 0;
        } else if (game_data.setup && game_data.setup['P' + i]) {
            // Los PV iniciales son 2 por los dos poblados de setup
            // Esta es una heurística si no se encuentran en el último turno.
            victoryPoints = game_data.setup['P' + i].length; 
        }
        $('#puntos_victoria_J' + (i + 1)).text(victoryPoints);

        // 2. Actualizar Recursos
        const playerHandResources = currentTurnState['hand_P' + i];
        if (playerHandResources) {
            resourcesOrder.forEach(resourceName => {
                const quantity = playerHandResources[resourceName] || 0;
                $('#hand_P' + i + ' .resources-grid .' + resourceName + ' .' + resourceName + '_quantity').text(quantity);
            });
        } else {
            console.warn("[DEBUG] No se encontró hand_P" + i + " en los datos del turno/ronda.");
             resourcesOrder.forEach(resourceName => {
                $('#hand_P' + i + ' .resources-grid .' + resourceName + ' .' + resourceName + '_quantity').text(0);
            });
        }

        // 3. Actualizar Cartas de Desarrollo
        const devCardsOnHand = currentTurnState['development_cards_P' + i];
        const devCardCounts = {
            knight: 0,
            victory_point: 0,
            road_building: 0,
            year_of_plenty: 0,
            monopoly: 0
        };

        if (devCardsOnHand && Array.isArray(devCardsOnHand)) {
            devCardsOnHand.forEach(card => {
                let cardName = null;
                if (card.type === PYTHON_KNIGHT_CARD_TYPE) { // Knight
                    cardName = DEV_CARD_TYPE_MAP[PYTHON_KNIGHT_EFFECT]; // Asume effect 0 para knight
                } else if (card.type === PYTHON_VICTORY_POINT_CARD_TYPE) { // Victory Point
                    cardName = DEV_CARD_TYPE_MAP[PYTHON_VICTORY_POINT_EFFECT]; // Asume effect 1 para VP
                } else if (card.type === PYTHON_PROGRESS_CARD_TYPE) { // Progress Card
                    cardName = DEV_CARD_TYPE_MAP[card.effect]; // Usa el efecto para determinar el tipo de carta de progreso
                }

                if (cardName && devCardCounts.hasOwnProperty(cardName)) {
                    devCardCounts[cardName]++;
                }
            });
        }
         else {
            console.warn("[DEBUG] No se encontró development_cards_P" + i + " o no es un array en los datos del turno/ronda.");
        }

        for (const cardName in devCardCounts) {
            $('#hand_P' + i + ' .dev-cards-grid .' + cardName + ' .' + cardName + '_quantity').text(devCardCounts[cardName]);
        }
        
        // Actualizar badges de Mayor Ejército y Ruta más larga (si estuvieran en el JSON)
        // Esta información no parece estar consistentemente en `end_turn` o `start_turn` de la traza actual.
        // Se necesitaría añadir `largest_army_P${i}` y `longest_road_P${i}` al JSON.
        // Por ahora, se dejan como estaban (ocultos o con el valor del último estado procesado por el visualizador)
        // Ejemplo de cómo se haría si los datos estuvieran:
        // if (currentTurnState['largest_army_P' + i]) { $('#largest_army_P' + i).show(); } else { $('#largest_army_P' + i).hide(); }
        // if (currentTurnState['longest_road_P' + i]) { $('#longest_road_P' + i).show(); } else { $('#longest_road_P' + i).hide(); }
    }
    console.log("[DEBUG] UI actualizada con datos del JSON.");
}

// Funciones auxiliares para los logs mejorados
function getResourceIcon(resourceId) {
    const resourceIcons = {
        0: '<i class="fas fa-seedling text-success"></i>', // cereal
        1: '<i class="fas fa-mountain text-secondary"></i>', // mineral
        2: '<i class="fas fa-cubes text-warning"></i>', // clay
        3: '<i class="fas fa-tree text-success"></i>', // wood
        4: '<i class="fas fa-cut text-light"></i>' // wool
    };
    return resourceIcons[resourceId] || '<i class="fas fa-question"></i>';
}

function getResourceQuantity(resourceData) {
    // Si resourceData es un número, devuelve ese número
    if (typeof resourceData === 'number') return resourceData;
    // Si es un objeto, suma todos los valores
    if (typeof resourceData === 'object') {
        return Object.values(resourceData).reduce((sum, val) => sum + val, 0);
    }
    return 1; // valor por defecto
}

function getBuildingIcon(building) {
    const buildingIcons = {
        'S舎': '<i class="fas fa-home text-primary me-2"></i>',
        'settlement': '<i class="fas fa-home text-primary me-2"></i>',
        'C都市': '<i class="fas fa-city text-warning me-2"></i>',
        'city': '<i class="fas fa-city text-warning me-2"></i>',
        'R道': '<i class="fas fa-road text-secondary me-2"></i>',
        'road': '<i class="fas fa-road text-secondary me-2"></i>'
    };
    return buildingIcons[building] || '<i class="fas fa-hammer text-muted me-2"></i>';
}

function getBuildingName(building) {
    const buildingNames = {
        'S舎': 'un poblado',
        'settlement': 'un poblado',
        'C都市': 'una ciudad',
        'city': 'una ciudad',
        'R道': 'una carretera',
        'road': 'una carretera'
    };
    return buildingNames[building] || building;
}

function getCardIcon(cardType) {
    const cardIcons = {
        'knight': '<i class="fas fa-shield-alt text-danger me-2"></i>',
        'victory_point': '<i class="fas fa-trophy text-warning me-2"></i>',
        'road_building': '<i class="fas fa-road text-info me-2"></i>',
        'year_of_plenty': '<i class="fas fa-gift text-success me-2"></i>',
        'monopoly': '<i class="fas fa-coins text-warning me-2"></i>'
    };
    return cardIcons[cardType] || '<i class="fas fa-cards text-muted me-2"></i>';
}

function getCardName(cardType) {
    const cardNames = {
        'knight': 'Soldado',
        'victory_point': 'Punto de Victoria',
        'road_building': 'Construcción de Carreteras',
        'year_of_plenty': 'Año de Abundancia',
        'monopoly': 'Monopolio'
    };
    return cardNames[cardType] || cardType;
}

// Función para hacer auto-scroll en los logs
function autoScrollLog(logElementId) {
    const logElement = document.getElementById(logElementId);
    if (logElement) {
        setTimeout(() => {
            logElement.scrollTop = logElement.scrollHeight;
        }, 100);
    }
}

function deleteCaretStyling() {
    // Función para limpiar estilos de indicadores de cambio en recursos y cartas
    jQuery('.increment').removeClass('fa-caret-up fa-caret-down fa-minus');
    jQuery('.resource-item, .dev-card-item').removeClass('increased decreased neutral');
    
    // También limpiar los estilos antiguos si existen
    jQuery('.hand .increased, .hand .decreased, .hand .neutral').removeClass('increased decreased neutral');
    jQuery('.hand .increment').removeClass('fa-caret-up fa-caret-down fa-minus');
}

function move_thief(past_terrain, new_terrain, robbed_player, stolen_material_id, comes_from_card) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
    let actual_player = parseInt($('#contador_turnos').val()) - 1;

    // Mover el ladrón del terreno anterior
    if (past_terrain !== undefined && game_obj && game_obj.setup && game_obj.setup.board && game_obj.setup.board.board_terrain[past_terrain]) {
        if (game_obj.setup.board.board_terrain[past_terrain]['probability'] != 0) {
            jQuery('#terrain_' + past_terrain + ' .terrain_number').html('<span>' + game_obj.setup.board.board_terrain[past_terrain]['probability'] + '</span>');
        } else {
            jQuery('#terrain_' + past_terrain + ' .terrain_number').html('')
        }
    }

    // Colocar el ladrón en el nuevo terreno
    if (new_terrain !== undefined) {
        jQuery('#terrain_' + new_terrain + ' .terrain_number').html('<i class="fa-solid fa-user-ninja fa-2x" data-toggle="tooltip" data-placement="top" title="Ladrón"></i>');
    }

    // Manejar el robo de recursos si aplica
    if (comes_from_card && stolen_material_id !== undefined && robbed_player !== undefined && robbed_player !== -1) {
        let actual_player_material_quantity = $('#hand_P' + actual_player + ' .' + materials[stolen_material_id] + '_quantity');
        let robbed_player_material_quantity = $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id] + '_quantity');
        
        // Actualizar las cantidades si los elementos existen
        if (actual_player_material_quantity.length && robbed_player_material_quantity.length) {
            let actualValue = parseInt(actual_player_material_quantity.text()) || 0;
            let robbedValue = parseInt(robbed_player_material_quantity.text()) || 0;
            
            actual_player_material_quantity.text(actualValue + 1);
            robbed_player_material_quantity.text(Math.max(0, robbedValue - 1));
        }
    }
}

function changeHandObject(player, hand_obj) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
    let dev_cards = ['knight', 'victory_point', 'road_building', 'year_of_plenty', 'monopoly'];

    // Actualizar recursos
    materials.forEach(function (material) {
        if (hand_obj && hand_obj[material] !== undefined) {
            $('#hand_P' + player + ' .resources-grid .' + material + ' .' + material + '_quantity').text(hand_obj[material]);
        }
    });

    // Actualizar cartas de desarrollo
    dev_cards.forEach(function (card) {
        // Asumiendo que las cartas de desarrollo están dentro del mismo objeto `hand_obj`
        // y que sus claves coinciden con los nombres de las clases (ej: hand_obj['knight'])
        if (hand_obj && hand_obj[card] !== undefined) {
            $('#hand_P' + player + ' .dev-cards-grid .' + card + ' .' + card + '_quantity').text(hand_obj[card]);
        } else if (hand_obj && hand_obj['development_cards'] && hand_obj['development_cards'][card] !== undefined) {
            // Alternativa: si las cartas están en un sub-objeto 'development_cards'
             $('#hand_P' + player + ' .dev-cards-grid .' + card + ' .' + card + '_quantity').text(hand_obj['development_cards'][card]);
        }
    });
}

function on_development_card_played(card_played_info) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
    let resourceIcons = ['🌾', '⛰️', '🧱', '🪵', '🐑'];

    let contador_turnos = jQuery('#contador_turnos');
    let other_useful_info_text = jQuery('#other_useful_info_text');
    let actual_player = $('#contador_turnos').val() - 1;
    
    if (!card_played_info || !card_played_info.played_card) {
        console.warn("[DEBUG] on_development_card_played: card_played_info no válido");
        return;
    }
    
    let quantity = jQuery('#hand_P' + actual_player + ' .dev-cards-grid .' + card_played_info.played_card + ' .' + card_played_info.played_card + '_quantity');

    // Actualizar el contador de la carta jugada
    if (quantity.length) {
        let currentValue = parseInt(quantity.text()) || 0;
        quantity.text(Math.max(0, currentValue - 1));
        
        // Animar la disminución
        quantity.addClass('animate__animated animate__pulse text-danger');
        setTimeout(() => {
            quantity.removeClass('animate__animated animate__pulse text-danger');
        }, 1000);
    }

    let html = '<div class="log-entry play-card mb-2">';
    html += getCardIcon(card_played_info.played_card);
    html += '<strong>Jugador ' + actual_player + '</strong> jugó ';
    html += '<span class="fw-bold">' + getCardName(card_played_info.played_card) + '</span>';
    
    switch (card_played_info.played_card) {
        case 'knight':
            html += ' ⚔️';
            if (card_played_info.past_thief_terrain !== undefined && card_played_info.thief_terrain !== undefined) {
                move_thief(card_played_info.past_thief_terrain, card_played_info.thief_terrain, card_played_info.robbed_player, card_played_info.stolen_material_id, true);
                html += '<br><small class="ms-4">🥷 Movió el ladrón del terreno ' + card_played_info.past_thief_terrain + ' al ' + card_played_info.thief_terrain;
                if (card_played_info.robbed_player !== undefined && card_played_info.robbed_player !== -1) {
                    html += ' y robó al Jugador ' + card_played_info.robbed_player + ' 💰';
                }
                html += '</small>';
            }
            break;
        case 'victory_point':
            html += ' 🏆<br><small class="ms-4">Punto de Victoria revelado ✨</small>';
            break;
        case 'monopoly':
            html += ' 💰';
            if (card_played_info.material_chosen !== undefined) {
                let material_chosen = materials[card_played_info.material_chosen];
                let materialIcon = resourceIcons[card_played_info.material_chosen];
                html += '<br><small class="ms-4">Monopolio de: ' + materialIcon + ' ' + material_chosen + '</small>';
                
                // Actualizar las manos de todos los jugadores si está disponible
                for (let i = 0; i < 4; i++) {
                    if (card_played_info['hand_P' + i]) {
                        changeHandObject(i, card_played_info['hand_P' + i]);
                    }
                }
            }
            break;
        case 'year_of_plenty':
            html += ' 🎁';
            if (card_played_info.materials_selected) {
                let material1Icon = resourceIcons[card_played_info.materials_selected.material];
                let material2Icon = resourceIcons[card_played_info.materials_selected.material_2];
                let materials_chosen = [
                    material1Icon + ' ' + materials[card_played_info.materials_selected.material], 
                    material2Icon + ' ' + materials[card_played_info.materials_selected.material_2]
                ];
                html += '<br><small class="ms-4">Recursos elegidos: ' + materials_chosen.join(', ') + '</small>';
                
                if (card_played_info['hand_P' + actual_player]) {
                    changeHandObject(actual_player, card_played_info['hand_P' + actual_player]);
                }
            }
            break;
        case 'road_building':
            html += ' 🛤️';
            if (card_played_info.roads) {
                html += '<br><small class="ms-4">Construcción de carreteras: ';
                if (card_played_info.valid_road_1) {
                    html += '🚧 Carretera 1 (nodo ' + card_played_info.roads.node_id + ' → ' + card_played_info.roads.road_to + ') ';
                    // Dibujar la carretera en el tablero
                    let road_id_str = card_played_info.roads.node_id < card_played_info.roads.road_to ? 
                        `road_${card_played_info.roads.node_id}_${card_played_info.roads.road_to}` : 
                        `road_${card_played_info.roads.road_to}_${card_played_info.roads.node_id}`;
                    animateRoadBuilding(road_id_str, actual_player);
                }
                if (card_played_info.valid_road_2) {
                    html += '🚧 Carretera 2 (nodo ' + card_played_info.roads.node_id_2 + ' → ' + card_played_info.roads.road_to_2 + ') ';
                    // Dibujar la segunda carretera en el tablero
                    let road_id_str = card_played_info.roads.node_id_2 < card_played_info.roads.road_to_2 ? 
                        `road_${card_played_info.roads.node_id_2}_${card_played_info.roads.road_to_2}` : 
                        `road_${card_played_info.roads.road_to_2}_${card_played_info.roads.node_id_2}`;
                    animateRoadBuilding(road_id_str, actual_player);
                }
                html += '</small>';
            }
            break;
        default:
            break;
    }
    
    html += '</div>';
    other_useful_info_text.append(html);
    autoScrollLog('other_useful_info_text');
    
    // Animar la carta que se acaba de jugar
    animateCardPlay(actual_player, card_played_info.played_card);
}

function animateDiceRoll(totalValue) {
    // Dividir el valor total en dos dados (simulando dos dados de 6 caras)
    let dice1Value, dice2Value;
    
    if (totalValue <= 6) {
        dice1Value = Math.floor(Math.random() * Math.min(totalValue, 6)) + 1;
        dice2Value = totalValue - dice1Value;
        if (dice2Value < 1) {
            dice2Value = 1;
            dice1Value = totalValue - 1;
        }
    } else {
        dice1Value = Math.floor(Math.random() * 6) + 1;
        dice2Value = totalValue - dice1Value;
        if (dice2Value > 6) {
            dice1Value = totalValue - 6;
            dice2Value = 6;
        }
    }

    // Actualizar el valor total en la UI
    $('#diceroll .dice-value').text(totalValue);
    
    // Mostrar el overlay de dados
    const overlay = $('#dice-overlay');
    overlay.fadeIn(300);
    
    // Animar los dados individualmente
    const dice1 = $('.dice-1');
    const dice2 = $('.dice-2');
    
    // Limpiar clases anteriores
    dice1.removeClass('rolling').removeClass(function (index, className) {
        return (className.match(/(^|\s)show-\S+/g) || []).join(' ');
    });
    dice2.removeClass('rolling').removeClass(function (index, className) {
        return (className.match(/(^|\s)show-\S+/g) || []).join(' ');
    });
    
    // Añadir animación de rotación
    dice1.addClass('rolling');
    dice2.addClass('rolling');
    
    // Actualizar valores mostrados en el resultado
    $('#dice-value-1').text(dice1Value);
    $('#dice-value-2').text(dice2Value);
    $('#dice-total').text(totalValue);
    
    // Después de un tiempo, mostrar el resultado y quitar la animación
    setTimeout(function() {
        dice1.removeClass('rolling').addClass('show-' + dice1Value);
        dice2.removeClass('rolling').addClass('show-' + dice2Value);
        
        // Ocultar el overlay después de mostrar el resultado
        setTimeout(function() {
            overlay.fadeOut(500);
        }, 2000);
    }, 2000);
    
    console.log(`[DEBUG] Dados animados: ${dice1Value} + ${dice2Value} = ${totalValue}`);
}

// Nueva función para actualizar cartas de desarrollo
function updateDevCards(playerIndex, devCardsArray) {
    const devCardCounts = {
        knight: 0,
        victory_point: 0,
        road_building: 0,
        year_of_plenty: 0,
        monopoly: 0
    };
    
    const DEV_CARD_TYPE_MAP = {
        0: 'knight',
        1: 'victory_point',
        2: 'road_building',
        3: 'year_of_plenty',
        4: 'monopoly'
    };
    
    if (devCardsArray && Array.isArray(devCardsArray)) {
        devCardsArray.forEach(card => {
            let cardName = null;
            if (card.type === 0) { // Knight
                cardName = 'knight';
            } else if (card.type === 1) { // Victory Point
                cardName = 'victory_point';
            } else if (card.type === 2) { // Progress Card
                cardName = DEV_CARD_TYPE_MAP[card.effect];
            }
            
            if (cardName && devCardCounts.hasOwnProperty(cardName)) {
                devCardCounts[cardName]++;
            }
        });
    }
    
    // Actualizar UI
    for (const cardName in devCardCounts) {
        const cardElement = $(`#hand_P${playerIndex} .dev-cards-grid .${cardName} .${cardName}_quantity`);
        if (cardElement.length) {
            const oldValue = parseInt(cardElement.text()) || 0;
            const newValue = devCardCounts[cardName];
            
            cardElement.text(newValue);
            
            // Animar cambio si es diferente
            if (oldValue !== newValue) {
                cardElement.addClass('animate__animated animate__bounceIn');
                setTimeout(() => {
                    cardElement.removeClass('animate__animated animate__bounceIn');
                }, 1000);
            }
        }
    }
}
