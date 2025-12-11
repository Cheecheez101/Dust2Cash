import os
import logging
import random
import httpx
from httpx import HTTPError
from django.core.cache import cache
from core.models import AccountVerification
from core.utils.phone import normalize_phone_number
from typing import Any, Dict

username = os.getenv('AFRICAS_TALKING_USERNAME', 'sandbox')
api_key = os.getenv('AFRICAS_TALKING_API_KEY')
sms_api_url = os.getenv('AFRICAS_TALKING_SMS_URL', 'https://api.sandbox.africastalking.com/version1/messaging')
if not api_key:
    logging.warning('AFRICAS_TALKING_API_KEY is unset; SMS sending will fail.')

OTP_CACHE_KEY = 'otp:{phone}'


def _send_via_rest(phone_number: str, message: str) -> str:
    payload = {
        'username': username,
        'to': phone_number,
        'message': message,
    }
    headers = {
        'apiKey': api_key or '',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    # httpx handles TLS/HTTP2 better than requests on OpenSSL 3.x
    with httpx.Client(http2=True, timeout=30.0) as client:
        response = client.post(sms_api_url, headers=headers, data=payload)
        logging.info("Africa's Talking raw response: %s", response.text)
        response.raise_for_status()
        return response.text


def send_otp(phone_number: str) -> str:
    normalized_phone = normalize_phone_number(phone_number)
    logging.info('Normalized phone number: %s', normalized_phone)
    otp = str(random.randint(100000, 999999))
    message = f"Your Dust2Cash verification code is {otp}"
    try:
        gateway_response = _send_via_rest(normalized_phone, message)
    except HTTPError as exc:
        logging.error('Failed to send OTP via REST API: %s', exc)
        raise ValueError('Unable to reach the SMS gateway; please try again later.') from exc
    cache.set(OTP_CACHE_KEY.format(phone=normalized_phone), otp, timeout=300)
    return gateway_response


def verify_otp(phone_number: str, user_input: str, *, user=None) -> bool:
    normalized_phone = normalize_phone_number(phone_number)
    cached_otp = cache.get(OTP_CACHE_KEY.format(phone=normalized_phone))
    if cached_otp and cached_otp == user_input:
        cache.delete(OTP_CACHE_KEY.format(phone=normalized_phone))
        if user is not None:
            account = AccountVerification.objects.get_or_create(user=user)[0]
            account.mark_phone_verified()
        return True
    return False
