"""
  userapp
  AirMapSDK - Example

  Created by AirMap Team on 6/28/16.
  Copyright (c) 2016 AirMap, Inc. All rights reserved.
"""

from airmap.connect import Connect
from airmap.airdefs import Startup, Advisory, Weather, Notify, Public
from airmap.statusAPI import Status
from airmap.flightAPI import Flight
from airmap.telemetryAPI import Telemetry
import gps
import socket
import time
import sys

curMode = Startup.Drone.State.connect
test = True
lat = None
lon = None
xapikey = {"Content-Type":"application/json; charset=utf-8","X-API-Key":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVkZW50aWFsX2lkIjoiY3JlZGVudGlhbHxHTk5nbUxuaTlYM1p3UlRYTU9sMnFmS0o1Z0xLIiwiYXBwbGljYXRpb25faWQiOiJhcHBsaWNhdGlvbnxuOW41QmtZc0JhNkFvM3NBUkpHeXlVYWxZUUVZIiwib3JnYW5pemF0aW9uX2lkIjoiZGV2ZWxvcGVyfDJ6b2JiN3loeGVZNHFrQzNQUngwWkhLTXoyMzgiLCJpYXQiOjE0NzExMjY1NDJ9.v4STUtbJa3uJZFsJLpWZRgUYoyz1X6BxKW8kokerjCg"}

airconnect = Connect()
airflight = Flight()
airconnect.set_Timeout(16)
airconnect.set_XAPIKey(xapikey)

airconnect.get_boardID()

Ret = airconnect.connect()

if Ret:
	airconnect.get_SecureToken()
	myPilotID = "auth0|57afa31f5c3b7fc31fda8663"


	airflight.get_FlightList(myPilotID)
	airflight.cmd_KillFlights(myPilotID)


