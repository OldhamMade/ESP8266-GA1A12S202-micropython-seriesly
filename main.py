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


def publish():
    """Publish sensor and memory details to Seriesly."""
    luminosity = sensors.light.get_data()

    data = json_dump({
        'location': settings.LOCATION.lower(),
        'luminosity': luminosity,
        'gc_mem_free': gc.mem_free(),

    })

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
    wifi.connect()
    publish()


def sleep():
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, 1000 * settings.SLEEP_INTERVAL)
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
