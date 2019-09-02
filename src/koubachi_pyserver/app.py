#!/usr/bin/python3

import time
import json
from typing import Dict, Iterable, Tuple
from http.server import BaseHTTPRequestHandler
import yaml
from flask import Flask, request, Response
import paho.mqtt.publish as publish
from koubachi_crypto import decrypt, encrypt

from sensors import SENSORS

# The sensor only accepts HTTP/1.1
BaseHTTPRequestHandler.protocol_version = 'HTTP/1.1'

CONTENT_TYPE = "application/x-koubachi-aes-encrypted"

app = Flask(__name__)


def get_device_key(mac_address: str) -> bytes:
    return bytes.fromhex(app.config['devices'][mac_address]['key'])


def get_device_calibration_parameters(mac_address: str) -> Dict[str, float]:
    return app.config['devices'][mac_address]['calibration_parameters']


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
    # TODO
    return 1565643961


def post_readings(mac_address: str, body: Dict[str, Iterable[Tuple[int, int, float]]]) -> None:
    calibration_parameters = get_device_calibration_parameters(mac_address)
    readings = []
    for reading in body['readings']:
        ts, sensor_type_id, value_raw = reading
        sensor_type = SENSORS.get(sensor_type_id, ('', False, None, None))
        if sensor_type[1]:
            if sensor_type[3] is None:
                value = None
            else:
                value = sensor_type[3](value_raw, calibration_parameters)
            readings.append({
                'ts': ts * 1000,
                'values': {
                    sensor_type[0] + '_raw': value_raw,
                    sensor_type[0]: value
                }
            })
    if readings:
        payload = {mac_address: readings}
        # TODO
        print(payload)
        # publish.single(app.config.MQTT_TOPIC, json.dumps(payload), hostname=app.config.MQTT_HOST, auth=app.config.MQTT_AUTH)


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
    post_readings(mac_address, body_parsed)
    response = f"current_time={int(time.time())}&last_config_change={get_device_last_config_change(mac_address)}"
    response_enc = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response_enc, status=201, content_type=CONTENT_TYPE)


if __name__ == '__main__':
    with open("config.yml") as f:
        config = yaml.load(f.read())
    for device in ['devices']:
        app.config[device] = config[device]
    app.run(host='0.0.0.0', port=8005)
