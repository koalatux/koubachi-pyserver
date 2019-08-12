#!/usr/bin/python3

import time
import json
from http.server import BaseHTTPRequestHandler
from flask import Flask, request, Response
import paho.mqtt.publish as publish
from koubachi_crypto import decrypt, encrypt

import config
from sensors import SENSORS

# The sensor only accepts HTTP/1.1
BaseHTTPRequestHandler.protocol_version = 'HTTP/1.1'

CONTENT_TYPE = "application/x-koubachi-aes-encrypted"

app = Flask(__name__)


def get_device_key(mac_address):
    return bytes.fromhex(config.devices[mac_address]['key'])


def get_device_config(_mac_address):
    cfg = {
        "transmit_interval": 55202,
        "transmit_app_led": 1,
        "sensor_app_led": 0,
        "day_threshold": 10.0,
    }
    cfg.update({f"sensor_enabled[{k}]": int(v[1]) for k, v in SENSORS.items()})
    cfg.update({f"sensor_polling_interval[{k}]": v[2] for k, v in SENSORS.items() if v[1]})
    return "&".join([f"{k}={v}" for k, v in cfg.items()])


def get_device_last_config_change(_mac_address):
    return 1565643961


def post_readings(mac_address, body):
    readings = []
    for reading in body['readings']:
        ts, sensor_type_id, value_raw = reading
        sensor_type = SENSORS.get(sensor_type_id, (None, False))
        if sensor_type[1]:
            readings.append({
                'ts': ts * 1000,
                'values': {SENSORS[sensor_type_id][0]: value_raw}
            })
    payload = {mac_address: readings}
    publish.single(config.MQTT_TOPIC, json.dumps(payload), hostname=config.MQTT_HOST, auth=config.MQTT_AUTH)


@app.route('/v1/smart_devices/<mac_address>', methods=['PUT'])
def connect(mac_address):
    key = get_device_key(mac_address)
    _body = decrypt(key, request.get_data())
    response = f"current_time={int(time.time())}&last_config_change={get_device_last_config_change(mac_address)}"
    response = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response, content_type=CONTENT_TYPE)


@app.route('/v1/smart_devices/<mac_address>/config', methods=['POST'])
def get_config(mac_address):
    key = get_device_key(mac_address)
    _body = decrypt(key, request.get_data())
    response = f"current_time={int(time.time())}&{get_device_config(mac_address)}"
    response = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response, content_type=CONTENT_TYPE)


@app.route('/v1/smart_devices/<mac_address>/readings', methods=['POST'])
def add_readings(mac_address):
    key = get_device_key(mac_address)
    body = decrypt(key, request.get_data())
    body = json.loads(body.replace(b"'", b'"'))
    post_readings(mac_address, body)
    response = f"current_time={int(time.time())}&last_config_change={get_device_last_config_change(mac_address)}"
    response = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response, status=201, content_type=CONTENT_TYPE)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8005)
