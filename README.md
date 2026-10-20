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
