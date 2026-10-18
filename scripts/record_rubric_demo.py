"""Produce a <= 2 minute rubric walkthrough from the REAL VS Code renderer.

macOS prerequisites: a temporary VS Code window exposing CDP on localhost:9333,
Playwright Chromium, imageio-ffmpeg, and the system Spanish voice Paulina.
Screenshots contain actual editor selections, actual HTTP interactions and actual
VS Code terminal commands. Only captions and system-voice narration are added.
No source code is edited by the capture process. Intermediate files go to /tmp.
"""
import json
import math
import re
import subprocess
import textwrap
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
WORK = Path('/private/tmp/analyzer-rubric-video')
WORK.mkdir(exist_ok=True)
OUT = ROOT / 'evidence'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
SCENES = []


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def duration(path):
    result = subprocess.run([FFMPEG, '-i', str(path)], capture_output=True, text=True)
    return re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stderr)


def seconds(path):
    m = duration(path)
    return int(m[1])*3600+int(m[2])*60+float(m[3])


def register(frames, criterion, caption, speech, source):
    SCENES.append({'frames': frames, 'criterion': criterion, 'caption': caption, 'speech': speech, 'source': source})
    print(f'Capturada escena {len(SCENES):02d}: {caption}', flush=True)


def snap(page, name):
    path = WORK / (name + '.png')
    page.screenshot(path=str(path), scale='css')
    return str(path)


with sync_playwright() as p:
    ide_browser = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    ide = next(page for ctx in ide_browser.contexts for page in ctx.pages if 'workbench' in page.url)
    ide.set_viewport_size({'width': 1600, 'height': 800})
    ide.keyboard.press('Escape')
    close = ide.locator('[aria-label^="Hide Secondary Side Bar"]')
    if close.count() and close.first.is_visible():
        close.first.click()
    close = ide.locator('[aria-label^="Hide Panel"]')
    if close.count() and close.first.is_visible():
        close.first.click()
    ide.keyboard.press('Escape')

    def code(file, line, visual_lines, criterion, caption, speech):
        close = ide.locator('[aria-label^="Hide Panel"]')
        if close.count() and close.first.is_visible():
            close.first.click()
        ide.keyboard.press('Escape')
        ide.keyboard.press('Meta+p')
        ide.keyboard.insert_text(file)
        ide.wait_for_timeout(650)
        ide.keyboard.press('Enter')
        ide.wait_for_timeout(450)
        ide.keyboard.press('Control+g')
        ide.keyboard.insert_text(str(line))
        ide.wait_for_timeout(180)
        ide.keyboard.press('Enter')
        ide.wait_for_timeout(180)
        ide.keyboard.press('Home')
        frames = [snap(ide, f'{len(SCENES):02d}-code-start')]
        for i in range(visual_lines):
            ide.keyboard.press('Shift+ArrowDown')
            if i % 3 == 2 or i == visual_lines-1:
                frames.append(snap(ide, f'{len(SCENES):02d}-select-{i}'))
        register(frames, criterion, caption, speech, f'VS Code real: {file}, desde línea {line}')

    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width':1600,'height':800}, color_scheme='light')
    app = context.new_page()
    app.goto('http://127.0.0.1:8000/')
    expect(app.get_by_text('201230010100', exact=True)).to_be_visible()
    register([snap(app, '00-home')], 'RECORRIDO DE LA RÚBRICA · 10 PUNTOS', 'Melvin Edgardo Peña Caballero · Arquitectura de Computadoras · UTH', 'Demostración de los siete criterios de la rúbrica, desde el código hasta su ejecución.', 'Aplicación real en Docker')
    app.get_by_role('link', name='Entrar al analizador').click()
    app.get_by_role('textbox', name='Número:', exact=True).fill('100')
    app.get_by_label('Base de origen').select_option('16')
    app.locator('#number-form').scroll_into_view_if_needed()
    # Native focus/selection makes the actual input receiving the data visible.
    app.get_by_role('textbox', name='Número:', exact=True).select_text()
    register([snap(app, '01-input')], '1 · CONVERSIONES Y AJUSTE A BYTES · 2.0 PUNTOS', 'Entrada: 100 · Base elegida: hexadecimal (16). La base se selecciona; no se adivina.', 'Ingresamos cien en hexadecimal. La base se selecciona explícitamente; no se adivina por los dígitos.', 'Formulario real: input number y select base')

    code('analyzer/forms.py', 6, 6, '1 · CONVERSIONES Y AJUSTE A BYTES · 2.0 PUNTOS', 'NumberForm.number crea el input de texto; base ofrece 2, 8, 10 y 16.', 'En forms punto py, number crea el campo de texto; base define los cuatro sistemas admitidos.')
    code('analyzer/views.py', 24, 8, '4 · ESTRUCTURA Y FUNCIONAMIENTO DJANGO · 1.5 PUNTOS', 'request.POST → NumberForm → is_valid(): recepción y validación en el servidor.', 'En views punto py, request POST recibe la entrada e is valid ejecuta las validaciones del formulario.')
    code('analyzer/forms.py', 9, 6, '1 · FLUJO DE CONVERSIÓN', 'NumberForm.clean() llama convert_number(number, base).', 'El método clean envía el número y su base al método convert number.')
    code('analyzer/services.py', 18, 3, '1 · CONVERSIONES Y AJUSTE A BYTES', 'int(significant, base) interpreta el número usando la base seleccionada.', 'En services punto py, int interpreta el número según la base seleccionada.')
    code('analyzer/services.py', 21, 6, '1 · CONVERSIONES Y AJUSTE A BYTES', 'bit_length → bits significativos · (bits + 7) // 8 → bytes · format → relleno binario.', 'Bit length cuenta bits significativos. El redondeo determina bytes; format completa el binario con ceros.')
    app.get_by_role('button', name='Convertir número').click()
    expect(app.locator('dd').filter(has_text='0000000100000000')).to_be_visible()
    app.locator('#number-result').scroll_into_view_if_needed()
    register([snap(app, '07-valid')], '1 · RESULTADO DE LA CONVERSIÓN', '100₁₆ = 256₁₀ · 00000001 00000000 · 9 bits significativos · 2 bytes.', 'Cien hexadecimal equivale a doscientos cincuenta y seis: nueve bits significativos, completados a dos bytes.', 'Resultado real, agrupación binaria y explicación de relleno')

    code('analyzer/services.py', 7, 14, '3 · VALIDACIÓN Y MENSAJES DE ERROR · 1.0 PUNTO', 'Se validan vacíos, negativos, dígitos de la base y rango 0–65 535.', 'Aquí se rechazan vacíos, negativos, dígitos inválidos y valores fuera del rango permitido.')
    app.get_by_role('textbox', name='Número:', exact=True).fill('102')
    app.get_by_label('Base de origen').select_option('2')
    app.get_by_role('button', name='Convertir número').click()
    expect(app.locator('.errorlist')).to_contain_text('Dígitos inválidos')
    app.locator('#number-form').scroll_into_view_if_needed()
    register([snap(app, '09-error')], '3 · ERROR REAL DE VALIDACIÓN', '102 en base 2 → error: el dígito 2 no pertenece al sistema binario.', 'Ciento dos en base dos produce un error claro: dos no es un dígito binario.', 'Error real devuelto por Django')

    code('analyzer/forms.py', 20, 6, '2 · ANÁLISIS DE CARACTERES Y UTF-8 · 1.5 PUNTOS', 'TextForm.text recibe el texto y clean_text() lo envía a analyze_text().', 'Text Form recibe el texto y clean text lo envía al analizador de caracteres.')
    code('analyzer/services.py', 26, 16, '2 · ANÁLISIS DE CARACTERES Y UTF-8', 'Máximo 20 puntos de código · ord(char) → código · encode("utf-8") → bytes.', 'Analyze text admite veinte puntos de código. Ord obtiene el identificador; encode genera los bytes UTF ocho.')
    app.get_by_label('Texto (máximo 20 caracteres)').fill('España')
    app.get_by_role('button', name='Analizar texto').click()
    expect(app.get_by_role('cell', name='C3 B1', exact=True)).to_be_visible()
    app.locator('#text-result').scroll_into_view_if_needed()
    row = app.get_by_role('row').filter(has=app.get_by_role('cell', name='ñ', exact=True))
    # The row is highlighted with browser text selection, without altering its values.
    row.evaluate('(row) => {const range=document.createRange();range.selectNodeContents(row);const s=getSelection();s.removeAllRanges();s.addRange(range);}')
    register([snap(app, '12-utf8')], '2 · RESULTADO UTF-8 CON Ñ', 'ñ → decimal 241 · U+00F1 · hexadecimal F1 · bytes UTF-8 C3 B1.', 'La eñe tiene código doscientos cuarenta y uno y ocupa dos bytes: ce tres, be uno.', 'Tabla real: fila de ñ seleccionada')

    code('config/urls.py', 4, 5, '4 · ESTRUCTURA Y FUNCIONAMIENTO DJANGO · 1.5 PUNTOS', 'urls.py conecta / y /analizador/ con las vistas; render() entrega las plantillas.', 'Las rutas conectan portada y analizador con sus vistas y plantillas de Django.')
    code('analyzer/tests.py', 43, 8, '5 · PRUEBAS AUTOMATIZADAS · 1.0 PUNTO', 'tests.py: 14 pruebas de conversiones, límites, errores y UTF-8 con ñ.', 'Tests punto py incluye catorce pruebas de conversiones, límites, errores y el caso de la eñe.')

    def terminal(command, name, criterion, caption, speech, wait=4500):
        ide.keyboard.press('Escape')
        ide.keyboard.press('Meta+Shift+p')
        ide.keyboard.insert_text('Terminal: Create New Terminal')
        ide.wait_for_timeout(700)
        ide.keyboard.press('Enter')
        ide.wait_for_timeout(1000)
        maximize = ide.locator('[aria-label="Maximize Panel"]')
        if maximize.count() and maximize.first.is_visible():
            maximize.first.click()
        ide.keyboard.type("export PS1='$ '; clear", delay=3)
        ide.keyboard.press('Enter')
        ide.wait_for_timeout(500)
        ide.keyboard.type(command, delay=3)
        ide.keyboard.press('Enter')
        ide.wait_for_timeout(wait)
        register([snap(ide, name)], criterion, caption, speech, 'Terminal real de VS Code: '+command)

    terminal('docker compose exec -T web python manage.py test --verbosity 1', '15-tests-terminal', '5 · PRUEBAS EJECUTADAS EN PYTHON 3.12', 'docker compose exec -T web python manage.py test --verbosity 1 → 14 pruebas: OK.', 'Ejecutamos las pruebas dentro del contenedor: las catorce terminan correctamente.')
    code('Dockerfile', 1, 9, '6 · DOCKERFILE Y COMPOSE · 1.5 PUNTOS', 'FROM python:3.12-slim · instalación de dependencias · ejecución con Gunicorn.', 'El Dockerfile usa Python tres punto doce slim e inicia Django con Gunicorn.')
    code('compose.yaml', 3, 6, '6 · PUERTO Y LÍMITES DE RECURSOS', 'ports: 8000:8000 · mem_limit: 256m · cpus: 1.0.', 'Compose publica el puerto ocho mil y limita la memoria a doscientos cincuenta y seis megas y una CPU.')
    terminal("docker compose ps --format '{{.Service}}: {{.State}} ({{.Health}})'; docker stats --no-stream --format 'CPU: {{.CPUPerc}} | RAM: {{.MemUsage}}' $(docker compose ps -q web); docker inspect --format 'RAM={{.HostConfig.Memory}} CPU={{.HostConfig.NanoCpus}}' $(docker compose ps -q web)", '18-docker-terminal', '6 · CONTENEDOR ACTIVO Y DOCKER STATS', 'stats muestra consumo real; inspect confirma 268435456 bytes de RAM y 1000000000 NanoCPUs.', 'Docker stats muestra consumo real. Inspect confirma los límites de memoria y CPU aplicados.', wait=5500)
    code('README.md', 8, 5, '7 · README, EXPLICACIÓN Y EVIDENCIAS · 1.5 PUNTOS', 'README: comandos de construcción, ejecución, pruebas y verificación de recursos.', 'El README documenta cómo construir, ejecutar y verificar la aplicación.')
    code('README.md', 77, 20, '7 · VON NEUMANN Y KERNEL COMPARTIDO', 'CPU ejecuta · RAM almacena · E/S comunica. Docker comparte el kernel del host Linux.', 'La CPU ejecuta, la memoria guarda y la entrada y salida comunica. Docker comparte el kernel del host Linux.')

    context.close()
    browser.close()
    # Disconnect from CDP by ending Playwright; do not close the user's VS Code.

# Generate Spanish system narration and ensure the complete video stays below two minutes.
for i, scene in enumerate(SCENES):
    voice=WORK/f'{i:02d}-voice.aiff'
    run(['say','-v','Paulina','-r','195','-o',str(voice),scene['speech']],stdout=subprocess.DEVNULL)
    scene['voice']=str(voice)
    scene['voice_seconds']=seconds(voice)
raw=sum(s['voice_seconds']+.35 for s in SCENES)
speed=max(1.0, raw/114.0)
print(f'Narración: {raw:.2f}s; factor de tempo: {speed:.3f}',flush=True)

cursor=0
segments=[]
srt=[]
manifest=[]
for i, scene in enumerate(SCENES):
    length=math.ceil((scene['voice_seconds']/speed+.35)*24)/24
    head=WORK/f'{i:02d}-heading.txt'; head.write_text(scene['criterion'])
    caption=WORK/f'{i:02d}-caption.txt'; caption.write_text('\n'.join(textwrap.wrap(scene['caption'],105)))
    concat=WORK/f'{i:02d}-frames.ffconcat'
    frames=scene['frames']
    changes=min(.16,(length*.2)/max(1,len(frames)-1))
    lines=['ffconcat version 1.0']
    for frame in frames[:-1]: lines.extend([f"file '{frame}'",f'duration {changes:.4f}'])
    lines.extend([f"file '{frames[-1]}'",f'duration {length-changes*(len(frames)-1):.4f}',f"file '{frames[-1]}'"])
    concat.write_text('\n'.join(lines)+'\n')
    out=WORK/f'{i:02d}-segment.mp4'
    vf=(f'scale=1600:800:force_original_aspect_ratio=decrease,pad=1600:900:(ow-iw)/2:0:color=0x102019,'
        f'drawbox=x=0:y=800:w=1600:h=100:color=0x102019:t=fill,'
        f'drawtext=fontfile={FONT}:textfile={head}:fontcolor=0x9edbb4:fontsize=20:x=30:y=811,'
        f'drawtext=fontfile={FONT}:textfile={caption}:fontcolor=white:fontsize=23:line_spacing=4:x=30:y=842,'
        f'fps=24,tpad=stop_mode=clone:stop_duration={length:.6f}')
    run([FFMPEG,'-y','-f','concat','-safe','0','-i',str(concat),'-i',scene['voice'],'-vf',vf,'-af',f'atempo={speed:.6f},apad','-t',f'{length:.4f}','-frames:v',str(round(length*24)),'-fps_mode','cfr','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k',str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    segments.append(out)
    def timestamp(sec):
        ms=round(sec*1000); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    srt.append(f'{i+1}\n{timestamp(cursor)} --> {timestamp(cursor+length)}\n{scene["speech"]}\n')
    manifest.append({'start_seconds':round(cursor,2),'end_seconds':round(cursor+length,2),'criterion':scene['criterion'],'caption':scene['caption'],'narration':scene['speech'],'source':scene['source']})
    cursor+=length
    print(f'Render {i+1}/{len(SCENES)}',flush=True)
final_concat=WORK/'segments.ffconcat'
final_concat.write_text('ffconcat version 1.0\n'+'\n'.join(f"file '{part}'" for part in segments)+'\n')
final=OUT/'demostracion-rubrica.mp4'
run([FFMPEG,'-y','-f','concat','-safe','0','-i',str(final_concat),'-c','copy','-movflags','+faststart',str(final)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
(OUT/'demostracion-rubrica.srt').write_text('\n'.join(srt))
(OUT/'rubric-video'/'timeline.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
assert seconds(final)<120, 'El video excede los dos minutos.'
print(f'Video terminado: {seconds(final):.2f}s; {final.stat().st_size} bytes',flush=True)
