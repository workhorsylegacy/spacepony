#!/usr/bin/env python

import gtk, dbus


# Initiate a connection to the Session Bus
bus = dbus.SessionBus()

# Associate Pidgin's D-Bus interface with Python objects
obj = bus.get_object("im.pidgin.purple.PurpleService", 
					"/im/pidgin/purple/PurpleObject")
purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

# Specify status ID values
STATUS_OFFLINE = 1
STATUS_AVAILABLE = 2
STATUS_UNAVAILABLE = 3
STATUS_INVISIBLE = 4
STATUS_AWAY = 5
STATUS_EXTENDED_AWAY = 6
STATUS_MOBILE = 7
STATUS_TUNE = 8

def set_status(name, kind, message):
	# Create a new saved status with the specified name and kind

	status = purple.PurpleSavedstatusNew(name, kind)
	# Associate the specified availability message with the new saved status
	purple.PurpleSavedstatusSetMessage(status, message)
	# Activate the new saved status
	purple.PurpleSavedstatusActivate(status)


# Iterate through every active account
for account_id in purple.PurpleAccountsGetAllActive():
	# Create a new status for video games
	#set_status("Dbus fooin", STATUS_AVAILABLE,
	#		"Dbus messin' with pidgin")

	# Retrieve the current status
	status = purple.PurpleSavedstatusGetCurrent()

	# Display the username and availability status/message for each account
	print "name: " + purple.PurpleAccountGetUsername(account_id)
	print "password: " + purple.PurpleAccountGetPassword(account_id)
	print "status: " + purple.PurplePrimitiveGetIdFromType(purple.PurpleSavedstatusGetType(status))
	print "message: " + purple.PurpleSavedstatusGetMessage(status) or ""
	print "protocol: " + purple.PurpleAccountGetProtocolId(account_id)
	print "icon: " + purple.PurpleAccountGetBuddyIconPath(account_id)


