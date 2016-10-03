"""
  test_createflightapi
  AirMapSDK - Unit Test Create Flight API

  Created by AirMap Team on 6/28/16.
  Copyright (c) 2016 AirMap, Inc. All rights reserved.
"""

from airmap.connect import Connect
from airmap.airdefs import Startup, Notify, Public, Globals
from airmap.flightAPI import Flight
import socket
import time
import sys

def test_start():

	curMode = Startup.Drone.State.connect
	testFail = 0
	xapikey = {"Content-Type":"application/json; charset=utf-8","X-API-Key":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVkZW50aWFsX2lkIjoiY3JlZGVudGlhbHxHTk5nbUxuaTlYM1p3UlRYTU9sMnFmS0o1Z0xLIiwiYXBwbGljYXRpb25faWQiOiJhcHBsaWNhdGlvbnxuOW41QmtZc0JhNkFvM3NBUkpHeXlVYWxZUUVZIiwib3JnYW5pemF0aW9uX2lkIjoiZGV2ZWxvcGVyfDJ6b2JiN3loeGVZNHFrQzNQUngwWkhLTXoyMzgiLCJpYXQiOjE0NzExMjY1NDJ9.v4STUtbJa3uJZFsJLpWZRgUYoyz1X6BxKW8kokerjCg"}

	lat = '34.013252'
	lon = '-118.499112'
	alt = '101.3'
	ground_speed = '10.8'
	heading = '84.6'
	barometer = '28.4'
	log_perct = '31.2'
	bogeyid = '37849329'
	drone_mode = "follow-me"
	battery_chrg= '11.2'
	cur_status= "warning"

	airconnect = Connect()
	airflight = Flight()
	airconnect.set_Timeout(16)
	airconnect.set_XAPIKey(xapikey)

	Ret = airconnect.connect()

	if Ret:
	
		airconnect.get_SecureToken()
		if Globals.myToken == "":
			testFail = 1

		flightID = airflight.create_FlightPoint (2,lat,lon,Public.on,Notify.on)
		if len(flightID) != 35:
			testFail = 1
		myPilotID = airflight.get_PilotID()
		if len(myPilotID) != 30:
			testFail = 1

		Ret = airflight.end_Flight(flightID)
		if Ret == False:
			testFail = 1
		Ret = airflight.delete_Flight(flightID)
		if Ret == False:
			testFail = 1

		flightID = airflight.create_FlightPoint (2,lat,lon,Public.on,Notify.on)
		if len(flightID) != 35:
			testFail = 1
		Ret = airflight.end_Flight(flightID)
		if Ret == False:
			testFail = 1
		flights = airflight.get_FlightList(myPilotID)
		if flights == "":
			testFail = 1
		try:
			airflight.cmd_KillFlights(myPilotID)
		except:
			testFail = 1
	
	return testFail
