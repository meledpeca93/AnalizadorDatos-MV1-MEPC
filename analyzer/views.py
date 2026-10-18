from django.shortcuts import render
from .forms import NumberForm, TextForm


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
    return render(request, 'analyzer/index.html', {'number_form': number_form, 'text_form': text_form, 'result': result, 'rows': rows})
