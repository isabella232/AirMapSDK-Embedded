from __future__ import print_function
from __future__ import absolute_import


"""
  telemetryAPI
  AirMapSDK

  Created by AirMap Team on 6/28/16.
  Copyright (c) 2016 AirMap, Inc. All rights reserved.
"""
# telemetryAPI.py -- telemetry API functions

import time
import random
import struct
import socket
import os

import airmap.telemetry_pb2

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class Position(object):
    def __init__(self, **kwargs):
        # turn a Python time (float) into a milliseconds int
        kwargs['timestamp'] = int(1000*kwargs.get('timestamp', time.time()))

        self._pb = airmap.telemetry_pb2.Position(**kwargs)


class Speed(object):
    def __init__(self, **kwargs):
        self._pb = airmap.telemetry_pb2.Speed(**kwargs)


class Barometer(object):
    def __init__(self, **kwargs):
        self._pb = airmap.telemetry_pb2.Barometer(**kwargs)


class Client:
    '''
    Example use:

        from airmap.telemetryAPI import Client, Position, Speed

        client = Client(
                flight_id = b''.join([ chr(i) for i in range(16)]),
                encryption_key='453e14ff2a7abdcacb5d71cf0f856c46a7a67c01f8510b70fe906f13410af857'.decode('hex'),
                host='udp_receive',
        )

        client.\
            add_message(Position(latitude=33.123456789, longitude=-117.123456789, altitude=123.4, timestamp=1478017100.0)).\
            add_message(Speed(ground_speed=123.45, true_heading=234.5)).\
            add_message(Position(latitude=33.223456789, longitude=-117.123456789, altitude=122.4, timestamp=1478017100.200)).\
            send()
    '''
    MSG_TYPE_ID = {
        Position: 1,
        Speed: 2,
        Barometer: 3,
    }

    def __init__(self, flight_id, encryption_key,
	host='telemetry.airmap.com', port=6060):

        # assert correct flight_id format
        assert len(flight_id) == 16
        assert len(encryption_key) == 32
        # todo: should this client call startComm to initiate?

        self._flight_id = flight_id
        self._encryption_key = encryption_key
        self._host = socket.gethostbyname(host)
        self._port = port

        self._seqnum = 0
        self._msgs = []
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def add_message(self, message):
        self._msgs.append(message)
        return self

    def send(self):
        pbuf = self._flight_id
        self._seqnum += 1

        iv = os.urandom(16)

        msg_list_buf = ''
        for msg in self._msgs:
            msg_buf = msg._pb.SerializeToString()
            msg_list_buf += \
                struct.pack('!HH',
                    self.MSG_TYPE_ID[type(msg)],
                    len(msg_buf)
                ) + \
                msg_buf

        enc_type_id = struct.pack('!B', 1)
        packet_header_buf = \
            self._flight_id + \
            struct.pack('!I', self._seqnum) + \
            enc_type_id + \
            iv

        packet_buf = \
            packet_header_buf + \
            _encrypt(msg_list_buf, iv, self._encryption_key)

        assert len(packet_buf) < 32 * 1024
        self._sock.sendto(packet_buf, (self._host, self._port))
        self._msgs = []


def _encrypt(pt, iv, key):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    pad_len = 16 - (len(pt) % 16)

    return encryptor.update(pt + chr(pad_len)*pad_len) + encryptor.finalize()
