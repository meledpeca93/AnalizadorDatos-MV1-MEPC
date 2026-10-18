from django import forms
from .services import convert_number, analyze_text


class NumberForm(forms.Form):
    number = forms.CharField(label='Número', required=False, strip=False, widget=forms.TextInput(attrs={'placeholder': 'Ej. 255', 'autocomplete': 'off', 'aria-describedby': 'number-help base-help', 'spellcheck': 'false'}))
    base = forms.TypedChoiceField(label='Base de origen', choices=[(2, 'Binario · base 2'), (8, 'Octal · base 8'), (10, 'Decimal · base 10'), (16, 'Hexadecimal · base 16')], coerce=int, initial=10, error_messages={'invalid_choice': 'Seleccione una base válida: 2, 8, 10 o 16.', 'required': 'Seleccione una base de origen.'})

    def clean(self):
        data = super().clean()
        if 'base' in data:
            try:
                self.result = convert_number(data.get('number', ''), data['base'])
            except ValueError as exc:
                self.add_error('number', str(exc))
        return data


class TextForm(forms.Form):
    text = forms.CharField(label='Texto (máximo 20 caracteres)', required=False, strip=False, widget=forms.TextInput(attrs={'placeholder': 'Escriba algo, por ejemplo España', 'autocomplete': 'off', 'aria-describedby': 'text-help', 'spellcheck': 'false'}))

    def clean_text(self):
        text = self.cleaned_data['text']
        try:
            self.rows = analyze_text(text)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return text
