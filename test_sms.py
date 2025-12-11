import os
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager


class TLS12HttpAdapter(HTTPAdapter):
    """Forces requests to negotiate TLS 1.2 when talking to Africa's Talking."""

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        pool_kwargs['ssl_context'] = ctx
        return super().init_poolmanager(connections, maxsize, block, **pool_kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        proxy_kwargs['ssl_context'] = ctx
        return super().proxy_manager_for(proxy, **proxy_kwargs)


url = os.getenv('AFRICAS_TALKING_SMS_URL', 'https://api.sandbox.africastalking.com/version1/messaging')
headers = {
    'apiKey': os.getenv('AFRICAS_TALKING_API_KEY', ''),
    'Content-Type': 'application/x-www-form-urlencoded',
}
data = {
    'username': os.getenv('AFRICAS_TALKING_USERNAME', 'sandbox'),
    'to': os.getenv('TEST_SMS_PHONE', '+254703241748'),
    'message': 'Test OTP from Dust2Cash',
}

session = requests.Session()
session.mount('https://', TLS12HttpAdapter())
response = session.post(url, headers=headers, data=data, timeout=20, verify=True)
print(response.status_code)
print(response.text)
