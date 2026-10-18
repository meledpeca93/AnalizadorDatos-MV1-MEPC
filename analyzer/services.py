DIGITS = {2: '01', 8: '01234567', 10: '0123456789', 16: '0123456789abcdefABCDEF'}


def convert_number(raw, base):
    if base not in DIGITS:
        raise ValueError('Seleccione una base válida: 2, 8, 10 o 16.')
    value = raw.strip()
    if not value:
        raise ValueError('Ingrese un número.')
    if value.startswith('-'):
        raise ValueError('No se permiten valores negativos.')
    if any(char not in DIGITS[base] for char in value):
        raise ValueError(f'Dígitos inválidos para la base {base}. Use únicamente {DIGITS[base]}.')
    # Remove leading zeros before parsing to avoid Python integer-string limits.
    significant = value.lstrip('0') or '0'
    if len(significant) > {2: 16, 8: 6, 10: 5, 16: 4}[base]:
        raise ValueError('El valor debe estar entre 0 y 65 535.')
    number = int(significant, base)
    if number > 65535:
        raise ValueError('El valor debe estar entre 0 y 65 535.')
    bits = max(1, number.bit_length())
    byte_count = (bits + 7) // 8
    return {'decimal': number, 'binary': format(number, f'0{byte_count * 8}b'), 'octal': format(number, 'o'), 'hexadecimal': format(number, 'X'), 'bits': bits, 'bytes': byte_count}


def analyze_text(text):
    if not text:
        raise ValueError('Ingrese un texto.')
    if len(text) > 20:
        raise ValueError('El texto debe tener como máximo 20 caracteres.')
    rows = []
    for char in text:
        try:
            encoded = char.encode('utf-8')
        except UnicodeEncodeError as exc:
            raise ValueError('El texto contiene un carácter Unicode no válido.') from exc
        rows.append({'character': char, 'decimal': ord(char), 'codepoint': f'U+{ord(char):04X}', 'hexadecimal': f'{ord(char):X}', 'utf8': ' '.join(f'{byte:02X}' for byte in encoded), 'byte_count': len(encoded)})
    return rows
