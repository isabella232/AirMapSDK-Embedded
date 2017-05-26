"""
  flightAPI
  AirMapSDK

  Created by AirMap Team on 6/28/16.
  Copyright (c) 2016 AirMap, Inc. All rights reserved.
"""

# flightAPI.py -- Flight API functions

import traceback
import httplib
import urllib
import json
import ssl
import time
import datetime
import socket
from airdefs import Advisory, Advisories, Properties, Globals
import os
import subprocess
import traceback

class Flight:
	
	os = __import__('os')
	connection = None
	headers = None
	thisGlobals = Globals()

	def __init__(self):
		pass

	def get_FlightList(self, pilotID):
		connection = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
		headers = Globals.xapikey
		try:
        		connection.request('GET', '/flight/v2/?pilot_id='+str(pilotID)+'&enhance=true', '', headers)
        		result = connection.getresponse().read()
			parsed_json = json.loads(result)
			flight_collection = parsed_json['data']['results']
			return flight_collection
		except:
			traceback.print_exc()

	def cmd_KillFlights(self, pilotID):
		connection = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
		headers = Globals.xapikey
		try:
        		connection.request('GET', '/flight/v2/?pilot_id='+str(pilotID)+'&enhance=true', '', headers)
        		result = connection.getresponse().read()
			parsed_json = json.loads(result)
			flight_collection = parsed_json['data']['results']
			for flights in flight_collection:
				endFlight = flights['id']
				#destroy flight
				print "deleting {}".format(endFlight)
				try:
					connectFlight = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
					headers = Globals.xapikey
					headers['Authorization'] = "Bearer {}".format(Globals.myToken)
					connectFlight.request('POST', '/flight/v2/{}/delete'.format(endFlight), '', headers)
        				result = connectFlight.getresponse().read()
        				#print(result)
				except:
        				print "Kill Flights Error..."
					traceback.print_exc()
		except:
			traceback.print_exc()

	def get_PilotID(self):
		if Globals.pilotIDValid == True:
			return Globals.pilot_id
		else:
			return False

	def create_FlightPoint(self, time, lat, lon, public, notify):
		startTime = datetime.datetime.utcnow()
		endTime = startTime + datetime.timedelta(0,(time*60))
		startTime = startTime.isoformat() + "-00:00"
		endTime = endTime.isoformat() + "-00:00"
		print startTime
		print endTime
		try:
			connectFlight = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
			headers = Globals.xapikey
			headers['Authorization'] = "Bearer {}".format(Globals.myToken)
			connectFlight.request('POST', '/flight/v2/point', json.dumps({"latitude":float(lat),"longitude":float(lon),"max_altitude":100,"start_time":"{}".format(startTime),"end_time":"" + endTime + "","public":bool(public),"notify":bool(notify)}), headers)
        		result = connectFlight.getresponse().read()
        		#Globals.strPrint(self.thisGlobals,result)
			try:
				parsed_json = json.loads(result)
				parsed_status = parsed_json['status']
				print parsed_status
				Globals.pilot_id = parsed_json['data']['pilot_id']
				Globals.pilotIDValid = True
				#Globals.strPrint (self.thisGlobals,Globals.pilot_id)
			except:
				Globals.strPrint (self.thisGlobals,"Pilot ID not found...Retry!")
				Globals.strPrint (self.thisGlobals,result)
				return False
			if parsed_status != "success":
				return False
			Globals.myFlightID = parsed_json['data']['id']	
		except:
        		print "Create Flight Error..."
			traceback.print_exc()

		return Globals.myFlightID

	def create_FlightPolygon(self, time, lat, lon, public, notify):
		startTime = datetime.datetime.utcnow()
		endTime = startTime + datetime.timedelta(0,(time*60))
		startTime = startTime.isoformat() + "-00:00"
		endTime = endTime.isoformat() + "-00:00"
		print startTime
		print endTime
		try:
			connectFlight = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
			headers = Globals.xapikey
			headers['Authorization'] = "Bearer {}".format(Globals.myToken)
			connectFlight.request('POST', '/flight/v2/polygon', json.dumps({"latitude":float(lat),"longitude":float(lon),"max_altitude":100,"start_time":"{}".format(startTime),"end_time":"" + endTime + "","public":bool(public),"notify":bool(notify),"geometry":{"type":"Polygon","coordinates":[[[-119.91422653198242,39.69345079688953],[-119.87028121948241,39.69318661894411],[-119.84676361083986,39.736234274337846],[-119.91336822509766,39.736234274337846],[-119.91422653198242,39.69345079688953]]]}}), headers)
        		result = connectFlight.getresponse().read()
        		#Globals.strPrint(self.thisGlobals,result)
			try:
				parsed_json = json.loads(result)
				parsed_status = parsed_json['status']
				print parsed_status
				Globals.pilot_id = parsed_json['data']['pilot_id']
				Globals.pilotIDValid = True
				#Globals.strPrint (self.thisGlobals,Globals.pilot_id)
			except:
				Globals.strPrint (self.thisGlobals,"Pilot ID not found...Retry!")
				Globals.strPrint (self.thisGlobals,result)
				return False
			if parsed_status != "success":
				return False
			Globals.myFlightID = parsed_json['data']['id']	
		except:
        		print "Create Flight Error..."
			traceback.print_exc()

		return Globals.myFlightID

	def end_Flight(self, flightID):
		try:
			connectFlight = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
			headers = Globals.xapikey
			headers['Authorization'] = "Bearer {}".format(Globals.myToken)
			connectFlight.request('POST', '/flight/v2/{}/end'.format(flightID), '', headers)
        		result = connectFlight.getresponse().read()
			parsed_json = json.loads(result)
        		parsed_status = parsed_json['status']
			if parsed_status != "success":
				return False
			else:
				return True
		except:
        		print "End Flight Error..."
			traceback.print_exc()

	def delete_Flight(self, flightID):
		try:
			connectFlight = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
			headers = Globals.xapikey
			headers['Authorization'] = "Bearer {}".format(Globals.myToken)
			connectFlight.request('POST', '/flight/v2/{}/delete'.format(flightID), '', headers)
        		result = connectFlight.getresponse().read()
			parsed_json = json.loads(result)
			parsed_status = parsed_json['status']
        		if parsed_status != "success":
				return False
			else:
				return True
		except:
        		print "End Flight Error..."
			traceback.print_exc()

	def start_comm(self, flightID):
		try:
			connectFlight = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
			headers = Globals.xapikey
			headers['Authorization'] = "Bearer {}".format(Globals.myToken)
			connectFlight.request('POST', '/flight/v2/{}/start-comm'.format(flightID), '', headers)
        		result = connectFlight.getresponse().read()
			parsed_json = json.loads(result)
			print parsed_json
			#parsed_status = parsed_json['data']['key']['data']
			parsed_status = parsed_json['data']['key']
			print "H:" + parsed_status
			#thisKey = (''.join(str(hex(i)[2:].zfill(2)) for i in parsed_status)).decode('hex')
			thisKey = parsed_status.decode('base64') 
			return thisKey
		except:
        		print "Could Not Start Comms..."
			traceback.print_exc()

	def end_comm(self, flightID):
		try:
			connectFlight = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
			headers = Globals.xapikey
			headers['Authorization'] = "Bearer {}".format(Globals.myToken)
			connectFlight.request('POST', '/flight/v2/{}/start-comm'.format(flightID), '', headers)
        		result = connectFlight.getresponse().read()
			parsed_json = json.loads(result)
			parsed_status = parsed_json['status']
        		if parsed_status != "success":
				return False
			else:
				return True
		except:
        		print "Could Not End Comms..."
			traceback.print_exc()

	
	def recover_Pilot(self):
	
		try:
			connectFlight = httplib.HTTPSConnection(Globals.httpsAddr, Globals.httpsPort, timeout=Globals.timeOut)
			headers = Globals.xapikey
			headers['Authorization'] = "Bearer {}".format(Globals.myToken)
			connectFlight.request('GET', '/pilot/v2/profile', "", headers)
        		result = connectFlight.getresponse().read()
			try:
				parsed_json = json.loads(result)
				parsed_status = parsed_json['status']
				print parsed_status
				Globals.pilot_id = parsed_json['data']['id']
				Globals.pilotIDValid = True
			except:
				Globals.strPrint (self.thisGlobals,"Pilot Recover ID not found...Retry!")
				Globals.strPrint (self.thisGlobals,result)
				return False
			if parsed_status != "success":
				return False
		except:
        		print "Create Flight Error..."
			traceback.print_exc()

		return Globals.pilot_id

