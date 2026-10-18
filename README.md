# Analizador de representación de datos

Aplicación web educativa en **Python 3.12 y Django 5.2**, servida con Gunicorn. Convierte enteros sin signo entre bases 2, 8, 10 y 16 y analiza puntos de código Unicode y sus bytes UTF-8. No necesita base de datos ni migraciones.

## Ejecutar con Docker (recomendado)

Requisitos: Docker Engine con Compose, o Docker Desktop iniciado; puerto 8000 libre.

```sh
docker compose up --build -d
docker compose ps
```

Abrir **http://localhost:8000**. El servicio tiene un límite de **256 MiB de RAM y 1 CPU** mediante `mem_limit: 256m` y `cpus: 1.0`. Gunicorn utiliza un trabajador con dos hilos y un usuario sin privilegios.

```sh
# Pruebas dentro de Python 3.12
docker compose exec -T web python manage.py test --verbosity 2
# Consumo instantáneo (evidencia real, no valores simulados)
docker stats --no-stream $(docker compose ps -q web)
# Verificar límites: Memory=268435456, NanoCpus=1000000000
docker inspect --format '{{.HostConfig.Memory}} {{.HostConfig.NanoCpus}}' $(docker compose ps -q web)
# Logs y apagado
docker compose logs web
docker compose down
```

## Ejecutar sin Docker

```sh
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py test --verbosity 2
python manage.py runserver 127.0.0.1:8000
```

## Comportamiento y ejemplos

- `FF`, base 16 → decimal `255`, binario `11111111`, octal `377`, hexadecimal `FF`; 8 bits significativos, 1 byte.
- `256`, base 10 → `0000000100000000`; 9 bits significativos, 2 bytes.
- `0` → `00000000`; se adopta la convención de 1 bit significativo y 1 byte mínimo.
- `65535` → `1111111111111111`; 16 bits y 2 bytes.
- `102`, base 2 → error de dígitos. `-1` → error de negativos. `65536` → error de rango.
- `ñ` → decimal `241`, punto `U+00F1`, hexadecimal `F1`, UTF-8 `C3 B1` (dos bytes).

Se aceptan dígitos hexadecimales en ambas cajas y ceros iniciales. Se eliminan espacios exteriores del número; se rechazan signos, prefijos (`0x`), separadores y espacios interiores. El binario se completa a `8 × ceil(bits/8)`; el rango solicitado requiere solamente 8 o 16 bits.

El texto admite hasta **20 puntos de código Unicode** y conserva espacios. Un emoji o una letra con marcas combinadas puede contener varios puntos de código: no se cuentan grafemas. Los bytes UTF-8 se muestran en hexadecimal separados por espacios, diferenciados del hexadecimal del punto de código. `␠` hace visible un espacio. Las dos operaciones se envían de manera independiente y los resultados corresponden al último formulario enviado.

## Estructura y pruebas

- `config/`: configuración Django, rutas y entrada WSGI.
- `analyzer/services.py`: conversión, validación y codificación.
- `analyzer/forms.py`: validaciones de los formularios en el servidor.
- `analyzer/views.py` y `templates/analyzer/index.html`: vista y página adaptable.
- `analyzer/tests.py`: 14 pruebas con subcasos: bases válidas, límites de bytes, cero, dígitos inválidos, bases no admitidas, valores negativos, vacíos, rango, ceros iniciales extensos, ñ, emoji, espacios, longitud, solicitudes HTTP, escape HTML y CSRF.
- `evidence/`: resultados de ejecución y video, cuando se hayan generado.

La página incluye etiquetas accesibles, diseño adaptable, escape automático de HTML y protección CSRF. La hoja de estilos está incluida en la plantilla, sin dependencias externas ni archivos estáticos que requieran servir por separado. Para exposición fuera de localhost, configurar `DJANGO_ALLOWED_HOSTS`, un `DJANGO_SECRET_KEY` privado y HTTPS en un proxy; el Compose entregado está pensado para demostración local.

## Arquitectura de Von Neumann

La **CPU** ejecuta el intérprete Python y las instrucciones de conversión, validación y codificación. La **unidad de control** coordina estas instrucciones y la **unidad aritmético-lógica** realiza operaciones enteras, comparaciones y desplazamientos usados para las representaciones binarias. La **RAM** guarda instrucciones y datos de trabajo: objetos Python, entradas, resultados y peticiones HTTP. El **almacenamiento** conserva el código, las dependencias y las capas de la imagen. La **entrada/salida** recibe datos mediante el navegador y la red y devuelve HTML con los resultados. Los buses y la jerarquía de memoria permiten transferir instrucciones y datos entre estos componentes; la aplicación los usa a través del sistema operativo.

Un contenedor aísla procesos y recursos mediante mecanismos del kernel, como namespaces y cgroups; **no arranca un kernel propio** como una máquina virtual. Los procesos Python realizan llamadas al kernel del host Linux del contenedor. En Docker Desktop para macOS o Windows, ese host es la máquina virtual Linux administrada por Docker: los contenedores comparten su kernel Linux, no directamente el kernel de macOS o Windows. Los límites de Compose restringen memoria y tiempo de CPU; 1 CPU es una cuota, no una reserva de un núcleo físico exclusivo.

## Entrega

Consultar `evidence/README.md` para el estado verificado de las evidencias, el video y la publicación. El video debe durar menos de dos minutos y mostrar conversión válida, error, ñ, pruebas y contenedor en ejecución. El enlace a un repositorio o Drive debe verificarse con acceso desde la cuenta del evaluador antes de entregar.
