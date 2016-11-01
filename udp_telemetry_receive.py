import socket
import struct

import airmap.telemetry_pb2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 6060))

MSG_TYPE = [
    None,
    airmap.telemetry_pb2.Position,
    airmap.telemetry_pb2.Speed,
    airmap.telemetry_pb2.Barometer,
]


from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

encryption_key='453e14ff2a7abdcacb5d71cf0f856c46a7a67c01f8510b70fe906f13410af857'.decode('hex')

def decrypt(ct, iv, key):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    pt = decryptor.update(ct) + decryptor.finalize()
    pad_length = ord(pt[-1])
    return pt[:-pad_length]

while True:
    data, addr = sock.recvfrom(32 * 1024)

    pkt_header_fmt = '!16sIB16s'
    pkt_header_fmt_size = struct.calcsize(pkt_header_fmt)

    msg_header_fmt = '!HH'
    msg_header_len = struct.calcsize('!HH')

    assert len(data) > pkt_header_fmt_size
    flight_id, seqnum, enc_type_id, iv = struct.unpack_from(pkt_header_fmt, data)
    #print(flight_id, seqnum, enc_type_id, iv)
    assert enc_type_id == 1
    msg_list_buf = decrypt(data[pkt_header_fmt_size:], iv, encryption_key)

    offset = 0
    #print(len(msg_list_buf))
    while offset < len(msg_list_buf):
        msg_type_id, msg_len = struct.unpack_from('!HH', msg_list_buf, offset)
        #print(msg_type_id, msg_len)
        assert msg_len < 32 * 1024
        #print("offset: ", offset)
        offset += msg_header_len

        obj = MSG_TYPE[msg_type_id]()
        obj.ParseFromString(msg_list_buf[offset:offset+msg_len])
        print(type(obj), obj)

        offset += msg_len
