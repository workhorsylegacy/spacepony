#!/usr/bin/env python

import dbus, gobject, dbus.glib
import base64
import sys, threading, traceback
from pyactiveresource.activeresource import ActiveResource


# Create the models
class User(ActiveResource):
	_site = "http://localhost:3000"

class PidginAccount(ActiveResource):
	_site = "http://localhost:3000"

class TomboyNote(ActiveResource):
	_site = "http://localhost:3000"

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

def add_pidgin_account(account_id, save_now = True):
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
	if save_now:
		pidgin_account.save()
	pidgin_accounts[account_id] = pidgin_account

	if save_now:
		print "Server: Added Pidgin account " + pidgin_account.name + " with the protocol " + pidgin_account.protocol + "."

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

	print "Server: Removed Pidgin account " + pidgin_account.name + " with the protocol " + pidgin_account.protocol + "."

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

			print "Server: Changed Pidgin status for account " + pidgin_account.name + " to '" + pidgin_account.status + \
				"' with the message '" + pidgin_account.message + "'."

def add_tomboy_note(note, save_now = True):
	note_name = str(tomboy.GetNoteTitle(note))

	# Skip adding the note if it already exists
	if tomboy_notes.has_key(note_name):
		return

	# Save the note
	tomboy_note = TomboyNote()
	tomboy_note.user_id = user.id
	tomboy_note.name = note_name
	tomboy_note.body = base64.b64encode(str(tomboy.GetNoteCompleteXml(note)))
	tomboy_note.created_at = None
	tags = []
	for tag in tomboy.GetTagsForNote(note):
		tags.append(str(tag))
	tomboy_note.tag = str.join(', ', tags)
	if save_now:
		tomboy_note.save()
	tomboy_notes[note_name] = tomboy_note

	if save_now:
		print "Server: Note added: " + tomboy_note.name

def update_tomboy_note(note):
	note_name = str(tomboy.GetNoteTitle(note))

	# Skip the note if it does not exist
	if not tomboy_notes.has_key(note_name):
		return

	# Save the changes to the note
	tomboy_note = tomboy_notes[note_name]
	tomboy_note.name = note_name
	tomboy_note.body = base64.b64encode(str(tomboy.GetNoteCompleteXml(note)))
	tags = []
	for tag in tomboy.GetTagsForNote(note):
		tags.append(str(tag))
	tomboy_note.tag = str.join(', ', tags)
	tomboy_note.save()

	print "Server: Note updated: " + tomboy_note.name


def remove_tomboy_note(note):
	note_name = str(tomboy.GetNoteTitle(note))

	# Remove the note only if it exists
	tomboy_note = None
	if tomboy_notes.has_key(note_name):
		tomboy_note = tomboy_notes[note_name]
	else:
		return

	# Remove the note
	tomboy_note.delete()
	tomboy_notes.pop(note_name)

	print "Server: Note deleted: " + tomboy_note.name


class Puller(threading.Thread):
	def __init__(self, name='Puller'):
		self._stopevent = threading.Event()
		threading.Thread.__init__(self, name=name)

	def run(self):
		try:
			# Add all the local tomboy notes
			for note in tomboy.ListAllNotes():
				add_tomboy_note(note, False)

			# Add all the pidgin accounts
			for account_id in purple.PurpleAccountsGetAllActive():
				add_pidgin_account(account_id, False)

			while not self._stopevent.isSet():
				# Pull all notes from the server
				server_notes = []
				for n in TomboyNote._find_every():
					server_notes.append(TomboyNote(n))

				# Update notes from server
				for note_name, client_note in tomboy_notes.iteritems():
					for server_note in server_notes:
						# Save new notes from client to server
						if tomboy_note.created_at == None:
							tomboy_note.save()
							print "Server: Note added: " + tomboy_note.name
						# Update notes that are on the server
						elif server_note.id == client_note.id and \
						server_note.updated_at != client_note.updated_at:
							print "found changed note: " + client_note.name
							# Update the note in our cache
							client_note.name = server_note.name
							client_note.body = server_note.body
							client_note.tag = server_note.tag
							client_note.created_at = server_note.created_at
							client_note.updated_at = server_note.updated_at

							# Update the note in tomboy
							for note in tomboy.ListAllNotes():
								if str(note) == note_id:
									print "updated note: " + client_note.name
									tomboy.SetNoteCompleteXml(note, base64.b64decode(client_note.body))

				time.sleep(5)

		except Exception:
			traceback.print_exc(file=sys.stdout)
			exit(1)

	def join(self, timeout=None):
		threading.Thread.join(self, timeout)


def onAccountStatusChanged(account_id, old, new):
	update_pidgin_account_status(account_id, old, new)

def onAccountAdded(account_id):
	add_pidgin_account(account_id)

def onAccountRemoved(account_id):
	remove_pidgin_account(account_id)

def onNoteAdded(note):
	add_tomboy_note(note)

def onNoteSaved(note):
	update_tomboy_note(note)

# FIXME: Figure out what the second argument is. There is no documentation
def onNoteDeleted(note, unknown_object):
	remove_tomboy_note(note)

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

bus.add_signal_receiver(onNoteSaved,
						dbus_interface = "org.gnome.Tomboy.RemoteControl",
						signal_name = "NoteSaved")

bus.add_signal_receiver(onNoteAdded,
						dbus_interface = "org.gnome.Tomboy.RemoteControl",
						signal_name = "NoteAdded")

bus.add_signal_receiver(onNoteDeleted,
						dbus_interface = "org.gnome.Tomboy.RemoteControl",
						signal_name = "NoteDeleted")




print "client running ..."
pidgin_accounts = {}
tomboy_notes = {}
user = None

# Add a new user to the server
if len(User._find_every()) == 0:
	# Create a user and save it
	user = User()
	user.name = 'mattjones'
	user.email = 'mattjones@workhorsy.org'
	user.password = 'password'
	user.password_confirmation = 'password'
	user.save()

# Copy the user from the server
else:
	# Get user from server
	user = User._find_every()[0]

#puller = Puller()
#puller.run()

# Wait here and run events
gobject.MainLoop().run()



