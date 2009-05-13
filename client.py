#!/usr/bin/env python

import dbus, gobject, dbus.glib
import base64, time, decimal
import sys, os, threading, traceback
import ctypes, pynotify
from xml2dict import *
from pyactiveresource.activeresource import ActiveResource
from pyactiveresource import util
from pyactiveresource import connection

# Move the path to the location of the current file
os.chdir(os.sys.path[0])

# Change the name of this process to spacepony
try:
	libc = ctypes.CDLL('libc.so.6')
	libc.prctl(15, 'spacepony', 0, 0, 0)
except:
	pass

USERNAME = "mattjones"
PASSWORD = "password"
EMAIL = "mattjones@workhorsy.org"
SERVER_SOCKET = "localhost:3000"
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

# Initialize pynotify
if not pynotify.init("Sync notification"):
	print "Failed to initialize pynotify. Exiting ..."
	sys.exit(1)

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
newest_tomboy_timestamp = None
newest_pidgin_timestamp = None
needs_first_sync = True
ignore_tomboy_event = {}
ignore_pidgin_event = {}

def notify_tomboy(title, body):
	n = pynotify.Notification(title, body, 
	"file:///usr/share/app-install/icons/tomboy.png")
	n.show()

def notify_tomboy_summary(count_new_notes, count_updated_notes):
	# If there were no changes
	if count_new_notes + count_updated_notes == 0:
		notify_tomboy("Notes synced from server", "No new notes or updates.")
		return

	# If there were changes show the number
	message = ""
	if count_new_notes > 0:
		message += " New notes: " + str(count_new_notes)
	if count_updated_notes > 0:
		message += " Updated notes: " + str(count_updated_notes)
	notify_tomboy("Notes synced from server", message)

def notify_pidgin(title, body):
	n = pynotify.Notification(title, body, 
	"file:///usr/share/icons/hicolor/48x48/apps/pidgin.png")
	n.show()

def notify_pidgin_summary(count_new_accounts, count_updated_accounts):
	# If there were no changes
	if count_new_accounts + count_updated_accounts == 0:
		notify_pidgin("Pidgin Accounts synced from server", "No new accounts or updates.")
		return

	# If there were changes show the number
	message = ""
	if count_new_accounts > 0:
		message += " New accounts: " + str(count_new_accounts)
	if count_updated_accounts > 0:
		message += " Updated accounts: " + str(count_updated_accounts)
	notify_pidgin("Accounts synced from server", message)

def add_pidgin_account(account_id, save_now = True):
	global newest_pidgin_timestamp
	global ignore_pidgin_event
	global pidgin_accounts
	account_guid = purple.PurpleAccountGetUsername(account_id) + ':' + purple.PurpleAccountGetProtocolId(account_id)

	# skip this event if it is in the list of ignores
	if ignore_pidgin_event.has_key(account_guid) and ignore_pidgin_event[account_guid] > 0:
		ignore_pidgin_event[account_guid] -= 1
		return

	# Skip adding the account if it already exists
	if pidgin_accounts.has_key(account_guid):
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
		pidgin_account = PidginAccount.find(pidgin_account.id, user_id=pidgin_account.user_id)
		pidgin_accounts[account_guid] = pidgin_account
		set_newest_pidgin_timestamp(pidgin_account.updated_timestamp)
	pidgin_accounts[account_guid] = pidgin_account

	if save_now:
		print "Server: Added Pidgin account " + pidgin_account.name + " with the protocol " + pidgin_account.protocol + "."

def update_pidgin_account_status(account_id, old, new):
	global newest_pidgin_timestamp
	global ignore_pidgin_event
	global pidgin_accounts
	account_guid = purple.PurpleAccountGetUsername(account_id) + ':' + purple.PurpleAccountGetProtocolId(account_id)

	# skip this event if it is in the list of ignores
	if ignore_pidgin_event.has_key(account_guid) and ignore_pidgin_event[account_guid] > 0:
		ignore_pidgin_event[account_guid] -= 1
		return

	# Skip the account if it does not exist
	if not pidgin_accounts.has_key(account_guid):
		print "no pidgin account with guid: " + account_guid
		return

	# Get the new status
	status = purple.PurpleSavedstatusGetCurrent()

	# Save the new status
	pidgin_account = pidgin_accounts[account_guid]
	pidgin_account.status = str(purple.PurplePrimitiveGetIdFromType(purple.PurpleSavedstatusGetType(status)))
	pidgin_account.message = str(purple.PurpleSavedstatusGetMessage(status) or "")

	try:
		pidgin_account.save()
		pidgin_account = PidginAccount.find(pidgin_account.id, user_id=pidgin_account.user_id)
		pidgin_accounts[account_guid] = pidgin_account
		set_newest_pidgin_timestamp(pidgin_account.updated_timestamp)
	except Exception, err:
		if str(err) == "HTTP Error 404: Not Found":
			pidgin_accounts.pop(account_guid)

	print "Server: Changed Pidgin status for account " + pidgin_account.name + " to '" + pidgin_account.status + \
		"' with the message '" + pidgin_account.message + "'."

def remove_pidgin_account(account_id):
	global ignore_pidgin_event
	global pidgin_accounts
	account_guid = purple.PurpleAccountGetUsername(account_id) + ':' + purple.PurpleAccountGetProtocolId(account_id)

	# skip this event if it is in the list of ignores
	if ignore_pidgin_event.has_key(account_guid) and ignore_pidgin_event[account_guid] > 0:
		ignore_pidgin_event[account_guid] -= 1
		return

	# Just return if it does not exist
	if not pidgin_accounts.has_key(account_guid):
		return

	# Remove the account
	pidgin_account = pidgin_accounts[account_guid]
	try:
		pidgin_accounts.destroy()
	except:
		pass
	pidgin_accounts.pop(account_guid)

	print "Server: Removed Pidgin account " + pidgin_account.name + " with the protocol " + pidgin_account.protocol + "."

def add_tomboy_note(note, save_now = True):
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
		tomboy_note = TomboyNote.find(tomboy_note.id, user_id=tomboy_note.user_id)
		tomboy_notes[tomboy_note.guid] = tomboy_note
		set_newest_tomboy_timestamp(tomboy_note.updated_timestamp)
	tomboy_notes[note_guid] = tomboy_note

	if save_now:
		print "Server: Note added: " + tomboy_note.name

def update_tomboy_note(note):
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
		tomboy_note = TomboyNote.find(tomboy_note.id, user_id=tomboy_note.user_id)
		tomboy_notes[tomboy_note.guid] = tomboy_note
		set_newest_tomboy_timestamp(tomboy_note.updated_timestamp)
	except Exception, err:
		if str(err) == "HTTP Error 404: Not Found":
			tomboy.HideNote(note)
			tomboy.DeleteNote(note)
			tomboy_notes.pop(note_guid)

	print "Server: Note updated: " + tomboy_note.name


def remove_tomboy_note(note):
	global ignore_tomboy_event
	global tomboy_notes
	note_guid = str(note).replace("note://tomboy/", "")

	# skip this event if it is in the list of ignores
	if ignore_tomboy_event.has_key(note_guid) and ignore_tomboy_event[note_guid] > 0:
		ignore_tomboy_event[note_guid] -= 1
		return

	# Just return if it does not exist
	if not tomboy_notes.has_key(note_guid):
		return

	# Remove the note
	tomboy_note = tomboy_notes[note_guid]
	try:
		tomboy_note.destroy()
	except:
		pass
	tomboy_notes.pop(note_guid)

	print "Server: Note deleted: " + tomboy_note.name

def set_newest_tomboy_timestamp(value):
	global newest_tomboy_timestamp

	if value == None or value <= newest_tomboy_timestamp:
		return

	newest_tomboy_timestamp = value
	f = open('newest_tomboy_timestamp', 'w')
	f.write(str(newest_tomboy_timestamp))
	f.close()

def get_newest_tomboy_timestamp():
	global newest_tomboy_timestamp

	if newest_tomboy_timestamp == None and os.path.exists('newest_tomboy_timestamp'):
		f = open('newest_tomboy_timestamp', 'r')
		try:
			value = decimal.Decimal(f.read())
			if value != '':
				newest_tomboy_timestamp = value
		except:
			pass
		f.close()

	return newest_tomboy_timestamp

def set_newest_pidgin_timestamp(value):
	global newest_pidgin_timestamp

	if value == None or value <= newest_pidgin_timestamp:
		return

	newest_pidgin_timestamp = value
	f = open('newest_pidgin_timestamp', 'w')
	f.write(str(newest_pidgin_timestamp))
	f.close()

def get_newest_pidgin_timestamp():
	global newest_pidgin_timestamp

	if newest_pidgin_timestamp == None and os.path.exists('newest_pidgin_timestamp'):
		f = open('newest_pidgin_timestamp', 'r')
		try:
			value = decimal.Decimal(f.read())
			if value != '':
				newest_pidgin_timestamp = value
		except:
			pass
		f.close()

	return newest_pidgin_timestamp

"""
Syncs notes to and from the server
"""
class Syncer(threading.Thread):
	def __init__(self, name='Syncer'):
		self._stopevent = threading.Event()
		threading.Thread.__init__(self, name=name)

	def __first_sync_pidgin(self):
		global ignore_pidgin_event
		global pidgin_accounts
		count_new_accounts = 0
		count_updated_accounts = 0

		# Add all the local pidgin accounts
		for account in purple.PurpleAccountsGetAll():
			add_pidgin_account(account, False)

		# Find the pidgin accounts on the server that are newer or updated
		newest_timestamp = get_newest_pidgin_timestamp() or 0
		server_accounts = {}
		for server_account in PidginAccount.get('get_newer', newest_timestamp=newest_timestamp, user_id=user.id):
			server_guid = server_account.name + ':' + server_account.protocol
			server_account = PidginAccount(server_account)
			server_accounts[server_guid] = server_account

		# Update the pidgin accounts on the server and client
		for server_account in server_accounts.values():
			server_guid = server_account.name + ':' + server_account.protocol
			# Is on server and client ...
			if pidgin_accounts.has_key(server_guid):
				pidgin_account = pidgin_accounts[server_guid]
				# but client's is newer
				if pidgin_account.id and pidgin_account.updated_timestamp > server_account.updated_timestamp:
					pidgin_account.save()
					print "First Sync: Account updated(client newer): " + pidgin_account.name
					count_updated_accounts += 1
				# but server's is newer
				else:
					account_id = purple.PurpleAccountsFind(server_account.name, server_account.protocol)

					if not ignore_pidgin_event.has_key(pidgin_account): ignore_pidgin_event[pidgin_account] = 0
					ignore_pidgin_event[pidgin_account] += 1

					if pidgin_account.name != server_account.name:
						purple.PurpleAccountSetUsername(account_id, pidgin_account.name)
					if pidgin_account.hashed_password != server_account.hashed_password:
						purple.PurpleAccountSetPassword(account_id, pidgin_account.name)
					if pidgin_account.salt != server_account.salt:
						pass
					if pidgin_account.status != server_account.status or \
						pidgin_account.message != server_account.message:
						purple.PurpleSavedstatusSetMessage(server_account.status, server_account.message)
					if pidgin_account.protocol != server_account.protocol:
						purple.PurpleAccountSetProtocolId(account_id, server_account.protocol)
					if pidgin_account.icon != server_account.icon:
						purple.PurpleAccountSetBuddyIconPath(account_id, server_account.protocol)

					pidgin_accounts[server_guid] = server_account

					print "First Sync: Account updated(server newer): " + server_account.name
					count_updated_accounts += 1

		# Save the pidgin accounts that are just on the server
		for server_account in server_accounts.values():
			server_guid = server_account.name + ':' + server_account.protocol

			if not pidgin_accounts.has_key(server_guid):
				if not ignore_pidgin_event.has_key(server_guid): ignore_pidgin_event[server_guid] = 0
				ignore_pidgin_event[server_guid] += 1

				pidgin_accounts[server_guid] = server_account
				account = purple.PurpleAccountNew(server_account.name, server_account.protocol)
				print "First Sync: Account added(new from server): " + server_account.name
				count_new_notes += 1

		# Save the pidgin accounts that are just on the client
		for pidgin_account in pidgin_accounts.values():
			account_guid = pidgin_account.name + ':' + pidgin_account.protocol
			if not server_accounts.has_key(account_guid):
				pidgin_account.save()
				print "First Sync: Account added(new from client): " + pidgin_account.name
				count_new_accounts += 1

		# Get the updated_timestamp of the newest pidgin account
		for pidgin_account in pidgin_accounts.values():
			set_newest_pidgin_timestamp(pidgin_account.updated_timestamp)

		notify_pidgin_summary(count_new_accounts, count_updated_accounts)

	def __first_sync_tomboy(self):
		global ignore_tomboy_event
		global tomboy_notes
		count_new_notes = 0
		count_updated_notes = 0

		# Add all the local tomboy notes
		for note in tomboy.ListAllNotes():
			add_tomboy_note(note, False)

		# Find the notes on the server that are newer or updated
		newest_timestamp = get_newest_tomboy_timestamp() or 0
		server_notes = {}
		for server_note in TomboyNote.get('get_newer', newest_timestamp=newest_timestamp, user_id=user.id):
			server_note = TomboyNote(server_note)
			server_notes[server_note.guid] = server_note

		# Update the notes on the server and client
		for server_note in server_notes.values():
			# Is on server and client ...
			if tomboy_notes.has_key(server_note.guid):
				tomboy_note = tomboy_notes[server_note.guid]
				# but client's is newer
				if tomboy_note.id and tomboy_note.updated_timestamp > server_note.updated_timestamp:
					tomboy_note.save()
					print "First Sync: Note updated(client newer): " + tomboy_note.name
					count_updated_notes += 1
				# but server's is newer
				else:
					if tomboy_note.body != server_note.body or tomboy_note.name != server_note.name or tomboy_note.tag != server_note.tag:
						if not ignore_tomboy_event.has_key(tomboy_note.guid): ignore_tomboy_event[tomboy_note.guid] = 0
						ignore_tomboy_event[tomboy_note.guid] += 1

						tomboy_notes[tomboy_note.guid] = server_note
						tomboy.SetNoteCompleteXml("note://tomboy/" + tomboy_note.guid, base64.b64decode(server_note.body))
					print "First Sync: Note updated(server newer): " + tomboy_note.name
					count_updated_notes += 1

		# Save the notes that are just on the server
		for server_note in server_notes.values():
			if not tomboy_notes.has_key(server_note.guid):
				if not ignore_tomboy_event.has_key(server_note.guid): ignore_tomboy_event[server_note.guid] = 0
				ignore_tomboy_event[server_note.guid] += 1

				tomboy_notes[server_note.guid] = server_note
				note = tomboy.CreateNamedNoteWithUri(server_note.name, "note://tomboy/" + server_note.guid)
				tomboy.SetNoteCompleteXml(note, base64.b64decode(server_note.body))
				print "First Sync: Note added(new from server): " + server_note.name
				count_new_notes += 1

		# Save the notes that are just on the client
		for tomboy_note in tomboy_notes.values():
			if not server_notes.has_key(tomboy_note.guid):
				tomboy_note.save()
				print "First Sync: Note added(new from client): " + tomboy_note.name
				count_new_notes += 1

		# Get the updated_timestamp of the newest note
		for tomboy_note in tomboy_notes.values():
			set_newest_tomboy_timestamp(tomboy_note.updated_timestamp)

		notify_tomboy_summary(count_new_notes, count_updated_notes)

	def __normal_sync_pidgin(self):
		#FIXME: Make this work just like the tomboy one
		pass

	def __normal_sync_tomboy(self):
		global ignore_tomboy_event
		global tomboy_notes

		# Find the notes on the server that are newer or updated
		newest_timestamp = get_newest_tomboy_timestamp() or 0
		server_notes = {}
		for server_note in TomboyNote.get('get_newer', newest_timestamp=newest_timestamp, user_id=user.id):
			server_note = TomboyNote(server_note)
			server_notes[server_note.guid] = server_note

		# Update the notes on the server and client
		for server_note in server_notes.values():
			# Is on server and client ...
			if tomboy_notes.has_key(server_note.guid):
				tomboy_note = tomboy_notes[server_note.guid]
				# but client's is newer
				if tomboy_note.id and tomboy_note.updated_timestamp > server_note.updated_timestamp:
					tomboy_note.save()
					tomboy_note = TomboyNote.find(tomboy_note.id, user_id=tomboy_note.user_id)
					tomboy_notes[tomboy_note.guid] = tomboy_note
					print "Normal Sync: Note updated(client newer): " + tomboy_note.name
				# but server's is newer
				else:
					if tomboy_note.body != server_note.body or tomboy_note.name != server_note.name or tomboy_note.tag != server_note.tag:
						if not ignore_tomboy_event.has_key(tomboy_note.guid): ignore_tomboy_event[tomboy_note.guid] = 0
						ignore_tomboy_event[tomboy_note.guid] += 1

						tomboy_note = server_note
						tomboy_notes[tomboy_note.guid] = server_note
						tomboy.SetNoteCompleteXml("note://tomboy/" + server_note.guid, base64.b64decode(server_note.body))
						print "Normal Sync: Note updated(server newer): " + tomboy_note.name
						notify_tomboy("Updated tomboy note", tomboy_note.name)

				set_newest_tomboy_timestamp(tomboy_note.updated_timestamp)

		# Save the notes that are just on the server
		for server_note in server_notes.values():
			if not tomboy_notes.has_key(server_note.guid):
				if not ignore_tomboy_event.has_key(server_note.guid): ignore_tomboy_event[server_note.guid] = 0
				ignore_tomboy_event[server_note.guid] += 1

				tomboy_notes[server_note.guid] = server_note
				note = tomboy.CreateNamedNoteWithUri(server_note.name, "note://tomboy/" + server_note.guid)
				tomboy.SetNoteCompleteXml(note, base64.b64decode(server_note.body))
				set_newest_tomboy_timestamp(server_note.updated_timestamp)
				print "Normal Sync: Note added(new from server): " + server_note.name
				notify_tomboy("Added tomboy note", server_note.name)

	def run(self):
		global needs_first_sync

		while not self._stopevent.isSet():
			try:
				if needs_first_sync:
					self.__first_sync_pidgin()
					self.__first_sync_tomboy()
					needs_first_sync = False
				else:
					self.__normal_sync_pidgin()
					self.__normal_sync_tomboy()
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
user = User(User.get('get_logged_in_user'))

syncer = Syncer()
syncer.start()

# Wait here and run events
gobject.MainLoop().run()



