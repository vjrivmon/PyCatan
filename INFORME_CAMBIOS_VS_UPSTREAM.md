# Informe de Cambios — Fork (vjrivmon) vs Upstream (jaumejordan)

Este documento detalla TODOS los cambios realizados en el fork respecto al repositorio original de Jaume, explicando cada bug encontrado, su causa raíz, y cómo se solucionó.

---

## Pregunta: ¿El `Game/index.html` sustituye al `Visualizer/index.html` anterior?

**Sí.** La carpeta `Game/` es el nuevo visualizador completo que sustituye a `Visualizer/`. El visualizador antiguo (`Visualizer/`) usaba jQuery + Bootstrap + un JS de ~4600 líneas. El nuevo (`Game/`) es vanilla JS/CSS/HTML puro, sin dependencias, con assets mejorados (`nuevos_assets/`).

Ficheros del nuevo visualizador:
- `Game/index.html` — Estructura HTML
- `Game/game.js` — Toda la lógica (~2000 líneas)
- `Game/styles.css` — Todos los estilos
- `Game/debug_server.py` — Servidor de verificación
- `Game/trace_auditor.py` — Auditor offline de trazas
- `Game/test_game_fixed.json` — Traza de referencia verificada

---

## BUGS DEL BACKEND (16 bugs corregidos)

### B1. Agentes corrompían `self.hand` durante planificación de trades
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` |
| **Causa** | Los agentes (`AlexPelochoJaime`, `CarlesZaida`, `Crabisa`, `Sigma`, `AdrianHeras`, `PabloAleixAlex`, `Tristan`, `Edo`) llamaban `self.hand.remove_material()` dentro de `on_commerce_phase()` para calcular ofertas. Como `self.hand` es el **mismo objeto** que `player['resources']`, modificaban el estado real del juego. |
| **Efecto** | Trades marcados como "inviable" descuentaban recursos al jugador. Materiales desaparecían del juego. |
| **Solución** | Se crearon `_save_all_hands()` / `_restore_all_hands()` que hacen `deepcopy` de las manos antes de cada llamada a agentes y restauran después. Se aplica en: `call_to_agent_on_commerce_phase`, `call_to_agent_on_build_phase`, `call_to_agent_on_turn_start`, `call_to_agent_on_turn_end`, `_on_tradeoffer_response`, y `on_having_more_than_7_materials_when_thief_is_called`. |
| **En upstream** | Bug presente — los agentes modifican `self.hand` libremente. |

### B2. Auto-robo con el ladrón
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` — `move_thief()` |
| **Causa** | No había validación de que `adjacent_player != actual_player`. El agente podía devolver su propio ID. |
| **Efecto** | Un jugador se robaba a sí mismo (confirmado en game_8.json: P2 se roba a P2). |
| **Solución** | Si `adjacent_player == current_player`, se busca automáticamente otro jugador adyacente. |
| **En upstream** | Bug presente. |

### B3. Descarte con ladrón: `floor(n/2)` en vez de `ceil(n/2)`
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` — `check_if_thief_is_called()` |
| **Causa** | `max_hand = math.floor(total / 2)`. Un jugador con 11 cartas se quedaba con 5 en vez de 6. |
| **Solución** | Cambiado a `math.ceil(total / 2)`. |
| **En upstream** | Bug presente. |

### B4. `set_actual_player` no sincronizaba `agent_manager.actual_player`
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` |
| **Causa** | Solo se establecía `turn_manager.actual_player`, pero `_steal_from_player()` leía `agent_manager.actual_player`. |
| **Efecto** | El material robado se asignaba al jugador incorrecto. |
| **Solución** | Ahora sincroniza ambos. |
| **En upstream** | Bug presente. |

### B5. Trade ratio (4:1/3:1/2:1) no almacenado en JSON
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` — `on_commerce_response()` |
| **Causa** | El ratio se calculaba pero no se guardaba en la traza. |
| **Solución** | Se añade `commerce_phase_object['trade_ratio'] = trade_ratio`. |
| **En upstream** | Faltaba este campo. |

### B6. Giver/Receiver invertido en trades entre jugadores
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` — `send_trade_to_everyone()` |
| **Causa** | Los parámetros de `_trade_with_player(trade_offer, giver, receiver)` estaban invertidos en ambas ramas (ofertas normales y contra-ofertas). |
| **Efecto** | El jugador que ofrecía recibía lo que debía dar, y viceversa. |
| **Solución** | Se invirtieron las ramas. |
| **En upstream** | Bug presente. |

### B7. Doble descarte con el ladrón
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` — `check_if_thief_is_called()` |
| **Causa** | `on_having_more_than_7_materials_when_thief_is_called()` del agente modificaba `self.hand` (estado real). Después, el GameManager descartaba MÁS materiales usando el total ya reducido. |
| **Efecto** | Jugador con 11 cartas terminaba con 4 en vez de 6. |
| **Solución** | Save/restore alrededor de la llamada al agente. |
| **En upstream** | Bug presente. |

### B8. `build_road` permitía construir a través de rival
| | |
|-|-|
| **Fichero** | `Classes/Board.py` — `build_road()` |
| **Causa** | No verificaba que el nodo de inicio no perteneciera a un rival. |
| **Solución** | Si `nodes[start]['player'] != -1 && != player`, se rechaza. |
| **En upstream** | Bug presente. |

### B9. `DevelopmentCard` sin `id`, `DevelopmentDeck` sin `current_index`
| | |
|-|-|
| **Fichero** | `Classes/DevelopmentCards.py` |
| **Causa** | La clase fue refactorizada pero sin mantener compatibilidad con los tests. |
| **Solución** | Se añadió `id`, `current_index`, `shuffle_deck()`, validación en `add_card()`. |
| **En upstream** | Estos atributos estaban documentados en los tests pero faltaban en el código. |

### B10. `Materials.has_more()` aceptaba valores negativos
| | |
|-|-|
| **Fichero** | `Classes/Materials.py` |
| **Causa** | `has_more(Materials(1, 0, -1, 0, 0))` devolvía True porque -1 <= cualquier_valor. |
| **Solución** | Se añade `if materials.check_negative(): return False`. |
| **En upstream** | Bug presente. |

### B11. Carta de desarrollo jugable el mismo turno de compra
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py`, `Managers/GameDirector.py` |
| **Causa** | No había tracking de cartas compradas este turno. Regla Catán: no se puede jugar una carta recién comprada. |
| **Solución** | `cards_bought_this_turn = []` se resetea cada turno. Al jugar, se verifica que la carta no esté en esta lista. |
| **En upstream** | Bug presente — la regla estaba documentada en comentarios pero no implementada. |

### B12. Flag `already_played_development_card` se reseteaba por ronda
| | |
|-|-|
| **Fichero** | `Managers/GameDirector.py` — `round_start()` |
| **Causa** | `set_card_used(False)` se llamaba UNA VEZ al inicio de la ronda. Si P0 jugaba carta, P1-P3 no podían. |
| **Solución** | Movido al bucle `for i in range(4)`, reset por turno. |
| **En upstream** | Bug presente. |

### B13. Spam de `failed_victory_point` (1000+ entradas por traza)
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py`, `Managers/GameDirector.py` |
| **Causa** | VP cards no se eliminaban tras intento fallido. Agentes reintentaban cada fase. |
| **Solución** | Intentos fallidos se silencian — no se añaden a la traza JSON. |
| **En upstream** | Bug presente. |

### B14. Road building: bucle `while` con condición AND incorrecta
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` — `play_development_card()` línea 676 |
| **Causa** | `while not built['response'] and not built_2['response']` — con AND, si la segunda carretera no existe (`built_2 = True`), el bucle no entra y la primera carretera no se construye. |
| **Solución** | Cambiado a `or`. |
| **En upstream** | Bug presente. |

### B15. Road building: variable incorrecta (copy-paste)
| | |
|-|-|
| **Fichero** | `Managers/GameManager.py` — línea 702 |
| **Causa** | `if built['response']` debería ser `if built_2['response']` para validar la segunda carretera. |
| **Solución** | Cambiado a `built_2['response']`. |
| **En upstream** | Bug presente. |

---

## CAMBIOS EN AGENTES

En **ningún agente** se ha modificado su lógica interna. Los únicos cambios en agentes tracked son:

| Agente | Cambio | Razón |
|--------|--------|-------|
| `AdrianHerasAgent.py` | `on_commerce_phase()` → `on_commerce_phase(self, board_instance=None)` | Compatibilidad con firma de la interfaz |
| `AlexPastorAgent.py` | `on_commerce_phase()` → `on_commerce_phase(self, board_instance=None)` | Compatibilidad con firma de la interfaz |
| `RandomAgent.py` | `on_commerce_phase()` → `on_commerce_phase(self, board_instance=None)` | Compatibilidad con firma de la interfaz |

Los 8 agentes nuevos (`AlexPelochoJaime`, `CarlesZaida`, `Crabisa`, `Edo`, `Genetic`, `PabloAleixAlex`, `Sigma`, `Tristan`) se añadieron como ficheros nuevos — son agentes de estudiantes que no existían en upstream. Su lógica interna NO se ha modificado; todos los bugs que causaban se corrigen a nivel de GameManager con save/restore.

---

## CAMBIOS EN EL FRONTEND (Game/)

El visualizador en `Game/` es **completamente nuevo** respecto al `Visualizer/` de upstream.

| Mejora | Descripción |
|--------|-------------|
| **Navegación hacia atrás** | `prevRound/prevPhase` ahora aplica correctamente `applyCurrentPhase()` después de rebuild |
| **Logs se limpian entre turnos** | Separadores visuales por turno ("Turno de J1 — Ronda 3") |
| **Emojis → imágenes** | `resIcon()` genera `<img>` inline usando `nuevos_assets/materiales/` |
| **Commerce UI clara** | Muestra quién ofrece, cantidades de puerto (Da: Madera x4 → Recibe: Cereal x1), estados descriptivos |
| **Deltas persistentes** | Badges +1/-1 se quedan fijos hasta el siguiente cambio. Verde=dados, azul=comercio, rojo=pérdida |
| **Jugador activo por opacidad** | Inactivos al 45%, activo al 100% con borde dorado |
| **Cartas agrupadas** | Una carta + "x3" en vez de repetir 3 iconos |
| **Input de ronda** | Campo editable para saltar a cualquier ronda |
| **Performance** | `nextRound()` avanza incrementalmente. Scroll diferido. `clearEventLog` usa `innerHTML` |
| **Secciones diferenciadas** | "Registro de Eventos" en marrón, "Comercios" en verde |

---

## CAMBIOS EN TESTS

| Test | Cambio |
|------|--------|
| `test_game_manager.py` | `test_check_if_thief_is_called`: actualizado para `ceil` en vez de `floor`. `test_play_development_card`: simula nuevo turno antes de jugar carta. |
| `test_audit_integrity.py` | **NUEVO** — 11 tests que verifican cada bug corregido + integridad de traza completa |

---

## HERRAMIENTAS NUEVAS

| Herramienta | Uso |
|-------------|-----|
| `Game/debug_server.py` | Servidor que sirve el visualizador e inyecta verificación JSON-vs-Frontend en tiempo real |
| `Game/trace_auditor.py` | Auditor offline: recorre una traza JSON verificando todas las reglas de Catán |

---

## RESUMEN: TODOS LOS FICHEROS MODIFICADOS

### Backend (vs upstream)
- `Managers/GameManager.py` — B1-B7, B10-B15 (protección agentes, ladrón, trades, cartas desarrollo, road building)
- `Managers/GameDirector.py` — B12 (reset por turno), filtro de cartas fallidas
- `Classes/Board.py` — B8 (build_road bloqueada por rival)
- `Classes/DevelopmentCards.py` — B9 (id, current_index, shuffle_deck, add_card validación)
- `Classes/Materials.py` — B10 (has_more rechaza negativos)

### Agentes (vs upstream)
- `Agents/AdrianHerasAgent.py` — Solo firma `on_commerce_phase`
- `Agents/AlexPastorAgent.py` — Solo firma `on_commerce_phase`
- `Agents/RandomAgent.py` — Solo firma `on_commerce_phase`
- 8 agentes nuevos añadidos (no existían en upstream)

### Frontend (nuevo, no existía en upstream)
- `Game/index.html`, `Game/game.js`, `Game/styles.css`

### Tests
- `Tests/test_game_manager.py` — 2 tests actualizados
- `Tests/test_audit_integrity.py` — 11 tests nuevos

### Verificación
- `Game/debug_server.py`, `Game/trace_auditor.py`
- `Game/test_game_fixed.json` — Traza verificada de referencia (0 errores)
