#!/usr/bin/python3

import time
import json
from http.server import BaseHTTPRequestHandler
from flask import Flask, request, Response
import paho.mqtt.publish as publish
from koubachi_crypto import decrypt, encrypt

import config

# The sensor only accepts HTTP/1.1
BaseHTTPRequestHandler.protocol_version = 'HTTP/1.1'

CONTENT_TYPE = "application/x-koubachi-aes-encrypted"

app = Flask(__name__)


def get_device_key(mac_address):
    return bytes.fromhex(config.devices[mac_address]['key'])


def get_device_config(mac_address):
    return config.devices[mac_address]['config']


def get_device_last_config_change(mac_address):
    return config.devices[mac_address]['last_config_change']


def post_readings(mac_address, body):
    readings = []
    for reading in body['readings']:
        ts, sensor_type, value_raw = reading
        if sensor_type in config.SENSOR_TYPE_MAP:
            readings.append({
                'ts': ts * 1000,
                'values': {config.SENSOR_TYPE_MAP[sensor_type]: value_raw}
            })
    payload = {mac_address: readings}
    publish.single(config.MQTT_TOPIC, json.dumps(payload), hostname=config.MQTT_HOST, auth=config.MQTT_AUTH)


@app.route('/v1/smart_devices/<mac_address>', methods=['PUT'])
def connect(mac_address):
    key = get_device_key(mac_address)
    body = decrypt(key, request.get_data())
    response = f"current_time={int(time.time())}&last_config_change={get_device_last_config_change(mac_address)}"
    response = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response, content_type=CONTENT_TYPE)


@app.route('/v1/smart_devices/<mac_address>/config', methods=['POST'])
def get_config(mac_address):
    key = get_device_key(mac_address)
    body = decrypt(key, request.get_data())
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
