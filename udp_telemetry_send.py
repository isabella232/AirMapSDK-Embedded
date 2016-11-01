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

client.\
    add_message(Speed(ground_speed=123.45, true_heading=234.5)).\
    send()
