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
import pymavlink.mavutil as mavutil
import re
import datetime
import math

curMode = Startup.Drone.State.connect
flightEnable = False
logFlight = True
flightTimeMin = 2
trigAlt = None
trigTime = None
xapikey = {"Content-Type":"application/json; charset=utf-8","X-API-Key":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVkZW50aWFsX2lkIjoiY3JlZGVudGlhbHxHTk5nbUxuaTlYM1p3UlRYTU9sMnFmS0o1Z0xLIiwiYXBwbGljYXRpb25faWQiOiJhcHBsaWNhdGlvbnxuOW41QmtZc0JhNkFvM3NBUkpHeXlVYWxZUUVZIiwib3JnYW5pemF0aW9uX2lkIjoiZGV2ZWxvcGVyfDJ6b2JiN3loeGVZNHFrQzNQUngwWkhLTXoyMzgiLCJpYXQiOjE0NzExMjY1NDJ9.v4STUtbJa3uJZFsJLpWZRgUYoyz1X6BxKW8kokerjCg"}
filename = "/home/root/log-" + str(time.time()) + ".txt"

if logFlight:
	logbook = open(filename, 'w')

if ( len(sys.argv) < 2):
	print "Usage: python userapp.py { test | gpsd | auto }"
	sys.exit(1)
else:
	runType = sys.argv[1]


if sys.argv[1] == "test":
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
	cur_status= "ready"
	print "GPS test mode enabled..."
elif sys.argv[1] == "gpsd":
	barometer = '28.4'
	log_perct = '31.2'
	bogeyid = '37849329'
	drone_mode = "follow-me"
	battery_chrg= '11.2'
	cur_status= "green"
	try:
    		#Access GPS
		gpsReady = False
    		gpsd = gps.gps(mode=gps.WATCH_ENABLE)

		while not gpsReady:
			print "Waiting for GPS..."
			# Read the GPS state
			gpsd.next()

			# Wait for GPS lock
			if (gpsd.valid & gps.LATLON_SET) != 0:
				lat = gpsd.fix.latitude
				lon = gpsd.fix.longitude
				trigAlt = alt = gpsd.fix.altitude
        			heading = gpsd.fix.track
       				ground_speed = gpsd.fix.speed
        			gpstime = gpsd.utc
				gpsReady = True #breakout
            
	except socket.error:
    		print "Error: gpsd service does not seem to be running, plug in USB GPS, run fake-gps-data.sh or run set 'test' flag"
    		sys.exit(1)
else:
	try:
		print "Waiting for GPS lock..."
		mav = mavutil.mavlink_connection('udpin:' + '127.0.0.1:14550')
		mav.wait_heartbeat()
		barometer = '28.4'
		log_perct = '31.2'
		bogeyid = '37849329'
		drone_mode = "follow-me"
		battery_chrg= '11.2'
		cur_status= "warning"
		updatePos = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    		if updatePos is not None:
			print(updatePos)
			gpsdata = re.split(': |, ', str(updatePos))
			lat = (float(gpsdata[3])/10000000)
			lon = (float(gpsdata[5])/10000000)
			trigAlt = alt = (float(gpsdata[7])/1000)
			heading = (float(gpsdata[17][:-1])/100)
			ground_speed = math.sqrt( ((float(gpsdata[11])/100) * (float(gpsdata[11])/100)) + ((float(gpsdata[13])/100) * (float(gpsdata[13])/100)) )

	except socket.error:
    		print "Error: Mavlink service not found."
    		sys.exit(1)
print lat
print lon
print trigAlt

trigTime = datetime.datetime.utcnow()
airconnect = Connect()
airstatus = Status()
airflight = Flight()
airtelemetry = Telemetry()
airconnect.set_Timeout(16)
airconnect.set_XAPIKey(xapikey)

airconnect.get_boardID()

Ret = airconnect.connect()

if Ret:
	if airstatus.get_status(str(lat),str(lon),Weather.on):
		flightStatus = airstatus.get_StatusColor()
		print flightStatus
		maxDistance = airstatus.get_MaxDistance()
		print maxDistance

		statusCode = airstatus.get_StatusCode()
		print statusCode

		temperature = airstatus.get_Temperature()
		print temperature

		visibility = airstatus.get_Visibility()
		print visibility

		humidity = airstatus.get_Humidity()
		print humidity

		condition = airstatus.get_Condition()
		print condition

		precipitation = airstatus.get_Precipitation()
		print precipitation

		windGusting = airstatus.get_WindGusting()
		print windGusting

		windSpeed = airstatus.get_WindSpeed()
		print windSpeed

		windHeading = airstatus.get_WindHeading()
		print windHeading

		Ret = airstatus.cmd_ProcessAdvisories()
		print Ret

		Advisories = airstatus.get_Advisories()
		try:
			xIndex = 0
			while True:
				thisAdvisory = Advisories[xIndex]
				try:
					yIndex = 0
					while True:
						if str(Advisories[xIndex].properties[yIndex].prop_value)[0] == '[':
							print str(Advisories[xIndex].properties[yIndex].prop_name)
							try:
								zIndex = 0;
								while True:
									print str(Advisories[xIndex].properties[yIndex].prop_value[zIndex].prop_name) + " : " + str(Advisories[xIndex].properties[yIndex].prop_value[zIndex].prop_value)
									zIndex += 1
							except:
								pass
						else:
							print str(Advisories[xIndex].properties[yIndex].prop_name) + " : " + str(Advisories[xIndex].properties[yIndex].prop_value)
						yIndex += 1
				except:
					pass 
				print xIndex
				xIndex += 1
		except:
			print "Finished Advisory Print Task..."

		oneAdvisory = airstatus.get_Advisory(3)
		yIndex = 0
		try:
			while True:
				if str(oneAdvisory.properties[yIndex].prop_value)[0] == '[':
					print str(oneAdvisory.properties[yIndex].prop_name)
					try:
						zIndex = 0;
						while True:
							print str(oneAdvisory.properties[yIndex].prop_value[zIndex].prop_name) + " : " + str(oneAdvisory.properties[yIndex].prop_value[zIndex].prop_value)
							zIndex += 1
					except:
						pass
				else:
					print str(oneAdvisory.properties[yIndex].prop_name) + " : " + str(oneAdvisory.properties[yIndex].prop_value)
				yIndex += 1
		except:
			print "Advisory Complete..."


		airconnect.get_SecureToken()

		flightID = airflight.create_FlightPoint (flightTimeMin,str(lat),str(lon),Public.on,Notify.on)
		myPilotID = airflight.get_PilotID()

		endTime = trigTime + datetime.timedelta(0,flightTimeMin*60)	
		print "Telemetry..."
		while ( ((trigAlt <= (alt+1)) or (flightEnable == False)) and (datetime.datetime.utcnow() < endTime) ):
			if sys.argv[1] == "test":
				response = airtelemetry.post_Telemetry(flightID,lat,lon,alt,ground_speed,heading,barometer,cur_status,battery_chrg,drone_mode,bogeyid,log_perct)
				print response
			elif sys.argv[1] == "gpsd":
				gpsd.next()
        
				alt = gpsd.fix.altitude
        			lat = gpsd.fix.latitude
        			lon = gpsd.fix.longitude
        			heading = gpsd.fix.track
       				ground_speed = gpsd.fix.speed
        			gpstime = gpsd.utc

				print lat
				print lon
        			print heading
       				print ground_speed
        			print gpstime

				if math.isnan(gpsd.fix.latitude) or math.isnan(gpsd.fix.longitude) or math.isnan(gpsd.fix.track) or math.isnan(gpsd.fix.speed) or math.isnan(gpsd.fix.altitude) or gpsd.fix.latitude == 0.0:
                			print "Waiting for GPS lock..."
                			time.sleep(2)
                			continue
				response = airtelemetry.post_Telemetry(flightID,lat,lon,alt,ground_speed,heading,barometer,cur_status,battery_chrg,drone_mode,bogeyid,log_perct)
				print response
			else:
				updatePos = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    				if updatePos is not None:
					#print(updatePos)
					gpsdata = re.split(': |, ', str(updatePos))
					#print (str(float(gpsdata[3])/10000000))
					#print (str(float(gpsdata[5])/10000000))
					#print (str(float(gpsdata[7])/1000))
					lat = (float(gpsdata[3])/10000000)
					lon = (float(gpsdata[5])/10000000)
					alt = (float(gpsdata[7])/1000)
					heading = (float(gpsdata[17][:-1])/100)
					ground_speed = math.sqrt( ((float(gpsdata[11])/100) * (float(gpsdata[11])/100)) + ((float(gpsdata[13])/100) * (float(gpsdata[13])/100)) )

					if math.isnan(lat) or math.isnan(lon) or math.isnan(alt) or lat == 0.0:
                				print "Waiting for GPS lock..."
                				time.sleep(2)
                				continue

					response = airtelemetry.post_Telemetry(flightID,lat,lon,alt,ground_speed,heading,barometer,cur_status,battery_chrg,drone_mode,bogeyid,log_perct)
					print response
			if logFlight:	
				logbook.write ("Mission:\tlat: " + str(lat) + "\tlon: " + str(lon) + "\talt: " + str(alt) + "\n")


			if (alt > (trigAlt+3)):
				flightEnable = True

			time.sleep(1)
		
		if logFlight:	
			logbook.close()

		airflight.end_Flight(flightID)
		airflight.get_FlightList(myPilotID)
		airflight.cmd_KillFlights(myPilotID)


