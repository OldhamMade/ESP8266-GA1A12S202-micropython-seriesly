from esp import sleep_type as sleep, SLEEP_MODEM
from network import WLAN, STA_IF
from logging import getLogger

import settings

log = getLogger(__name__)
net = None


def connect():
    """Connect to the local wifi network."""
    global net
    net = WLAN(STA_IF)
    if not net.isconnected():
        log.warning(
            "no network, attempting to connect to %s",
            settings.WIFI_SSID
        )
        net.active(True)
        net.connect(settings.WIFI_SSID, settings.WIFI_PW)
        while not net.isconnected():
            pass
    status()


class ConnectionContextManager(object):
    """Context manager to a wifi connection to blocks."""

    def __enter__(self):
        return connect()

    def __exit__(self, type, value, traceback):
        sleep(SLEEP_MODEM)
        return True


connection = ConnectionContextManager


def status():
    """Log the status of the wifi connection."""
    try:
        log.info('network config: %s', net.ifconfig())
    except AttributeError:
        log.warning('network not connected')
