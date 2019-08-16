def convert_lm94022_temperature(x, calibration_parameters):
    x = (x - calibration_parameters['RN171_SMU_DC_OFFSET']) * calibration_parameters['RN171_SMU_GAIN'] * 3.0
    x = (453.512485591335 - 163.565776259726 * x - 10.5408332222805 * (x ** 2)
         - calibration_parameters['LM94022_TEMPERATURE_OFFSET'])
    return x


def convert_sfh3710_light(x, calibration_parameters):
    x = ((x - calibration_parameters['SFH3710_DC_OFFSET_CORRECTION'])
         * calibration_parameters['RN171_SMU_GAIN'] / 20.0 * 7.2)
    x = 3333326.67 * ((abs(x) + x) / 2)
    return x


def convert_soil_moisture(x, calibration_parameters):
    x = ((x - calibration_parameters['SOIL_MOISTURE_MIN'])
         * ((8778.25 - 3515.25) / (calibration_parameters['SOIL_MOISTURE_DISCONTINUITY']
                                   - calibration_parameters['SOIL_MOISTURE_MIN'])) + 3515.25)
    x = (8.130159393183e-018 * x ** 5
         - 0.000000000000259586800701037 * x ** 4
         + 0.00000000328783014726288 * x ** 3
         - 0.0000206371829755294 * x ** 2
         + 0.0646453707101697 * x
         - 79.7740602786336)
    return max(0, min(6, x))


def convert_tsl2561_light(x, _calibration_parameters):
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
        y = 0.0
    elif data1 / data0 > 0.8:
        y = 0.00146 * data0 - 0.00112 * data1
    elif data1 / data0 > 0.61:
        y = 0.0128 * data0 - 0.0153 * data1
    elif data1 / data0 > 0.50:
        y = 0.0224 * data0 - 0.031 * data1
    else:
        y = 0.0304 * data0 - 0.062 * data0 * (data1 / data0) ** 1.4
    return y * 5.0


# We are configuring all sensors, the device will ignore unavailable sensors
# Sensor Type ID: (type, enabled, polling interval, conversion function)
SENSORS = {
    1: ("board_temperature", False, 3600, lambda x, _: x),
    2: ("battery_voltage", True, 86400, lambda x, _: x),
    6: ("button", True, None, lambda x, _: x / 1000),
    7: ("temperature", True, 3600, convert_lm94022_temperature),
    8: ("light", True, 3600, convert_sfh3710_light),
    9: ("rssi", True, None, lambda x, _: x),
    10: ("soil_sensors_trigger", True, 18000, None),
    11: ("soil_temperature", True, None, lambda x, _: x - 2.5),
    12: ("soil_moisture", True, None, convert_soil_moisture),
    15: ("temperature", True, 3600, lambda x, _: -46.85 + 175.72 * x / 2 ** 16),
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
