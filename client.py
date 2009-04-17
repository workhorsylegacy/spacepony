#!/usr/bin/env python

import dbus, gobject, dbus.glib
from PyRest import PyRest
from PyRest import PyResource

# Create the models
User = PyResource.connect("http://localhost:3000", "user")
PidginAccount = PyResource.connect("http://localhost:3000", "pidgin_account")

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

# Delete all the models on the server
for pidgin_account in PidginAccount.find_all():
	pidgin_account.delete()

for user in User.find_all():
	user.delete()

# Create a user and save it
pidgin_accounts = []
user = User()
user.name = 'mattjones'
user.email = 'mattjones@workhorsy.org'
user.password = 'password'
user.password_confirmation = 'password'
user.save()

# Add an account for each pidgin account
for account_id in purple.PurpleAccountsGetAllActive():
	# Retrieve the current status
	status = purple.PurpleSavedstatusGetCurrent()

	pidgin_account = PidginAccount()
	pidgin_account.user_id = user.id
	pidgin_account.name = str(purple.PurpleAccountGetUsername(account_id))
	pidgin_account.password = str(purple.PurpleAccountGetPassword(account_id))
	pidgin_account.status = str(purple.PurplePrimitiveGetIdFromType(purple.PurpleSavedstatusGetType(status)))
	pidgin_account.message = str(purple.PurpleSavedstatusGetMessage(status) or "")
	pidgin_account.protocol = str(purple.PurpleAccountGetProtocolId(account_id))
	pidgin_account.icon = str(purple.PurpleAccountGetBuddyIconPath(account_id))
	pidgin_account.save()
	pidgin_accounts.append(pidgin_account)

# Update the status on the server when it changes on the client
def onAccountStatusChanged(acct_id, old, new):
	# Look through all the pidgin accounts to find the one that changed
	for pidgin_account in pidgin_accounts:
		if str(purple.PurpleAccountGetUsername(acct_id)) == pidgin_account.name and \
			str(purple.PurpleAccountGetProtocolId(acct_id)) == pidgin_account.protocol:

			# Get the new status
			status = purple.PurpleSavedstatusGetCurrent()
			status = str(purple.PurplePrimitiveGetIdFromType(purple.PurpleSavedstatusGetType(status)))

			# Save the new status
			pidgin_account.status = status
			pidgin_account.save()


# Bind the events
bus.add_signal_receiver(onAccountStatusChanged,
						dbus_interface = "im.pidgin.purple.PurpleInterface",
						signal_name = "AccountStatusChanged")

# Wait here an run events that happen
print "client running ..."
gobject.MainLoop().run()



