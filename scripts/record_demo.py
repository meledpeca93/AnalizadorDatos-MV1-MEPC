"""Optional developer tool: pip install playwright imageio-ffmpeg.
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/analyzer-playwright python scripts/record_demo.py
Requires Playwright Chromium and the running Compose service. Records real HTTP interactions
and displays output captured from real Docker commands; does not alter the app.
"""
import html
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / 'evidence'


def command(args):
    proc = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return '$ ' + ' '.join(args) + '\n\n' + proc.stdout


def log_page(page, title, output):
    page.set_content('<html lang="es"><meta charset="utf-8"><body style="margin:36px;background:#102337;color:#d8f6ec;font-family:monospace"><h1 style="font-size:25px">' + html.escape(title) + '</h1><p>Salida real de comandos ejecutados durante esta grabación</p><pre style="font-size:16px;line-height:1.4;white-space:pre-wrap">' + html.escape(output) + '</pre></body></html>')


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 900}, record_video_dir=str(EVIDENCE / 'raw-video'), record_video_size={'width': 1280, 'height': 900})
    page = context.new_page()
    page.goto('http://127.0.0.1:8000/')
    page.screenshot(path=str(EVIDENCE / 'home.png'), full_page=True)
    page.wait_for_timeout(3000)
    page.get_by_role('link', name='Entrar al analizador').click()
    page.wait_for_timeout(1500)
    page.get_by_role('textbox', name='Número:', exact=True).fill('100')
    page.get_by_label('Base de origen').select_option('16')
    page.get_by_role('button', name='Convertir número').click()
    page.locator('dd').filter(has_text='0000000100000000').wait_for()
    page.screenshot(path=str(EVIDENCE / 'conversion.png'), full_page=True)
    page.wait_for_timeout(6500)
    page.get_by_role('textbox', name='Número:', exact=True).fill('102')
    page.get_by_label('Base de origen').select_option('2')
    page.get_by_role('button', name='Convertir número').click()
    page.get_by_text('Dígitos inválidos', exact=False).wait_for()
    page.screenshot(path=str(EVIDENCE / 'validation.png'), full_page=True)
    page.wait_for_timeout(5000)
    page.get_by_label('Texto (máximo 20 caracteres)').fill('España')
    page.get_by_role('button', name='Analizar texto').click()
    page.get_by_role('cell', name='C3 B1', exact=True).wait_for()
    page.screenshot(path=str(EVIDENCE / 'utf8.png'), full_page=True)
    page.wait_for_timeout(6500)
    # Independent responsive check; return to desktop for the evidence views.
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.screenshot(path=str(EVIDENCE / 'mobile.png'), full_page=True)
    page.set_viewport_size({'width': 1280, 'height': 900})
    tests = command(['docker', 'compose', 'exec', '-T', 'web', 'python', 'manage.py', 'test', '--verbosity', '2'])
    log_page(page, '14 pruebas automatizadas · Python 3.12 en Docker', tests)
    page.screenshot(path=str(EVIDENCE / 'tests.png'), full_page=True)
    page.wait_for_timeout(8000)
    container = subprocess.check_output(['docker', 'compose', 'ps', '-q', 'web'], cwd=ROOT, text=True).strip()
    stats = '\n'.join([command(['docker', 'compose', 'exec', '-T', 'web', 'python', '--version']), command(['docker', 'compose', 'ps']), command(['docker', 'stats', '--no-stream', container]), command(['docker', 'inspect', '--format', 'Memory={{.HostConfig.Memory}} NanoCpus={{.HostConfig.NanoCpus}}', container])])
    log_page(page, 'Contenedor activo · límite 256 MiB / 1 CPU', stats)
    page.screenshot(path=str(EVIDENCE / 'container.png'), full_page=True)
    page.wait_for_timeout(9000)
    video = page.video
    context.close()
    source = video.path()
    browser.close()

import imageio_ffmpeg
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-i', str(source), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(EVIDENCE / 'demostracion.mp4')], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('Video generado: evidence/demostracion.mp4')
