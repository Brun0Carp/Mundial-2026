# Mundial 26 3D

Juego de fútbol retro en 3D con el Mundial 2026 completo: 48 selecciones, sorteo, fase de grupos, eliminatorias, penales y ceremonia de premiación.

Todo el juego está en un solo archivo: `index.html`. Se abre directo en el navegador, sin instalar nada (necesita internet para cargar three.js y las fuentes).

## Cómo jugar

- **Cámaras:** TV (vista de transmisión, por defecto), cerca (tercera persona) y amplia. Se cambian desde el menú.
- **Teclado:** flechas o WASD para moverte, X pase, Z o espacio tiro/barrida, Shift o C correr, P o Esc pausa.
- **Celular:** joystick táctil y botones A (pase), B (tiro) y C (correr).
- **Mandos Bluetooth** (Xbox, PlayStation, Switch Pro, 8BitDo): stick o cruceta para moverte, A/✕ pase, B/○ tiro, Y/△ cambiar jugador, gatillos para correr, Start pausa.
- **Barra TURBO:** correr la gasta; si se vacía, el jugador se cansa hasta recuperarse.

## Multijugador

Las salas con código de 4 caracteres funcionan solo cuando el juego se abre como artefacto en claude.ai, porque usan la conexión entre jugadores de claude.ai. Abierto desde este repositorio o desde GitHub Pages, el resto del juego funciona igual, pero el multijugador muestra un aviso.

## Publicarlo con GitHub Pages

En el repositorio: **Settings → Pages → Build and deployment → Deploy from a branch**, rama `main`, carpeta `/ (root)`. El juego queda en `https://<usuario>.github.io/mundial-26-3d/`. En cuentas gratis, GitHub Pages requiere que el repositorio sea público.

---

# Crónicas de Valdoria (RPG medieval)

Un pequeño juego de rol en pixel art ambientado en la Edad Media. Está entero en `rpg-medieval.html`: los gráficos, los mapas y la música chiptune se generan en el propio archivo, sin imágenes externas (solo usa internet para la fuente pixelada; sin conexión usa una fuente de respaldo).

**Historia:** el dragón Ignaroth ha despertado en la Cueva de Ceniza. Aldren, un escudero de la aldea de Robledal, debe cruzar el Bosque Umbrío, encontrar la llave de la reja y derrotarlo.

- **Mundo:** aldea con herrería y posada, bosque con río y encuentros aleatorios, cueva con lava y el dragón.
- **Combate por turnos:** atacar, magia (Fuego, Curación y, desde el nivel 5, Rayo), objetos y huir. Siete enemigos distintos con ataques especiales y un jefe final.
- **Progresión:** niveles y experiencia, oro, armas y armaduras, pociones y elixires, cofres y una espada legendaria escondida.
- **Guardado:** en la posada o desde el menú, más un autoguardado al cambiar de zona (se guarda en el navegador). Cada partida guarda una copia de seguridad: si la principal se daña, se carga la copia. Si caes, despiertas en la posada con la mitad del oro.
- **Misiones:** el Diario del menú indica el objetivo actual, y cumplir objetivos también da experiencia.
- **Opciones:** volumen de música y de efectos, intensidad del temblor de pantalla, destellos (se pueden cambiar por un tinte suave) y velocidad del texto.

**Controles:** flechas o WASD para moverte, Z / Enter / Espacio para hablar y aceptar, X / Esc para el menú y volver, M para silenciar. También funciona con mando (cruceta o stick, A para aceptar, B o Start para el menú). En el celular aparecen una cruceta y los botones A y B.

**Cómo está hecho:** se aplicaron las skills de `gamedev-skills/awesome-gamedev-agent-skills` instaladas en `.claude/skills/` (`rpg`, `save-systems`, `dialogue-systems`, `game-feel`, `input-systems`, `audio-design`, `game-ui-ux` y `create-game-assets`). Los diálogos de los personajes son datos (un grafo con condiciones) que se validan automáticamente. Todo el arte está dibujado a mano píxel a píxel en el propio código, sin imágenes generadas por IA ni recursos de terceros.

Con GitHub Pages activado, queda en `https://<usuario>.github.io/<repositorio>/rpg-medieval.html`.
