import logging
from importlib import import_module

from django.conf import settings

logger = logging.getLogger(__name__)


class BaseSMSAdapter:
    """Base class for SMS delivery adapters."""

    def send(self, phone_number, message):
        """Send an SMS message. Returns True on success, False on failure."""
        raise NotImplementedError


class DummySMSAdapter(BaseSMSAdapter):
    """Logs SMS to console. Ships as default until SMPP is configured."""

    def send(self, phone_number, message):
        logger.info("SMS [DUMMY] to %s: %s", phone_number, message)
        return True


def get_sms_adapter():
    """Load the SMS adapter class from Django settings."""
    adapter_path = getattr(
        settings,
        "NOTIFICATION_SMS_ADAPTER",
        "notification.adapters.DummySMSAdapter",
    )
    module_path, class_name = adapter_path.rsplit(".", 1)
    module = import_module(module_path)
    adapter_class = getattr(module, class_name)
    return adapter_class()
