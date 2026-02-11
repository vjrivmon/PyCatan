# 🏰 Interfaz de Juego de Catán

Interfaz moderna y completa para visualizar y jugar partidas de Catán desde archivos JSON de trazas.

## 🎯 Características

### Elementos Principales del Juego

- **Tablero Hexagonal**: Visualización completa del tablero con 19 hexágonos
  - Diferentes tipos de terreno (trigo, mineral, arcilla, madera, lana, desierto)
  - Fichas de números en cada hexágono (con marcado especial para 6 y 8)
  - Indicador visual del ladrón
  - Nodos para asentamientos y ciudades
  - Carreteras entre nodos

- **Panel de Jugadores**: Información completa de cada jugador
  - Puntos de victoria (VP)
  - Recursos en mano (trigo, mineral, arcilla, madera, lana)
  - Indicador visual del jugador activo
  - Colores distintivos por jugador

- **Sistema de Acciones**: Visualización de acciones en tiempo real
  - Tiradas de dados
  - Construcciones (asentamientos, ciudades, carreteras)
  - Comercio con banco y entre jugadores
  - Compra de cartas de desarrollo

- **Controles de Navegación**: 
  - Navegación por rondas, turnos y fases
  - Botón de play/pausa para reproducción automática
  - Controles intuitivos y responsivos

- **Panel de Información**:
  - Visualización de dados (dado 1 + dado 2 = total)
  - Historial de eventos del juego
  - Información de ronda, turno y fase actual

## 🚀 Uso

1. **Abrir la interfaz**: Abre `index.html` en tu navegador
2. **Cargar partida**: Haz clic en "Cargar Partida" y selecciona un archivo JSON de traza
3. **Navegar**: Usa los controles para navegar por la partida
4. **Reproducción automática**: Haz clic en el botón de play para reproducir automáticamente

## 📁 Estructura de Archivos

```
Game/
├── index.html      # Estructura HTML principal
├── styles.css      # Estilos y diseño visual
├── game.js         # Lógica del juego y renderizado
└── README.md       # Este archivo
```

## 🎨 Diseño

La interfaz utiliza un diseño moderno con:
- **Tema oscuro** con colores del juego de Catán
- **Tipografía elegante**: Playfair Display para títulos, Inter para cuerpo
- **Animaciones suaves** y transiciones
- **Diseño responsivo** que se adapta a diferentes tamaños de pantalla
- **Efectos visuales** como sombras, gradientes y hover states

## 🔧 Tecnologías

- HTML5
- CSS3 (con variables CSS y clip-path para hexágonos)
- JavaScript vanilla (sin dependencias externas)
- Fuentes de Google Fonts

## 📊 Formato de Datos

La interfaz espera archivos JSON con la siguiente estructura:

```json
{
  "setup": {
    "board": {
      "board_nodes": [...],
      "board_terrain": [...]
    }
  },
  "game": {
    "round_0": {
      "turn_P0": {
        "phase_0": {
          "hand_P0": {...},
          "dice_roll": {...},
          ...
        }
      }
    }
  }
}
```

## 🎮 Controles

- **⏮ Ronda Anterior**: Retrocede a la ronda anterior
- **⏪ Turno Anterior**: Retrocede al turno anterior
- **◀ Fase Anterior**: Retrocede a la fase anterior
- **▶ Play/Pausa**: Reproduce o pausa la partida automáticamente
- **▶ Fase Siguiente**: Avanza a la siguiente fase
- **⏩ Turno Siguiente**: Avanza al siguiente turno
- **⏭ Ronda Siguiente**: Avanza a la siguiente ronda

## 🌟 Características Destacadas

1. **Visualización en Tiempo Real**: Los cambios se reflejan inmediatamente al navegar
2. **Información Completa**: Muestra recursos, puntos de victoria y acciones de cada jugador
3. **Interfaz Intuitiva**: Diseño claro y fácil de usar
4. **Rendimiento Optimizado**: Renderizado eficiente incluso con partidas largas
5. **Accesibilidad**: Contraste adecuado y navegación por teclado

## 🔮 Mejoras Futuras

- [ ] Posicionamiento preciso de nodos y carreteras
- [ ] Animaciones de transición entre fases
- [ ] Modo de pantalla completa para el tablero
- [ ] Exportación de imágenes del estado del juego
- [ ] Estadísticas y análisis de partidas
- [ ] Modo oscuro/claro configurable
- [ ] Soporte para múltiples idiomas

## 📝 Notas

- Los archivos JSON deben seguir el formato de trazas generado por el simulador PyCatan
- El posicionamiento de hexágonos está optimizado para el layout estándar de Catán
- La interfaz es completamente cliente-side, no requiere servidor

## 🐛 Solución de Problemas

**El tablero no se muestra correctamente:**
- Verifica que el archivo JSON tenga la estructura correcta
- Asegúrate de que el navegador soporte CSS clip-path

**Los jugadores no se actualizan:**
- Verifica que el archivo contenga información de `hand_P0` a `hand_P3`
- Comprueba la consola del navegador para errores

**Los controles no funcionan:**
- Asegúrate de haber cargado un archivo válido primero
- Verifica que JavaScript esté habilitado en tu navegador
