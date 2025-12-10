import os
import logging
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk import (
    TransactionalEmailsApi,
    SendSmtpEmail,
    SendSmtpEmailSender,
    SendSmtpEmailTo,
)


# Helper to send transactional emails via Sendinblue (Brevo)
# Mirrors the portfolio snippet: configure the SDK with an API key and call send_transac_email

SIB_API_KEY = os.getenv('SIB_API_KEY') or os.getenv('BREVO_API_KEY')
SIB_SENDER_EMAIL = os.getenv('SIB_SENDER_EMAIL') or os.getenv('BREVO_SENDER_EMAIL')
SIB_SENDER_NAME = os.getenv('SIB_SENDER_NAME') or os.getenv('BREVO_SENDER_NAME')

logger = logging.getLogger(__name__)

if not SIB_API_KEY:
    # We don't raise at import time to allow local dev without SIB configured; functions will raise if used.
    pass


def _get_api_client():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = SIB_API_KEY
    api_client = sib_api_v3_sdk.ApiClient(configuration)
    return TransactionalEmailsApi(api_client)


def is_email_client_configured() -> bool:
    """Lightweight probe for templates/views to check if Brevo is ready."""
    return bool(SIB_API_KEY and (SIB_SENDER_EMAIL or SIB_SENDER_NAME))


def send_transactional_email(
    to_email: str,
    subject: str,
    html_content: str,
    *,
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None,
    text_content: Optional[str] = None,
) -> dict:
    """Send a transactional HTML email via Sendinblue.

    Returns the API response dict on success. Raises RuntimeError on missing config or ApiException on API errors.
    """
    if not SIB_API_KEY:
        raise RuntimeError("SIB_API_KEY (BREVO_API_KEY) environment variable is not set")

    sender_email = sender_email or SIB_SENDER_EMAIL
    sender_name = sender_name or SIB_SENDER_NAME or 'Dust2Cash'
    if not sender_email:
        raise RuntimeError("Sender email not configured: set SIB_SENDER_EMAIL or BREVO_SENDER_EMAIL")

    api = _get_api_client()

    sender = SendSmtpEmailSender(name=sender_name, email=sender_email)
    to = [SendSmtpEmailTo(email=to_email)]
    message = SendSmtpEmail(
        sender=sender,
        to=to,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )

    try:
        result = api.send_transac_email(message)
        # The SDK returns an object; convert to dict for easier handling
        return result.to_dict() if hasattr(result, 'to_dict') else result
    except ApiException as e:
        # Re-raise with a clearer message
        logger.exception("Sendinblue API error when sending to %s", to_email)
        raise RuntimeError(f"Sendinblue API error: {e}")


__all__ = ['send_transactional_email', 'is_email_client_configured']
