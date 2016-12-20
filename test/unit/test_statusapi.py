"""
  test_statusapi
  AirMapSDK - Unit Test Status API

  Created by AirMap Team on 6/28/16.
  Copyright (c) 2016 AirMap, Inc. All rights reserved.
"""

from airmap.connect import Connect
from airmap.airdefs import Startup, Globals, Advisory, Weather
from airmap.statusAPI import Status
import gps
import socket
import time
import sys

def test_start():
	curMode = Startup.Drone.State.connect
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
	testFail = 0

	airconnect = Connect()
	airstatus = Status()
	thisAdvisory = Advisory()
	airconnect.set_Timeout(16)
	airconnect.set_XAPIKey(xapikey)

	Ret = airconnect.connect()

	if Ret:
		if airstatus.get_status(lat,lon,Weather.on):
			if ( (airstatus.get_StatusColor() != thisAdvisory.Color.Colors.red) or (airstatus.get_StatusColor() != thisAdvisory.Color.Colors.yellow) ):
				testFail = 1
			if airstatus.get_MaxDistance() != 0:
				testFail = 1
			if airstatus.get_StatusCode() != airstatus.get_StatusCode():
				testFail = 1
			if airstatus.cmd_ProcessAdvisories() != True:
				testFail = 1		
			Advisories = airstatus.get_Advisories()
			try:
				xIndex = 0
				while True:
					thisAdvisory = Advisories[xIndex]
					xIndex += 1
			except:
				print "Finished Advisory Print Task..."

			if xIndex <= 3:
				print "..............................."
				testFail = 1
	else:
		testFail = 1

	return testFail



