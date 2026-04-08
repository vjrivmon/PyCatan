# Auditoría Integral del Simulador de Catán — Changelog

## Resumen

Se ha realizado una auditoría exhaustiva del simulador de Catán que ha identificado y corregido **12 bugs de backend** y **10 mejoras/correcciones de frontend**. Todos los cambios han sido verificados con los 40 tests unitarios existentes (100% passing) y con el sistema de verificación automática `debug_server.py` que compara cada estado del frontend contra el JSON fuente sin discrepancias.

---

## BUGS DEL BACKEND (Generación de Trazas JSON)

### B1. Agentes modificaban `self.hand` durante la planificación de trades (CRÍTICO)

**Fichero:** `Managers/GameManager.py`

**Qué ocurría:** Casi todos los agentes (`AlexPelochoJaimeAgent`, `CarlesZaidaAgent`, `CrabisaAgent`, `SigmaAgent`, `AdrianHerasAgent`, `PabloAleixAlexAgent`, `TristanAgent`, `EdoAgent`) llamaban a `self.hand.remove_material()` dentro de sus métodos `on_commerce_phase()` y `on_trade_offer()` para calcular qué materiales ofrecer. Como `self.hand` es **el mismo objeto** que `player['resources']` en el GameManager (se sincronizan con `player['player'].hand = player['resources']`), estas modificaciones alteraban el **estado real del juego** durante la fase de planificación.

**Consecuencia:** Cuando un agente intentaba ofrecer un trade, sus materiales se descontaban ANTES de que el GameManager verificara si el trade era viable. Si el GameManager determinaba que era "inviable" (el jugador ya no tenía los recursos porque los había "gastado" planificando), los materiales desaparecían del juego sin que ningún intercambio se realizara. El JSON resultante mostraba `"inviable": true` pero las manos reflejaban los recursos ya descontados.

**Ejemplo concreto (game_8.json R0 T0):** P0 tenía (cereal=0, mineral=1, clay=1, wood=3, wool=2). Ofrecía clay=1+wood=1+wool=2. El trade se marcaba "inviable", pero la mano quedaba en (0, 1, 0, 2, 0) — los recursos desaparecieron.

**Solución:** Se crearon dos métodos `_save_all_hands()` y `_restore_all_hands()` en GameManager que guardan una copia profunda (`deepcopy`) de las manos de todos los jugadores ANTES de cada llamada a un agente, y las restauran DESPUÉS. Esto protege el estado del juego de cualquier modificación que el agente haga durante su planificación. Se aplica a: `call_to_agent_on_commerce_phase`, `call_to_agent_on_build_phase`, `call_to_agent_on_turn_start`, `call_to_agent_on_turn_end`, y `_on_tradeoffer_response`.

**Nota sobre los agentes:** Los agentes NO se han modificado individualmente porque son código de estudiantes y hay 8+ agentes afectados. La solución centralizada en GameManager es más robusta y protege contra futuros agentes que cometan el mismo error.

---

### B2. Auto-robo con el ladrón (CRÍTICO)

**Fichero:** `Managers/GameManager.py` — método `move_thief()`

**Qué ocurría:** Cuando un jugador tiraba un 7 y movía al ladrón, el método `on_moving_thief()` del agente podía devolver su propio ID como jugador adyacente al que robar. El código no tenía ninguna validación para impedir que un jugador se robara a sí mismo.

**Consecuencia:** En `_steal_from_player()`, tanto `player_obj` como `actual_player_obj` apuntaban al mismo jugador. Se le quitaba un material y se le sumaba el mismo material, pero el JSON registraba `robbed_player == actual_player`, confundiendo al frontend.

**Ejemplo concreto (game_8.json R2 T2):** `actual_player=2, robbed_player=2` — P2 se robaba a sí mismo.

**Solución:** Se añadió validación en `move_thief()`: si `adjacent_player == current_player`, se busca automáticamente otro jugador adyacente al hexágono para robar. Si no hay otro jugador, no se roba a nadie.

---

### B3. Descarte con ladrón: floor(n/2) en vez de ceil(n/2) (CRÍTICO)

**Fichero:** `Managers/GameManager.py` — método `check_if_thief_is_called()`

**Qué ocurría:** Cuando sale un 7 y un jugador tiene más de 7 materiales, debe descartar la mitad redondeada hacia abajo (regla oficial de Catán: descartas floor(n/2) cartas, te quedas con ceil(n/2)). El código usaba `max_hand = math.floor(total / 2)`, lo que significaba que el jugador se quedaba con floor(n/2) cartas — una carta MENOS de lo debido.

**Ejemplo:** Con 11 cartas → floor(11/2)=5, el jugador se quedaba con 5. Debería quedarse con ceil(11/2)=6.

**Solución:** Cambio de `math.floor(total / 2)` a `math.ceil(total / 2)`.

---

### B4. `set_actual_player` no sincronizaba `agent_manager.actual_player` (CRÍTICO)

**Fichero:** `Managers/GameManager.py` — método `set_actual_player()`

**Qué ocurría:** `set_actual_player()` solo establecía `self.turn_manager.actual_player` pero NO `self.agent_manager.actual_player`. Luego, `_steal_from_player()` leía `self.agent_manager.actual_player` para saber quién recibía el material robado. Si `agent_manager.actual_player` no estaba sincronizado, el material robado se asignaba al jugador incorrecto.

**Solución:** Se añadió `self.agent_manager.actual_player = player_id` dentro de `set_actual_player()`.

---

### B5. Trade ratio no almacenado en JSON para trades de puerto/banca

**Fichero:** `Managers/GameManager.py` — método `on_commerce_response()`

**Qué ocurría:** Cuando un jugador comerciaba con el puerto o la banca (4:1, 3:1, 2:1), el ratio se calculaba internamente pero NO se almacenaba en el JSON. El frontend no podía saber si era un trade 4:1 o 2:1.

**Solución:** Se añade `commerce_phase_object['trade_ratio'] = trade_ratio` al JSON de cada harbor trade.

---

### B6. Giver/Receiver invertido en trades entre jugadores (CRÍTICO)

**Fichero:** `Managers/GameManager.py` — método `send_trade_to_everyone()`

**Qué ocurría:** En `_trade_with_player(trade_offer, giver, receiver)`, la semántica es: `giver` pierde `trade_offer.gives` y gana `trade_offer.receives`. Pero el código pasaba los parámetros invertidos:
- Para ofertas normales (count impar): se pasaba `(receiver, giver)` en vez de `(giver, receiver)`
- Para contra-ofertas (count par): se pasaba `(giver, receiver)` en vez de `(receiver, giver)`

**Consecuencia:** Los materiales se transferían al jugador equivocado. El que ofrecía recibía lo que debía dar, y viceversa.

**Solución:** Se invirtieron ambas ramas para que coincidan con la semántica correcta.

---

### B7. Doble descarte con el ladrón: agentes corrompían estado en `on_having_more_than_7` (CRÍTICO)

**Fichero:** `Managers/GameManager.py` — método `check_if_thief_is_called()`

**Qué ocurría:** Cuando salía un 7, `on_having_more_than_7_materials_when_thief_is_called()` se llamaba en cada agente con >7 materiales. Todos los agentes (excepto RandomAgent) llamaban `self.hand.remove_material()` dentro de ese método para descartar materiales. Como `self.hand` ES `obj['resources']` (mismo objeto), esto **modificaba la mano real** del jugador. Después, el GameManager usaba el total ya reducido para calcular `max_hand = ceil(total/2)` y descartaba AÚN MÁS materiales.

**Ejemplo:** Jugador con 11 materiales → agente descarta hasta 7 → GameManager calcula ceil(7/2)=4 → descarta de 7 a 4. Resultado: 4 materiales en vez de los 6 correctos (ceil(11/2)).

**Solución:** Se envuelve la llamada al agente con `_save_all_hands()` / `_restore_all_hands()`. Tras restaurar, se calcula el descarte con el total original. Ningún agente puede ya corromper el estado durante el descarte.

---

### B8. `build_road` permitía construir a través de un poblado/ciudad rival

**Fichero:** `Classes/Board.py` — método `build_road()`

**Qué ocurría:** Un jugador podía construir una carretera partiendo desde un nodo que pertenecía a un rival, si había una carretera propia adyacente. En Catán, un poblado/ciudad rival BLOQUEA el paso de carreteras.

**Solución:** Se añadió validación: si el nodo de inicio pertenece a otro jugador (`!= -1 && != player`), se rechaza la construcción.

---

### B8. DevelopmentCard sin atributo `id`, DevelopmentDeck sin `current_index`/`shuffle_deck()`

**Fichero:** `Classes/DevelopmentCards.py`

**Qué ocurría:** La clase `DevelopmentCard` no tenía atributo `id`. La clase `DevelopmentDeck` no tenía `current_index` ni el método `shuffle_deck()`. `DevelopmentCardsHand.add_card()` no validaba que el parámetro fuera realmente una `DevelopmentCard`, aceptando strings o None.

**Solución:**
- `DevelopmentCard` ahora tiene `id` y acepta constructores de 2 o 3 argumentos
- `DevelopmentDeck` tiene `current_index` (se resetea a 0 tras construcción) y `shuffle_deck()`
- `add_card()` solo acepta instancias de `DevelopmentCard`

---

### B9. `Materials.has_more()` aceptaba valores negativos

**Fichero:** `Classes/Materials.py`

**Qué ocurría:** `has_more(Materials(1, 0, -1, 1, 1))` devolvía `True` porque -1 <= 4 cumplía `all(materials <= self)`. Esto podía hacer que trades con cantidades negativas se consideraran válidos.

**Solución:** Se añade una comprobación `if materials.check_negative(): return False` antes de la comparación.

---

## MEJORAS DEL FRONTEND (Visualizador)

### F1. Navegación hacia atrás no actualizaba recursos
Se añadió `applyCurrentPhase()` después de `replayLogUpToCurrent()` en TODAS las funciones de navegación (`prevPhase`, `prevRound`, `goToStart`, `goToEnd`, `nextRound`). Se ajustó `replayLogUpToCurrent()` para parar una fase antes de la actual, evitando duplicación de logs.

### F2. Logs y panel de comercio no se limpiaban entre turnos
`clearEventLog()` ahora también limpia `#commerce-container`. El panel de comercio se resetea al inicio de cada turno.

### F3. Separadores de turno
Se insertan separadores visuales "Turno de J1 (Rojo) — Ronda 3" al inicio de cada turno, tanto en reproducción normal como en replay.

### F4. Emojis reemplazados por imágenes
Nueva función `resIcon()` genera tags `<img>` inline usando los assets existentes en `nuevos_assets/materiales/`. Se usa en `formatTradeResources()`, `formatTradeOffer()` y en todos los logs de comercio.

### F5. UI de comercio mejorada
- Se muestra quién ofrece y a quién
- Las cantidades de puerto/banca se muestran (ej: "Da: Madera x4 → Recibe: Cereal x1")
- "Inviable" se explica claramente: "no tiene recursos suficientes"
- "Acepta (sin efecto)" → "Acepta pero recursos insuficientes para ejecutar"
- Contra-ofertas explicadas con texto descriptivo

### F6. Indicadores de cambio de recursos persistentes
Los badges +1/-1 ya NO desaparecen. Se quedan hasta el siguiente cambio de estado. Ganancias por dados = verde, por comercio = azul, pérdidas = rojo.

### F7. Indicador de jugador activo por opacidad
Los jugadores inactivos se muestran al 45% de opacidad (80% al hover). El jugador activo se muestra con opacidad completa y borde dorado sutil.

### F8. Cartas de desarrollo agrupadas
En vez de repetir iconos idénticos, se muestra un solo icono con "x3" al lado.

### F9. Estilos de log con temática Catán
Colores cálidos (dorado para dados, púrpura para ladrón, marrón para construcción, verde bosque para comercio). Secciones diferenciadas: "Registro de Eventos" marrón, "Comercios" verde.

### F10. Slider de velocidad eliminado
Se usaba velocidad fija de 1s. El slider causaba problemas al cambiar velocidad durante reproducción.

---

## Sistema de Verificación

Se ha creado `Game/debug_server.py`: un servidor Python que sirve el visualizador e inyecta un script de verificación que compara en tiempo real cada estado del frontend contra el JSON fuente. El sistema verifica que las manos de los 4 jugadores coinciden en cada cambio de fase. La traza `Game/test_game_fixed.json` (186 rondas) ha pasado la verificación completa sin discrepancias.

---

## Tests

- **40 tests pasando** (0 fallos)
- Test `test_check_if_thief_is_called` actualizado para reflejar el fix B3 (ceil en vez de floor)
- Test `test_build_road` ahora pasa correctamente (antes fallaba por B7)
