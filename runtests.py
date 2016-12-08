from test.unit import test_access, test_statusapi, test_createflightapi, test_telemetryapi
import sys

testFail = 0

ret = test_access.test_start()
if ret == 1:
	print "Access Test Failed..."
	testFail = 1
else:
	print "Pass: Access Test"

ret = test_statusapi.test_start()
if ret == 1:
	print "Status Test Failed..."
	testFail = 1
else:
	print "Pass: Status Test"

ret = test_createflightapi.test_start()
if ret == 1:
	print "Create Flight Test Failed..."
	testFail = 1
else:
	print "Pass: Create Flight Test"

ret = test_telemetryapi.test_start()
if ret == 1:
	print "Telemetry Test Failed..."
	testFail = 1
else:
	print "Pass: Telemetry Test"


if testFail == 0:
	print "Final: **All Tests Passed**"
else:
	print "Final: **Test Failed**"
