from django.test import SimpleTestCase, Client
from .services import convert_number, analyze_text


class ConversionTests(SimpleTestCase):
    def test_valid_bases(self):
        for raw, base in [('11111111', 2), ('377', 8), ('255', 10), ('fF', 16)]:
            with self.subTest(base=base):
                self.assertEqual(convert_number(raw, base), {'decimal': 255, 'binary': '11111111', 'octal': '377', 'hexadecimal': 'FF', 'bits': 8, 'bytes': 1})

    def test_byte_boundaries(self):
        for raw, bits, count in [('0', 1, 1), ('1', 1, 1), ('127', 7, 1), ('256', 9, 2), ('65535', 16, 2)]:
            with self.subTest(raw=raw):
                result = convert_number(raw, 10)
                self.assertEqual((result['bits'], result['bytes']), (bits, count))
                self.assertEqual(len(result['binary']), count * 8)
                self.assertEqual(int(result['binary'], 2), int(raw))
        self.assertEqual(convert_number('0', 10)['binary'], '00000000')

    def test_invalid_digits(self):
        for raw, base in [('102', 2), ('8', 8), ('a', 10), ('G', 16), ('0xFF', 16), ('1_0', 10), ('+1', 10), ('１', 10)]:
            with self.subTest(raw=raw, base=base), self.assertRaisesRegex(ValueError, 'Dígitos inválidos'):
                convert_number(raw, base)

    def test_invalid_base(self):
        with self.assertRaisesRegex(ValueError, 'base válida'):
            convert_number('10', 3)

    def test_out_of_range(self):
        for raw, base in [('65536', 10), ('10000', 16), ('200000', 8), ('1' * 17, 2), ('9' * 5000, 10)]:
            with self.subTest(base=base), self.assertRaisesRegex(ValueError, 'entre 0 y 65 535'):
                convert_number(raw, base)

    def test_empty_and_negative(self):
        for raw, message in [('', 'Ingrese'), ('   ', 'Ingrese'), ('-1', 'negativos')]:
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, message):
                convert_number(raw, 10)

    def test_leading_zeros(self):
        self.assertEqual(convert_number('0' * 5000 + '1', 10)['decimal'], 1)


class TextTests(SimpleTestCase):
    def test_enye_utf8(self):
        row = analyze_text('ñ')[0]
        self.assertEqual(row, {'character': 'ñ', 'decimal': 241, 'codepoint': 'U+00F1', 'hexadecimal': 'F1', 'utf8': 'C3 B1', 'byte_count': 2})

    def test_multibyte_and_space(self):
        self.assertEqual(analyze_text('🌎')[0]['utf8'], 'F0 9F 8C 8E')
        self.assertEqual(analyze_text(' ')[0]['utf8'], '20')

    def test_length(self):
        self.assertEqual(len(analyze_text('ñ' * 20)), 20)
        for text in ['', 'a' * 21]:
            with self.assertRaises(ValueError):
                analyze_text(text)


class PageTests(SimpleTestCase):
    def test_get_and_post(self):
        self.assertContains(self.client.get('/'), 'Analizador de representación de datos')
        response = self.client.post('/', {'action': 'number', 'number': '100', 'base': '16'})
        self.assertContains(response, '0000000100000000')
        self.assertContains(self.client.post('/', {'action': 'text', 'text': 'ñ'}), 'C3 B1')

    def test_form_errors(self):
        for data, message in [({'action': 'number', 'number': '', 'base': '10'}, 'Ingrese un número'), ({'action': 'number', 'number': '-1', 'base': '10'}, 'negativos'), ({'action': 'number', 'number': '2', 'base': '2'}, 'Dígitos inválidos'), ({'action': 'number', 'number': '65536', 'base': '10'}, '65 535'), ({'action': 'number', 'number': '1', 'base': '3'}, 'base válida'), ({'action': 'text', 'text': ''}, 'Ingrese un texto'), ({'action': 'text', 'text': 'a' * 21}, 'máximo 20'), ({'action': 'other'}, 'operación válida')]:
            with self.subTest(data=data):
                self.assertContains(self.client.post('/', data), message)

    def test_html_is_escaped(self):
        response = self.client.post('/', {'action': 'text', 'text': '<script>'})
        self.assertNotContains(response, '<script>')
        self.assertContains(response, '&lt;')

    def test_csrf_protection(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post('/', {'action': 'text', 'text': 'ñ'}).status_code, 403)
