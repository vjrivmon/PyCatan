let game_obj = {};
let round_obj = {};
let turn_obj = {};
let phase_obj = {};

let game_direction = 'forward'; // or "backward"
let autoPlayInterval = null;
let isPlaying = false;
let originalNodePositions = {}; // Nueva variable global para almacenar posiciones

// Coordenadas predefinidas para los nodos (internas y externas para puertos)
// NOTA: Estas coordenadas necesitarán un ajuste fino.
// Las 'internal' se basan en el HTML original.
// Las 'external' son una aproximación y deben ser verificadas/ajustadas.
const nodeCoordinates = [
    { internal: { top: '97px', left: '184px' }, external: { top: '87px', left: '174px'} }, // 0 - Puerto potencial
    { internal: { top: '75px', left: '232px' }, external: { top: '65px', left: '232px'} }, // 1 - Puerto potencial
    { internal: { top: '97px', left: '282px' }, external: { top: '87px', left: '292px'} }, // 2 - Puerto potencial
    { internal: { top: '75px', left: '330px' }, external: { top: '65px', left: '330px'} }, // 3 - Puerto potencial
    { internal: { top: '97px', left: '379px' }, external: { top: '87px', left: '389px'} }, // 4 - Puerto potencial
    { internal: { top: '75px', left: '428px' }, external: { top: '65px', left: '428px'} }, // 5 - Puerto potencial
    { internal: { top: '97px', left: '477px' }, external: { top: '87px', left: '487px'} }, // 6 - Puerto potencial
    { internal: { top: '184px', left: '138px' }, external: { top: '184px', left: '128px'} }, // 7 - Puerto potencial
    { internal: { top: '157px', left: '184px' }, external: null }, // 8
    { internal: { top: '184px', left: '234px' }, external: null }, // 9
    { internal: { top: '157px', left: '282px' }, external: null }, // 10
    { internal: { top: '184px', left: '334px' }, external: null }, // 11 (ejemplo interno)
    { internal: { top: '157px', left: '379px' }, external: null }, // 12
    { internal: { top: '184px', left: '432px' }, external: null }, // 13
    { internal: { top: '157px', left: '477px' }, external: null }, // 14
    { internal: { top: '184px', left: '530px' }, external: { top: '184px', left: '540px'} }, // 15 - Puerto potencial
    { internal: { top: '270px', left: '86px' }, external: { top: '270px', left: '76px'} },   // 16 - Puerto potencial
    { internal: { top: '247px', left: '138px' }, external: null }, // 17
    { internal: { top: '270px', left: '184px' }, external: null }, // 18
    { internal: { top: '247px', left: '232px' }, external: null }, // 19
    { internal: { top: '270px', left: '282px' }, external: { top: '280px', left: '282px' } }, // 20 (ejemplo externo tuyo, ajustado top levemente)
    { internal: { top: '247px', left: '330px' }, external: null }, // 21
    { internal: { top: '270px', left: '379px' }, external: null }, // 22
    { internal: { top: '247px', left: '428px' }, external: null }, // 23
    { internal: { top: '270px', left: '477px' }, external: null }, // 24
    { internal: { top: '247px', left: '530px' }, external: null }, // 25
    { internal: { top: '270px', left: '578px' }, external: { top: '270px', left: '588px'} }, // 26 - Puerto potencial
    { internal: { top: '330px', left: '86px' }, external: { top: '330px', left: '76px'} },   // 27 - Puerto potencial
    { internal: { top: '355px', left: '138px' }, external: null }, // 28
    { internal: { top: '330px', left: '184px' }, external: null }, // 29
    { internal: { top: '355px', left: '234px' }, external: null }, // 30
    { internal: { top: '330px', left: '282px' }, external: null }, // 31
    { internal: { top: '355px', left: '334px' }, external: null }, // 32
    { internal: { top: '330px', left: '379px' }, external: null }, // 33
    { internal: { top: '355px', left: '432px' }, external: null }, // 34
    { internal: { top: '330px', left: '477px' }, external: null }, // 35
    { internal: { top: '355px', left: '530px' }, external: null }, // 36
    { internal: { top: '330px', left: '578px' }, external: { top: '330px', left: '588px'} }, // 37 - Puerto potencial
    { internal: { top: '419px', left: '138px' }, external: { top: '419px', left: '128px'} }, // 38 - Puerto potencial
    { internal: { top: '442px', left: '184px' }, external: null }, // 39
    { internal: { top: '419px', left: '232px' }, external: null }, // 40
    { internal: { top: '442px', left: '282px' }, external: null }, // 41
    { internal: { top: '419px', left: '330px' }, external: null }, // 42
    { internal: { top: '442px', left: '379px' }, external: null }, // 43
    { internal: { top: '419px', left: '428px' }, external: null }, // 44
    { internal: { top: '442px', left: '477px' }, external: null }, // 45
    { internal: { top: '419px', left: '530px' }, external: { top: '419px', left: '540px'} }, // 46 - Puerto potencial
    { internal: { top: '502px', left: '184px' }, external: { top: '512px', left: '174px'} }, // 47 - Puerto potencial
    { internal: { top: '529px', left: '234px' }, external: { top: '539px', left: '234px'} }, // 48 - Puerto potencial
    { internal: { top: '502px', left: '282px' }, external: { top: '512px', left: '292px'} }, // 49 - Puerto potencial
    { internal: { top: '529px', left: '334px' }, external: { top: '539px', left: '334px'} }, // 50 - Puerto potencial
    { internal: { top: '502px', left: '379px' }, external: { top: '512px', left: '389px'} }, // 51 - Puerto potencial
    { internal: { top: '529px', left: '432px' }, external: { top: '539px', left: '432px'} }, // 52 - Puerto potencial
    { internal: { top: '502px', left: '477px' }, external: { top: '512px', left: '487px'} }  // 53 - Puerto potencial
];

// Identificadores de nodos que son elegibles para mostrarse como puertos exteriores.
// Esto es una suposición basada en un tablero estándar de Catan. Ajustar según sea necesario.
const harborEligibleNodeIds = [0, 1, 2, 3, 4, 5, 6, 7, 15, 16, 26, 27, 37, 38, 46, 47, 48, 49, 50, 51, 52, 53];

// Variable para almacenar las posiciones originales de los nodos (si se cargan del HTML al inicio)
// ESTA ES LA DECLARACIÓN GLOBAL EN LÍNEA 8, SE MANTIENE INTACTA.
// let originalNodePositions = {}; 

// Almacenar posiciones originales al cargar el DOM (si aún hay nodos en el HTML al inicio)
jQuery(document).ready(function() {
    // La línea que el error marcaba como 77:
    // DEBE SER UNA ASIGNACIÓN O ELIMINARSE SI NO ES NECESARIA AQUÍ.
    // Si antes era 'let originalNodePositions = {}' o 'var ...', ahora es solo asignación:
    originalNodePositions = {}; // Asegura que se inicializa/vacía el objeto global.
    
    // jQuery('.node').each(function() {
    //     const nodeId = this.id;
    //     if (nodeId) { // Asegurarse de que el nodo tenga un ID
    //         const position = jQuery(this).position(); // Usar .position() para coordenadas relativas al offset parent
    //         if (position) {
    //             originalNodePositions[nodeId] = {
    //                 top: jQuery(this).css('top'), // Mantener como string 'px'
    //                 left: jQuery(this).css('left') // Mantener como string 'px'
    //             };
    //         }
    //     }
    // });
    // console.log("[DEBUG] Posiciones originales de nodos capturadas:", originalNodePositions);
});


function renderBoardNodes(boardNodesData) {
    const nodesContainer = jQuery('.nodes');
    nodesContainer.empty(); // Limpiar nodos existentes

    if (!boardNodesData) {
        console.error("[DEBUG] renderBoardNodes: No se proporcionaron datos de nodos.");
        return;
    }

    boardNodesData.forEach(nodeData => {
        if (typeof nodeData.id === 'undefined') {
            console.warn("[DEBUG] renderBoardNodes: Nodo sin ID encontrado.", nodeData);
            return; // Saltar este nodo
        }

        const nodeId = nodeData.id;
        const coordsDefinition = nodeCoordinates[nodeId];

        if (!coordsDefinition) {
            console.warn('[DEBUG] renderBoardNodes: No hay coordenadas definidas para el nodo ' + nodeId + '.');
            return; // Saltar este nodo si no hay coordenadas
        }

        let chosenCoords;
        let isHarborVisual = false;

        // Determinar si el nodo debe visualizarse como un puerto exterior
        // HarborConstants.NONE es -1 en el backend
        if (nodeData.harbor !== -1 && harborEligibleNodeIds.includes(nodeId) && coordsDefinition.external) {
            chosenCoords = coordsDefinition.external;
            isHarborVisual = true;
        } else {
            chosenCoords = coordsDefinition.internal;
        }
        
        if (!chosenCoords || typeof chosenCoords.top === 'undefined' || typeof chosenCoords.left === 'undefined') {
            console.warn('[DEBUG] renderBoardNodes: Coordenadas incompletas o no válidas para el nodo ' + nodeId + '. Se usarán las internas por defecto o (0,0).');
            chosenCoords = coordsDefinition.internal || { top: '0px', left: '0px' }; // Fallback
        }

        const nodeDiv = jQuery('<div>')
            .addClass('node')
            .attr('id', 'node_' + nodeId)
            .css({
                top: chosenCoords.top,
                left: chosenCoords.left,
                position: 'absolute',
                'z-index': 10 // z-index base para nodos
            });

        if (isHarborVisual) {
            nodeDiv.addClass('is-harbor-active'); // Clase para estilizar puertos activos si es necesario
            // Aquí se podría añadir el ícono del puerto específico.
            // Por ejemplo, basándose en nodeData.harbor y constantes de tipo de puerto.
            // enhanceHarborNodes() podría ser adaptada para esto o llamada después.
            const harborType = getHarborTypeConstant(nodeData.harbor); // Necesitarás mapear el int a un string
            const harborIcon = getHarborIcon(harborType); // Función para obtener el icono HTML
            nodeDiv.append('<div class="harbor-content-dynamic">' + harborIcon + '</div>');
        }
        
        // Si el nodo tiene un jugador (poblado/ciudad), añadir clase de jugador y emoji
        if (nodeData.player !== -1) {
            paint_it_player_color(nodeData.player, nodeDiv); // Aplica clase de color
            let buildingType = nodeData.has_city ? 'city' : 'settlement';
            let playerEmoji = getPlayerEmoji(nodeData.player);
            let buildingEmoji = getBuildingEmoji(buildingType); // Debería devolver 🏠 o 🏛️
            
            // Asegurar que el contenido del emoji tenga un z-index alto
            let emojiSpan = jQuery('<span>')
                .addClass('building-on-node') // Nueva clase para control de z-index específico
                .css({'z-index': 25 }) // z-index alto para edificios sobre nodos
                .html('<span class="player-emoji">' + playerEmoji + '</span><span class="building-emoji">' + buildingEmoji + '</span>');
            nodeDiv.append(emojiSpan);

        }


        nodesContainer.append(nodeDiv);
    });
    // console.log("[DEBUG] Nodos renderizados dinámicamente.");
}

// Función auxiliar para mapear el tipo de puerto numérico a un string (ejemplo)
function getHarborTypeConstant(harborId) {
    // Estos valores deben coincidir con HarborConstants en Python
    const harborTypes = {
        0: 'HARBOR_CEREAL', 
        1: 'HARBOR_MINERAL',
        2: 'HARBOR_CLAY',
        3: 'HARBOR_WOOD',
        4: 'HARBOR_WOOL',
        5: 'HARBOR_ALL', // Puerto 3:1
        // -1 o cualquier otro valor sería HarborConstants.NONE
    };
    return harborTypes[harborId] || 'NONE';
}

// Función auxiliar para obtener el icono HTML del puerto (ejemplo)
function getHarborIcon(harborTypeString) {
    // Deberás tener iconos/clases CSS para cada tipo de puerto
    switch (harborTypeString) {
        case 'HARBOR_CEREAL': return '<i class="fas fa-wheat-awn"></i><span>2:1</span>';
        case 'HARBOR_MINERAL': return '<i class="fas fa-mountain"></i><span>2:1</span>';
        case 'HARBOR_CLAY': return '<i class="fas fa-dumpster-fire"></i><span>2:1</span>'; //  ej icono para arcilla
        case 'HARBOR_WOOD': return '<i class="fas fa-tree"></i><span>2:1</span>';
        case 'HARBOR_WOOL': return '<i class="fas fa-sheep"></i><span>2:1</span>';
        case 'HARBOR_ALL': return '<span>3:1</span>';
        default: return ''; // Sin icono si no es un puerto conocido
    }
}


function init_events() {
    let input = jQuery('#get_file');
    let load_game = jQuery('#load_game');
    
    // Inicializar controles de auto-play
    initAutoPlayControls();
    
    // Inicializar controles de zoom y pantalla completa
    initZoomControls();
    
    // Añadir evento para probar la animación de dados
    jQuery('#test_dice_btn').on('click', function() {
        testDiceAnimation();
    });
    
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
                console.log('[DEBUG] Contenido crudo del archivo:', evt.target.result.substring(0, 200) + "..."); // Loguear solo una parte
                try {
                    game_obj = JSON.parse(evt.target.result);
                    console.log('[DEBUG] JSON parseado correctamente. game_obj:', game_obj);
                } catch (e) {
                    console.error('[DEBUG] Error al parsear JSON:', e);
                    alert("Error al leer el archivo JSON. Asegúrate de que el formato es correcto.");
                    $('#uploadModal').modal('hide');
                    if (loadSelectedFileBtn) loadSelectedFileBtn.disabled = true; // Corregido
                    return;
                }

                debugGameStructure(game_obj); // Loguea la estructura del juego

                console.log('[DEBUG] Antes de stopAutoPlay().');
                stopAutoPlay(); // Detener cualquier autoplay previo
                console.log('[DEBUG] Después de stopAutoPlay().');

                console.log('[DEBUG] Antes de setup() (preparación inicial).');
                setup(); // Esto llama a terrainSetup, nodeSetup y addSetupBuildings. nodeSetup aquí configura clases y tooltips, pero su ajuste de posición será sobreescrito por reset_game.
                console.log('[DEBUG] Después de setup().');
                
                console.log('[DEBUG] Antes de init_events_with_game_obj().');
                init_events_with_game_obj(); // Inicializa eventos que dependen del game_obj (como los de autoplay)
                console.log('[DEBUG] Después de init_events_with_game_obj().');

                console.log('[DEBUG] Antes de addLogFromJSON().');
                addLogFromJSON(); // Carga el log del juego si existe en el JSON
                console.log('[DEBUG] Después de addLogFromJSON().');

                console.log('[DEBUG] Antes de reset_game().');
                reset_game(); // Esta función es CLAVE: limpia el tablero y RESTAURA las posiciones originales de los nodos desde 'originalNodePositions'.
                console.log('[DEBUG] Después de reset_game().');

                // CON LAS POSICIONES BASE YA ESTABLECIDAS POR reset_game(), PROCEDEMOS A AJUSTAR PUERTOS Y COLOCAR EDIFICIOS INICIALES.
                console.log('[DEBUG] Antes de la llamada DEFINITIVA a nodeSetup() para ajustar puertos.');
                nodeSetup(); // AHORA nodeSetup ajustará los puertos basándose en las posiciones restauradas por reset_game. Los console.log internos de nodeSetup nos dirán si el .css() funciona.
                console.log('[DEBUG] Después de la llamada DEFINITIVA a nodeSetup().');

                console.log('[DEBUG] Antes de la llamada DEFINITIVA a addSetupBuildings().');
                addSetupBuildings(); // Coloca los edificios iniciales (pueblos, carreteras) según el game_obj.setup.
                console.log('[DEBUG] Después de la llamada DEFINITIVA a addSetupBuildings().');

                console.log('[DEBUG] Antes de updateUIDataFromGameObj().');
                updateUIDataFromGameObj(game_obj); // Actualiza la UI (puntos, cartas, etc.) con el estado del juego.
                console.log('[DEBUG] Después de updateUIDataFromGameObj().');
                
                // Mejoras visuales y controles post-carga
                enhanceHarborNodes(); 
                enhanceDiceRoll();  
                applyWaterEffects(); 
                initZoomControls(); 

                $('#uploadModal').modal('hide');
                if (loadSelectedFileBtn) loadSelectedFileBtn.disabled = false; // Corregido (asumimos que queremos habilitarlo tras éxito)
                
                checkVictory(); // Comprobar si hay victoria al cargar el juego

                console.log('[DEBUG] Modal cerrado. Carga de partida completada.');
                $(document).trigger('gameLoaded'); // Evento para otros scripts, si es necesario.
            };
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
                setup(); // This will call nodeSetup() and addSetupBuildings() for the initial state
                reset_game(); // This resets the board, restoring original positions
                // updateUIDataFromGameObj(game_obj); // Moved later
                // ¡VUELVO A DIBUJAR LOS PUERTOS! (también en el flujo del input clásico)
                nodeSetup(); // This call is crucial to re-apply harbor logic AND compensation
                addSetupBuildings(); // Ensure setup buildings are placed correctly after node adjustments
                updateUIDataFromGameObj(game_obj); // Finally, update all UI data
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

    // Asegurar que todos los nodos sean absolutamente posicionados ANTES de capturar sus estilos.
    // Esto es crucial para que top/left se interpreten correctamente desde el HTML.
    jQuery('.node').css('position', 'absolute');

    // Almacenar posiciones originales de los nodos del HTML al inicio
    // Esto debe hacerse antes de cualquier operación que pueda modificar los estilos inline
    // jQuery('.node').each(function() {
    //     if (this.id) {
    //         const topPos = jQuery(this).css('top');
    //         const leftPos = jQuery(this).css('left');
            
    //         originalNodePositions[this.id] = { 
    //             top: topPos, 
    //             left: leftPos 
    //         };
    //         console.log(`[DEBUG init_events] Nodo ${this.id}: Almacenando posición original leída como top=${topPos}, left=${leftPos}`);
    //     } else {
    //         console.warn('[DEBUG init_events] Se encontró un nodo sin ID, no se almacenará su posición.');
    //     }
    // });
}

function reset_game() {
    // Limpiar contenido y clases de jugador del tablero.
    jQuery('.node').empty().removeClass('player-red player-blue player-green player-yellow');
    jQuery('.road').empty().removeAttr('style').removeClass('player-red player-blue player-green player-yellow');
    jQuery('.vertical_road').empty().removeAttr('style').removeClass('player-red player-blue player-green player-yellow');

    // Remover 'style' de los nodos para una limpieza completa antes de restaurar posiciones.
    jQuery('.node').removeAttr('style');

    // Restaurar posiciones base de los nodos y asegurar position: absolute usando nodeCoordinates
    jQuery('.node').each(function() {
        const nodeIdNumeric = parseInt(this.id.replace('node_', '')); // Obtener el índice numérico del nodo
        if (!isNaN(nodeIdNumeric) && nodeCoordinates[nodeIdNumeric] && nodeCoordinates[nodeIdNumeric].internal) {
            // Determinar si usar coordenadas externas o internas para puertos (lógica similar a renderBoardNodes)
            // Esto es importante para que nodeSetup parta de la misma base visual que renderBoardNodes.
            let coordsToUse;
            const gameNodeData = (game_obj && game_obj.setup && game_obj.setup.board && game_obj.setup.board.board_nodes) 
                               ? game_obj.setup.board.board_nodes[nodeIdNumeric] : null;

            if (gameNodeData && gameNodeData.harbor !== -1 && harborEligibleNodeIds.includes(nodeIdNumeric) && nodeCoordinates[nodeIdNumeric].external) {
                coordsToUse = nodeCoordinates[nodeIdNumeric].external;
                 console.log(`[DEBUG reset_game] Nodo ${this.id}: Usando coordenadas EXTERNAS de nodeCoordinates para reset: top=${coordsToUse.top}, left=${coordsToUse.left}`);
            } else {
                coordsToUse = nodeCoordinates[nodeIdNumeric].internal;
                 console.log(`[DEBUG reset_game] Nodo ${this.id}: Usando coordenadas INTERNAS de nodeCoordinates para reset: top=${coordsToUse.top}, left=${coordsToUse.left}`);
            }
            
            if (!coordsToUse || typeof coordsToUse.top === 'undefined' || typeof coordsToUse.left === 'undefined') {
                console.warn(`[DEBUG reset_game] Coordenadas (internal/external) incompletas o no válidas en nodeCoordinates para ${this.id}. Usando (0,0).`);
                coordsToUse = { top: '0px', left: '0px' }; 
            }

            jQuery(this).css({
                top: coordsToUse.top,
                left: coordsToUse.left,
                position: 'absolute' // Crucial para que top/left tengan efecto
            });
        } else if (this.id) {
            console.warn(`[DEBUG reset_game] No hay coordenadas en nodeCoordinates para ${this.id} o falta .internal/.external. Usando (0,0).`);
            jQuery(this).css({
                 position: 'absolute',
                 top: '0px', 
                 left: '0px' 
             });
        }
    });
    
    // Resetear estilos visuales de los nodos (esto NO debe sobreescribir top, left, position)
    jQuery('.node').css({
        'background-color': '',
        'border': '',
        'border-radius': '', // O un valor por defecto si los nodos siempre son redondos
        'transform': '',
        'box-shadow': '', // Limpiar sombra de puertos
        'z-index': ''    // Resetear z-index
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
            
            // Aplicar z-index alto a las carreteras de configuración inicial
            road.css('z-index', '35');

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

// Función mejorada para configurar los nodos y sus puertos
function nodeSetup() {
    if (!game_obj || !game_obj.setup || !game_obj.setup.board || !game_obj.setup.board.board_nodes) {
        console.warn("[DEBUG] nodeSetup: game_obj.setup.board.board_nodes no está disponible. No se pueden configurar los nodos.");
        return;
    }
    const nodes = game_obj.setup.board.board_nodes;
    const compensationShift = 5; // AJUSTADO A 5px

    // Loguear box-sizing una vez para el primer nodo que se procese
    let boxSizingLogged = false;

    for (let i = 0; i < nodes.length; i++) {
        let nodeDiv = jQuery('#node_' + i);
        const nodeId = nodeDiv.attr('id'); // es 'node_X'

        if (nodeDiv && typeof nodeDiv.length !== 'undefined' && nodeDiv.length > 0) {
            if (!boxSizingLogged) {
                const firstNodeElement = nodeDiv[0];
                if (firstNodeElement) {
                    const computedStyle = window.getComputedStyle(firstNodeElement);
                    console.log(`[nodeSetup INIT] Box-sizing del primer nodo (${nodeId}): ${computedStyle.boxSizing}`);
                    boxSizingLogged = true;
                }
            }
        } else {
            console.error(`[nodeSetup INIT] nodeDiv para ${nodeId} no es un objeto jQuery válido o está vacío. Saltando este nodo.`);
            continue;
        }

        nodeDiv.empty()
               .removeClass('is-harbor')
               .removeAttr('data-bs-toggle')
               .removeAttr('data-bs-original-title')
               .removeAttr('title');

        // La restauración de estilos base (top, left, position) ahora la hace reset_game() de forma más robusta.
        // nodeDiv[0].style.cssText = ''; // No es necesario si reset_game limpia bien.
        
        const nodeIdNumeric = i; // i es el índice numérico del nodo
        let baseCoords;

        if (nodeCoordinates[nodeIdNumeric]) {
            const nodeDataFromBoard = nodes[i]; // Es game_obj.setup.board.board_nodes[i]
            
            // Determinar si usar coordenadas externas o internas como base para el cálculo de 'compensationShift'
            // Esta lógica debe ser consistente con la usada en renderBoardNodes y reset_game para 'chosenCoords' o 'coordsToUse'.
            if (nodeDataFromBoard.harbor !== -1 && harborEligibleNodeIds.includes(nodeIdNumeric) && nodeCoordinates[nodeIdNumeric].external) {
                baseCoords = nodeCoordinates[nodeIdNumeric].external;
                 console.log(`[DEBUG nodeSetup] Nodo ${nodeId}: Usando base EXTERNA de nodeCoordinates: top=${baseCoords.top}, left=${baseCoords.left}`);
            } else {
                baseCoords = nodeCoordinates[nodeIdNumeric].internal;
                 console.log(`[DEBUG nodeSetup] Nodo ${nodeId}: Usando base INTERNA de nodeCoordinates: top=${baseCoords.top}, left=${baseCoords.left}`);
            }

            if (!baseCoords || typeof baseCoords.top === 'undefined' || typeof baseCoords.left === 'undefined') {
                 console.warn(`[nodeSetup] Coordenadas base (internal/external) incompletas en nodeCoordinates para ${nodeId}. Usando 0,0.`);
                 baseCoords = { top: '0px', left: '0px' };
            }
        } else {
            console.warn(`[nodeSetup] No se encontraron nodeCoordinates para ${nodeId} (índice ${nodeIdNumeric}). El nodo podría no posicionarse correctamente. Usando 0,0.`);
            baseCoords = { top: '0px', left: '0px' };
        }
        
        // Asegurar que la posición base esté aplicada antes de cualquier modificación para puertos
        // Esto ya debería estar correcto por reset_game, pero una reafirmación no daña.
        nodeDiv.css({
            top: baseCoords.top,
            left: baseCoords.left,
            position: 'absolute'
        });

        if (nodes[i]['harbor'] !== -1) {
            nodeDiv.addClass('is-harbor');
            nodeDiv.attr('data-bs-toggle', 'tooltip');

            let tooltipTitle = '';
            let harborContent = ''; 
            const spanStyle = 'font-size: 10px; font-weight: bold;';

            // Mapeo corregido y detallado para harborContent
            switch (nodes[i]['harbor']) {
                case 0: // Cereal (Trigo)
                    tooltipTitle = 'Puerto de Cereal 2:1';
                    harborContent = `<div class="harbor-content harbor-cereal"><i class="fas fa-wheat-awn" style="color: #fbbc05;"></i><span style="${spanStyle}">2:1</span></div>`;
                    break;
                case 1: // Mineral
                    tooltipTitle = 'Puerto de Mineral 2:1';
                    harborContent = `<div class="harbor-content harbor-mineral"><i class="fas fa-mountain" style="color: #9aa0a6;"></i><span style="${spanStyle}">2:1</span></div>`;
                    break;
                case 2: // Arcilla (Ladrillo)
                    tooltipTitle = 'Puerto de Arcilla 2:1';
                    harborContent = `<div class="harbor-content harbor-clay"><i class="fas fa-cube" style="color: #ff8a65;"></i><span style="${spanStyle}">2:1</span></div>`;
                    break;
                case 3: // Madera
                    tooltipTitle = 'Puerto de Madera 2:1';
                    harborContent = `<div class="harbor-content harbor-wood"><i class="fas fa-tree" style="color: #34a853;"></i><span style="${spanStyle}">2:1</span></div>`;
                    break;
                case 4: // Lana
                    tooltipTitle = 'Puerto de Lana 2:1';
                    harborContent = `<div class="harbor-content harbor-wool"><i class="fas fa-scroll" style="color: #a5d6a7;"></i><span style="${spanStyle}">2:1</span></div>`; // fas fa-scroll o fas fa-sheep
                    break;
                case 5: // General
                    tooltipTitle = 'Puerto General 3:1';
                    harborContent = `<div class="harbor-content harbor-general"><i class="fas fa-anchor" style="color: #1a73e8;"></i><span style="${spanStyle}">3:1</span></div>`;
                    break;
                default:
                    tooltipTitle = 'Puerto Desconocido';
                    harborContent = '<i class="fas fa-question-circle"></i> ?'; // Icono genérico para desconocido
            }

            nodeDiv.html(harborContent);
            nodeDiv.attr('title', tooltipTitle);
            nodeDiv.attr('data-bs-original-title', tooltipTitle);

            nodeDiv.css({
                'background-color': 'rgba(26, 115, 232, 0.2)',
                'border': '2px solid #1a73e8',
                'border-radius': '50%',
                'box-shadow': '0 0 10px rgba(26, 115, 232, 0.3)',
                'z-index': '5' 
            });

            // Usar baseCoords (obtenidas de nodeCoordinates) para el cálculo del shift
            let originalTopStr = baseCoords.top;
            let originalLeftStr = baseCoords.left;

            let currentTopPx = parseInt(originalTopStr, 10);
            let currentLeftPx = parseInt(originalLeftStr, 10);

            if (isNaN(currentTopPx) || isNaN(currentLeftPx)) {
                console.warn(`[DEBUG nodeSetup] Coordenadas base parseadas inválidas para ${nodeId}: top='${originalTopStr}', left='${originalLeftStr}'. Usando 0,0 como fallback para el shift.`);
                currentTopPx = 0;
                currentLeftPx = 0;
            }

            const newTop = (currentTopPx - compensationShift) + 'px';
            const newLeft = (currentLeftPx - compensationShift) + 'px';

            const domElement = nodeDiv[0];
            if (domElement && domElement.style) {
                domElement.style.setProperty('top', newTop, 'important');
                domElement.style.setProperty('left', newLeft, 'important');
                 console.log(`[DEBUG nodeSetup] Puerto ${nodeId}: Aplicando SHIFT. Base: (${originalTopStr}, ${originalLeftStr}), Shifted: (${newTop}, ${newLeft})`);
            } else {
                console.error(`[DEBUG nodeSetup] No se pudo acceder a .style para ${nodeId} al aplicar shift de puerto.`);
            }

            // --- INICIO SUPER DEBUG (SOLO PARA PUERTOS) ---
            if (domElement) { 
                const computed = window.getComputedStyle(domElement);
                console.groupCollapsed(`[SUPER DEBUG ${nodeId}] Estado final del puerto`);
                console.log(`Originales leídos para cálculo: top=${originalTopStr}, left=${originalLeftStr}. Shift: ${compensationShift}`);
                console.log(`Valores compensados esperados: top=${newTop}, left=${newLeft}`);
                console.log("--- Valores DIRECTOS de node.style ---");
                console.log(`  node.style.top: '${domElement.style.top}'`);
                console.log(`  node.style.left: '${domElement.style.left}'`);
                console.log(`  node.style.position: '${domElement.style.position}'`);
                console.log(`  node.style.backgroundColor: '${domElement.style.backgroundColor}'`);
                console.log(`  node.style.borderColor: '${domElement.style.borderColor}'`);
                console.log(`  node.style.borderWidth: '${domElement.style.borderWidth}'`);
                console.log(`  node.style.width (inline): '${domElement.style.width}'`); 
                console.log(`  node.style.height (inline): '${domElement.style.height}'`); 
                console.log("--- Valores COMPUTADOS (getComputedStyle) ---");
                console.log(`  Computed top: ${computed.top}`);
                console.log(`  Computed left: ${computed.left}`);
                console.log(`  Computed position: ${computed.position}`);
                console.log(`  Computed backgroundColor: ${computed.backgroundColor}`);
                console.log(`  Computed borderColor: ${computed.borderColor}`);
                console.log(`  Computed borderWidth: ${computed.borderTopWidth} (top)`); 
                console.log(`  Computed width (total): ${computed.width}`);
                console.log(`  Computed height (total): ${computed.height}`);
                console.log(`  Computed box-sizing: ${computed.boxSizing}`);
                console.log("--- Dimensiones Offset ---");
                console.log(`  offsetWidth: ${domElement.offsetWidth}px`);
                console.log(`  offsetHeight: ${domElement.offsetHeight}px`);
                console.groupEnd();
            }
            // --- FIN SUPER DEBUG ---
        } 
    } 

    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        })
    } else {
        if (jQuery.ui) {
            $(document).tooltip(); 
        }
    }
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
        renderBoardNodes(game_obj.setup.board.board_nodes); // NUEVA LLAMADA
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
    
    // Verificar si ya existen los controles de zoom
    if (!document.querySelector('.map-controls button')) {
        console.log('[DEBUG] Inicializando controles de zoom.');
        initZoomControls();
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
        
        // DEBUG: Verificar que los elementos de log existen
        console.log('[DEBUG] Elementos de log encontrados:', {
            commerce_log_text: jQuery('#commerce_log_text').length,
            other_useful_info_text: jQuery('#other_useful_info_text').length
        });
        
        // NO limpiar logs automáticamente - solo al cambiar de fase explícitamente
        // jQuery('#commerce_log_text').html('');
        // jQuery('#other_useful_info_text').html('');
        deleteCaretStyling();

        let _this = $(this);
        turn_obj = round_obj[contador_turnos.val()];
        
        // Obtener la clave de la fase actual
        let currentPhaseKey = contador_fases.val();
        phase_obj = turn_obj[currentPhaseKey];
        
        console.log('[DEBUG] Procesando fase:', currentPhaseKey, 'con datos:', phase_obj);

        // Lógica para procesar cada fase basándose en la clave de la fase
        if (currentPhaseKey == "start_turn") {
            // Procesar inicio de turno
            handleStartTurn(phase_obj, currentPhaseKey);
        } else if (currentPhaseKey == "commerce_phase") {
            // Procesar fase de comercio
            handleCommercePhase(phase_obj, currentPhaseKey);
        } else if (currentPhaseKey == "build_phase") {
            // Procesar fase de construcción
            handleBuildPhase(phase_obj, currentPhaseKey);
        } else if (currentPhaseKey == "end_turn") {
            // Procesar fin de turno
            handleEndTurn(phase_obj, currentPhaseKey);
        } else {
            // Procesar otras fases basándose en la estructura original
            handleGenericPhase(phase_obj, currentPhaseKey);
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
    
    // Obtener emojis de recursos para elementos flotantes
    const catanEmojis = [
        '🏠', '🏛️', '🛣️', '🌾', '🧱', '🪵', '⛰️', '🐑', 
        '🎲', '📊', '📈', '🎯', '🏆', '👑', '💎', '🔄'
    ];
    
    // Modificar el nombre del ganador con estilo y animación
    const playerNames = ['Rojo', 'Azul', 'Verde', 'Amarillo'];
    const playerName = playerNames[playerIndex] || `Jugador ${playerIndex + 1}`;
    
    // Añadir emoji según el color del jugador
    const playerEmoji = getPlayerEmoji(playerIndex);
    
    $('#winner-name').html(`
        <span style="color:${colors[0]};">
            ${playerEmoji} ¡Jugador ${playerName} ha ganado! ${playerEmoji}
        </span>
    `);
    
    // Mostrar el modal de victoria
    $('#victory-modal').modal('show');
    
    // Limpiar elementos anteriores
    $('.catan-elements-container').empty();
    $('.floating-particle').remove();
    
    // Añadir elementos flotantes relacionados con Catán
    for (let i = 0; i < 20; i++) {
        const randomEmoji = catanEmojis[Math.floor(Math.random() * catanEmojis.length)];
        const delay = Math.random() * 5;
        const size = 20 + Math.random() * 40;
        const left = Math.random() * 100;
        
        const element = $(`<div class="catan-element" style="
            left: ${left}%;
            font-size: ${size}px;
            animation-delay: ${delay}s;
        ">${randomEmoji}</div>`);
        
        $('.catan-elements-container').append(element);
    }
    
    // Crear partículas flotantes con los colores del jugador
    for (let i = 0; i < 30; i++) {
        createFloatingParticle(colors);
    }
    
    // Configuración del confeti usando canvas-confetti
    const duration = 8 * 1000; // 8 segundos de duración
    const animationEnd = Date.now() + duration;
    const defaults = { 
        startVelocity: 30, 
        spread: 360, 
        ticks: 60, 
        zIndex: 9999,
        colors: colors,
        shapes: ['circle', 'square'],
        scalar: 1.2
    };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    // Disparar confeti inicial grande
    confetti({
        ...defaults,
        particleCount: 150,
        origin: { x: 0.5, y: 0.5 }
    });

    // Continuar disparando confeti durante la duración especificada
    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);
        
        // Disparar confeti desde múltiples posiciones
        confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
        });
        confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
        });
    }, 250);
    
    // Confeti adicional en forma de cascada
    setTimeout(() => {
        confetti({
            particleCount: 200,
            angle: 60,
            spread: 55,
            origin: { x: 0, y: 0.6 },
            colors: colors,
            zIndex: 9999
        });
        confetti({
            particleCount: 200,
            angle: 120,
            spread: 55,
            origin: { x: 1, y: 0.6 },
            colors: colors,
            zIndex: 9999
        });
    }, 1000);
    
    // Efecto de explosión final después de unos segundos
    setTimeout(() => {
        confetti({
            particleCount: 150,
            spread: 180,
            origin: { x: 0.5, y: 0.5 },
            colors: colors,
            scalar: 2,
            shapes: ['star', 'circle'],
            zIndex: 9999
        });
    }, 3500);
    
    // Manejar el botón de compartir victoria
    $('.share-victory-btn').off('click').on('click', function() {
        // Mostrar un mensaje informativo
        alert(`¡Comparte tu victoria del Jugador ${playerName} con tus amigos!`);
    });
    
    console.log(`[DEBUG] Confeti de victoria mostrado para Jugador ${playerIndex + 1}`);
}

// Función para crear partículas flotantes decorativas
function createFloatingParticle(colors) {
    const particle = document.createElement('div');
    particle.className = 'floating-particle';
    
    // Tamaño aleatorio
    const size = 5 + Math.random() * 15;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    
    // Color aleatorio del array de colores
    const color = colors[Math.floor(Math.random() * colors.length)];
    particle.style.backgroundColor = color;
    
    // Posición inicial aleatoria
    const startX = Math.random() * 100;
    const startY = Math.random() * 100;
    particle.style.left = `${startX}%`;
    particle.style.top = `${startY}%`;
    
    // Forma aleatoria (círculo o cuadrado)
    particle.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
    
    // Movimiento aleatorio
    const endX = (Math.random() - 0.5) * 80;
    const endY = (Math.random() - 0.5) * 80;
    const rotation = Math.random() * 360;
    
    particle.style.setProperty('--end-x', `${endX}px`);
    particle.style.setProperty('--end-y', `${endY}px`);
    particle.style.setProperty('--rotation', `${rotation}deg`);
    
    // Duración aleatoria
    const duration = 3 + Math.random() * 7;
    particle.style.animationDuration = `${duration}s`;
    
    // Retraso aleatorio
    const delay = Math.random() * 5;
    particle.style.animationDelay = `${delay}s`;
    
    // Añadir al modal
    document.querySelector('.victory-animation-container').appendChild(particle);
    
    // Eliminar después de la animación
    setTimeout(() => {
        if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
        }
    }, (duration + delay) * 1000);
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
            // 'transform': 'scale(1)', // GSAP se encargará de la escala
            'z-index': '10',
            'opacity': 1 // Asegurar que sea visible desde el principio
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
        
        // Animación de aparición con GSAP (sin ocultar)
        if (typeof gsap !== 'undefined') {
            gsap.fromTo(nodeElement, 
                { scale: 0.8, opacity: 1 }, // Comienza visible y un poco más pequeño
                {
                    duration: 0.5,
                    scale: 1, // Anima a tamaño completo
                    opacity: 1,
                    ease: "power1.out"
                }
            );
        }
        
        // Efecto de construcción (si aún se desea, puede mantenerse)
        createConstructionEffect(nodeElement.offset().left, nodeElement.offset().top);
        
        // Se elimina la clase animate__bounceIn y el setTimeout correspondiente
        // nodeElement.addClass('animate__animated animate__bounceIn');
        // setTimeout(() => {
        //     nodeElement.removeClass('animate__animated animate__bounceIn');
        // }, 1000);
        
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
            'z-index': '35' // Ajustado para estar sobre terrenos y nodos base
        });
        
        // Añadir emoji de carretera
        roadElement.html(`<span style="font-size: 12px; color: white;">🛤️</span>`);
        
        // Animación de construcción eliminada para que nunca se escondan
        // roadElement.addClass('animate__animated animate__fadeIn');
        // setTimeout(() => {
        //     roadElement.removeClass('animate__animated animate__fadeIn');
        // }, 1000);
        
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
    
    // Animar la aparición sin ocultar el objeto
    if (typeof gsap !== 'undefined') {
        gsap.fromTo(object_to_paint, 
            { scale: 0.8, opacity: 1 }, // Comienza ligeramente más pequeño pero totalmente opaco
            {
                duration: 0.5,
                scale: 1, // Anima al tamaño completo
                opacity: 1, // Asegura que la opacidad se mantenga en 1
                ease: "power1.out"
            }
        );
    }
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
                // Mostrar la animación de confeti para el jugador ganador
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
                
                console.log(`[INFO] Partida finalizada: Jugador ${i} ha ganado con ${victoryPoints} puntos de victoria.`);
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
                //y: -50,
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
            
            // --- SECCIÓN ELIMINADA PARA QUITAR EFECTO DE LATIDO ---
            // Ya no aplicamos la animación de pulsación con GSAP
            /*
            gsap.to(this, {
                duration: 2,
                repeat: -1,
                yoyo: true,
                scale: 1.1,
                ease: "sine.inOut"
            });
            */
            // --- FIN DE SECCIÓN ELIMINADA ---
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
    // Obtener un número aleatorio entre 2 y 12 (suma de dos dados)
    const randomValue = Math.floor(Math.random() * 11) + 2;
    console.log("Probando animación de dados con valor total: " + randomValue);
    
    // Agregar mensaje en el log del juego
    const diceEmoji = getDiceEmoji(randomValue);
    const logHtml = `<div class="log-entry dice-roll mb-2" style="border-left-color: #9b59b6; background-color: rgba(155, 89, 182, 0.1);">
        <i class="fas fa-dice text-purple me-2"></i>
        <strong>🎲 Prueba de dados: ${diceEmoji} ${randomValue}</strong>
    </div>`;
    jQuery('#other_useful_info_text').append(logHtml);
    autoScrollLog('other_useful_info_text');
    
    // Ejecutar la animación
    animateDiceRoll(randomValue);
}

// Añadir evento para probar la animación al cargar la página
jQuery(document).ready(function($) {
    console.log("Documento listo para animación de dados");
    
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
                    
                    // Verificar si algún jugador ha ganado (10 puntos de victoria)
                    let hasWinner = false;
                    let winnerIndex = -1;
                    let maxPoints = 0;
                    
                    for (let i = 1; i <= 4; i++) {
                        const victoryPoints = parseInt($('#puntos_victoria_J' + i).text()) || 0;
                        if (victoryPoints >= 10) {
                            hasWinner = true;
                            winnerIndex = i - 1;
                            maxPoints = victoryPoints;
                            break;
                        } else if (victoryPoints > maxPoints) {
                            maxPoints = victoryPoints;
                            winnerIndex = i - 1;
                        }
                    }
                    
                    // Mostrar animación de victoria
                    setTimeout(() => {
                        if (hasWinner) {
                            // Mostrar la animación de confeti para el jugador ganador
                            showVictoryConfetti(winnerIndex);
                            
                            // Log de victoria
                            let html = `<div class="log-entry victory mb-2">
                                <i class="fas fa-crown text-warning me-2"></i>
                                <strong class="text-warning">🎉 ¡JUGADOR ${winnerIndex + 1} HA GANADO! 🎉</strong>
                                <br><small class="ms-4">Victoria con ${maxPoints} puntos</small>
                            </div>`;
                            jQuery('#other_useful_info_text').append(html);
                            autoScrollLog('other_useful_info_text');
                            
                            // Resaltar el jugador ganador
                            $(`#player-card-${winnerIndex}`).addClass('winner-glow');
                        } else if (winnerIndex >= 0) {
                            // Si no hay un ganador con 10 puntos, mostrar al jugador con más puntos
                            // Añadir un mensaje al log indicando el fin de la partida
                            let finPartidaHtml = `<div class="log-entry end-game mb-2" style="border-left-color: #6c757d; background-color: rgba(108, 117, 125, 0.1);">
                                <i class="fas fa-flag-checkered text-secondary me-2"></i>
                                <strong>🏁 ¡La partida ha terminado!</strong>
                                <br><small class="ms-4">Jugador ${winnerIndex + 1} lidera con ${maxPoints} puntos</small>
                            </div>`;
                            jQuery('#other_useful_info_text').append(finPartidaHtml);
                            autoScrollLog('other_useful_info_text');
                            
                            // Mostrar confeti para el jugador con más puntos aunque no haya ganado oficialmente
                            showVictoryConfetti(winnerIndex);
                            
                            // Resaltar al jugador con mayor puntuación
                            $(`#player-card-${winnerIndex}`).addClass('winner-glow');
                        } else {
                            // Si no hay un ganador claro
                            let finPartidaHtml = `<div class="log-entry end-game mb-2" style="border-left-color: #6c757d; background-color: rgba(108, 117, 125, 0.1);">
                                <i class="fas fa-flag-checkered text-secondary me-2"></i>
                                <strong>🏁 ¡La partida ha terminado!</strong>
                            </div>`;
                            jQuery('#other_useful_info_text').append(finPartidaHtml);
                            autoScrollLog('other_useful_info_text');
                            
                            // Fallback a alert si no hay ganador
                            setTimeout(() => {
                                alert('¡La partida ha terminado!');
                            }, 500);
                        }
                    }, 500);
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

    // Mapeo de constantes de tipo de carta desde Python
    const DEV_CARD_TYPE_MAP = {
        0: 'knight',       // KNIGHT_EFFECT
        1: 'victory_point',// VICTORY_POINT_EFFECT
        2: 'road_building',
        3: 'year_of_plenty',
        4: 'monopoly'
    };

    // Mapeo de constantes
    const PYTHON_KNIGHT_CARD_TYPE = 0;
    const PYTHON_VICTORY_POINT_CARD_TYPE = 1;
    const PYTHON_PROGRESS_CARD_TYPE = 2;

    // Mapeo de efectos
    const PYTHON_ROAD_BUILDING_EFFECT = 2;
    const PYTHON_YEAR_OF_PLENTY_EFFECT = 3;
    const PYTHON_MONOPOLY_EFFECT = 4;

    // Buscar la última fase con datos completos
    let finalGameState = null;
    
    // Recorrer todas las rondas para encontrar la última información completa
    for (let roundKey in game_data.game) {
        let roundData = game_data.game[roundKey];
        for (let turnKey in roundData) {
            let turnData = roundData[turnKey];
            for (let phaseKey in turnData) {
                let phaseData = turnData[phaseKey];
                
                // Buscar el estado más completo posible
                if (phaseData && typeof phaseData === 'object') {
                    let hasPlayerData = false;
                    let hasVictoryPoints = false;
                    
                    // Verificar si tiene datos de jugadores
                    for (let i = 0; i < 4; i++) {
                        if (phaseData['hand_P' + i] || phaseData['development_cards_P' + i]) {
                            hasPlayerData = true;
                        }
                    }
                    
                    // Verificar si tiene puntos de victoria
                    if (phaseData.victory_points) {
                        hasVictoryPoints = true;
                    }
                    
                    // Si tiene datos útiles, usarlo como estado final
                    if (hasPlayerData || hasVictoryPoints) {
                        finalGameState = phaseData;
                        console.log("[DEBUG] Estado del juego encontrado en:", roundKey, turnKey, phaseKey);
                    }
                }
            }
        }
    }

    // Si no encontramos un estado final en las fases, buscar en el setup
    if (!finalGameState && game_data.setup) {
        console.log("[DEBUG] No se encontró estado final, usando datos de setup");
        finalGameState = {
            victory_points: {},
            // Inicializar puntos de victoria basados en setup (2 por cada poblado inicial)
        };
        
        // Calcular puntos de victoria iniciales del setup
        for (let i = 0; i < 4; i++) {
            if (game_data.setup['P' + i]) {
                finalGameState.victory_points['J' + i] = game_data.setup['P' + i].length;
            } else {
                finalGameState.victory_points['J' + i] = 0;
            }
        }
    }

    if (!finalGameState) {
        console.warn("[DEBUG] No se encontró estado del juego válido");
        return;
    }

    console.log("[DEBUG] Estado final del juego a usar:", JSON.parse(JSON.stringify(finalGameState)));

    const resourcesOrder = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

    // Actualizar datos para cada jugador
    for (let i = 0; i < 4; i++) {
        console.log(`[DEBUG] Actualizando jugador ${i}`);
        
        // 1. Actualizar Puntos de Victoria
        let victoryPoints = 0;
        if (finalGameState.victory_points && finalGameState.victory_points['J' + i] !== undefined) {
            victoryPoints = parseInt(finalGameState.victory_points['J' + i]) || 0;
        } else if (game_data.setup && game_data.setup['P' + i]) {
            // Fallback al setup si no hay datos de victoria
            victoryPoints = game_data.setup['P' + i].length; 
        }
        
        const vpElement = $('#puntos_victoria_J' + (i + 1));
        console.log(`[DEBUG] Actualizando PV del jugador ${i} a ${victoryPoints}`);
        animateNumberUpdate(vpElement, victoryPoints, parseInt(vpElement.text()) || 0);

        // 2. Actualizar Recursos
        const playerHandResources = finalGameState['hand_P' + i];
        console.log(`[DEBUG] Recursos del jugador ${i}:`, playerHandResources);
        
        if (playerHandResources) {
            resourcesOrder.forEach(resourceName => {
                const quantity = playerHandResources[resourceName] || 0;
                const resourceElement = $('#hand_P' + i + ' .resources-grid .' + resourceName + ' .' + resourceName + '_quantity');
                console.log(`[DEBUG] Actualizando ${resourceName} del jugador ${i} a ${quantity}`);
                animateNumberUpdate(resourceElement, quantity, parseInt(resourceElement.text()) || 0);
            });
        } else {
            console.warn(`[DEBUG] No se encontró hand_P${i} en el estado final`);
            // Resetear a 0 si no hay datos
            resourcesOrder.forEach(resourceName => {
                const resourceElement = $('#hand_P' + i + ' .resources-grid .' + resourceName + ' .' + resourceName + '_quantity');
                animateNumberUpdate(resourceElement, 0, parseInt(resourceElement.text()) || 0);
            });
        }

        // 3. Actualizar Cartas de Desarrollo
        const devCardsOnHand = finalGameState['development_cards_P' + i];
        console.log(`[DEBUG] Cartas de desarrollo del jugador ${i}:`, devCardsOnHand);
        
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
                if (card.type === PYTHON_KNIGHT_CARD_TYPE) {
                    cardName = 'knight';
                } else if (card.type === PYTHON_VICTORY_POINT_CARD_TYPE) {
                    cardName = 'victory_point';
                } else if (card.type === PYTHON_PROGRESS_CARD_TYPE) {
                    // Usar el efecto para determinar el tipo de carta de progreso
                    if (card.effect === PYTHON_ROAD_BUILDING_EFFECT) {
                        cardName = 'road_building';
                    } else if (card.effect === PYTHON_YEAR_OF_PLENTY_EFFECT) {
                        cardName = 'year_of_plenty';
                    } else if (card.effect === PYTHON_MONOPOLY_EFFECT) {
                        cardName = 'monopoly';
                    }
                }

                if (cardName && devCardCounts.hasOwnProperty(cardName)) {
                    devCardCounts[cardName]++;
                }
            });
        } else {
            console.warn(`[DEBUG] No se encontró development_cards_P${i} o no es un array`);
        }

        // Actualizar UI de cartas de desarrollo
        for (const cardName in devCardCounts) {
            const cardElement = $('#hand_P' + i + ' .dev-cards-grid .' + cardName + ' .' + cardName + '_quantity');
            console.log(`[DEBUG] Actualizando ${cardName} del jugador ${i} a ${devCardCounts[cardName]}`);
            animateNumberUpdate(cardElement, devCardCounts[cardName], parseInt(cardElement.text()) || 0);
        }
        
        // 4. Actualizar badges especiales (si están disponibles en el JSON)
        // Nota: Estos datos pueden no estar disponibles en el JSON actual
        if (finalGameState['largest_army_P' + i]) {
            $('#largest_army_P' + i).show();
        } else {
            $('#largest_army_P' + i).hide();
        }
        
        if (finalGameState['longest_road_P' + i]) {
            $('#longest_road_P' + i).show();
        } else {
            $('#longest_road_P' + i).hide();
        }
    }
    
    console.log("[DEBUG] UI actualizada completamente con datos del JSON.");
    
    // Verificar si hay un ganador después de actualizar los datos
    // Esta verificación es importante para detectar automáticamente
    // cuando un jugador ha alcanzado los 10 puntos de victoria
    checkVictory();
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

    // Actualizar recursos con animación
    materials.forEach(function (material) {
        if (hand_obj && hand_obj[material] !== undefined) {
            const resourceElement = $('#hand_P' + player + ' .resources-grid .' + material + ' .' + material + '_quantity');
            const oldValue = parseInt(resourceElement.text()) || 0;
            animateNumberUpdate(resourceElement, hand_obj[material], oldValue);
        }
    });

    // Actualizar cartas de desarrollo con animación
    dev_cards.forEach(function (card) {
        let cardElement = null;
        let newValue = null;
        
        // Asumiendo que las cartas de desarrollo están dentro del mismo objeto `hand_obj`
        if (hand_obj && hand_obj[card] !== undefined) {
            cardElement = $('#hand_P' + player + ' .dev-cards-grid .' + card + ' .' + card + '_quantity');
            newValue = hand_obj[card];
        } else if (hand_obj && hand_obj['development_cards'] && hand_obj['development_cards'][card] !== undefined) {
            // Alternativa: si las cartas están en un sub-objeto 'development_cards'
            cardElement = $('#hand_P' + player + ' .dev-cards-grid .' + card + ' .' + card + '_quantity');
            newValue = hand_obj['development_cards'][card];
        }
        
        if (cardElement && cardElement.length && newValue !== null) {
            const oldValue = parseInt(cardElement.text()) || 0;
            animateNumberUpdate(cardElement, newValue, oldValue);
        }
    });
}

function on_development_card_played(card_played_info) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

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
        animateNumberUpdate(quantity, Math.max(0, currentValue - 1), currentValue);
    }

    let cardEmoji = getDevCardEmoji(card_played_info.played_card);
    let html = '<div class="log-entry play-card mb-2">';
    html += getCardIcon(card_played_info.played_card);
    html += '<strong>🃏 Jugador ' + (actual_player + 1) + '</strong> jugó ';
    html += '<span class="fw-bold">' + cardEmoji + ' ' + getCardName(card_played_info.played_card) + '</span>';
    
    switch (card_played_info.played_card) {
        case 'knight':
            if (card_played_info.past_thief_terrain !== undefined && card_played_info.thief_terrain !== undefined) {
                move_thief(card_played_info.past_thief_terrain, card_played_info.thief_terrain, card_played_info.robbed_player, card_played_info.stolen_material_id, true);
                html += '<br><small class="ms-4">🥷 Movió el ladrón del terreno ' + card_played_info.past_thief_terrain + ' al ' + card_played_info.thief_terrain;
                if (card_played_info.robbed_player !== undefined && card_played_info.robbed_player !== -1) {
                    html += '<br>💰 Robó una carta al Jugador ' + (card_played_info.robbed_player + 1);
                }
                html += '</small>';
            }
            break;
        case 'victory_point':
            html += '<br><small class="ms-4">🏆 Punto de Victoria revelado ✨</small>';
            break;
        case 'monopoly':
            if (card_played_info.material_chosen !== undefined) {
                let material_chosen = materials[card_played_info.material_chosen];
                let materialEmoji = getResourceEmoji(material_chosen);
                html += '<br><small class="ms-4">💰 Monopolio de: ' + materialEmoji + ' ' + material_chosen.toUpperCase() + '</small>';
                
                // Actualizar las manos de todos los jugadores si está disponible
                for (let i = 0; i < 4; i++) {
                    if (card_played_info['hand_P' + i]) {
                        changeHandObject(i, card_played_info['hand_P' + i]);
                    }
                }
            }
            break;
        case 'year_of_plenty':
            if (card_played_info.materials_selected) {
                let material1Emoji = getResourceEmoji(materials[card_played_info.materials_selected.material]);
                let material2Emoji = getResourceEmoji(materials[card_played_info.materials_selected.material_2]);
                let materials_chosen = [
                    material1Emoji + ' ' + materials[card_played_info.materials_selected.material].toUpperCase(), 
                    material2Emoji + ' ' + materials[card_played_info.materials_selected.material_2].toUpperCase()
                ];
                html += '<br><small class="ms-4">🎁 Recursos elegidos: ' + materials_chosen.join(', ') + '</small>';
                
                if (card_played_info['hand_P' + actual_player]) {
                    changeHandObject(actual_player, card_played_info['hand_P' + actual_player]);
                }
            }
            break;
        case 'road_building':
            if (card_played_info.roads) {
                html += '<br><small class="ms-4">🛤️ Construcción de carreteras:<br>';
                if (card_played_info.valid_road_1) {
                    html += '🚧 Carretera 1: nodo ' + card_played_info.roads.node_id + ' → ' + card_played_info.roads.road_to + '<br>';
                    // Dibujar la carretera en el tablero
                    let road_id_str = card_played_info.roads.node_id < card_played_info.roads.road_to ? 
                        `road_${card_played_info.roads.node_id}_${card_played_info.roads.road_to}` : 
                        `road_${card_played_info.roads.road_to}_${card_played_info.roads.node_id}`;
                    animateRoadBuilding(road_id_str, actual_player);
                }
                if (card_played_info.valid_road_2) {
                    html += '🚧 Carretera 2: nodo ' + card_played_info.roads.node_id_2 + ' → ' + card_played_info.roads.road_to_2;
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

// Nueva función para actualizar cartas de desarrollo con animación
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
    
    // Actualizar UI con animación
    for (const cardName in devCardCounts) {
        const cardElement = $(`#hand_P${playerIndex} .dev-cards-grid .${cardName} .${cardName}_quantity`);
        if (cardElement.length) {
            const oldValue = parseInt(cardElement.text()) || 0;
            const newValue = devCardCounts[cardName];
            
            // Usar la nueva función de animación
            animateNumberUpdate(cardElement, newValue, oldValue);
        }
    }
}

// Función helper para animar la actualización de números
function animateNumberUpdate(element, newValue, oldValue = null) {
    if (!element || !element.length) return;
    
    // Determinar el tipo de cambio
    const currentValue = parseInt(element.text()) || 0;
    const finalValue = parseInt(newValue) || 0;
    
    // Actualizar el valor
    element.text(finalValue);
    
    // Determinar el tipo de animación según el cambio
    let animationClass = 'quantity-updated';
    if (oldValue !== null) {
        if (finalValue > oldValue) {
            animationClass = 'quantity-increase';
        } else if (finalValue < oldValue) {
            animationClass = 'quantity-decrease';
        } else {
            animationClass = 'quantity-neutral';
        }
    }
    
    // Añadir la clase de animación
    element.addClass(animationClass);
    
    // Después de 750ms, quitar la clase y añadir la transición a normal
    setTimeout(() => {
        element.removeClass(animationClass);
        element.addClass('fade-to-normal');
        
        // Quitar la clase fade-to-normal después de completar la transición
        setTimeout(() => {
            element.removeClass('fade-to-normal');
        }, 750);
    }, 750);
    
    console.log(`[DEBUG] Animando actualización: ${currentValue} → ${finalValue}`);
}

// Función para obtener emojis de recursos
function getResourceEmoji(resourceName) {
    const resourceEmojis = {
        'cereal': '🌾',
        'mineral': '⛰️', 
        'clay': '🧱',
        'wood': '🪵',
        'wool': '🐑'
    };
    return resourceEmojis[resourceName] || '❓';
}

// Función para obtener emojis de cartas de desarrollo
function getDevCardEmoji(cardName) {
    const cardEmojis = {
        'knight': '⚔️',
        'victory_point': '🏆',
        'road_building': '🛣️',
        'year_of_plenty': '🎁',
        'monopoly': '💰'
    };
    return cardEmojis[cardName] || '🃏';
}

// Función para obtener emojis de construcciones
function getBuildingEmoji2(buildingType) {
    const buildingEmojis = {
        'S舎': '🏠',
        'settlement': '🏠',
        'town': '🏠',
        'C都市': '🏛️',
        'city': '🏛️',
        'R道': '🛤️',
        'road': '🛤️'
    };
    return buildingEmojis[buildingType] || '🏗️';
}

// Función para obtener emoji de dados según el valor
function getDiceEmoji(diceValue) {
    const diceEmojis = {
        1: '⚀',
        2: '⚁', 
        3: '⚂',
        4: '⚃',
        5: '⚄',
        6: '⚅',
        7: '⚀⚀',  // Dos dados que suman 7
        8: '⚁⚂',  // Dos dados que suman 8
        9: '⚂⚂',  // Dos dados que suman 9
        10: '⚃⚃', // Dos dados que suman 10
        11: '⚄⚄', // Dos dados que suman 11
        12: '⚅⚅'  // Dos dados que suman 12
    };
    return diceEmojis[diceValue] || '🎲';
}

// Función para manejar el inicio de turno
function handleStartTurn(phase_obj, phaseKey) {
    console.log('[DEBUG] handleStartTurn:', phase_obj);
    
    if (phase_obj && phase_obj.player !== undefined) {
        $('#hand_P' + phase_obj.player).css('border', 'solid 3px black');
        
        if (phase_obj.dice !== undefined) {
            updateDiceRoll(phase_obj.dice);
            
            let diceEmoji = getDiceEmoji(phase_obj.dice);
            let html = `<div class="log-entry dice-roll mb-2">
                <i class="fas fa-dice text-primary me-2"></i>
                <strong>🎮 Jugador ${phase_obj.player + 1}</strong> inició su turno
                <br><small class="ms-4">🎲 Tiró los dados: ${diceEmoji} <span class="badge bg-primary">${phase_obj.dice}</span></small>
            </div>`;
            jQuery('#other_useful_info_text').append(html);
            autoScrollLog('other_useful_info_text');
        } else {
            let html = `<div class="log-entry start-turn mb-2">
                <i class="fas fa-play text-primary me-2"></i>
                <strong>🎮 Jugador ${phase_obj.player + 1}</strong> inició su turno
            </div>`;
            jQuery('#other_useful_info_text').append(html);
            autoScrollLog('other_useful_info_text');
        }
    }
    
    // Actualizar manos y datos
    updatePhaseData(phase_obj);
}

// Función para obtener el jugador actual
function getCurrentPlayer() {
    // Intentar obtener el jugador desde el contador de turnos
    let currentTurnKey = $('#contador_turnos').val();
    if (currentTurnKey) {
        // Si el turno es como "P0", "P1", etc., extraer el número
        let match = currentTurnKey.match(/P(\d+)/);
        if (match) {
            return parseInt(match[1]);
        }
        
        // Si el turno es como "turn_P0", extraer el número
        match = currentTurnKey.match(/turn_P(\d+)/);
        if (match) {
            return parseInt(match[1]);
        }
        
        // Si es un número directo
        if (!isNaN(parseInt(currentTurnKey))) {
            return parseInt(currentTurnKey) - 1; // Convertir de 1-based a 0-based
        }
    }
    
    // Fallback: intentar obtener desde phase_obj global
    if (phase_obj && phase_obj.player !== undefined) {
        return phase_obj.player;
    }
    
    return 0; // Fallback al jugador 0
}

// Función para manejar la fase de comercio
function handleCommercePhase(phase_obj, phaseKey) {
    console.log('[DEBUG] handleCommercePhase - Datos completos:', JSON.stringify(phase_obj, null, 2));
    console.log('[DEBUG] handleCommercePhase - Claves disponibles:', Object.keys(phase_obj || {}));
    
    let hasLoggedActivity = false; // Para evitar logs duplicados
    
    if (phase_obj && typeof phase_obj === 'object') {
        // Buscar actividades de comercio en el objeto
        let commerceActivities = [];
        let hasActivity = false;
        
        // Verificar si hay comercio con el banco
        if (phase_obj.trade_bank || phase_obj.bank_trade || phase_obj.give || phase_obj.receive) {
            hasActivity = true;
            commerceActivities.push({
                type: 'bank',
                data: phase_obj
            });
        }
        
        // Verificar si hay comercio entre jugadores
        if (phase_obj.trade_players || phase_obj.player_trade || phase_obj.player_id_send || phase_obj.offer) {
            hasActivity = true;
            commerceActivities.push({
                type: 'players',
                data: phase_obj
            });
        }
        
        // Verificar si hay compra de cartas de desarrollo
        if (phase_obj.buy_card || phase_obj.development_card_purchased || 
           (phase_obj.player !== undefined && Object.keys(phase_obj).some(key => key.includes('development_cards')))) {
            hasActivity = true;
            commerceActivities.push({
                type: 'buy_card',
                data: phase_obj
            });
        }
        
        // Verificar si hay construcciones (gastar recursos)
        if (phase_obj.build || phase_obj.construction || phase_obj.what_build || phase_obj.node_id) {
            hasActivity = true;
            commerceActivities.push({
                type: 'construction',
                data: phase_obj
            });
        }
        
        // Si no hay actividades específicas detectadas, buscar en cualquier subclave
        if (!hasActivity) {
            // Recorrer todas las claves del objeto para buscar actividades
            for (let key in phase_obj) {
                if (typeof phase_obj[key] === 'object' && phase_obj[key] !== null) {
                    if (key.includes('trade') || key.includes('bank')) {
                        commerceActivities.push({
                            type: 'bank',
                            data: phase_obj[key]
                        });
                        hasActivity = true;
                    } else if (key.includes('build') || key.includes('construction')) {
                        commerceActivities.push({
                            type: 'construction',
                            data: phase_obj[key]
                        });
                        hasActivity = true;
                    } else if (key.includes('buy') || key.includes('card')) {
                        commerceActivities.push({
                            type: 'buy_card',
                            data: phase_obj[key]
                        });
                        hasActivity = true;
                    }
                }
            }
        }
        
        // Si hay actividades específicas, procesarlas
        if (hasActivity && commerceActivities.length > 0) {
            console.log('[DEBUG] Actividades de comercio encontradas:', commerceActivities);
            commerceActivities.forEach(activity => {
                switch(activity.type) {
                    case 'bank':
                        logBankTrade(activity.data);
                        hasLoggedActivity = true;
                        break;
                    case 'players':
                        logPlayerTrade(activity.data);
                        hasLoggedActivity = true;
                        break;
                    case 'buy_card':
                        logCardPurchase(activity.data);
                        hasLoggedActivity = true;
                        break;
                    case 'construction':
                        logConstruction(activity.data);
                        hasLoggedActivity = true;
                        break;
                }
            });
        }
    }
    
    // Solo mostrar log general si no hubo actividades específicas
    if (!hasLoggedActivity) {
        console.log('[DEBUG] No se encontraron actividades específicas, mostrando log general');
        let currentPlayer = getCurrentPlayer();
        let html = `<div class="log-entry commerce-general mb-2">
            <i class="fas fa-store text-info me-2"></i>
            <strong>🛍️ Jugador ${currentPlayer + 1}</strong> - Fase de Comercio
            <br><small class="ms-4">💼 Oportunidad para intercambios, compras y construcciones</small>
        </div>`;
        jQuery('#commerce_log_text').append(html);
        autoScrollLog('commerce_log_text');
    }
    
    updatePhaseData(phase_obj);
}

// Función para manejar la fase de construcción
function handleBuildPhase(phase_obj, phaseKey) {
    console.log('[DEBUG] handleBuildPhase:', phase_obj);
    
    let hasLoggedActivity = false; // Para evitar logs duplicados
    
    if (phase_obj && typeof phase_obj === 'object') {
        // Buscar construcciones en el objeto
        let hasConstruction = false;
        
        // Verificar construcciones directas
        if (phase_obj.build || phase_obj.construction || phase_obj.what_build || phase_obj.node_id) {
            hasConstruction = true;
            logConstruction(phase_obj);
            hasLoggedActivity = true;
        }
        
        // Buscar construcciones en subclaves
        if (!hasConstruction) {
            for (let key in phase_obj) {
                if (typeof phase_obj[key] === 'object' && phase_obj[key] !== null) {
                    if (key.includes('build') || key.includes('construction') || 
                       (phase_obj[key].what_build || phase_obj[key].node_id)) {
                        hasConstruction = true;
                        logConstruction(phase_obj[key]);
                        hasLoggedActivity = true;
                        break;
                    }
                }
            }
        }
    }
    
    // Solo mostrar mensaje general si no hay construcción específica
    if (!hasLoggedActivity) {
        let currentPlayer = getCurrentPlayer();
        let html = `<div class="log-entry build-phase mb-2">
            <i class="fas fa-tools text-warning me-2"></i>
            <strong>🏗️ Jugador ${currentPlayer + 1}</strong> - Fase de Construcción
            <br><small class="ms-4">🔨 Oportunidad para construir poblados, ciudades y carreteras</small>
        </div>`;
        jQuery('#other_useful_info_text').append(html);
        autoScrollLog('other_useful_info_text');
    }
}

// Función para manejar el fin de turno
function handleEndTurn(phase_obj, phaseKey) {
    console.log('[DEBUG] handleEndTurn:', phase_obj);
    
    let currentPlayer = getCurrentPlayer();
    if (phase_obj && phase_obj.player !== undefined) {
        currentPlayer = phase_obj.player;
        $('#hand_P' + phase_obj.player).css('border', 'solid 0px black');
    }
    
    let html = `<div class="log-entry end-turn mb-2">
        <i class="fas fa-stop text-secondary me-2"></i>
        <strong>🏁 Jugador ${currentPlayer + 1}</strong> terminó su turno
    </div>`;
    jQuery('#other_useful_info_text').append(html);
    autoScrollLog('other_useful_info_text');
    
    updatePhaseData(phase_obj);
}

// Función para manejar fases genéricas
function handleGenericPhase(phase_obj, phaseKey) {
    console.log('[DEBUG] handleGenericPhase:', phaseKey, phase_obj);
    
    // Procesar según el tipo de fase usando la lógica original
    if (phaseKey.includes('trade_bank') || (phase_obj && phase_obj.phase_type == "trade_bank")) {
        logBankTrade(phase_obj);
    } else if (phaseKey.includes('trade_players') || (phase_obj && phase_obj.phase_type == "trade_players")) {
        logPlayerTrade(phase_obj);
    } else if (phaseKey.includes('build') || (phase_obj && phase_obj.phase_type == "build")) {
        logConstruction(phase_obj);
    } else if (phaseKey.includes('buy_card') || (phase_obj && phase_obj.phase_type == "buy_card")) {
        logCardPurchase(phase_obj);
    } else if (phaseKey.includes('play_card') || (phase_obj && phase_obj.phase_type == "play_card")) {
        on_development_card_played(phase_obj);
    } else if (phaseKey.includes('give_cards') || (phase_obj && phase_obj.phase_type == "give_cards")) {
        logResourceDistribution(phase_obj);
    } else if (phaseKey.includes('discard') || (phase_obj && phase_obj.phase_type == "discard_cards")) {
        logCardDiscard(phase_obj);
    } else if (phaseKey.includes('rob') || phaseKey.includes('bandit') || (phase_obj && (phase_obj.phase_type == "rob_player" || phase_obj.phase_type == "move_bandit"))) {
        logThiefMovement(phase_obj);
    }
    
    updatePhaseData(phase_obj);
}

// Función para actualizar datos de fase común
function updatePhaseData(phase_obj) {
    if (!phase_obj) return;
    
    // Actualizar manos de jugadores
    if (phase_obj.player !== undefined && phase_obj['hand_P' + phase_obj.player]) {
        changeHandObject(phase_obj.player, phase_obj['hand_P' + phase_obj.player]);
    }
    
    // Actualizar todas las manos si están disponibles
    for (let i = 0; i < 4; i++) {
        if (phase_obj['hand_P' + i]) {
            changeHandObject(i, phase_obj['hand_P' + i]);
        }
    }
    
    // Actualizar puntos de victoria
    if (phase_obj.victory_points) {
        for (let i = 0; i < 4; i++) {
            if (phase_obj.victory_points['J' + i] !== undefined) {
                const vpElement = $('#puntos_victoria_J' + (i + 1));
                const oldVP = parseInt(vpElement.text()) || 0;
                const newVP = phase_obj.victory_points['J' + i];
                animateNumberUpdate(vpElement, newVP, oldVP);
            }
        }
    }
    
    // Actualizar cartas de desarrollo
    if (phase_obj.player !== undefined && phase_obj['development_cards_P' + phase_obj.player]) {
        updateDevCards(phase_obj.player, phase_obj['development_cards_P' + phase_obj.player]);
    }
    
    // Después de un breve delay, actualizar con los datos completos del juego
}

// Aplicar movimiento del ladrón en el tablero
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

// Función para mostrar información de debugging sobre el juego cargado
function debugGameStructure(game_data) {
    console.log('[DEBUG] === INFORMACIÓN DEL JUEGO CARGADO ===');
    
    if (!game_data) {
        console.log('[DEBUG] No hay datos del juego');
        return;
    }
    
    // Información básica
    console.log('[DEBUG] Claves principales:', Object.keys(game_data));
    
    // Información del setup
    if (game_data.setup) {
        console.log('[DEBUG] Setup disponible con claves:', Object.keys(game_data.setup));
        for (let i = 0; i < 4; i++) {
            if (game_data.setup['P' + i]) {
                console.log(`[DEBUG] Jugador ${i} en setup:`, game_data.setup['P' + i].length, 'construcciones iniciales');
            }
        }
    }
    
    // Información del juego
    if (game_data.game) {
        console.log('[DEBUG] Rondas disponibles:', Object.keys(game_data.game).length);
        
        // Analizar una ronda de muestra para entender la estructura
        let firstRoundKey = Object.keys(game_data.game)[0];
        let firstRound = game_data.game[firstRoundKey];
        console.log(`[DEBUG] Primera ronda (${firstRoundKey}) tiene turnos:`, Object.keys(firstRound));
        
        // Analizar un turno de muestra
        let firstTurnKey = Object.keys(firstRound)[0];
        let firstTurn = firstRound[firstTurnKey];
        console.log(`[DEBUG] Primer turno (${firstTurnKey}) tiene fases:`, Object.keys(firstTurn));
        
        // Buscar datos de jugadores en las fases
        for (let phaseKey of Object.keys(firstTurn)) {
            let phase = firstTurn[phaseKey];
            if (phase && typeof phase === 'object') {
                let hasPlayerData = false;
                for (let i = 0; i < 4; i++) {
                    if (phase['hand_P' + i] || phase['development_cards_P' + i] || phase.victory_points) {
                        hasPlayerData = true;
                        break;
                    }
                }
                if (hasPlayerData) {
                    console.log(`[DEBUG] Fase ${phaseKey} contiene datos de jugadores`);
                    
                    // Mostrar ejemplo de datos de un jugador
                    for (let i = 0; i < 4; i++) {
                        if (phase['hand_P' + i]) {
                            console.log(`[DEBUG] Jugador ${i} recursos:`, phase['hand_P' + i]);
                        }
                        if (phase['development_cards_P' + i]) {
                            console.log(`[DEBUG] Jugador ${i} cartas desarrollo:`, phase['development_cards_P' + i]);
                        }
                    }
                    
                    if (phase.victory_points) {
                        console.log('[DEBUG] Puntos de victoria:', phase.victory_points);
                    }
                    break; // Solo mostrar el primer ejemplo encontrado
                }
            }
        }
    }
    
    console.log('[DEBUG] === FIN INFORMACIÓN DEL JUEGO ===');
}

// Variable para evitar logs duplicados
let lastLoggedPhase = '';
let lastLoggedMessage = '';

// Función para evitar logs duplicados
function shouldSkipLog(phaseKey, message) {
    let currentLog = phaseKey + '|' + message;
    if (currentLog === lastLoggedMessage) {
        return true; // Saltar este log porque es duplicado
    }
    lastLoggedMessage = currentLog;
    return false;
}

// Función para logging de comercio bancario
function logBankTrade(tradeData) {
    console.log('[DEBUG] logBankTrade:', tradeData);
    
    let giveText = 'N/A';
    let receiveText = 'N/A';
    let player = tradeData.player !== undefined ? tradeData.player : getCurrentPlayer();
    
    if (tradeData.give && typeof tradeData.give === 'object') {
        let giveItems = [];
        for (let resource in tradeData.give) {
            if (tradeData.give[resource] > 0) {
                let emoji = getResourceEmoji(resource);
                giveItems.push(`${emoji} ${tradeData.give[resource]}`);
            }
        }
        giveText = giveItems.join(' ') || 'N/A';
    }
    
    if (tradeData.receive && typeof tradeData.receive === 'object') {
        let receiveItems = [];
        for (let resource in tradeData.receive) {
            if (tradeData.receive[resource] > 0) {
                let emoji = getResourceEmoji(resource);
                receiveItems.push(`${emoji} ${tradeData.receive[resource]}`);
            }
        }
        receiveText = receiveItems.join(' ') || 'N/A';
    }
    
    let html = `<div class="log-entry trade-bank mb-2">
        <i class="fas fa-university text-success me-2"></i>
        <strong>🏛️ Jugador ${player + 1}</strong> comerció con el banco
        <br><small class="ms-4">
            📤 Dio: ${giveText}
            <br>📥 Recibió: ${receiveText}
        </small>
    </div>`;
    
    jQuery('#commerce_log_text').append(html);
    autoScrollLog('commerce_log_text');
}

// Función para logging de comercio entre jugadores
function logPlayerTrade(tradeData) {
    console.log('[DEBUG] logPlayerTrade:', tradeData);
    
    let fromPlayer = tradeData.player_id_send !== undefined ? tradeData.player_id_send : getCurrentPlayer();
    let toPlayer = tradeData.player_id_receive !== undefined ? tradeData.player_id_receive : -1;
    
    let html = `<div class="log-entry trade-players mb-2">
        <i class="fas fa-handshake text-info me-2"></i>
        <strong>🤝 Comercio entre jugadores</strong>
        <br><small class="ms-4">`;
    
    if (toPlayer !== -1) {
        html += `👤 Jugador ${fromPlayer + 1} ↔️ Jugador ${toPlayer + 1}`;
    } else {
        html += `👤 Jugador ${fromPlayer + 1} ↔️ Otro jugador`;
    }
    
    html += `</small>
    </div>`;
    
    jQuery('#commerce_log_text').append(html);
    autoScrollLog('commerce_log_text');
}

// Función para logging de compra de cartas de desarrollo
function logCardPurchase(purchaseData) {
    console.log('[DEBUG] logCardPurchase:', purchaseData);
    
    let player = purchaseData.player !== undefined ? purchaseData.player : getCurrentPlayer();
    
    let html = `<div class="log-entry buy-card mb-2">
        <i class="fas fa-shopping-cart text-warning me-2"></i>
        <strong>🛒 Jugador ${player + 1}</strong> compró una carta de desarrollo
        <br><small class="ms-4">💳 Gastó recursos para obtener una carta</small>
    </div>`;
    
    jQuery('#commerce_log_text').append(html);
    autoScrollLog('commerce_log_text');
}

// Función para logging de construcciones
function logConstruction(constructionData) {
    console.log('[DEBUG] logConstruction:', constructionData);
    
    let player = constructionData.player !== undefined ? constructionData.player : getCurrentPlayer();
    let building = constructionData.what_build || constructionData.construction || 'construcción';
    let buildingEmoji = getBuildingEmoji2(building);
    let buildingName = getBuildingName(building);
    
    let html = `<div class="log-entry construction mb-2">
        <i class="fas fa-hammer text-warning me-2"></i>
        <strong>🔨 Jugador ${player + 1}</strong> construyó ${buildingEmoji} ${buildingName}`;
    
    if (constructionData.node_id !== undefined) {
        html += `<br><small class="ms-4">📍 Ubicación: nodo ${constructionData.node_id}</small>`;
    }
    
    html += '</div>';
    
    jQuery('#other_useful_info_text').append(html);
    autoScrollLog('other_useful_info_text');
}

// Función para logging de distribución de recursos por dados
function logResourceDistribution(distributionData) {
    console.log('[DEBUG] logResourceDistribution:', distributionData);
    
    let html = `<div class="log-entry resource-distribution mb-2">
        <i class="fas fa-coins text-success me-2"></i>
        <strong>💰 Distribución de recursos</strong>
        <br><small class="ms-4">🎲 Los jugadores recibieron recursos por la tirada de dados</small>
    </div>`;
    
    jQuery('#other_useful_info_text').append(html);
    autoScrollLog('other_useful_info_text');
}

// Función para logging de descarte de cartas
function logCardDiscard(discardData) {
    console.log('[DEBUG] logCardDiscard:', discardData);
    
    let player = discardData.player !== undefined ? discardData.player : getCurrentPlayer();
    
    let html = `<div class="log-entry card-discard mb-2">
        <i class="fas fa-trash text-danger me-2"></i>
        <strong>🗑️ Jugador ${player + 1}</strong> descartó cartas
        <br><small class="ms-4">😈 Por efecto del ladrón (más de 7 cartas)</small>
    </div>`;
    
    jQuery('#other_useful_info_text').append(html);
    autoScrollLog('other_useful_info_text');
}

// Función para logging de movimiento del ladrón
function logThiefMovement(thiefData) {
    console.log('[DEBUG] logThiefMovement:', thiefData);
    
    let player = thiefData.player !== undefined ? thiefData.player : getCurrentPlayer();
    
    let html = `<div class="log-entry thief-movement mb-2">
        <i class="fas fa-user-ninja text-dark me-2"></i>
        <strong>🥷 Jugador ${player + 1}</strong> movió el ladrón`;
    
    if (thiefData.thief_terrain !== undefined) {
        html += `<br><small class="ms-4">📍 Nuevo terreno: ${thiefData.thief_terrain}</small>`;
    }
    
    if (thiefData.robbed_player !== undefined && thiefData.robbed_player !== -1) {
        html += `<br><small class="ms-4">💰 Robó una carta al Jugador ${thiefData.robbed_player + 1}</small>`;
    }
    
    html += '</div>';
    
    jQuery('#other_useful_info_text').append(html);
    autoScrollLog('other_useful_info_text');
}

// Función para inicializar los controles de zoom y pantalla completa
function initZoomControls() {
    const zoomInBtn = document.getElementById('zoom-in');
    const zoomOutBtn = document.getElementById('zoom-out');
    const fullscreenBtn = document.getElementById('fullscreen');
    const gamefield = document.getElementById('gamefield');
    const gamefieldExternal = document.getElementById('gamefield_external');
    
    // Estado de zoom actual
    let zoomState = 'normal'; // 'normal', 'zoomed-in', 'zoomed-out'
    let isFullscreen = false;
    
    // Evento para acercar
    zoomInBtn.addEventListener('click', function() {
        // Solo permitir zoom in si no estamos ya en ese estado
        if (zoomState !== 'zoomed-in') {
            // Eliminar clase previa
            gamefield.classList.remove('zoomed-out');
            // Añadir nueva clase
            gamefield.classList.add('zoomed-in');
            zoomState = 'zoomed-in';
        }
    });
    
    // Evento para alejar
    zoomOutBtn.addEventListener('click', function() {
        // Solo permitir zoom out si no estamos ya en ese estado
        if (zoomState !== 'zoomed-out') {
            // Eliminar clase previa
            gamefield.classList.remove('zoomed-in');
            // Añadir nueva clase
            gamefield.classList.add('zoomed-out');
            zoomState = 'zoomed-out';
        }
    });
    
    // Evento para restablecer zoom (doble clic en el mapa)
    gamefield.addEventListener('dblclick', function() {
        // Eliminar todas las clases de zoom
        gamefield.classList.remove('zoomed-in', 'zoomed-out');
        zoomState = 'normal';
    });
    
    // Evento para pantalla completa
    fullscreenBtn.addEventListener('click', function() {
        toggleFullscreen();
    });
    
    // Función para alternar pantalla completa
    function toggleFullscreen() {
        if (!isFullscreen) {
            // Entrar en modo pantalla completa
            gamefieldExternal.classList.add('fullscreen');
            fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
            fullscreenBtn.title = "Salir de pantalla completa";
            isFullscreen = true;
            
            // Capturar tecla ESC para salir de pantalla completa
            document.addEventListener('keydown', handleEscKey);
        } else {
            // Salir de modo pantalla completa
            exitFullscreen();
        }
    }
    
    // Función para salir de pantalla completa
    function exitFullscreen() {
        gamefieldExternal.classList.remove('fullscreen');
        fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
        fullscreenBtn.title = "Pantalla completa";
        isFullscreen = false;
        
        // Eliminar listener de tecla ESC
        document.removeEventListener('keydown', handleEscKey);
    }
    
    // Función para manejar la tecla ESC
    function handleEscKey(e) {
        if (e.key === 'Escape' && isFullscreen) {
            exitFullscreen();
        }
    }
    
    // También podemos añadir soporte para el API Fullscreen nativo del navegador
    if (document.documentElement.requestFullscreen) {
        // Agregar un segundo botón para pantalla completa nativa del navegador
        const nativeFullscreenBtn = document.createElement('button');
        nativeFullscreenBtn.id = 'native-fullscreen';
        nativeFullscreenBtn.title = 'Pantalla completa del navegador';
        nativeFullscreenBtn.innerHTML = '<i class="fas fa-desktop"></i>';
        document.querySelector('.map-controls').appendChild(nativeFullscreenBtn);
        
        nativeFullscreenBtn.addEventListener('click', function() {
            if (!document.fullscreenElement) {
                gamefieldExternal.requestFullscreen().catch(err => {
                    console.error(`Error al intentar mostrar en pantalla completa: ${err.message}`);
                });
            } else {
                document.exitFullscreen();
            }
        });
    }
}