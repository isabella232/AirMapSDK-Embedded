"""
  test_telemetryapi
  AirMapSDK - Unit Test Telemetry API

  Created by AirMap Team on 6/28/16.
  Copyright (c) 2016 AirMap, Inc. All rights reserved.
"""

from airmap.connect import Connect
from airmap.airdefs import Startup, Notify, Public, Globals
from airmap.flightAPI import Flight
from airmap.telemetryAPI import Telemetry
import gps
import socket
import time
import sys
import os
import subprocess, signal

def test_start():
	curMode = Startup.Drone.State.connect
	testFail = 0
	xapikey = {"Content-Type":"application/json; charset=utf-8","X-API-Key":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVkZW50aWFsX2lkIjoiY3JlZGVudGlhbHxHTk5nbUxuaTlYM1p3UlRYTU9sMnFmS0o1Z0xLIiwiYXBwbGljYXRpb25faWQiOiJhcHBsaWNhdGlvbnxuOW41QmtZc0JhNkFvM3NBUkpHeXlVYWxZUUVZIiwib3JnYW5pemF0aW9uX2lkIjoiZGV2ZWxvcGVyfDJ6b2JiN3loeGVZNHFrQzNQUngwWkhLTXoyMzgiLCJpYXQiOjE0NzExMjY1NDJ9.v4STUtbJa3uJZFsJLpWZRgUYoyz1X6BxKW8kokerjCg"}

	try:
		#Start GPS
		p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
		out, err = p.communicate()
		for line in out.splitlines():
			if 'gpsfake' in line:
				pid = int(line.split(None, 1)[0])
				os.kill(pid, signal.SIGKILL)
			if 'run-fake-gps' in line:
				pid = int(line.split(None, 1)[0])
				os.kill(pid, signal.SIGKILL)
			if 'gpsd' in line:
				pid = int(line.split(None, 1)[0])
				os.kill(pid, signal.SIGKILL)
		subprocess.Popen('./run-fake-gps.sh', shell=True, stderr=subprocess.STDOUT)
		time.sleep(5)
    		#Access GPS
		gpsReady = False
    		gpsd = gps.gps(mode=gps.WATCH_ENABLE)

		while not gpsReady:
			print "Waiting for GPS..."
			# Read the GPS state
			gpsd.next()

			# Wait for GPS lock
			if (gpsd.valid & gps.LATLON_SET) != 0:
				lat = str(gpsd.fix.latitude)
				lon = str(gpsd.fix.longitude)
				alt = str(gpsd.fix.altitude)
				ground_speed = str(gpsd.fix.speed)
				heading = str(gpsd.fix.track)
				gpstime = str(gpsd.fix.time)
				curMode = str(gpsd.fix.mode)
				gpsReady = True #breakout
            
	except socket.error:
    		print "Error: gpsd service does not seem to be running, plug in USB GPS, run fake-gps-data.sh or run set 'test' flag"
    		sys.exit(1)

	barometer = '28.4'
	log_perct = '31.2'
	bogeyid = '37849329'
	drone_mode = "follow-me"
	battery_chrg= '11.2'
	cur_status= "warning"

	print lat
	print lon
	print alt
	print ground_speed
	print heading
	print time

	airconnect = Connect()
	airflight = Flight()
	airtelemetry = Telemetry()
	airconnect.set_Timeout(16)
	airconnect.set_XAPIKey(xapikey)

	Ret = airconnect.connect()

	if Ret:
	
		airconnect.get_SecureToken()
		if Globals.myToken == "":
			testFail = 1

		try:
			flightID = airflight.create_FlightPoint (2,lat,lon,Public.on,Notify.on)
			if len(flightID) != 35:
				testFail = 1
			myPilotID = airflight.get_PilotID()
			if len(myPilotID) != 30:
				testFail = 1
		except:
			print flightID
			print myPilotID
			testFail = 1

		print "Telemetry..."
		testCount = 0
		response = airtelemetry.post_Telemetry(flightID,lat,lon,alt,ground_speed,heading,barometer,cur_status,battery_chrg,drone_mode,bogeyid,log_perct)
		
		if len(response) < 24:		
			testFail = 1
			testCount = 18
			print "No Telemetry..."
		else:
			print response

		while testCount < 18:
			gpsReady = False
			while not gpsReady:
				print "Waiting for GPS..."
				# Read the GPS state
				gpsd.next()

				# Wait for GPS lock
				if (gpsd.valid & gps.LATLON_SET) != 0:
					lat = str(gpsd.fix.latitude)
					lon = str(gpsd.fix.longitude)
					alt = str(gpsd.fix.altitude)
					ground_speed = str(gpsd.fix.speed)
					heading = str(gpsd.fix.track)
					gpstime = str(gpsd.fix.time)
					curMode = str(gpsd.fix.mode)
					gpsReady = True #breakout

			response = airtelemetry.post_Telemetry(flightID,lat,lon,alt,ground_speed,heading,barometer,cur_status,battery_chrg,drone_mode,bogeyid,log_perct)
			testCount += 1			
			if len(response) < 14:		
				testFail = 1
				testCount = 18
				print "No Telemetry..."
			else:
				print response

		Ret = airflight.end_Flight(flightID)
		if Ret == False:
			testFail = 1
		Ret = airflight.delete_Flight(flightID)
		if Ret == False:
			testFail = 1

		
		flights = airflight.get_FlightList(myPilotID)
		if flights == "":
			testFail = 1
		try:
			airflight.cmd_KillFlights(myPilotID)
		except:
			testFail = 1

	#clean up
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if 'gpsfake' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
		if 'run-fake-gps' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
		if 'gpsd' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
	
	return testFail


