#!/usr/bin/python3

import time
from http.server import BaseHTTPRequestHandler
from flask import Flask, request, Response
from koubachi_crypto import decrypt, encrypt

from config import devices

BaseHTTPRequestHandler.protocol_version = 'HTTP/1.1'

CONTENT_TYPE = "application/x-koubachi-aes-encrypted"

app = Flask(__name__)


def get_key(mac_address):
    return bytes.fromhex(devices[mac_address]['key'])


def get_config(mac_address):
    return devices[mac_address]['config']


def get_last_config_change(mac_address):
    return devices[mac_address]['last_config_change']


@app.route('/v1/smart_devices/<mac_address>', methods=['PUT'])
def connect(mac_address):
    key = get_key(mac_address)
    body = decrypt(key, request.get_data())
    print(body)
    response = f"current_time={int(time.time())}&last_config_change={get_last_config_change(mac_address)}"
    print(response)
    response = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response, content_type=CONTENT_TYPE)


@app.route('/v1/smart_devices/<mac_address>/config', methods=['POST'])
def get_config(mac_address):
    key = get_key(mac_address)
    body = decrypt(key, request.get_data())
    print(body)
    response = f"current_time={int(time.time())}&{get_config(mac_address)}"
    print(response)
    response = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response, content_type=CONTENT_TYPE)


@app.route('/v1/smart_devices/<mac_address>/readings', methods=['POST'])
def add_readings(mac_address):
    key = get_key(mac_address)
    body = decrypt(key, request.get_data())
    print(body)
    response = f"current_time={int(time.time())}&last_config_change={get_last_config_change(mac_address)}"
    print(response)
    response = encrypt(key, bytes(response, encoding='utf-8'))
    return Response(response, status=201, content_type=CONTENT_TYPE)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8005)
