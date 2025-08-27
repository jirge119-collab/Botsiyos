import re

def is_luhn_valid(card_number: str) -> bool:
    """
    Valida un número de tarjeta usando el algoritmo de Luhn.
    """
    try:
        # Limpiar el número de tarjeta de cualquier caracter que no sea un dígito
        card_number = re.sub(r'\D', '', card_number)
        if not card_number.isdigit():
            return False

        num_digits = len(card_number)
        s = 0
        parity = (num_digits - 1) % 2

        for i, digit in enumerate(card_number):
            d = int(digit)
            if i % 2 == parity:
                d *= 2
            if d > 9:
                d -= 9
            s += d

        return s % 10 == 0
    except (ValueError, TypeError):
        return False

def get_card_brand(card_number: str) -> str:
    """
    Identifica la marca de la tarjeta basándose en su número.
    """
    card_number = re.sub(r'\D', '', card_number)

    # Patrones de IIN (Issuer Identification Number)
    if re.match(r"^4[0-9]{12}(?:[0-9]{3})?$", card_number):
        return "Visa"
    elif re.match(r"^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$", card_number):
        return "Mastercard"
    elif re.match(r"^3[47][0-9]{13}$", card_number):
        return "American Express"
    elif re.match(r"^6(?:011|5[0-9]{2})[0-9]{12}$", card_number):
        return "Discover"
    elif re.match(r"^3(?:0[0-5]|[68][0-9])[0-9]{11}$", card_number):
        return "Diners Club"
    elif re.match(r"^(?:2131|1800|35\d{3})\d{11}$", card_number):
        return "JCB"
    else:
        return "Unknown"
