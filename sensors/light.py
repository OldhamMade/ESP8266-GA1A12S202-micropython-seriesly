from machine import ADC

import settings

PIN = ADC(settings.PIN_LIGHT_SENSOR)


def get_data():
    """Return the current luminosity."""
    return PIN.read()
