from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_safe
from .forms import NumberForm, TextForm


@require_safe
def home(request):
    return render(request, 'analyzer/home.html')


@require_safe
@cache_control(public=True, max_age=86400)
def uth_logo(request):
    # Serve the supplied identity asset with Gunicorn too, without DEBUG/static serving.
    return FileResponse((settings.BASE_DIR / 'UTH Logo.png').open('rb'), content_type='image/png')


def index(request):
    number_form, text_form = NumberForm(), TextForm()
    result, rows = None, None
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'number':
            number_form = NumberForm(request.POST)
            if number_form.is_valid():
                result = number_form.result
        elif action == 'text':
            text_form = TextForm(request.POST)
            if text_form.is_valid():
                rows = text_form.rows
        else:
            number_form = NumberForm(request.POST)
            number_form.is_valid()
            number_form.add_error(None, 'Seleccione una operación válida.')
    byte_groups = []
    padding_bits = 0
    if result:
        padding_bits = len(result['binary']) - result['bits']
        bits = [{'value': bit, 'padding': i < padding_bits} for i, bit in enumerate(result['binary'])]
        byte_groups = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    base = number_form['base'].value()
    allowed_digits = {'2': '0 y 1', '8': 'del 0 al 7', '10': 'del 0 al 9', '16': 'del 0 al 9 y de A a F (también minúsculas)'}.get(str(base), 'Seleccione una base válida.')
    return render(request, 'analyzer/index.html', {'number_form': number_form, 'text_form': text_form, 'result': result, 'rows': rows, 'byte_groups': byte_groups, 'padding_bits': padding_bits, 'utf8_total': sum(row['byte_count'] for row in rows or []), 'allowed_digits': allowed_digits})
