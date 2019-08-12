def convert_lm94022_temperature(x, calibration_temperature_offset):
    return 453.512485591335 - 163.565776259726 * x - 10.5408332222805 * (x ** 2) - calibration_temperature_offset


def convert_soil_moisture(x):
    x = (8.130159393183e-018 * x ** 5
         - 0.000000000000259586800701037 * x ** 4
         + 0.00000000328783014726288 * x ** 3
         - 0.0000206371829755294 * x ** 2
         + 0.0646453707101697 * x
         - 79.7740602786336)
    return 100 * 10 ** max(0, min(6, x))


def convert_tsl2561_light(x):
    x = int(x)
    data0 = (x >> 16) & 0xfffe
    data1 = x & 0xfffe
    gain = (x >> 16) & 0x1
    int_time = x & 0x1
    if gain == 0x0:
        data0 *= 16
        data1 *= 16
    if int_time == 0x0:
        data0 *= 1 / 0.252
        data1 *= 1 / 0.252
    if data0 == 0 or data1 / data0 > 1.30:
        return 0.0
    elif data1 / data0 > 0.8:
        return 0.00146 * data0 - 0.00112 * data1
    elif data1 / data0 > 0.61:
        return 0.0128 * data0 - 0.0153 * data1
    elif data1 / data0 > 0.50:
        return 0.0224 * data0 - 0.031 * data1
    else:
        return 0.0304 * data0 - 0.062 * data0 * (data1 / data0) ** 1.4


# We are configuring all sensors, the device will ignore unavailable sensors
# Sensor Type ID: (type, enabled, polling interval, conversion function)
SENSORS = {
    1: ("board temperature", False, 3600, lambda x: x),
    2: ("battery voltage", True, 86400, lambda x: x),
    6: ("button", True, None, lambda x: x / 1000),
    7: ("temperature", True, 3600, convert_lm94022_temperature),
    8: ("light", True, 3600, lambda x: 3333326.67 * ((abs(x) + x) / 2)),
    9: ("rssi", True, None, lambda x: x),
    10: ("soil sensors trigger", True, 18000, None),
    11: ("soil temperature", True, None, lambda x: x),
    12: ("soil moisture", True, None, convert_soil_moisture),
    15: ("temperature", True, 3600, lambda x: -46.85 + 175.72 * x / 2 ** 16),
    29: ("light", True, 3600, convert_tsl2561_light),
    # statistics
    4096: ("", False, None, None),
    4112: ("", False, None, None),
    4113: ("", False, None, None),
    4114: ("", False, None, None),
    4115: ("", False, None, None),
    4116: ("", False, None, None),
    4128: ("", False, None, None),
    # errors
    8192: ("", False, None, None),
    8193: ("", False, None, None),
    8194: ("", False, None, None),
    8195: ("", False, None, None),
}
