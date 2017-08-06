import gc
import micropython
import machine

from json import dumps as json_dump
from urequests import post

from logging import getLogger

import led
import wifi
import sensors.light
import settings
from util import log_exception

micropython.alloc_emergency_exception_buf(100)
gc.collect()  # clean up mem after imports

log = getLogger(__name__)

SLEEP_TIME = 1000 * settings.SLEEP_INTERVAL


def get_data():
    """Get data to publish as a JSON string."""
    return json_dump({
        'location': settings.LOCATION.lower(),
        'luminosity': sensors.light.get_data(),
        'gc_mem_free': gc.mem_free(),

    })


def publish(data):
    """Publish sensor and memory details to Seriesly."""

    with wifi.connection():
        resp = post(
            settings.DB_URI,
            data=data
        )

    status = resp.status_code

    resp.close()

    if status != 201:
        log.warn('could not store %s', data)
        led.blink(settings.BLINK_TIMEOUT)
        led.blink(settings.BLINK_TIMEOUT)
        led.blink(settings.BLINK_TIMEOUT)
        return False

    log.info('successfully stored %s', data)
    return True


def execute():
    """Wake, connect to nwifi, publish details, and go back to sleep."""
    gc.collect()
    publish(get_data())


def sleep():
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, SLEEP_TIME)
    log.info('Sleeping for %s seconds', settings.SLEEP_INTERVAL)
    machine.deepsleep()


def main():
    try:
        execute()
    except Exception as e:
        log_exception(e)

    sleep()


if __name__ == '__main__':
    main()
