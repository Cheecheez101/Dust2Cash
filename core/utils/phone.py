import os
import re

DEFAULT_COUNTRY_CODE = os.getenv('DEFAULT_PHONE_COUNTRY_CODE', '254')


def normalize_phone_number(raw_number: str) -> str:
    if not raw_number:
        raise ValueError('Phone number is required')

    cleaned = re.sub(r'[^0-9+]', '', str(raw_number).strip())
    if cleaned.startswith('+2547'):
        normalized = cleaned
    elif cleaned.startswith('07'):
        normalized = f'+254{cleaned[1:]}'
    elif cleaned.startswith('2547'):
        normalized = f'+{cleaned}'
    elif cleaned.startswith('+'):
        normalized = cleaned
    else:
        raise ValueError('Invalid phone number format')

    if len(normalized) < 10 or len(normalized) > 15:
        raise ValueError('Phone number must be between 10 and 15 digits including country code')

    return normalized
