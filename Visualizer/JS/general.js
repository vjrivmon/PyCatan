let game_obj = {};
let round_obj = {};
let turn_obj = {};
let phase_obj = {};

let game_direction = 'forward'; // or "backward"


function init_events() {
    let input = jQuery('#get_file');
    let load_game = jQuery('#load_game');
    load_game.on('click', function (e) {
        input.click();
    })

    input.on('click', function (e) {
        input.val('')

        // resetear el tablero
        jQuery('.node').add('.road').add('.vertical_road').css('background', 'none').css('border', 'none').text('');
        $('#contador_rondas').val('').change();
        $('#contador_turnos').val('').change();
        $('#contador_fases').val('').change();
    })

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

function nodeSetup() {
    nodes = game_obj['setup']['board']['board_nodes'];

    for (let i = 0; i < nodes.length; i++) {
        let node = jQuery('#node_' + i);

        // TODO: Mejora a futuro: Añadir icono de puerto a las costeras O añadir un icono en el mar
        node.html(fromHarborNumberToMaterials(nodes[i]['harbor']));
    }
}

function fromHarborNumberToMaterials(harborNumber) {
    switch (harborNumber) {
        case 0:
            return '<i class="fa-solid fa-wheat-awn"></i><span>2:1</span>';
        case 1:
            return '<i class="fa-solid fa-mountain-sun"></i><span>2:1</span>';
        case 2:
            return '<i class="fa-solid fa-trowel-bricks"></i><span>2:1</span>';
        case 3:
            return '<i class="fa-solid fa-wand-sparkles"></i><span>2:1</span>';
        case 4:
            return '<i class="fa-brands fa-cotton-bureau"></i><span>2:1</span>';
        case 5:
            return '<span>3:1</span>'
        case -1:
            return '';
        default:
            //            alert('Caso ilegal de terreno');
            break;
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
    let playIntervalNumber = 0;

    contador_rondas.off().on('change', function (e) {
        if (contador_rondas.val() === '') {
            return;
        }

        if (parseInt(contador_rondas.val()) < 1) {
            contador_rondas.val(1).change();
        }
        if (parseInt(contador_rondas.val()) > Object.keys(game_obj['game']).length) {
            contador_rondas.val(Object.keys(game_obj['game']).length).change();

            play_btn.click()
        }

        jQuery('#actual_round').text(contador_rondas.val())

        round_obj = game_obj['game']['round_' + (contador_rondas.val() - 1)];
        contador_turnos.val(1).change();
    });
    contador_turnos.off().on('change', function (e) {
        if (contador_turnos.val() === '') {
            return;
        }

        let actual_player_json = parseInt(contador_turnos.val()) - 1; // 0 - 3

        if (parseInt(contador_turnos.val()) > 4) {
            contador_rondas.val(parseInt(contador_rondas.val()) + 1).change()
            contador_turnos.val(1).change()
            return;
        }
        if (parseInt(contador_turnos.val()) < 1) {
            if (parseInt(contador_rondas.val()) < 1) {
                contador_turnos.val(1).change();
            } else {
                contador_rondas.val(parseInt(contador_rondas.val()) - 1).change();
                contador_turnos.val(4).change();
            }
            return;
        }

        deleteCaretStyling();

        $('#P0').css('border', '5px solid lightcoral');
        $('#P1').css('border', '5px solid lightblue');
        $('#P2').css('border', '5px solid lightgreen');
        $('#P3').css('border', '5px solid lightyellow');

        let border_colors = ['red', 'blue', 'green', 'yellow'];
        $('#P' + actual_player_json).css('border', '5px solid ' + border_colors[actual_player_json]);

        turn_obj = round_obj['turn_P' + actual_player_json];
        //contador_fases.val(1).change();
    });
    contador_fases.off().on('change', function (e) {
        if (contador_fases.val() === '') {
            return;
        }
        let actual_player_json = parseInt(contador_turnos.val()) - 1; // 0 - 3

        if (parseInt(contador_fases.val()) > 4) {
            contador_turnos.val(parseInt(contador_turnos.val()) + 1).change();
            contador_fases.val(1).change();
            return;
        }

        if (parseInt(contador_fases.val()) < 1) {
            contador_turnos.val(parseInt(contador_turnos.val()) - 1).change();
            contador_fases.val(4).change();
            return;
        }

        let commerce_log_text = jQuery('#commerce_log_text');
        let other_useful_info_text = jQuery('#other_useful_info_text');
        let cereal_quantity_text = parseInt($('#hand_P' + actual_player_json + ' .cereal_quantity').text());
        let mineral_quantity_text = parseInt($('#hand_P' + actual_player_json + ' .mineral_quantity').text());
        let clay_quantity_text = parseInt($('#hand_P' + actual_player_json + ' .clay_quantity').text());
        let wood_quantity_text = parseInt($('#hand_P' + actual_player_json + ' .wood_quantity').text());
        let wool_quantity_text = parseInt($('#hand_P' + actual_player_json + ' .wool_quantity').text());
        let diceroll_div = jQuery('#diceroll');
        let html = '';

        other_useful_info_text.empty();
        switch (parseInt(contador_fases.val()) - 1) {
            case 0:
                phase_obj = turn_obj['start_turn'];

                commerce_log_text.empty();
                for (let i = 0; i < 4; i++) {
                    changeHandObject(i, phase_obj['hand_P' + i]);
                }

                if (game_direction === 'forward') {
                    diceroll_div.text('Diceroll: ' + phase_obj['dice']);

                    if (phase_obj['dice'] == 7) {
                        move_thief(phase_obj['past_thief_terrain'], phase_obj['thief_terrain'], phase_obj['robbed_player'], phase_obj['stolen_material_id'], false);
                    }

                    if (phase_obj['development_card_played'] && phase_obj['development_card_played'].length) {
                        // console.log('SE JUEGA CARTA DE DESAROLLO AL INICIO DEL TURNO' + '| Ronda: ' + contador_rondas.val() + ' Turno: ' + contador_turnos.val())
                        on_development_card_played(phase_obj['development_card_played'][0])
                    }
                } else if (game_direction === 'backward') {
                    phase_obj = turn_obj['commerce_phase'];
                    deleteCaretStyling();

                    for (let i = 0; i < phase_obj.length; i++) {
                        if (phase_obj[i]['trade_offer'] == 'played_card') {
                            off_development_card_played(phase_obj[i]['development_card_played'], actual_player_json)
                        }
                    }
                }
                break;
            case 1:
                phase_obj = turn_obj['commerce_phase'];
                commerce_log_text.empty();

                for (let i = 0; i < phase_obj.length; i++) {

                    if (phase_obj[i]['trade_offer'] == 'None') {
                        // break, porque debería de ser el último de todas maneras

                        // si no hay ningún comercio que ponga PJ: No trade
                        if (phase_obj.length == 1) {
                            html += '<div class="offer"><p>';
                            html += '<span class="commerce_P' + contador_turnos.val() + '">P' + contador_turnos.val() + '</span>: No trade';
                            html += '<p></div>'
                            html += '<hr/>'
                        }

                        break;
                    }
                    if (phase_obj[i]['inviable']) {
                        html += '<div class="offer"><p>';
                        html += '<span class="commerce_P' + contador_turnos.val() + '">P' + contador_turnos.val() + '</span>: Inviable trade';
                        html += '<p></div>'
                        html += '<hr/>'
                        // break, porque no se puede completar el comercio
                        break;
                    }
                    if (phase_obj[i]['harbor_trade']) {
                        let material_chosen_array = ['cereal', 'mineral', 'clay', 'wood', 'wool'];
                        let material_given = material_chosen_array[phase_obj[i]['trade_offer']['gives']];
                        let material_received = material_chosen_array[phase_obj[i]['trade_offer']['receives']];

                        html += '<div class="offer"><p>';
                        html += '<span class="commerce_P' + contador_turnos.val() + '">P' + contador_turnos.val() + '</span>: Harbor trade';
                        html += '<br><span class="gives">Gives: ';
                        html += material_given.charAt(0).toUpperCase() + material_given.slice(1);
                        jQuery('#hand_P' + actual_player_json + ' .' + material_given).removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                        jQuery('#hand_P' + actual_player_json + ' .' + material_given + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');

                        html += '</span>';
                        html += '<br><span class="receives">Receives: ';

                        html += material_received.charAt(0).toUpperCase() + material_received.slice(1);
                        jQuery('#hand_P' + actual_player_json + ' .' + material_received).removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                        jQuery('#hand_P' + actual_player_json + ' .' + material_received + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');

                        html += '</span>';
                        html += '</p></div>';
                        html += '<hr/>';

                        // se actualiza la mano del jugador si avanza, se ignora si va hacia atrás
                        if (game_direction === 'forward') {
                            changeHandObject(actual_player_json, phase_obj[i]['answer'])
                        }

                    } else if (phase_obj[i]['trade_offer'] == 'played_card') {
                        // Se ha jugado una carta de desarrollo

                        html += '<div><p>';
                        html += '<span class="commerce_P' + contador_turnos.val() + '">P' + contador_turnos.val() + '</span>: Played a development card';
                        html += '</p></div>';

                        if (game_direction === 'forward') {
                            on_development_card_played(phase_obj[i]['development_card_played']);
                        }
                    } else {
                        html += '<div class="offer"><p>';
                        html += '<span class="commerce_P' + contador_turnos.val() + '">P' + contador_turnos.val() + '</span>: Offer';
                        html += '<br><span class="gives">';
                        html += 'Gives: ' + 'Cereal: ' + phase_obj[i]['trade_offer']['gives']['cereal'] + ' | ';
                        html += 'Mineral: ' + phase_obj[i]['trade_offer']['gives']['mineral'] + ' | ';
                        html += 'Wool: ' + phase_obj[i]['trade_offer']['gives']['wool'] + ' | ';
                        html += 'Wood: ' + phase_obj[i]['trade_offer']['gives']['wood'] + ' | ';
                        html += 'Clay: ' + phase_obj[i]['trade_offer']['gives']['clay'] + '</span>';

                        html += '<br><span class="receives">';
                        html += 'Receives: ' + 'Cereal: ' + phase_obj[i]['trade_offer']['receives']['cereal'] + ' | ';
                        html += 'Mineral: ' + phase_obj[i]['trade_offer']['receives']['mineral'] + ' | ';
                        html += 'Wool: ' + phase_obj[i]['trade_offer']['receives']['wool'] + ' | ';
                        html += 'Wood: ' + phase_obj[i]['trade_offer']['receives']['wood'] + ' | ';
                        html += 'Clay: ' + phase_obj[i]['trade_offer']['receives']['clay'] + '</span>';
                        html += '</p></div>';

                        html += '<div class="answers">'
                        for (let j = 0; j < phase_obj[i]['answers'].length; j++) {
                            let counteroffer_counter = 0
                            for (let n = 0; n < phase_obj[i]['answers'][j].length; n++) {
                                html += '<div>';

                                if (phase_obj[i]['answers'][j][n]['count'] == 1) {

                                    if (phase_obj[i]['answers'][j][n]['response'] == true) {
                                        html += '<span class="commerce_P' + (parseInt(phase_obj[i]['answers'][j][n]['receiver']) + 1) + '"> P' + (parseInt(phase_obj[i]['answers'][j][n]['receiver']) + 1) + '</span>';
                                        if (phase_obj[i]['answers'][j][n]['completed']) {
                                            html += ': Accepted';

                                            // añadir materiales a mano
                                            let giver_nmbr = phase_obj[i]['answers'][j][n]['giver'];
                                            let receiver_nmbr = phase_obj[i]['answers'][j][n]['receiver'];

                                            let gives_cereal = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['cereal']);
                                            let gives_mineral = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['mineral']);
                                            let gives_clay = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['clay']);
                                            let gives_wood = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['wood']);
                                            let gives_wool = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['wool']);

                                            let receives_cereal = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['cereal']);
                                            let receives_mineral = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['mineral']);
                                            let receives_clay = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['clay']);
                                            let receives_wood = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['wood']);
                                            let receives_wool = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['wool']);

                                            if (game_direction === 'forward') {
                                                changeHandObject(giver_nmbr, {
                                                    'cereal': (parseInt($('#hand_P' + giver_nmbr + ' .cereal_quantity').text()) - gives_cereal + receives_cereal),
                                                    'mineral': (parseInt($('#hand_P' + giver_nmbr + ' .mineral_quantity').text()) - gives_mineral + receives_mineral),
                                                    'clay': (parseInt($('#hand_P' + giver_nmbr + ' .clay_quantity').text()) - gives_clay + receives_clay),
                                                    'wood': (parseInt($('#hand_P' + giver_nmbr + ' .wood_quantity').text()) - gives_wood + receives_wood),
                                                    'wool': (parseInt($('#hand_P' + giver_nmbr + ' .wool_quantity').text()) - gives_wool + receives_wool),
                                                });
                                                changeHandObject(receiver_nmbr, {
                                                    'cereal': (parseInt($('#hand_P' + receiver_nmbr + ' .cereal_quantity').text()) + gives_cereal - receives_cereal),
                                                    'mineral': (parseInt($('#hand_P' + receiver_nmbr + ' .mineral_quantity').text()) + gives_mineral - receives_mineral),
                                                    'clay': (parseInt($('#hand_P' + receiver_nmbr + ' .clay_quantity').text()) + gives_clay - receives_clay),
                                                    'wood': (parseInt($('#hand_P' + receiver_nmbr + ' .wood_quantity').text()) + gives_wood - receives_wood),
                                                    'wool': (parseInt($('#hand_P' + receiver_nmbr + ' .wool_quantity').text()) + gives_wool - receives_wool),
                                                });
                                            }

                                            // añadir caret
                                            if (gives_cereal - receives_cereal < 0) {
                                                $('#hand_P' + giver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_cereal - receives_cereal > 0) {
                                                $('#hand_P' + giver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }

                                            if (gives_mineral - receives_mineral < 0) {
                                                $('#hand_P' + giver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_mineral - receives_mineral > 0) {
                                                $('#hand_P' + giver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }

                                            if (gives_clay - receives_clay < 0) {
                                                $('#hand_P' + giver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_clay - receives_clay > 0) {
                                                $('#hand_P' + giver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }

                                            if (gives_wood - receives_wood < 0) {
                                                $('#hand_P' + giver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_wood - receives_wood > 0) {
                                                $('#hand_P' + giver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }

                                            if (gives_wool - receives_wool < 0) {
                                                $('#hand_P' + giver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_wool - receives_wool > 0) {
                                                $('#hand_P' + giver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }
                                            // fin añadir materiales a mano

                                        } else {
                                            html += ': Accepted | Cannot be completed (lack of materials)';
                                        }
                                    } else {
                                        if (phase_obj[i]['answers'][j][n]['count'] == phase_obj[i]['answers'][j].length) {
                                            html += '<span class="commerce_P' + (parseInt(phase_obj[i]['answers'][j][n]['receiver']) + 1) + '"> P' + (parseInt(phase_obj[i]['answers'][j][n]['receiver']) + 1) + '</span>';
                                            html += ': Denied';
                                        }
                                    }
                                } else {
                                    counteroffer_counter++;
                                    // hay contraoferta
                                    html += '<div class="offer"><p>';
                                    html += '<span class="commerce_P' + (phase_obj[i]['answers'][j][n]['giver'] + 1) + '">P' + (phase_obj[i]['answers'][j][n]['giver'] + 1) + '</span>: Counteroffer';
                                    html += '<br><span class="gives">';
                                    html += 'Gives: ' + 'Cereal: ' + phase_obj[i]['answers'][j][n]['trade_offer']['gives']['cereal'] + ' | ';
                                    html += 'Mineral: ' + phase_obj[i]['answers'][j][n]['trade_offer']['gives']['mineral'] + ' | ';
                                    html += 'Wool: ' + phase_obj[i]['answers'][j][n]['trade_offer']['gives']['wool'] + ' | ';
                                    html += 'Wood: ' + phase_obj[i]['answers'][j][n]['trade_offer']['gives']['wood'] + ' | ';
                                    html += 'Clay: ' + phase_obj[i]['answers'][j][n]['trade_offer']['gives']['clay'] + '</span>';

                                    html += '<br><span class="receives">';
                                    html += 'Receives: ' + 'Cereal: ' + phase_obj[i]['answers'][j][n]['trade_offer']['receives']['cereal'] + ' | ';
                                    html += 'Mineral: ' + phase_obj[i]['answers'][j][n]['trade_offer']['receives']['mineral'] + ' | ';
                                    html += 'Wool: ' + phase_obj[i]['answers'][j][n]['trade_offer']['receives']['wool'] + ' | ';
                                    html += 'Wood: ' + phase_obj[i]['answers'][j][n]['trade_offer']['receives']['wood'] + ' | ';
                                    html += 'Clay: ' + phase_obj[i]['answers'][j][n]['trade_offer']['receives']['clay'] + '</span>';
                                    html += '</p></div>';


                                    if (phase_obj[i]['answers'][j][n]['response'] == true) {

                                        html += '<span class="answers commerce_P' + (parseInt(phase_obj[i]['answers'][j][n]['receiver']) + 1) + '"> P' + (parseInt(phase_obj[i]['answers'][j][n]['receiver']) + 1) + '</span>';
                                        if (phase_obj[i]['answers'][j][n]['completed']) {
                                            html += ': Accepted';

                                            // añadir materiales a mano
                                            let giver_nmbr = phase_obj[i]['answers'][j][n]['giver'];
                                            let receiver_nmbr = phase_obj[i]['answers'][j][n]['receiver'];

                                            let gives_cereal = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['cereal']);
                                            let gives_mineral = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['mineral']);
                                            let gives_clay = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['clay']);
                                            let gives_wood = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['wood']);
                                            let gives_wool = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['gives']['wool']);

                                            let receives_cereal = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['cereal']);
                                            let receives_mineral = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['mineral']);
                                            let receives_clay = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['clay']);
                                            let receives_wood = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['wood']);
                                            let receives_wool = parseInt(phase_obj[i]['answers'][j][n]['trade_offer']['receives']['wool']);


                                            if (game_direction === 'forward') {
                                                changeHandObject(giver_nmbr, {
                                                    'cereal': (parseInt($('#hand_P' + giver_nmbr + ' .cereal_quantity').text()) - gives_cereal + receives_cereal),
                                                    'mineral': (parseInt($('#hand_P' + giver_nmbr + ' .mineral_quantity').text()) - gives_mineral + receives_mineral),
                                                    'clay': (parseInt($('#hand_P' + giver_nmbr + ' .clay_quantity').text()) - gives_clay + receives_clay),
                                                    'wood': (parseInt($('#hand_P' + giver_nmbr + ' .wood_quantity').text()) - gives_wood + receives_wood),
                                                    'wool': (parseInt($('#hand_P' + giver_nmbr + ' .wool_quantity').text()) - gives_wool + receives_wool),
                                                });
                                                changeHandObject(receiver_nmbr, {
                                                    'cereal': (parseInt($('#hand_P' + receiver_nmbr + ' .cereal_quantity').text()) + gives_cereal - receives_cereal),
                                                    'mineral': (parseInt($('#hand_P' + receiver_nmbr + ' .mineral_quantity').text()) + gives_mineral - receives_mineral),
                                                    'clay': (parseInt($('#hand_P' + receiver_nmbr + ' .clay_quantity').text()) + gives_clay - receives_clay),
                                                    'wood': (parseInt($('#hand_P' + receiver_nmbr + ' .wood_quantity').text()) + gives_wood - receives_wood),
                                                    'wool': (parseInt($('#hand_P' + receiver_nmbr + ' .wool_quantity').text()) + gives_wool - receives_wool),
                                                });
                                            }

                                            // añadir caret
                                            if (gives_cereal - receives_cereal < 0) {
                                                $('#hand_P' + giver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_cereal - receives_cereal > 0) {
                                                $('#hand_P' + giver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .cereal .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .cereal').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }

                                            if (gives_mineral - receives_mineral < 0) {
                                                $('#hand_P' + giver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_mineral - receives_mineral > 0) {
                                                $('#hand_P' + giver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .mineral .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .mineral').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }

                                            if (gives_clay - receives_clay < 0) {
                                                $('#hand_P' + giver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_clay - receives_clay > 0) {
                                                $('#hand_P' + giver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .clay .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .clay').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }

                                            if (gives_wood - receives_wood < 0) {
                                                $('#hand_P' + giver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_wood - receives_wood > 0) {
                                                $('#hand_P' + giver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .wood .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .wood').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }

                                            if (gives_wool - receives_wool < 0) {
                                                $('#hand_P' + giver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + giver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                                $('#hand_P' + receiver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
                                                $('#hand_P' + receiver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
                                            } else if (gives_wool - receives_wool > 0) {
                                                $('#hand_P' + giver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down')
                                                $('#hand_P' + giver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('decreased')
                                                $('#hand_P' + receiver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
                                                $('#hand_P' + receiver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                                            } else {
                                                $('#hand_P' + giver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + giver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                                $('#hand_P' + receiver_nmbr + ' .wool .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus')
                                                $('#hand_P' + receiver_nmbr + ' .wool').removeClass(['increased', 'neutral', 'decreased']).addClass('neutral')
                                            }
                                            // fin añadir materiales a mano

                                        } else {
                                            html += ': Accepted | Cannot be completed (lack of materials)';
                                        }
                                        // cerramos todos los divs de contraoferta
                                        for (let m = 0; m < counteroffer_counter; m++) {
                                            html += '</div>'
                                        }

                                    } else {
                                        if (phase_obj[i]['answers'][j][n]['count'] == phase_obj[i]['answers'][j].length) {
                                            // se niega la oferta
                                            html += '<span class="answers commerce_P' + (parseInt(phase_obj[i]['answers'][j][n]['receiver']) + 1) + '"> P' + (parseInt(phase_obj[i]['answers'][j][n]['receiver']) + 1) + '</span>';
                                            html += ': Denied';
                                            // cerramos todos los divs de contraoferta
                                            for (let m = 0; m < counteroffer_counter; m++) {
                                                html += '</div>'
                                            }
                                        } else {
                                            // se niega la oferta pero se ofrece contraoferta (se comprueba viendo si la cuenta es la misma que la longitud del array)
                                            counteroffer_counter++;
                                            html += '<div class="answers">'
                                        }
                                    }

                                }
                            }
                            html += '</p></div>'
                        }
                        html += '</div>' // div.answers
                        html += '</div>'
                        html += '<hr/>'

                    } // end if else
                } // end for
                commerce_log_text.append(html)

                if (game_direction === 'backward') {
                    phase_obj = turn_obj['build_phase'];
                    for (let i = 0; i < phase_obj.length; i++) {
                        if (phase_obj[i]['building'] !== null) {
                            switch (phase_obj[i]['building']) {
                                case 'town':
                                    if (phase_obj[i]['finished']) {
                                        let node = jQuery('#node_' + phase_obj[i]['node_id']);
                                        paint_it_player_color(null, node);
                                        node.html('');

                                        changeHandObject(actual_player_json, {
                                            'cereal': cereal_quantity_text + 1,
                                            'mineral': mineral_quantity_text + 0,
                                            'clay': clay_quantity_text + 1,
                                            'wood': wood_quantity_text + 1,
                                            'wool': wool_quantity_text + 1,
                                        });
                                        //                                        let str = 'node: ' + phase_obj[i]['node_id'] + ' | ' + 'type: ' + 'T' + '\r\n';
                                        //                                            textarea.text(textarea.text() + str);
                                    }
                                    break;
                                case 'city':
                                    if (phase_obj[i]['finished']) {
                                        let node = jQuery('#node_' + phase_obj[i]['node_id']);
                                        node.html('<i class="fa-solid fa-house"></i>');

                                        changeHandObject(actual_player_json, {
                                            'cereal': cereal_quantity_text + 2,
                                            'mineral': mineral_quantity_text + 3,
                                            'clay': clay_quantity_text + 0,
                                            'wood': wood_quantity_text + 0,
                                            'wool': wool_quantity_text + 0,
                                        });

                                        //                                        let str = 'node: ' + phase_obj[i]['node_id'] + ' | ' + 'type: ' + 'C' + '\r\n';
                                        //                                            textarea.text(textarea.text() + str);
                                    }
                                    break;
                                case 'road':
                                    if (phase_obj[i]['finished']) {
                                        let road = '';
                                        if (phase_obj[i]['node_id'] < phase_obj[i]['road_to']) {
                                            road = jQuery('#road_' + phase_obj[i]['node_id'] + '_' + phase_obj[i]['road_to']);
                                        } else {
                                            road = jQuery('#road_' + phase_obj[i]['road_to'] + '_' + phase_obj[i]['node_id']);
                                        }
                                        paint_it_player_color(null, road);

                                        changeHandObject(actual_player_json, {
                                            'cereal': cereal_quantity_text + 0,
                                            'mineral': mineral_quantity_text + 0,
                                            'clay': clay_quantity_text + 1,
                                            'wood': wood_quantity_text + 1,
                                            'wool': wool_quantity_text + 0,
                                        });
                                        //                                        let str = 'node: ' + phase_obj[i]['node_id'] + ' | ' + 'road_to: ' + phase_obj[i]['road_to'] + ' | ' + 'type: ' + 'R' + '\r\n'
                                        //                                            textarea.text(textarea.text() + str)
                                    }
                                    break;
                                case 'card':
                                    if (phase_obj[i]['finished']) {
                                        let card_div = jQuery(jQuery('#hand_P' + (actual_player_json) + ' .bottom_hand_row').children()[phase_obj[i]['card_effect']])
                                        let card_div_quantity = card_div.find('.' + card_div.data('id') + '_quantity')
                                        let card_div_increment = card_div.find('.increment')

                                        card_div_increment.removeClass(['fa-caret-up', 'fa-caret-down', 'fa-minus']);
                                        card_div.removeClass(['increased', 'decreased', 'neutral']);

                                        card_div_quantity.text(parseInt(card_div_quantity.text()) - 1)

                                        changeHandObject(actual_player_json, {
                                            'cereal': cereal_quantity_text + 1,
                                            'mineral': mineral_quantity_text + 1,
                                            'clay': clay_quantity_text + 0,
                                            'wood': wood_quantity_text + 0,
                                            'wool': wool_quantity_text + 1,
                                        });
                                    }
                                    break;
                                case 'played_card':
                                    for (let i = 0; i < phase_obj.length; i++) {
                                        if (phase_obj[i]['development_card_played']) {
                                            off_development_card_played(phase_obj[i]['development_card_played'], actual_player_json)
                                        }
                                    }
                                    break;
                                default:
                                    break;
                            }
                        }
                    }
                }
                break;
            case 2:
                phase_obj = turn_obj['build_phase'];

                for (let i = 0; i < phase_obj.length; i++) {
                    if (phase_obj[i]['building'] !== null) {
                        html += '<div>';
                        switch (phase_obj[i]['building']) {
                            case 'town':
                                if (phase_obj[i]['finished']) {
                                    let node = jQuery('#node_' + phase_obj[i]['node_id']);
                                    paint_it_player_color(actual_player_json, node);
                                    node.html('<i class="fa-solid fa-house"></i>');

                                    if (game_direction === 'forward') {
                                        changeHandObject(actual_player_json, {
                                            'cereal': cereal_quantity_text - 1,
                                            'mineral': mineral_quantity_text - 0,
                                            'clay': clay_quantity_text - 1,
                                            'wood': wood_quantity_text - 1,
                                            'wool': wool_quantity_text - 1,
                                        });
                                    }

                                    html += 'Building: Town | ' + 'Node: ' + phase_obj[i]['node_id'];
                                }
                                break;
                            case 'city':
                                if (phase_obj[i]['finished']) {
                                    let node = jQuery('#node_' + phase_obj[i]['node_id']);
                                    node.html('<i class="fa-solid fa-chess-rook"></i>');

                                    if (game_direction === 'forward') {
                                        changeHandObject(actual_player_json, {
                                            'cereal': cereal_quantity_text - 2,
                                            'mineral': mineral_quantity_text - 3,
                                            'clay': clay_quantity_text - 0,
                                            'wood': wood_quantity_text - 0,
                                            'wool': wool_quantity_text - 0,
                                        });
                                    }

                                    html += 'Building: City | ' + 'Node: ' + phase_obj[i]['node_id'];
                                }
                                break;
                            case 'road':
                                if (phase_obj[i]['finished']) {
                                    let road = '';
                                    if (phase_obj[i]['node_id'] < phase_obj[i]['road_to']) {
                                        road = jQuery('#road_' + phase_obj[i]['node_id'] + '_' + phase_obj[i]['road_to']);
                                    } else {
                                        road = jQuery('#road_' + phase_obj[i]['road_to'] + '_' + phase_obj[i]['node_id']);
                                    }
                                    paint_it_player_color(actual_player_json, road);

                                    if (game_direction === 'forward') {
                                        changeHandObject(actual_player_json, {
                                            'cereal': cereal_quantity_text - 0,
                                            'mineral': mineral_quantity_text - 0,
                                            'clay': clay_quantity_text - 1,
                                            'wood': wood_quantity_text - 1,
                                            'wool': wool_quantity_text - 0,
                                        });
                                    }
                                    html += 'Building: Road | ' + 'Node: ' + phase_obj[i]['node_id'] + ' | ' + 'Road_to: ' + phase_obj[i]['road_to'];
                                }
                                break;
                            case 'card':
                                let card_effects = ['Knight', 'Victory Point', 'Road Building', 'Year of plenty', 'Monopoly'];
                                if (phase_obj[i]['finished']) {
                                    let card_div = jQuery(jQuery('#hand_P' + actual_player_json + ' .bottom_hand_row').children()[phase_obj[i]['card_effect']])
                                    let card_div_quantity = card_div.find('.' + card_div.data('id') + '_quantity')
                                    let card_div_increment = card_div.find('.increment')

                                    // Se añade la clase caret-up y el color rojo para marcar el aumento de cartas
                                    card_div_increment.addClass('fa-caret-up');
                                    card_div.addClass('increased');

                                    if (game_direction === 'forward') {
                                        changeHandObject(actual_player_json, {
                                            'cereal': cereal_quantity_text - 1,
                                            'mineral': mineral_quantity_text - 1,
                                            'clay': clay_quantity_text - 0,
                                            'wood': wood_quantity_text - 0,
                                            'wool': wool_quantity_text - 1,
                                        });
                                        card_div_quantity.text(parseInt(card_div_quantity.text()) + 1)
                                    }
                                    html += 'Building: Card | ' + 'Card Type: ' + card_effects[phase_obj[i]['card_effect']];
                                }
                                break;
                            case 'played_card':
                                if (phase_obj[i]['development_card_played'] && game_direction === 'forward') {
                                    on_development_card_played(phase_obj[i]['development_card_played'])
                                }
                                break;
                            default:
                                break;
                        }
                        html += '</div>';
                    }
                }
                other_useful_info_text.append(html);
                if (game_direction === 'backward') {
                    phase_obj = turn_obj['end_turn'];

                    if (phase_obj['development_card_played'] && phase_obj['development_card_played'].length) {
                        // console.log('SE JUEGA CARTA DE DESAROLLO AL INICIO DEL TURNO' + '| Ronda: ' + contador_rondas.val() + ' Turno: ' + contador_turnos.val())
                        // console.log(phase_obj)
                        off_development_card_played(phase_obj['development_card_played'][0], actual_player_json)
                    }
                }
                break;
            case 3:
                phase_obj = turn_obj['end_turn'];
                let winner = '';

                if (phase_obj['development_card_played'] && phase_obj['development_card_played'].length && game_direction === 'forward') {
                    // console.log('SE JUEGA CARTA DE DESAROLLO AL FINAL DEL TURNO' + '| Ronda: ' + contador_rondas.val() + ' Turno: ' + contador_turnos.val())
                    // console.log(phase_obj)
                    on_development_card_played(phase_obj['development_card_played'][0])
                }

                for (let i = 0; i < 4; i++) {
                    jQuery('#puntos_victoria_J' + (i + 1)).text(phase_obj['victory_points']['J' + i])
                    if (parseInt(phase_obj['victory_points']['J' + i]) >= 10) {
                        winner = 'J' + (i + 1) + ' GANA'
                    }
                }

                if (winner !== '' && contador_turnos.val() >= 4) {
                    alert(winner);
                }

                if (game_direction === 'backward') {
                    let round = game_obj['game']['round_' + (contador_rondas.val() - 1)];
                    let next_player = actual_player_json + 1; // 1 - 4

                    if (next_player > 3) {
                        next_player = 0;
                        round = game_obj['game']['round_' + contador_rondas.val()]; // Se pasa de ronda y se le devuelve el turno al jugador 0
                    }

                    let next_turn_obj = round['turn_P' + next_player];
                    let next_phase_obj = next_turn_obj['start_turn'];
                    let diceroll = turn_obj['start_turn']['dice'];
                    diceroll_div.text('Diceroll: ' + diceroll);

                    if (next_phase_obj['development_card_played'] && next_phase_obj['development_card_played'].length) {
                        off_development_card_played(next_phase_obj['development_card_played'][0], next_player)
                    }

                    if (next_phase_obj['dice'] == 7) {
                        unmove_thief(next_phase_obj['past_thief_terrain'], next_phase_obj['thief_terrain'], next_player, next_phase_obj['robbed_player'], next_phase_obj['stolen_material_id'], false);
                    }
                }
                break;

            default:
                break;
        } // switch
    });


    //-------------------------------------------------
    ronda_previa_btn.off().on('click', function (e) {
        if (contador_turnos.val() == 1) {
            turno_previo_btn.click();
        }
        while (contador_turnos.val() > 1) {
            turno_previo_btn.click();
        }
    });
    ronda_siguiente_btn.off().on('click', function (e) {
        if (contador_turnos.val() == 1) {
            turno_siguiente_btn.click();
        }
        while (contador_turnos.val() > 1) {
            turno_siguiente_btn.click();
        }
    });

    //-------------------------------------------------
    turno_previo_btn.off().on('click', function (e) {
        if (contador_fases.val() == 1) {
            fase_previa_btn.click();
        }
        while (contador_fases.val() > 1) {
            fase_previa_btn.click();
        }
    });
    turno_siguiente_btn.off().on('click', function (e) {
        if (contador_fases.val() == 1) {
            fase_siguiente_btn.click();
        }
        while (contador_fases.val() > 1) {
            fase_siguiente_btn.click();
        }
    });

    //-------------------------------------------------
    fase_previa_btn.off().on('click', function (e) {
        game_direction = 'backward';
        let value = parseInt(contador_fases.val());
        contador_fases.val(value - 1).change();
    });
    fase_siguiente_btn.off().on('click', function (e) {
        game_direction = 'forward';
        let value = parseInt(contador_fases.val());
        contador_fases.val(value + 1).change();
    });

    millis_for_play.off().on('change', function (e) {
        jQuery('#millis_seleccionados').val(millis_for_play.val());
    });

    play_btn.off().on('click', function (e) {
        let _this = $(this);
        let _i = _this.find('i');

        if (_i.hasClass('fa-play')) {
            _i.removeClass('fa-play').addClass('fa-pause');

            _this.attr('title', 'Pause')

            //                    playIntervalNumber = setInterval(function() {
            //                        turno_siguiente_btn.click()
            //                    }, 500)
            playIntervalNumber = setInterval(function () {
                fase_siguiente_btn.click()
            }, millis_for_play.val())

        } else {
            _this.attr('title', 'Play')

            _i.removeClass('fa-pause').addClass('fa-play');
            clearInterval(playIntervalNumber)
        }

        $(function () {
            _this.tooltip('dispose')
            _this.tooltip()
        })
    })
}

function changeHandObject(player, hand_obj) {
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

    //TODO: Mejora a futuro: Debería de alguna manera mostrar que materiales se han actualizado. Si son iguales no deberían de recalcarse
    materials.forEach(function (material) {
        $('#hand_P' + player + ' .' + material + '_quantity').text(hand_obj[material]).change();
    });
    //    $('#hand_P' + player + ' .cereal_quantity').text(hand_obj['cereal']).change();
    //    $('#hand_P' + player + ' .clay_quantity').text(hand_obj['clay']).change();
    //    $('#hand_P' + player + ' .wood_quantity').text(hand_obj['wood']).change();
    //    $('#hand_P' + player + ' .wool_quantity').text(hand_obj['wool']).change();
    //    $('#hand_P' + player + ' .mineral_quantity').text(hand_obj['mineral']).change();
}

// utilities
function paint_it_player_color(player, object_to_paint) {
    object_to_paint = jQuery(object_to_paint);
    object_to_paint.css('color', 'black')
    switch (player) {
        case 0:
            object_to_paint.css('background', 'lightcoral') //.css('border', '1px solid black');
            break;
        case 1:
            object_to_paint.css('background', 'lightblue') //.css('border', '1px solid black');
            break;
        case 2:
            object_to_paint.css('background', 'lightgreen') //.css('border', '1px solid black');
            break;
        case 3:
            object_to_paint.css('background', 'lightyellow') //.css('border', '1px solid black');
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
        $('#hand_P' + actual_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus');
        $('#hand_P' + actual_player + ' .' + materials[stolen_material_id]).removeClass(['increased', 'neutral', 'decreased']).addClass('neutral');
    } else {
        $('#hand_P' + actual_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
        $('#hand_P' + actual_player + ' .' + materials[stolen_material_id]).removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
        $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
        $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id]).removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
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

    //    if (actual_player == robbed_player) {
    //        $('#hand_P' + robbing_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-minus');
    //        $('#hand_P' + robbing_player + ' .' + materials[stolen_material_id]).removeClass(['increased', 'neutral', 'decreased']).addClass('neutral');
    //    } else {
    //        $('#hand_P' + robbing_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
    //        $('#hand_P' + robbing_player + ' .' + materials[stolen_material_id]).removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
    //        $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id] + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
    //        $('#hand_P' + robbed_player + ' .' + materials[stolen_material_id]).removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
    //    }
}

function on_development_card_played(card) {
    // TODO: Mejora a futuro: mostrar dentro de "mayor ejercito" o algún lugar, cantidad de caballeros que tiene activos cada jugador.
    // TODO: Mejora a futuro: limitar altura de jQuery('#other_useful_info_text')
    let materials = ['cereal', 'mineral', 'clay', 'wood', 'wool'];

    let contador_turnos = jQuery('#contador_turnos');
    let other_useful_info_text = jQuery('#other_useful_info_text');
    let actual_player = $('#contador_turnos').val() - 1;
    let quantity = jQuery('#hand_P' + (jQuery('#contador_turnos').val() - 1) + ' .' + card['played_card'] + '_quantity');

    jQuery('#hand_P' + (contador_turnos.val() - 1) + ' .' + card['played_card']).removeClass(['increased', 'neutral', 'decreased']).addClass('decreased');
    jQuery('#hand_P' + (contador_turnos.val() - 1) + ' .' + card['played_card'] + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-down');
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
                jQuery('#hand_P' + actual_player + ' .' + material).removeClass(['increased', 'neutral', 'decreased']).addClass('increased');
                jQuery('#hand_P' + actual_player + ' .' + material + ' .increment').removeClass(['fa-caret-up', 'fa-minus', 'fa-caret-down']).addClass('fa-caret-up');
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
    jQuery('.increment').removeClass(['fa-caret-up', 'fa-caret-down', 'fa-minus']);
    jQuery('.increment').parent().removeClass(['increased', 'decreased', 'neutral']);
}

function setup() {
    //            nodeSetup();
    terrainSetup();
    addSetupBuildings();
}

// init()
window.addEventListener('load', function () {
    init_events();
}, false);
