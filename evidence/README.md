# Evidencias de ejecución

El video recomendado para la entrega es **[demostracion-rubrica.mp4](demostracion-rubrica.mp4)**: explica los siete criterios mediante selecciones reales de código en VS Code, resultados reales del navegador y comandos ejecutados en la terminal de VS Code. Tiene narración sintética en español, rótulos y [subtítulos](demostracion-rubrica.srt). Es un montaje de capturas reales con selecciones progresivas; no una grabación continua de escritorio ni una simulación del IDE. El [guion](guion-rubrica.md) y [timeline.json](rubric-video/timeline.json) permiten localizar cada escena.

Capturadas durante la implementación. Los archivos de texto contienen salidas reales, no ejemplos.

- `python-container.txt`: Python 3.12.15 dentro del contenedor.
- `tests-docker.txt`: 14 pruebas aprobadas dentro del contenedor.
- `tests-local.txt`: 14 pruebas aprobadas también con el Python 3.13 disponible localmente; la verificación del requisito Python 3.12 es la del contenedor.
- `docker-stats.txt`: muestra real de consumo frente al límite de 256 MiB. Los valores son instantáneos durante la verificación, no una prueba de carga.
- `docker-limits.txt`: `Memory=268435456 NanoCpus=1000000000`, equivalentes a 256 MiB y 1 CPU.
- `compose-ps.txt`: contenedor saludable y puerto 8000 publicado.
- `captured-at.txt`: fecha UTC de la captura.
- `demostracion.mp4`: grabación automatizada real del navegador. Muestra la portada académica de UTH, entrada al analizador, conversión de `100` base 16 a 256, error `102` base 2, texto `España`, las 14 pruebas ejecutadas en Docker y el contenedor activo con sus recursos. Las vistas de comandos presentan su salida real capturada durante la grabación; no son una terminal interactiva. Video sin audio.
- `conversion.png`, `validation.png`, `utf8.png`, `tests.png`, `container.png`, `mobile.png`: capturas de la demostración y comprobación adaptable.

Para actualizar las evidencias de texto, con Docker iniciado:

```sh
sh scripts/capture-evidence.sh
```

Para repetir la grabación (herramientas opcionales, fuera de las dependencias de la aplicación):

```sh
.venv/bin/pip install playwright imageio-ffmpeg
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/analyzer-playwright .venv/bin/python -m playwright install chromium ffmpeg
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/analyzer-playwright .venv/bin/python scripts/record_demo.py
```

Requiere Chromium de Playwright instalado y el contenedor escuchando en el puerto 8000.

## Revisión de la interfaz mejorada

`ui-checks.txt` registra la comprobación de ejemplos interactivos, copiado, agrupación de bits, foco de errores, tamaño UTF-8, contador Unicode, límites de texto, funcionamiento sin JavaScript y ausencia de desbordamientos de página en 360, 390, 768 y 1280 píxeles. Capturas: `ui-desktop.png`, `ui-number.png`, `ui-text.png` y `ui-mobile.png`.

## Portada académica

`home.png` y `home-mobile.png` muestran la presentación de UTH con estudiante, cuenta, asignatura y docente. `home-checks.txt` registra la carga real del logo, navegación entre portada y analizador y adaptación móvil.

## Publicación

Repositorio existente: https://github.com/meledpeca93/AnalizadorDatos-MV1-MEPC. Se verificó su acceso público y la presencia del video de demostración anterior. El nuevo video `demostracion-rubrica.mp4`, los subtítulos y el guion se generan localmente y deben incluirse en el siguiente commit y push para compartir esta versión actualizada con el evaluador.
