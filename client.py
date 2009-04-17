#!/usr/bin/env python

import dbus, gobject, dbus.glib
from PyRest import PyRest
from PyRest import PyResource

# Create the models
User = PyResource.connect("http://localhost:3000", "user")
PidginAccount = PyResource.connect("http://localhost:3000", "pidgin_account")

# Initiate a connection to the Session Bus
bus = dbus.SessionBus()

# Get Pidgin's D-Bus interface
obj = bus.get_object("im.pidgin.purple.PurpleService", 
					"/im/pidgin/purple/PurpleObject")
purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

# Get Tomboy's D-Bus interface
obj = bus.get_object("org.gnome.Tomboy", 
					"/org/gnome/Tomboy/RemoteControl")
tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")


# Specify status ID values
STATUS_OFFLINE = 1
STATUS_AVAILABLE = 2
STATUS_UNAVAILABLE = 3
STATUS_INVISIBLE = 4
STATUS_AWAY = 5
STATUS_EXTENDED_AWAY = 6
STATUS_MOBILE = 7
STATUS_TUNE = 8

def add_pidgin_account(account_id):
	# Skip adding the account if it already exists
	for pidgin_account in pidgin_accounts.values():
		if str(purple.PurpleAccountGetUsername(account_id)) == pidgin_account.name and \
			str(purple.PurpleAccountGetProtocolId(account_id)) == pidgin_account.protocol:
				return

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
	pidgin_accounts[account_id] = pidgin_account

	print "Added Pidgin account " + pidgin_account.name + " with the protocol " + pidgin_account.protocol + "."

def remove_pidgin_account(account_id):
	# Remove the account only if it exists
	pidgin_account = None
	if pidgin_accounts.has_key(account_id):
		pidgin_account = pidgin_accounts[account_id]
	else:
		return

	# Remove the account
	pidgin_account.delete()
	pidgin_accounts.pop(account_id)

	print "Removed Pidgin account " + pidgin_account.name + " with the protocol " + pidgin_account.protocol + "."

def update_pidgin_account_status(account_id, old, new):
	# Look through all the pidgin accounts to find the one that changed
	for pidgin_account in pidgin_accounts.values():
		if str(purple.PurpleAccountGetUsername(account_id)) == pidgin_account.name and \
			str(purple.PurpleAccountGetProtocolId(account_id)) == pidgin_account.protocol:

			# Get the new status
			status = purple.PurpleSavedstatusGetCurrent()

			# Save the new status
			pidgin_account.status = str(purple.PurplePrimitiveGetIdFromType(purple.PurpleSavedstatusGetType(status)))
			pidgin_account.message = str(purple.PurpleSavedstatusGetMessage(status) or "")
			pidgin_account.save()

			print "Changed Pidgin status for account " + pidgin_account.name + " to '" + pidgin_account.status + \
				"' with the message '" + pidgin_account.message + "'."

# Update the status on the server when it changes on the client
def onAccountStatusChanged(account_id, old, new):
	update_pidgin_account_status(account_id, old, new)

# Add accounts to the server when it is added on the client
def onAccountAdded(account_id):
	add_pidgin_account(account_id)

def onAccountRemoved(account_id):
	remove_pidgin_account(account_id)

# Bind the events
bus.add_signal_receiver(onAccountStatusChanged,
						dbus_interface = "im.pidgin.purple.PurpleInterface",
						signal_name = "AccountStatusChanged")

bus.add_signal_receiver(onAccountAdded,
						dbus_interface = "im.pidgin.purple.PurpleInterface",
						signal_name = "AccountAdded")

bus.add_signal_receiver(onAccountRemoved,
						dbus_interface = "im.pidgin.purple.PurpleInterface",
						signal_name = "AccountRemoved")


print "client running ..."

# Delete all the models on the server
for pidgin_account in PidginAccount.find_all():
	pidgin_account.delete()

for user in User.find_all():
	user.delete()

# Create a user and save it
pidgin_accounts = {}
user = User()
user.name = 'mattjones'
user.email = 'mattjones@workhorsy.org'
user.password = 'password'
user.password_confirmation = 'password'
user.save()

# Add an account for each pidgin account
for account_id in purple.PurpleAccountsGetAllActive():
	add_pidgin_account(account_id)

# Wait here and run events
gobject.MainLoop().run()



