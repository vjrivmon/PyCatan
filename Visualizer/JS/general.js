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
                
                // Inicializar juego
                console.log('[DEBUG] Antes de init_events_with_game_obj(). game_obj:', JSON.parse(JSON.stringify(game_obj))); // DEBUG
                init_events_with_game_obj();
                console.log('[DEBUG] Después de init_events_with_game_obj().'); // DEBUG

                console.log('[DEBUG] Antes de addLogFromJSON().'); // DEBUG
                addLogFromJSON();
                console.log('[DEBUG] Después de addLogFromJSON().'); // DEBUG

                console.log('[DEBUG] Antes de setup().'); // DEBUG
                setup();
                console.log('[DEBUG] Después de setup().'); // DEBUG

                console.log('[DEBUG] Antes de reset_game().'); // DEBUG
                reset_game();
                console.log('[DEBUG] Después de reset_game().'); // DEBUG
                
                // Cerrar el modal
                $('#uploadModal').modal('hide');
                console.log('[DEBUG] Modal cerrado. Carga de partida completada (en teoría).'); // DEBUG
                
                // Limpiar selección
                selectedFile = null;
                // selectedFileDisplay.innerHTML = ''; // Comentado
                loadSelectedFileBtn.disabled = true;
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
    let materials = ['cereal', 'clay', 'wool', 'wood', 'mineral'];
    let cards = ['knight', 'victory_point', 'road_building', 'year_of_plenty', 'monopoly'];
    let classes = materials.concat(cards);

    for (let i = 1; i < 5; i++) {
        $('#puntos_victoria_J' + i).text(0);
        classes.forEach(function (array_element) {
            $('#hand_P' + (i - 1) + ' .' + array_element + '_quantity').text(0);
        });
    }
}

function addLogFromJSON() {
    $('#contador_rondas').val(1).change()
    $('#contador_turnos').val(1).change()
    $('#contador_fases').val(1).change()

    $('#rondas_maximas').text(Object.keys(game_obj['game']).length)
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

            node.html('<i class="fa-solid fa-house"></i>');
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
        terrain_div.removeClass(['terrain_cereal', 'terrain_mineral', 'terrain_clay', 'terrain_wood', 'terrain_wool', 'terrain_desert'])
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
    // let playIntervalNumber = 0; // Comentado ya que la lógica de play está comentada

    console.log('[DEBUG] init_events_with_game_obj SIMPLIFICADA para depuración');

    // CONTENIDO PRINCIPAL DE LA FUNCIÓN COMENTADO PARA DEPURACIÓN
    /*
    contador_rondas.off().on('change', function (e) {
        // ... lógica original ...
    });
    contador_turnos.off().on('change', function (e) {
        // ... lógica original ...
    });
    contador_fases.off().on('change', function (e) {
        // ... lógica original MUY EXTENSA ...
    });
    */

    // Listeners simplificados para depuración (solo los de navegación básica)
    ronda_previa_btn.off().on('click', function (e) {
        console.log('[DEBUG] ronda_previa_btn click');
        // Aquí iría la lógica real, pero se omite para depurar
    });
    ronda_siguiente_btn.off().on('click', function (e) {
        console.log('[DEBUG] ronda_siguiente_btn click');
    });

    turno_previo_btn.off().on('click', function (e) {
        console.log('[DEBUG] turno_previo_btn click');
    });
    turno_siguiente_btn.off().on('click', function (e) {
        console.log('[DEBUG] turno_siguiente_btn click');
    });

    fase_previa_btn.off().on('click', function (e) {
        console.log('[DEBUG] fase_previa_btn click');
        game_direction = 'backward';
        let value = parseInt(contador_fases.val());
        if (!isNaN(value)) {
            contador_fases.val(value - 1).change();
        }
    });
    fase_siguiente_btn.off().on('click', function (e) {
        console.log('[DEBUG] fase_siguiente_btn click');
        game_direction = 'forward';
        let value = parseInt(contador_fases.val());
        if (!isNaN(value)) {
            contador_fases.val(value + 1).change();
        }
    });

    // millis_for_play y play_btn ya no tienen lógica activa aquí por ahora
    millis_for_play.off().on('change', function (e) {
        jQuery('#millis_seleccionados').val(millis_for_play.val());
    });

    play_btn.off().on('click', function (e) {
        // Contenido completamente comentado para evitar errores de sintaxis internos.
        /*
        let _this = $(this);
        let _i = _this.find('i');
        // ... resto del código comentado ...
        */
        console.log('[DEBUG] play_btn click (lógica principal comentada)');
    }); // Cierre del manejador de play_btn

} // Cierre de la función init_events_with_game_obj

// El resto del archivo JS sigue aquí...
// Nos aseguramos que no haya caracteres extraños antes de esta función
function changeHandObject(player, hand_obj) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
    let dev_cards = ['knight', 'victory_point', 'road_building', 'year_of_plenty', 'monopoly'];

    materials.forEach(function (material) {
        if (hand_obj[material] !== undefined) {
            $('#hand_P' + player + ' .' + material + '_quantity').text(hand_obj[material]);
        }
    });

    dev_cards.forEach(function (card) {
        // Asumiendo que las cartas de desarrollo están dentro del mismo objeto `hand_obj`
        // y que sus claves coinciden con los nombres de las clases (ej: hand_obj['knight'])
        if (hand_obj[card] !== undefined) {
            $('#hand_P' + player + ' .' + card + '_quantity').text(hand_obj[card]);
        } else if (hand_obj['development_cards'] && hand_obj['development_cards'][card] !== undefined) {
            // Alternativa: si las cartas están en un sub-objeto 'development_cards'
             $('#hand_P' + player + ' .' + card + '_quantity').text(hand_obj['development_cards'][card]);
        }
    });
}

function paint_it_player_color(player, object_to_paint) {
    object_to_paint = jQuery(object_to_paint);
    object_to_paint.css('color', 'black')
    switch (player) {
        case 0:
            object_to_paint.css('background', 'lightcoral')
            break;
        case 1:
            object_to_paint.css('background', 'lightblue')
            break;
        case 2:
            object_to_paint.css('background', 'lightgreen')
            break;
        case 3:
            object_to_paint.css('background', 'lightyellow')
            break;
        default:
            object_to_paint.css('background', 'none')
            break;
    }
}

function move_thief(past_terrain, new_terrain, robbed_player, stolen_material_id, comes_from_card) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
    let actual_player = parseInt($('#contador_turnos').val()) - 1;

    if (game_obj['setup']['board']['board_terrain'][past_terrain]['probability'] != 0) {
        jQuery('#terrain_' + past_terrain + ' .terrain_number').html('<span>' + game_obj['setup']['board']['board_terrain'][past_terrain]['probability'] + '</span>');
    } else {
        jQuery('#terrain_' + past_terrain + ' .terrain_number').html('')
    }

    jQuery('#terrain_' + new_terrain + ' .terrain_number').html('<i class="fa-solid fa-user-ninja fa-2x" data-toggle="tooltip" data-placement="top" title="Ladrón"></i>');

    if (comes_from_card) {
        let actual_player_material_quantity = $('#hand_P' + actual_player + ' .' + materials[stolen_material_id] + '_quantity');
        let robbed_player_material_quantity = $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id] + '_quantity');
        actual_player_material_quantity.val(actual_player_material_quantity.val() + 1);
        robbed_player_material_quantity.val(robbed_player_material_quantity.val() - 1);
    }

    if (actual_player == robbed_player) {
        $('#hand_P' + actual_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass('fa-caret-up fa-minus fa-caret-down').addClass('fa-minus');
        $('#hand_P' + actual_player + ' .' + materials[stolen_material_id]).removeClass('increased neutral decreased').addClass('neutral');
    } else {
        $('#hand_P' + actual_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass('fa-caret-up fa-minus fa-caret-down').addClass('fa-caret-up');
        $('#hand_P' + actual_player + ' .' + materials[stolen_material_id]).removeClass('increased neutral decreased').addClass('increased');
        $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass('fa-caret-up fa-minus fa-caret-down').addClass('fa-caret-down');
        $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id]).removeClass('increased neutral decreased').addClass('decreased');
    }
}

function unmove_thief(past_terrain, new_terrain, robbing_player, robbed_player, stolen_material_id, comes_from_card) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

    if (game_obj['setup']['board']['board_terrain'][past_terrain]['probability'] != 0) {
        jQuery('#terrain_' + new_terrain + ' .terrain_number').html('<span>' + game_obj['setup']['board']['board_terrain'][new_terrain]['probability'] + '</span>');
    } else {
        jQuery('#terrain_' + new_terrain + ' .terrain_number').html('')
    }

    jQuery('#terrain_' + past_terrain + ' .terrain_number').html('<i class="fa-solid fa-user-ninja fa-2x" data-toggle="tooltip" data-placement="top" title="Ladrón"></i>');

    if (comes_from_card) {
        let robbed_player_material_quantity = $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id] + '_quantity');
        let robbing_player_material_quantity = $('#hand_P' + robbing_player + ' .' + materials[stolen_material_id] + '_quantity');
        robbed_player_material_quantity.val(robbed_player_material_quantity.val() + 1);
        robbing_player_material_quantity.val(robbing_player_material_quantity.val() - 1);
    }

    deleteCaretStyling();
}

function on_development_card_played(card) {
    // TODO: Mejora a futuro: mostrar dentro de "mayor ejercito" o algún lugar, cantidad de caballeros que tiene activos cada jugador.
    // TODO: Mejora a futuro: limitar altura de jQuery('#other_useful_info_text')
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

    let contador_turnos = jQuery('#contador_turnos');
    let other_useful_info_text = jQuery('#other_useful_info_text');
    let actual_player = $('#contador_turnos').val() - 1;
    let quantity = jQuery('#hand_P' + (jQuery('#contador_turnos').val() - 1) + ' .' + card['played_card'] + '_quantity');

    jQuery('#hand_P' + (contador_turnos.val() - 1) + ' .' + card['played_card']).removeClass('increased neutral decreased').addClass('decreased');
    jQuery('#hand_P' + (contador_turnos.val() - 1) + ' .' + card['played_card'] + ' .increment').removeClass('fa-caret-up fa-minus fa-caret-down').addClass('fa-caret-down');
    quantity.text(parseInt(quantity.text()) - 1).change();

    let html = '<div>';
    switch (card['played_card']) {
        case 'knight':
            move_thief(card['past_thief_terrain'], card['thief_terrain'], card['robbed_player'], card['stolen_material_id'], true);
            html += 'Played card: knight | Past thief terrain: ' + card['past_thief_terrain'] + ' | New thief terrain: ' + card['thief_terrain'] + ' | Robbed player: ' + card['robbed_player'] + ' | Stolen material: ' + materials[card['stolen_material_id']];
            break;
        case 'victory_point':
            html += 'Played card: Victory point';
        case 'failed_victory_point':
            html += 'Played card: Failed victory point'
            break;

        case 'monopoly':
            let material_chosen = materials[card['material_chosen']];

            for (let i = 0; i < 4; i++) {
                changeHandObject(i, card['hand_P' + i]);
                jQuery('#hand_P' + i + ' .' + material_chosen).addClass('decreased');
                jQuery('#hand_P' + i + ' .' + material_chosen + ' .increment').addClass('fa-caret-down');
            }

            jQuery('#hand_P' + actual_player + ' .' + material_chosen).removeClass('decreased').addClass('increased');
            jQuery('#hand_P' + actual_player + ' .' + material_chosen + ' .increment').removeClass('fa-caret-down').addClass('fa-caret-up');

            html += 'Played card: Monopoly | Material chosen: ' + material_chosen
            break;

        case 'year_of_plenty':
            let materials_chosen = [materials[card['materials_selected']['material']], materials[card['materials_selected']['material_2']]];

            changeHandObject(actual_player, card['hand_P' + actual_player]);
            materials_chosen.forEach(function (material) {
                jQuery('#hand_P' + actual_player + ' .' + material).removeClass('increased neutral decreased').addClass('increased');
                jQuery('#hand_P' + actual_player + ' .' + material + ' .increment').removeClass('fa-caret-up fa-minus fa-caret-down').addClass('fa-caret-up');
            })

            html += 'Played card: Year of plenty | Material chosen 1: ' + materials_chosen[0] + ' | Material chosen 2: ' + materials_chosen[1];
            break;

        case 'road_building':
            let roads = card['roads'];

            if (card['valid_road_1']) {
                let road = '';
                if (roads['node_id'] < roads['road_to']) {
                    road = jQuery('#road_' + roads['node_id'] + '_' + roads['road_to']);
                } else {
                    road = jQuery('#road_' + roads['road_to'] + '_' + roads['node_id']);
                }
                paint_it_player_color(actual_player, road);
            }
            if (card['valid_road_2']) {
                let road = '';
                if (roads['node_id_2'] < roads['road_to_2']) {
                    road = jQuery('#road_' + roads['node_id_2'] + '_' + roads['road_to_2']);
                } else {
                    road = jQuery('#road_' + roads['road_to_2'] + '_' + roads['node_id_2']);
                }
                paint_it_player_color(actual_player, road);
            }

            html += 'Played card: Road building | Node 1: ' + roads['node_id'] + ' | Road to: ' + roads['road_to'] + ' | Valid road: ' + card['valid_road_1'] + ' | Node 2: ' + roads['node_id_2'] + ' | Road to 2: ' + roads['road_to_2'] + ' | Valid road 2: ' + card['valid_road_2'];
            break;

        case 'none':
        default:
            break;
    }
    html += '</div>';
    other_useful_info_text.append(html);
}

function off_development_card_played(card, player_that_played_card) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

    let contador_turnos = jQuery('#contador_turnos');
    let other_useful_info_text = jQuery('#other_useful_info_text');
    let actual_player = $('#contador_turnos').val() - 1;
    let quantity = jQuery('#hand_P' + (jQuery('#contador_turnos').val() - 1) + ' .' + card['played_card'] + '_quantity');

    quantity.text(parseInt(quantity.text()) + 1).change();

    switch (card['played_card']) {
        case 'knight':
            unmove_thief(card['past_thief_terrain'], card['thief_terrain'], player_that_played_card, card['robbed_player'], card['stolen_material_id'], true);
        case 'victory_point':
        case 'failed_victory_point':
        case 'monopoly':
        case 'year_of_plenty':
            break;

        case 'road_building':
            let roads = card['roads'];

            if (card['valid_road_1']) {
                let road = '';
                if (roads['node_id'] < roads['road_to']) {
                    road = jQuery('#road_' + roads['node_id'] + '_' + roads['road_to']);
                } else {
                    road = jQuery('#road_' + roads['road_to'] + '_' + roads['node_id']);
                }
                paint_it_player_color(-1, road);
            }
            if (card['valid_road_2']) {
                let road = '';
                if (roads['node_id_2'] < roads['road_to_2']) {
                    road = jQuery('#road_' + roads['node_id_2'] + '_' + roads['road_to_2']);
                } else {
                    road = jQuery('#road_' + roads['road_to_2'] + '_' + roads['node_id_2']);
                }
                paint_it_player_color(-1, road);
            }
            break;

        case 'none':
        default:
            break;
    }
}

function deleteCaretStyling() {
    jQuery('.increment').removeClass('fa-caret-up fa-caret-down fa-minus');
    jQuery('.increment').parent().removeClass('increased decreased neutral');
}

function setup() {
    //            nodeSetup();
    terrainSetup();
    addSetupBuildings();
    
    // Inicializar el botón de play y sus eventos si aún no lo están
    initAutoPlayControls();
}

// init()
window.addEventListener('load', function () {
    init_events();
}, false);

// Funciones para animaciones y efectos especiales
function initAnimations() {
    // Configuración de animaciones
    $('.terrain').each(function(index) {
        // Añadimos un pequeño retraso a la animación de cada terreno para crear un efecto cascada
        gsap.from(this, {
            duration: 0.8,
            delay: index * 0.05,
            y: -50,
            opacity: 0,
            ease: "power2.out"
        });
    });

    // Animación de los nodos
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

// Función mejorada para animar los dados - versión con dos dados
function animateDiceRoll(value) {
    console.log("Animando dados con valor total: " + value);
    
    // Calcular valores para los dos dados
    // Generamos valores aleatorios que sumen el valor total
    let dice1Value, dice2Value;
    
    if (value <= 7) {
        // Para valores menores o iguales a 7, tenemos más opciones de combinación
        dice1Value = Math.max(1, Math.min(6, Math.floor(Math.random() * value)));
    } else {
        // Para valores mayores a 7, aseguramos que ningún dado exceda 6
        dice1Value = Math.max(1, Math.min(6, Math.floor(Math.random() * 6) + 1));
    }
    
    dice2Value = value - dice1Value;
    
    // Si el segundo dado excede 6 o es menor que 1, ajustamos ambos valores
    if (dice2Value > 6) {
        dice1Value = Math.max(value - 6, 1);
        dice2Value = value - dice1Value;
    } else if (dice2Value < 1) {
        dice1Value = Math.min(value - 1, 6);
        dice2Value = value - dice1Value;
    }
    
    console.log("Valores de dados: " + dice1Value + " + " + dice2Value + " = " + value);
    
    // Verificar que el overlay existe
    const overlay = document.getElementById('dice-overlay');
    if (!overlay) {
        console.error("Error: Elemento 'dice-overlay' no encontrado");
        return;
    }
    
    // Pausar los controles del juego durante la animación
    const controls = document.querySelectorAll('#controles button');
    controls.forEach(button => button.disabled = true);
    
    // Mostrar el overlay
    overlay.classList.add('active');
    overlay.style.display = 'flex';
    
    // Obtener los dados y sus resultados
    const dice1 = document.querySelector('.dice-1');
    const dice2 = document.querySelector('.dice-2');
    
    if (!dice1 || !dice2) {
        console.error("Error: Elementos de dados no encontrados");
        overlay.classList.remove('active');
        controls.forEach(button => button.disabled = false);
        return;
    }
    
    const diceResult = document.querySelector('.dice-result');
    const diceValue1 = document.getElementById('dice-value-1');
    const diceValue2 = document.getElementById('dice-value-2');
    const diceTotal = document.getElementById('dice-total');
    
    // Asignar los valores finales
    if (diceValue1) diceValue1.textContent = dice1Value;
    if (diceValue2) diceValue2.textContent = dice2Value;
    if (diceTotal) diceTotal.textContent = value;
    
    // Reset de transformaciones previas
    dice1.style.transform = 'rotateX(0deg) rotateY(0deg) rotateZ(0deg)';
    dice2.style.transform = 'rotateX(0deg) rotateY(0deg) rotateZ(0deg)';
    
    // Valores de rotación para cada resultado de los dados
    let rotationValues = {
        1: [0, 0, 0],       // Frontal muestra 1
        2: [0, -90, 0],     // Derecha muestra 2
        3: [-90, 0, 0],     // Arriba muestra 3
        4: [90, 0, 0],      // Abajo muestra 4
        5: [0, 90, 0],      // Izquierda muestra 5
        6: [0, 180, 0]      // Atrás muestra 6
    };
    
    // Verificar que GSAP está disponible
    if (typeof gsap === 'undefined') {
        console.error("Error: GSAP no está disponible");
        // Fallback a CSS básico
        setTimeout(() => {
            if (diceResult) diceResult.classList.add('show');
            setTimeout(() => {
                overlay.classList.remove('active');
                controls.forEach(button => button.disabled = false);
            }, 2000);
        }, 1000);
        return;
    }
    
    // Asegurarnos de que los dados estén visibles
    dice1.style.opacity = "1";
    dice1.style.display = "block";
    dice2.style.opacity = "1";
    dice2.style.display = "block";
    
    // Animación de agitado inicial - Dado 1
    gsap.to(dice1, {
        duration: 0.5,
        rotationX: Math.random() * 720 - 360,
        rotationY: Math.random() * 720 - 360,
        rotationZ: Math.random() * 720 - 360,
        ease: "power1.inOut"
    });
    
    // Animación de agitado inicial - Dado 2
    gsap.to(dice2, {
        duration: 0.5,
        rotationX: Math.random() * 720 - 360,
        rotationY: Math.random() * 720 - 360,
        rotationZ: Math.random() * 720 - 360,
        ease: "power1.inOut",
        onComplete: function() {
            console.log("Primera animación completada");
            
            // Animación principal del Dado 1
            gsap.to(dice1, {
                duration: 2,
                rotationX: Math.random() * 1440 - 720,
                rotationY: Math.random() * 1440 - 720,
                rotationZ: Math.random() * 1440 - 720,
                ease: "power3.inOut"
            });
            
            // Animación principal del Dado 2
            gsap.to(dice2, {
                duration: 2,
                rotationX: Math.random() * 1440 - 720,
                rotationY: Math.random() * 1440 - 720,
                rotationZ: Math.random() * 1440 - 720,
                ease: "power3.inOut",
                onComplete: function() {
                    console.log("Segunda animación completada");
                    
                    // Animar hasta el resultado final - Dado 1
                    gsap.to(dice1, {
                        duration: 1,
                        rotationX: rotationValues[dice1Value][0],
                        rotationY: rotationValues[dice1Value][1],
                        rotationZ: rotationValues[dice1Value][2],
                        ease: "elastic.out(1, 0.8)"
                    });
                    
                    // Animar hasta el resultado final - Dado 2
                    gsap.to(dice2, {
                        duration: 1,
                        rotationX: rotationValues[dice2Value][0],
                        rotationY: rotationValues[dice2Value][1],
                        rotationZ: rotationValues[dice2Value][2],
                        ease: "elastic.out(1, 0.8)",
                        onComplete: function() {
                            console.log("Animación final completada");
                            
                            // Mostrar el resultado
                            if (diceResult) {
                                diceResult.classList.add('show');
                            }
                            dice1.classList.add('dice-shake');
                            dice2.classList.add('dice-shake');
                            
                            // Esperar un momento y ocultar la animación
                            setTimeout(function() {
                                if (diceResult) {
                                    diceResult.classList.remove('show');
                                }
                                overlay.classList.remove('active');
                                
                                // Actualizar la visualización del resultado en la interfaz
                                $('.dice-value').text(value);
                                $('#diceroll').addClass('animate__animated animate__bounceIn');
                                
                                // Habilitar los controles del juego nuevamente
                                controls.forEach(button => button.disabled = false);
                                
                                setTimeout(function() {
                                    $('#diceroll').removeClass('animate__animated animate__bounceIn');
                                }, 1000);
                            }, 2500);
                        }
                    });
                }
            });
        }
    });
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
    // Seleccionar el elemento a animar
    let element = $('#hand_P' + playerIndex + ' .' + resourceType + '_quantity');
    let icon = element.siblings('i.fa-solid').first();
    
    // Actualizar el texto
    let currentValue = parseInt(element.text());
    element.text(currentValue + quantity);
    
    // Animar el incremento
    if (quantity > 0) {
        icon.addClass('increased fa-bounce');
        setTimeout(() => icon.removeClass('increased fa-bounce'), 1000);
    } else if (quantity < 0) {
        icon.addClass('decreased fa-shake');
        setTimeout(() => icon.removeClass('decreased fa-shake'), 1000);
    }
}

// Función para animar construcciones
function animateBuilding(nodeId, buildingType, playerIndex) {
    let node = $('#node_' + nodeId);
    let icon;
    
    // Asignar el icono según el tipo de construcción
    if (buildingType === 'settlement') {
        icon = '<i class="fa-solid fa-house"></i>';
    } else if (buildingType === 'city') {
        icon = '<i class="fa-solid fa-building"></i>';
    }
    
    // Aplicar animación
    node.html(icon);
    node.css('transform', 'scale(0)');
    gsap.to(node[0], {
        duration: 0.5,
        scale: 1,
        ease: "elastic.out(1, 0.3)",
        onComplete: function() {
            paint_it_player_color(playerIndex, node);
        }
    });
}

// Función para animar la construcción de carreteras
function animateRoadBuilding(roadId, playerIndex) {
    let road = $('#' + roadId);
    
    // Animar la construcción
    road.css('transform', 'scaleX(0)');
    gsap.to(road[0], {
        duration: 0.5,
        scaleX: 1,
        ease: "power1.out",
        onComplete: function() {
            paint_it_player_color(playerIndex, road);
        }
    });
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
    for (let i = 0; i < 4; i++) {
        let points = parseInt($('#puntos_victoria_J' + (i + 1)).text());
        if (points >= 10) {
            showVictoryConfetti(i);
            return true;
        }
    }
    return false;
}

// Modificar función existente para incluir verificación de victoria
let originalSetup = setup;
setup = function() {
    originalSetup();
    initAnimations();
    
    // Renderizar jugadores dinámicamente
    renderPlayerProfiles();
    
    // Estilizar mejor los nodos de puerto
    enhanceHarborNodes();
    
    // Mejorar la animación de los dados
    enhanceDiceRoll();
    
    // Aplicar efectos de agua
    applyWaterEffects();
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
                    <div class="player-body">
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
    gsap.from('.player-card', {
        duration: 0.8,
        y: 50,
        opacity: 0,
        stagger: 0.2,
        ease: "power2.out"
    });
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
        const contador_fases = jQuery('#contador_fases');
        originalCounterFasesChange = contador_fases.off('change').get(0).onchange;
        
        // Reemplazar con nuestra función mejorada
        contador_fases.on('change', function(e) {
            if (contador_fases.val() === '') {
                return;
            }
            
            let actual_player_json = parseInt(jQuery('#contador_turnos').val()) - 1;
            
            // Si estamos en la fase 0 (inicio del turno) y avanzando
            if (parseInt(contador_fases.val()) === 1 && game_direction === 'forward') {
                // Obtener el objeto de fase
                const phase_obj = turn_obj['start_turn'];
                
                // Si hay un valor de dado, lanzar la animación
                if (phase_obj && phase_obj['dice']) {
                    animateDiceRoll(phase_obj['dice']);
                    
                    // Continuar con el resto del procesamiento después de la animación
                    setTimeout(function() {
                        // Llamar a la función original después de la animación
                        originalCounterFasesChange.call(contador_fases.get(0), e);
                    }, 3500); // Ajustar según la duración de la animación
                    
                    return; // Evitar la ejecución inmediata
                }
            }
            
            // Para otros casos, llamar a la función original directamente
            originalCounterFasesChange.call(contador_fases.get(0), e);
        });
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

// Mejorar la función setup para incluir los efectos de cursor
let originalSetupWithCursor = setup;
setup = function() {
    originalSetupWithCursor();
    initAnimations();
    
    // Renderizar jugadores dinámicamente
    renderPlayerProfiles();
    
    // Estilizar mejor los nodos de puerto
    enhanceHarborNodes();
    
    // Mejorar la animación de los dados
    enhanceDiceRoll();
    
    // Aplicar efectos de agua
    applyWaterEffects();
    
    // Inicializar efectos de cursor - desactivado por preferencia del usuario
    // initCursorEffects();
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
