# Guion del video por rúbrica

Archivo recomendado: [demostracion-rubrica.mp4](demostracion-rubrica.mp4). Narración en español con voz sintética del sistema y [subtítulos SRT](demostracion-rubrica.srt).

El montaje utiliza capturas del VS Code real: apertura de archivos, selecciones progresivas, resultados de la aplicación en Docker y comandos ejecutados en la terminal del IDE. Las salidas de pruebas y Docker no son simuladas. Se agregaron rótulos y narración para explicar el flujo.

| Tiempo | Criterio / escena | Qué se muestra |
| --- | --- | --- |
| 00:00–00:04 | RECORRIDO DE LA RÚBRICA · 10 PUNTOS | Melvin Edgardo Peña Caballero · Arquitectura de Computadoras · UTH |
| 00:04–00:11 | 1 · CONVERSIONES Y AJUSTE A BYTES · 2.0 PUNTOS | Entrada: 100 · Base elegida: hexadecimal (16). La base se selecciona; no se adivina. |
| 00:11–00:17 | 1 · CONVERSIONES Y AJUSTE A BYTES · 2.0 PUNTOS | NumberForm.number crea el input de texto; base ofrece 2, 8, 10 y 16. |
| 00:17–00:23 | 4 · ESTRUCTURA Y FUNCIONAMIENTO DJANGO · 1.5 PUNTOS | request.POST → NumberForm → is_valid(): recepción y validación en el servidor. |
| 00:23–00:27 | 1 · FLUJO DE CONVERSIÓN | NumberForm.clean() llama convert_number(number, base). |
| 00:27–00:31 | 1 · CONVERSIONES Y AJUSTE A BYTES | int(significant, base) interpreta el número usando la base seleccionada. |
| 00:31–00:38 | 1 · CONVERSIONES Y AJUSTE A BYTES | bit_length → bits significativos · (bits + 7) // 8 → bytes · format → relleno binario. |
| 00:38–00:45 | 1 · RESULTADO DE LA CONVERSIÓN | 100₁₆ = 256₁₀ · 00000001 00000000 · 9 bits significativos · 2 bytes. |
| 00:45–00:50 | 3 · VALIDACIÓN Y MENSAJES DE ERROR · 1.0 PUNTO | Se validan vacíos, negativos, dígitos de la base y rango 0–65 535. |
| 00:50–00:55 | 3 · ERROR REAL DE VALIDACIÓN | 102 en base 2 → error: el dígito 2 no pertenece al sistema binario. |
| 00:55–01:00 | 2 · ANÁLISIS DE CARACTERES Y UTF-8 · 1.5 PUNTOS | TextForm.text recibe el texto y clean_text() lo envía a analyze_text(). |
| 01:00–01:07 | 2 · ANÁLISIS DE CARACTERES Y UTF-8 | Máximo 20 puntos de código · ord(char) → código · encode("utf-8") → bytes. |
| 01:07–01:12 | 2 · RESULTADO UTF-8 CON Ñ | ñ → decimal 241 · U+00F1 · hexadecimal F1 · bytes UTF-8 C3 B1. |
| 01:12–01:16 | 4 · ESTRUCTURA Y FUNCIONAMIENTO DJANGO · 1.5 PUNTOS | urls.py conecta / y /analizador/ con las vistas; render() entrega las plantillas. |
| 01:16–01:22 | 5 · PRUEBAS AUTOMATIZADAS · 1.0 PUNTO | tests.py: 14 pruebas de conversiones, límites, errores y UTF-8 con ñ. |
| 01:22–01:27 | 5 · PRUEBAS EJECUTADAS EN PYTHON 3.12 | docker compose exec -T web python manage.py test --verbosity 1 → 14 pruebas: OK. |
| 01:27–01:32 | 6 · DOCKERFILE Y COMPOSE · 1.5 PUNTOS | FROM python:3.12-slim · instalación de dependencias · ejecución con Gunicorn. |
| 01:32–01:37 | 6 · PUERTO Y LÍMITES DE RECURSOS | ports: 8000:8000 · mem_limit: 256m · cpus: 1.0. |
| 01:37–01:43 | 6 · CONTENEDOR ACTIVO Y DOCKER STATS | stats muestra consumo real; inspect confirma 268435456 bytes de RAM y 1000000000 NanoCPUs. |
| 01:43–01:48 | 7 · README, EXPLICACIÓN Y EVIDENCIAS · 1.5 PUNTOS | README: comandos de construcción, ejecución, pruebas y verificación de recursos. |
| 01:48–01:54 | 7 · VON NEUMANN Y KERNEL COMPARTIDO | CPU ejecuta · RAM almacena · E/S comunica. Docker comparte el kernel del host Linux. |

## Flujo explicado

1. El usuario escribe en `NumberForm.number`, un `TextInput`, y elige `NumberForm.base`. La base no se detecta automáticamente: la selección indica cómo interpretar los dígitos.
2. La plantilla renderiza esos campos y envía el formulario mediante POST.
3. `index()` en `analyzer/views.py` recibe `request.POST` y construye `NumberForm`.
4. `is_valid()` ejecuta `NumberForm.clean()`, que llama a `convert_number(number, base)`.
5. `convert_number()` en `analyzer/services.py` valida dígitos y rango, interpreta con `int(..., base)` y prepara cuatro representaciones. `bit_length()` y `(bits + 7) // 8` calculan bits y bytes; `format()` agrega el relleno binario.
6. La vista envía el resultado a la plantilla. Se muestran el valor equivalente, los bits agrupados y una explicación del relleno.
7. Para texto: `TextForm.clean_text()` llama a `analyze_text()`. Se validan hasta 20 puntos de código; `ord()` da el código y `encode("utf-8")` produce los bytes.

## Correspondencia de los siete criterios

- **Conversiones (2.0):** entrada, base elegida, `convert_number`, cálculo de bits/bytes y conversión válida.
- **UTF-8 (1.5):** recepción del texto, `analyze_text`, `ord`, `encode` y fila de ñ seleccionada.
- **Validación (1.0):** código de los controles y error real al ingresar 102 en base 2.
- **Django (1.5):** formularios, recepción POST, validación, rutas, vistas y plantillas.
- **Pruebas (1.0):** código del caso ñ y ejecución real de las 14 pruebas dentro del contenedor.
- **Docker (1.5):** Dockerfile, Compose, puerto 8000, 256 MiB y 1 CPU; terminal con contenedor saludable, stats e inspect.
- **Documentación (1.5):** README con comandos, Von Neumann y kernel Linux compartido.

El nuevo video es un archivo local hasta que se incluya en el siguiente commit y push.
