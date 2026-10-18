# Evidencias de ejecución

Capturadas durante la implementación. Los archivos de texto contienen salidas reales, no ejemplos.

- `python-container.txt`: Python 3.12.15 dentro del contenedor.
- `tests-docker.txt`: 14 pruebas aprobadas dentro del contenedor.
- `tests-local.txt`: 14 pruebas aprobadas también con el Python 3.13 disponible localmente; la verificación del requisito Python 3.12 es la del contenedor.
- `docker-stats.txt`: 48.17 MiB / 256 MiB de RAM; CPU instantánea 0.05 %. Es una muestra en reposo, no una prueba de carga.
- `docker-limits.txt`: `Memory=268435456 NanoCpus=1000000000`, equivalentes a 256 MiB y 1 CPU.
- `compose-ps.txt`: contenedor saludable y puerto 8000 publicado.
- `captured-at.txt`: fecha UTC de la captura.
- `demostracion.mp4`: grabación automatizada real del navegador. Muestra conversión de `100` base 16 a 256, error `102` base 2, texto `España`, las 14 pruebas ejecutadas en Docker y el contenedor activo con sus recursos. Las vistas de comandos presentan su salida real capturada durante la grabación; no son una terminal interactiva. Video sin audio.
- `conversion.png`, `validation.png`, `utf8.png`, `tests.png`, `container.png`, `mobile.png`: capturas de la demostración y comprobación adaptable.

Para actualizar las evidencias de texto, con Docker iniciado:

```sh
sh scripts/capture-evidence.sh
```

Para repetir la grabación (herramientas opcionales, fuera de las dependencias de la aplicación):

```sh
.venv/bin/pip install playwright imageio-ffmpeg
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/analyzer-playwright .venv/bin/python -m playwright install ffmpeg
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/analyzer-playwright .venv/bin/python scripts/record_demo.py
```

Requiere Google Chrome instalado y el contenedor escuchando en el puerto 8000.

## Publicación pendiente

El proyecto y las evidencias están disponibles localmente. No se ha creado un enlace GitHub o Google Drive: falta habilitar una conexión de cuenta con capacidad para subir la entrega. No se presenta una URL ficticia. Una vez conectado GitHub, publicar los archivos y el MP4 (o adjuntarlo a una release) y verificar acceso para el evaluador. Como alternativa, subir la carpeta completa a Google Drive y habilitar acceso para el evaluador.
