#!/usr/bin/python3

import os
import time
import json
from typing import Dict, Iterable, List, Mapping, NamedTuple, Tuple, Union
from http.server import BaseHTTPRequestHandler
import yaml
from flask import Flask, request, Response
import paho.mqtt.publish as publish
from koubachi_pyserver.crypto import decrypt, encrypt
from koubachi_pyserver.sensors import Sensor, SENSORS

CONFIG_FILE = "config.yml"

# The sensor only accepts HTTP/1.1
BaseHTTPRequestHandler.protocol_version = 'HTTP/1.1'

CONTENT_TYPE = "application/x-koubachi-aes-encrypted"

app = Flask(__name__)


class RawReading(NamedTuple):
    timestamp: int
    sensor_type_id: int
    raw_value: Union[int, float]


class Reading(NamedTuple):
    timestamp: int
    sensor_type: str
    value: float
    raw_value: Union[int, float]


def get_device_key(mac_address: str) -> bytes:
    return bytes.fromhex(app.config['devices'][mac_address]['key'])


def get_device_calibration_parameters(mac_address: str) -> Mapping[str, float]:
    calibration_parameters = app.config['devices'][mac_address]['calibration_parameters']
    assert isinstance(calibration_parameters, dict)
    return calibration_parameters


def get_device_config(_mac_address: str) -> str:
    cfg = {
        "transmit_interval": 55202,
        "transmit_app_led": 1,
        "sensor_app_led": 0,
        "day_threshold": 10.0,
    }
    cfg.update({f"sensor_enabled[{k}]": int(v[1]) for k, v in SENSORS.items()})
    cfg.update({f"sensor_polling_interval[{k}]": v[2] for k, v in SENSORS.items() if v[1] and v[2] is not None})
    return "&".join([f"{k}={v}" for k, v in cfg.items()])


def get_device_last_config_change(_mac_address: str) -> int:
    return int(app.config['last_config_change'])


def convert_readings(mac_address: str, body: Mapping[str, Iterable[Tuple[int, int, float]]]) -> Iterable[Reading]:
    calibration_parameters = get_device_calibration_parameters(mac_address)
    readings = []
    for rdng in body['readings']:
        raw_reading = RawReading(*rdng)
        sensor = SENSORS.get(raw_reading.sensor_type_id, Sensor('', False, None, None))
        if not sensor.enabled or sensor.conversion_func is None:
            continue
        readings.append(Reading(
            raw_reading.timestamp,
            sensor.type,
            sensor.conversion_func(raw_reading.raw_value, calibration_parameters),
            raw_reading.raw_value,
        ))
    return readings


def get_mqtt_config(output: Dict[str, str]) -> Dict[str, Union[str, Dict[str, str]]]:
    cfg: Dict[str, Union[str, Dict[str, str]]] = {k: v for k, v in output.items() if k in ['topic', 'hostname']}
    username = output.get('username', None)
    if username is not None:
        auth = {'username': username}
        password = output.get('password', None)
        if password is not None:
            auth['password'] = password
        cfg['auth'] = auth
    return cfg


def handle_readings(mac_address: str, readings: Iterable[Reading]) -> None:
    output: Dict[str, str] = app.config['output']
    if output['type'] == 'csv_files':
        write_to_csv(mac_address, readings, directory=output['directory'])
    elif output['type'] == 'thingsboard_mqtt':
        cfg = get_mqtt_config(output)
        post_to_thingsboard_mqtt(mac_address, readings, **cfg)
    elif output['type'] == 'latestvals_mqtt':
        cfg = get_mqtt_config(output)
        assert isinstance(cfg['topic'], str)
        cfg['topic'] += '/' + mac_address
        post_to_latestvals_mqtt(readings, **cfg)
    else:
        NotImplementedError("Output type not implemented.")


def write_to_csv(mac_address: str, readings: Iterable[Reading], directory: str) -> None:
    grouped_readings: Dict[str, List[Reading]] = {}
    for reading in readings:
        grouped_readings.setdefault(reading.sensor_type, []).append(reading)
    for sensor_type, rdngs in grouped_readings.items():
        file_path = os.path.join(directory, f"{mac_address}_{sensor_type}.csv")
        try:
            with open(file_path, 'x') as file:
                # create file and write header line
                file.write(f"timestamp,{sensor_type},raw_value\r\n")
        except FileExistsError:
            pass
        with open(file_path, 'a') as file:
            file.writelines([f"{reading1.timestamp},{reading1.value},{reading1.raw_value}\r\n" for reading1 in rdngs])


def post_to_thingsboard_mqtt(mac_address: str, readings: Iterable[Reading],
                             **kwargs: Union[str, Mapping[str, str]]) -> None:
    if readings:
        thingsboard_payload = {
            mac_address: [{
                'ts': reading.timestamp * 1000,
                'values': {
                    reading.sensor_type: reading.value
                }
            } for reading in readings]
        }
        publish.single(payload=json.dumps(thingsboard_payload), **kwargs)


def post_to_latestvals_mqtt(readings: Iterable[Reading],
                            **kwargs: Union[str, Mapping[str, str]]) -> None:
    if readings:
        mqtt_payload = dict()
        # assuming readings as sorted by time, so new values overwrite old ones
        for reading in readings:
            mqtt_payload[reading.sensor_type] = reading.value
        publish.single(payload=json.dumps(mqtt_payload), **kwargs)


@app.route('/v1/smart_devices/<mac_address>', methods=['PUT'])
def connect(mac_address: str) -> Response:
    key = get_device_key(mac_address)
    _body = decrypt(key, request.get_data())
    response = f"current_time={int(time.time())}&last_config_change={get_device_last_config_change(mac_address)}"
    response_enc = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response_enc, content_type=CONTENT_TYPE)


@app.route('/v1/smart_devices/<mac_address>/config', methods=['POST'])
def get_config(mac_address: str) -> Response:
    key = get_device_key(mac_address)
    _body = decrypt(key, request.get_data())
    response = f"current_time={int(time.time())}&{get_device_config(mac_address)}"
    response_enc = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response_enc, content_type=CONTENT_TYPE)


@app.route('/v1/smart_devices/<mac_address>/readings', methods=['POST'])
def add_readings(mac_address: str) -> Response:
    key = get_device_key(mac_address)
    body = decrypt(key, request.get_data())
    body_parsed = json.loads(body.replace(b"'", b'"'))
    handle_readings(mac_address, convert_readings(mac_address, body_parsed))
    response = f"current_time={int(time.time())}&last_config_change={get_device_last_config_change(mac_address)}"
    response_enc = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response_enc, status=201, content_type=CONTENT_TYPE)


def main() -> None:
    app.config['last_config_change'] = os.path.getmtime(CONFIG_FILE)
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f.read())
    for cfg in ['output', 'devices']:
        app.config[cfg] = config[cfg]
    app.run(host='0.0.0.0', port=8005)


if __name__ == '__main__':
    main()
