#!/usr/bin/env python

import dbus, gobject, dbus.glib
import base64, time, decimal
import sys, threading, traceback
import ctypes
from xml2dict import *
from pyactiveresource.activeresource import ActiveResource
from pyactiveresource import util
from pyactiveresource import connection

# Change the name of this process to spacepony
try:
	libc = ctypes.CDLL('libc.so.6')
	libc.prctl(15, 'spacepony', 0, 0, 0)
except:
	pass

USERNAME = "mattjones"
PASSWORD = "password"
EMAIL = "mattjones@workhorsy.org"
SERVER_SOCKET = "192.168.1.101:3000"
SERVER_ADDRESS = "http://" + USERNAME + ":" + PASSWORD + "@" + SERVER_SOCKET

# Create the models
class User(ActiveResource):
	_site = SERVER_ADDRESS

class PidginAccount(ActiveResource):
	_site = SERVER_ADDRESS

class TomboyNote(ActiveResource):
	_site = SERVER_ADDRESS

# Make it so the dbus threads and python threads work at the same time
gobject.threads_init()
dbus.glib.init_threads()

# Initiate a connection to the Session Bus
bus = dbus.SessionBus()


# Aks dbus to auto start the programs we will be talking to
(success, status) = bus.start_service_by_name('org.gnome.Tomboy')
#(success, status) = bus.start_service_by_name('org.gnome.Rhythmbox')
#(success, status) = bus.start_service_by_name('im.pidgin.purple.PurpleService')

obj, purple, tomboy = None, None, None

# Get Pidgin's D-Bus interface
try:
	obj = bus.get_object("im.pidgin.purple.PurpleService", 
						"/im/pidgin/purple/PurpleObject")
	purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
except:
	raise Exception("Please start pidgin first.")

# Get Tomboy's D-Bus interface
try:
	obj = bus.get_object("org.gnome.Tomboy", 
						"/org/gnome/Tomboy/RemoteControl")
	tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")
except:
	raise Exception("Please start tomboy first.")

# Specify status ID values
STATUS_OFFLINE = 1
STATUS_AVAILABLE = 2
STATUS_UNAVAILABLE = 3
STATUS_INVISIBLE = 4
STATUS_AWAY = 5
STATUS_EXTENDED_AWAY = 6
STATUS_MOBILE = 7
STATUS_TUNE = 8

# FIXME: Globals are bad
pidgin_accounts = {}
tomboy_notes = {}
user = None
newest_updated_timestamp = None
needs_first_sync = True
ignore_tomboy_event = {}

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
	global newest_updated_timestamp
	global ignore_tomboy_event
	global tomboy_notes
	note_guid = str(note).replace("note://tomboy/", "")

	# skip this event if it is in the list of ignores
	if ignore_tomboy_event.has_key(note_guid) and ignore_tomboy_event[note_guid] > 0:
		ignore_tomboy_event[note_guid] -= 1
		return

	# Skip adding the note if it already exists
	if tomboy_notes.has_key(note_guid):
		return

	# Save the note
	tomboy_note = TomboyNote()
	tomboy_note.guid = note_guid
	tomboy_note.user_id = user.id
	tomboy_note.name = str(tomboy.GetNoteTitle(note))
	tomboy_note.body = base64.b64encode(str(tomboy.GetNoteCompleteXml(note)))
	tomboy_note.created_timestamp = None
	tags = []
	for tag in tomboy.GetTagsForNote(note):
		tags.append(str(tag))
	tomboy_note.tag = str.join(', ', tags)
	if save_now:
		tomboy_note.save()
	tomboy_notes[note_guid] = tomboy_note

	# Save the updated_timestamp as the new greatest
	if tomboy_note.id:
		newest_updated_timestamp = tomboy_note.updated_timestamp

	if save_now:
		print "Server: Note added: " + tomboy_note.name

def update_tomboy_note(note):
	global newest_updated_timestamp
	global ignore_tomboy_event
	global tomboy_notes
	note_guid = str(note).replace("note://tomboy/", "")

	# skip this event if it is in the list of ignores
	if ignore_tomboy_event.has_key(note_guid) and ignore_tomboy_event[note_guid] > 0:
		ignore_tomboy_event[note_guid] -= 1
		return

	# Skip the note if it does not exist
	if not tomboy_notes.has_key(note_guid):
		print "no note with guid: " + note_guid
		return

	# Save the changes to the note
	tomboy_note = tomboy_notes[note_guid]
	tomboy_note.name = str(tomboy.GetNoteTitle(note))
	tomboy_note.body = base64.b64encode(str(tomboy.GetNoteCompleteXml(note)))
	tags = []
	for tag in tomboy.GetTagsForNote(note):
		tags.append(str(tag))
	tomboy_note.tag = str.join(', ', tags)

	try:
		tomboy_note.save()
	except Exception, err:
		if str(err) == "HTTP Error 404: Not Found":
			tomboy.HideNote(note)
			tomboy.DeleteNote(note)
			tomboy_notes.pop(note_guid)

	print "Server: Note updated: " + tomboy_note.name


def remove_tomboy_note(note):
	global newest_updated_timestamp
	global ignore_tomboy_event
	global tomboy_notes
	note_guid = str(note).replace("note://tomboy/", "")

	# skip this event if it is in the list of ignores
	if ignore_tomboy_event.has_key(note_guid) and ignore_tomboy_event[note_guid] > 0:
		ignore_tomboy_event[note_guid] -= 1
		return

	# Remove the note only if it exists
	tomboy_note = None
	if tomboy_notes.has_key(note_guid):
		tomboy_note = tomboy_notes[note_guid]
	else:
		return

	# Remove the note
	try:
		tomboy_note.destroy()
	except:
		pass
	tomboy_notes.pop(note_guid)

	print "Server: Note deleted: " + tomboy_note.name

"""
Syncs notes to and from the server
"""
class Syncer(threading.Thread):
	def __init__(self, name='Syncer'):
		self._stopevent = threading.Event()
		threading.Thread.__init__(self, name=name)

	def __first_sync(self):
		global newest_updated_timestamp
		global needs_first_sync
		global ignore_tomboy_event
		global tomboy_notes

		# Add all the local tomboy notes
		for note in tomboy.ListAllNotes():
			add_tomboy_note(note, False)

		# Get list of all note titles and change dates from server
		datas = TomboyNote.get('all_note_meta_data')
		if len(datas) == 0 or str(datas) == "" or datas == "\n":
			datas = {}

		# Remove prefix from guids. They are only needed to be valid xml
		for key, value in datas.iteritems():
			datas.pop(key)
			datas[key.replace("guid_", "").replace("_", "-")] = value

		# Update the notes on the server and client
		for guid, data in datas.iteritems():
			# Is on server and client ...
			if tomboy_notes.has_key(guid):
				tomboy_note = tomboy_notes[guid]
				# but client's is newer
				if tomboy_note.id and tomboy_note.updated_timestamp > decimal.Decimal(data["updated_timestamp"]):
					tomboy_note.id = int(data['id'])
					tomboy_note.save()
					print "First Sync: Note updated(client newer): " + tomboy_note.name
				# but server's is newer
				else:
					client_note = tomboy_note
					tomboy_note = TomboyNote.find(data['id'])
					tomboy_notes[tomboy_note.guid] = tomboy_note
					if client_note.body != tomboy_note.body or client_note.name != tomboy_note.name or client_note.tag != tomboy_note.tag:
						if not ignore_tomboy_event.has_key(tomboy_note.guid): ignore_tomboy_event[tomboy_note.guid] = 0
						ignore_tomboy_event[tomboy_note.guid] += 1
						tomboy.SetNoteCompleteXml(note, base64.b64decode(tomboy_note.body))
					print "First Sync: Note updated(server newer): " + tomboy_note.name
		
		# Save the notes that are just on the client
		for guid, tomboy_note in tomboy_notes.iteritems():
			if not datas.has_key(guid):
				tomboy_note.save()
				print "First Sync: Note added(new from client): " + tomboy_note.name

		# Get the updated_timestamp of the newest note
		for tomboy_note in tomboy_notes.values():
			if newest_updated_timestamp == None or tomboy_note.updated_timestamp > newest_updated_timestamp:
				newest_updated_timestamp = tomboy_note.updated_timestamp

		needs_first_sync = False

	def __normal_sync(self):
		global newest_updated_timestamp
		global ignore_tomboy_event
		global tomboy_notes

		# Find the notes on the server that are newer or updated
		for server_note in TomboyNote.get('get_newer', newest_updated_timestamp=newest_updated_timestamp):
			# Convert the dict to a note
			tomboy_note = TomboyNote(server_note)

			# Update existing note
			if tomboy_notes.has_key(tomboy_note.guid):
				for note in tomboy.ListAllNotes():
					if str(note) == "note://tomboy/" + tomboy_note.guid:
						tomboy_notes[tomboy_note.guid] = tomboy_note
						if not ignore_tomboy_event.has_key(tomboy_note.guid): ignore_tomboy_event[tomboy_note.guid] = 0
						ignore_tomboy_event[tomboy_note.guid] += 1
						tomboy.SetNoteCompleteXml(note, base64.b64decode(tomboy_note.body))
						print "Syncer: Note updated: " + tomboy_note.name
			# Create new note
			else:
				tomboy_notes[tomboy_note.guid] = tomboy_note
				if not ignore_tomboy_event.has_key(tomboy_note.guid): ignore_tomboy_event[tomboy_note.guid] = 0
				ignore_tomboy_event[tomboy_note.guid] += 1
				note = tomboy.CreateNamedNoteWithUri(tomboy_note.name, "note://tomboy/" + tomboy_note.guid)
				tomboy.SetNoteCompleteXml(note, base64.b64decode(tomboy_note.body))
				print "Syncer: Note added: " + tomboy_note.name

			if newest_updated_timestamp == None or tomboy_note.updated_timestamp > newest_updated_timestamp:
				newest_updated_timestamp = tomboy_note.updated_timestamp

	def run(self):
		global needs_first_sync

		while not self._stopevent.isSet():
			try:
				if needs_first_sync:
					self.__first_sync()
				else:
					self.__normal_sync()
				time.sleep(5)

			except Exception:
				traceback.print_exc(file=sys.stdout)
				exit(1)

	def join(self, timeout=None):
		threading.Thread.join(self, timeout)


def onAccountStatusChanged(account_id, old, new):
	global needs_first_sync
	if needs_first_sync == True: return
	update_pidgin_account_status(account_id, old, new)

def onAccountAdded(account_id):
	global needs_first_sync
	if needs_first_sync == True: return
	add_pidgin_account(account_id)

def onAccountRemoved(account_id):
	global needs_first_sync
	if needs_first_sync == True: return
	remove_pidgin_account(account_id)

def onNoteAdded(note):
	global needs_first_sync
	if needs_first_sync == True: return
	add_tomboy_note(note)

def onNoteSaved(note):
	global needs_first_sync
	if needs_first_sync == True: return
	update_tomboy_note(note)

# FIXME: Figure out what the second argument is. There is no documentation
def onNoteDeleted(note, unknown_object):
	global needs_first_sync
	if needs_first_sync == True: return
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

# Create the user or make sure it exists
try:
	User.get('ensure_user_exists', name=USERNAME, password=PASSWORD, email=EMAIL)
except connection.UnauthorizedAccess, err:
	print 'Invalid login.'
	exit()
except connection.ResourceInvalid, err:
	print "Validation Failed:"
	for error in util.xml_to_dict(err.response.body)['error']:
		print "    " + error
	exit()

# Get the user from the server
user = User.get('get_logged_in_user')

syncer = Syncer()
syncer.start()

# Wait here and run events
gobject.MainLoop().run()



