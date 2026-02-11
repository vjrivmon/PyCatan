# Debug Task: Visualizador PyCatan - Sincronización JSON/UI

## Problema
El visualizador no muestra correctamente los recursos de los jugadores porque:
1. **Backend**: Los valores de recursos se guardan como **strings** (`'cereal': '4'`) en lugar de **int**
2. **Backend**: `end_turn` solo incluye `victory_points`, no incluye `hand_P*` actualizado
3. **Backend**: `build_phase` y `commerce_phase` no registran el estado de recursos después de cada acción
4. **Frontend**: `changeHandObject()` no maneja correctamente strings vs int

## Archivos a Modificar

### Backend
- `Classes/Materials.py` - línea 70-72: `__to_object__()` devuelve int, no str
- `Managers/GameDirector.py` - línea ~110: `end_turn()` incluir `hand_P*`
- `Managers/GameManager.py` - función `build_phase_object()`: incluir `hand_P*`
- `Managers/GameManager.py` - función `on_commerce_response()`: incluir `hand_P*`

### Frontend
- `Visualizer/JS/general.js` - `changeHandObject()`: manejar string e int con parseInt
- `Visualizer/JS/general.js` - `updatePhaseData()`: buscar recursos en todas las fases
- `Visualizer/JS/general.js` - `handleBuildPhase()`: actualizar recursos
- `Visualizer/JS/general.js` - `handleCommercePhase()`: actualizar recursos

---

## Criterios de Completitud (12 total)

### Backend (5)
- [x] B1: `hand_P*` son int, no string
- [x] B2: `build_phase` incluye `hand_P*` después de cada construcción
- [x] B3: `commerce_phase` incluye `hand_P*` después de cada comercio
- [x] B4: `end_turn` incluye `hand_P*`
- [x] B5: `validate_backend.py` pasa con 0 errores en 10 trazas

### Frontend (5)
- [x] F1: `changeHandObject()` maneja string e int
- [x] F2: `updatePhaseData()` actualiza en todas las fases
- [x] F3: `handleBuildPhase()` actualiza recursos visualmente
- [x] F4: `handleCommercePhase()` actualiza recursos visualmente
- [x] F5: Validación con Playwright: UI coincide con JSON al navegar

### Integración (2)
- [x] I1: Partida de prueba genera JSON válido
- [x] I2: Visualizador renderiza correctamente (verificado con Playwright)

---

## Comandos de Validación

```bash
# Backend
python .claude/debug/validate_backend.py Tests/test_traces/game_0.json

# Excel tracker
python .claude/debug/resource_tracker.py Tests/test_traces/game_0.json recursos.xlsx

# Frontend (requiere Playwright)
python .claude/debug/validate_frontend.py http://localhost:8000 Tests/test_traces/game_0.json
```

---

## Notas
- Generar nueva traza después de los cambios backend para validar formato
- El visualizador debe mostrar exactamente lo que dice el JSON en cada fase
