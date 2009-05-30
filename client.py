#!/usr/bin/env python

import dbus, gobject, dbus.glib, gconf
import base64, time, decimal, mimetypes
import sys, os, threading, traceback, commands
import ctypes, pynotify, pyinotify
from xml2dict import *
from pyactiveresource.activeresource import ActiveResource
from pyactiveresource import util
from pyactiveresource import connection

# Move the path to the location of the current file
os.chdir(os.sys.path[0])

# Initialize the mime types
mimetypes.init()

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

class Bin(ActiveResource):
	_site = SERVER_ADDRESS

# Make it so the dbus threads and python threads work at the same time
gobject.threads_init()
dbus.glib.init_threads()

# Initialize pynotify
if not pynotify.init("Sync notification"):
	print "Failed to initialize pynotify. Exiting ..."
	sys.exit(1)

class BaseSync(object):
	def __init__(self, app_name):
		self._app_name = app_name
		self._newest_timestamp = 0

	def set_newest_timestamp(self, value):
		if value == None or value <= self._newest_timestamp:
			return

		self._newest_timestamp = value
		f = open('newest_' + self._app_name + '_timestamp', 'w')
		f.write(str(self._newest_timestamp))
		f.close()

	def get_newest_timestamp(self):
		if self._newest_timestamp == None and os.path.exists('newest_' + self._app_name + '_timestamp'):
			f = open('newest_' + self._app_name + '_timestamp', 'r')
			try:
				value = decimal.Decimal(f.read())
				if value != '':
					self._newest_timestamp = value
			except:
				pass
			f.close()

		return self._newest_timestamp

class GConfFileSync(BaseSync):
	def __init__(self, user):
		super(GConfFileSync, self).__init__('background')
		self._user = user

	def start(self):
		self._gconf_client = gconf.client_get_default()
		self._gconf_client.add_dir('/', gconf.CLIENT_PRELOAD_NONE)
		self._gconf_client.notify_add('/', self.__on_gconf_key_changed)

	def __save_background(self, filename):
		# Read the file into a string
		print "Server: File saved: " + filename
		f = open(filename, 'rb')
		file_data = f.read()
		f.close()

		# Get the file mime type and extention
		mime_type = commands.getoutput("file -b -i \"" + filename + "\"")
		extention = mimetypes.guess_extension(mime_type).lstrip('.')

		# Update the background
		User.post('background/' + str(self._user.id), 
					body=file_data, 
					extension=extention, 
					mime_type=mime_type, 
					original_filename=filename)

		# Update the background timestamp
		background = Bin(User.get(str(self._user.id) + '/background'))
		self._user.background_id = background.id
		self.set_newest_timestamp(background.updated_timestamp)

	def __on_gconf_key_changed(self, client, id, entry, data):
		key = entry.key

		if key == "/desktop/gnome/background/picture_filename":
			value = self.__extract_gconf_value(entry.get_value())
			self.__save_background(value)

	def __extract_gconf_value(self, gconf_value):
		if gconf_value == None:
			return None

		type = gconf_value.type
		value = None
		if type == gconf.VALUE_INT:
			value = gconf_value.get_int()
		elif type == gconf.VALUE_STRING:
			value = gconf_value.get_string()
		elif type == gconf.VALUE_BOOL:
			value = gconf_value.get_bool()
		elif type == gconf.VALUE_FLOAT:
			value = gconf_value.get_float()
		elif type == gconf.VALUE_LIST:
			value = []
			list = gconf_value.get_list()
			for item in list:
				value.append(self.__extract_gconf_value(item))
		elif type == gconf.VALUE_SCHEMA or type == gconf.VALUE_PAIR or \
			type == gconf.VALUE_INVALID:
			pass
		else:
			raise "gconf value of unknown type " + str(type)

		return value

	def sync(self):
		whole_file_name = self._gconf_client.get_string('/desktop/gnome/background/picture_filename')

		if self.get_newest_timestamp() == None:
			self.set_newest_timestamp(os.path.getmtime(whole_file_name))

		# FIXME ActiveResource should return None when you do Bin(None)
		background = User.get(str(self._user.id) + '/background')
		if background: background = Bin(background)
		file_exists = os.path.exists(whole_file_name)

		# is on server and client
		if background and \
			background.file_name == whole_file_name and \
			file_exists:

			# but the client's is newer
			if self.get_newest_timestamp() > background.updated_timestamp:
				self.__save_background(whole_file_name)
				print "First Sync: Background added(updated from client): " + background.file_name
			# but the server's is newer
			elif self.get_newest_timestamp() < background.updated_timestamp:
				background = Bin(User.get(str(self._user.id) + '/background'))

				data = User.get(str(self._user.id) + '/background', 
												extension='jpeg', 
												mime_type='image/jpeg')
				f = open(background.file_name, 'wb')
				f.write(data)
				f.close()
				self._gconf_client.set_string(background.file_name)
				print "First Sync: Background added(updated from server): " + background.file_name

		# is just on the client
		elif background == None and file_exists:
			self.__save_background(whole_file_name)
			print "First Sync: Background added(new from client): " + whole_file_name

		# is just on the server
		elif background != None and not file_exists:
			background = Bin(User.get(str(self._user.id) + '/background'))

			data = User.get(str(self._user.id) + '/background', 
											extension='jpeg', 
											mime_type='image/jpeg')
			f = open(background.file_name, 'wb')
			f.write(data)
			f.close()
			self._gconf_client.set_string(background.file_name)
			print "First Sync: Background added(new from server): " + background.file_name

class WatchFileSync(BaseSync):
	class EventHandler(pyinotify.ProcessEvent):
		def __init__(self, parent):
			self._parent = parent

		# new
		def process_IN_CREATE(self, event):
			self._parent._save_avatar(event.name)

		# new
		def process_IN_MOVED_TO(self, event):
			self._parent._save_avatar(event.name)

		# update
		def process_IN_MODIFY(self, event):
			self._parent._save_avatar(event.name)

		# destroy
		def process_IN_DELETE(self, event):
			if not self._parent._file_we_want(event.name): return

		# destroy
		def process_IN_MOVED_FROM(self, event):
			if not self._parent._file_we_want(event.name): return

	def __init__(self, user):
		super(WatchFileSync, self).__init__('avatar')

		# Get the files to watch
		self._path = '/home/matt/'
		self._files = { 'avatar' : '.face'}

		self._avatar_syncer = BaseSync('avatar')

		self._user = user

	def get_files(self):
		return self._files.values()

	def _file_we_want(self, file_name):
		return self.get_files().count(file_name) > 0

	def _save_avatar(self, filename):
		if not self._file_we_want(filename): return

		# Read the file into a string
		original_filename = self._path + filename
		print "Server: File saved: " + original_filename
		f = open(original_filename, 'rb')
		file_data = f.read()
		f.close()

		# Get the file mime type and extention
		mime_type = commands.getoutput("file -b -i \"" + original_filename + "\"")
		extention = mimetypes.guess_extension(mime_type).lstrip('.')

		# Update the avatar
		User.post('avatar/' + str(self._user.id), 
					body=file_data, 
					extension=extention, 
					mime_type=mime_type, 
					original_filename=original_filename)

		# Update the avatar timestamp
		avatar = Bin(User.get(str(self._user.id) + '/avatar'))
		self._user.avatar_id = avatar.id
		self._avatar_syncer.set_newest_timestamp(avatar.updated_timestamp)

	def start(self):
		# Only get CRUD events
		mask = pyinotify.EventsCodes.IN_MODIFY | \
				pyinotify.EventsCodes.IN_DELETE | \
				pyinotify.EventsCodes.IN_CREATE | \
				pyinotify.EventsCodes.IN_MOVED_FROM | \
				pyinotify.EventsCodes.IN_MOVED_TO

		# Start watching the files
		wm = pyinotify.WatchManager()
		notifier = pyinotify.ThreadedNotifier(wm, WatchFileSync.EventHandler(self))
		notifier.start()
		wm.add_watch(self._path, mask)

	def sync(self):
		for file_type, file_name in self._files.iteritems():
			whole_file_name = self._path + file_name

			if file_type != 'avatar':
				break

			if self._avatar_syncer.get_newest_timestamp() == None:
				self._avatar_syncer.set_newest_timestamp(os.path.getmtime(whole_file_name))

			# FIXME ActiveResource should return None when you do Bin(None)
			avatar = User.get(str(self._user.id) + '/avatar')
			if avatar: avatar = Bin(avatar)
			file_exists = os.path.exists(whole_file_name)

			# is on server and client
			if avatar and \
				avatar.file_name == whole_file_name and \
				file_exists:

				# but the client's is newer
				if self._avatar_syncer.get_newest_timestamp() > avatar.updated_timestamp:
					self._save_avatar(file_name)
					print "First Sync: Avatar added(updated from client): " + avatar.file_name
				# but the server's is newer
				elif self._avatar_syncer.get_newest_timestamp() < avatar.updated_timestamp:
					avatar = Bin(User.get(str(self._user.id) + '/avatar'))

					data = User.get(str(self._user.id) + '/avatar', 
													extension='jpeg', 
													mime_type='image/jpeg')
					f = open(avatar.file_name, 'wb')
					f.write(data)
					f.close()
					print "First Sync: Avatar added(updated from server): " + avatar.file_name

			# is just on the client
			elif avatar == None and file_exists:
				self._save_avatar(file_name)
				print "First Sync: Avatar added(new from client): " + file_name

			# is just on the server
			elif avatar != None and not file_exists:
				avatar = Bin(User.get(str(self._user.id) + '/avatar'))

				data = User.get(str(self._user.id) + '/avatar', 
												extension='jpeg', 
												mime_type='image/jpeg')
				f = open(avatar.file_name, 'wb')
				f.write(data)
				f.close()
				print "First Sync: Avatar added(new from server): " + avatar.file_name

class PidginSync(BaseSync):
	# Specify status ID values
	STATUS_OFFLINE = 1
	STATUS_AVAILABLE = 2
	STATUS_UNAVAILABLE = 3
	STATUS_INVISIBLE = 4
	STATUS_AWAY = 5
	STATUS_EXTENDED_AWAY = 6
	STATUS_MOBILE = 7
	STATUS_TUNE = 8

	def __init__(self, bus, user):
		super(PidginSync, self).__init__('pidgin')
		self._newest_timestamp = None
		self._ignore_event = {}
		self._accounts = {}
		self._user = user

		#(success, status) = bus.start_service_by_name('im.pidgin.purple.PurpleService')

		# Get Pidgin's D-Bus interface
		try:
			obj = bus.get_object("im.pidgin.purple.PurpleService", 
								"/im/pidgin/purple/PurpleObject")
			self._purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
		except:
			raise Exception("Please start pidgin first.")

	def notify(self, title, body):
		n = pynotify.Notification(title, body, 
		"file:///usr/share/icons/hicolor/48x48/apps/pidgin.png")
		n.show()

	def notify_summary(self, count_new_accounts, count_updated_accounts):
		# If there were no changes
		if count_new_accounts + count_updated_accounts == 0:
			self.notify("Pidgin Accounts synced with server", "No new accounts or updates.")
			return

		# If there were changes show the number
		message = ""
		if count_new_accounts > 0:
			message += " New accounts: " + str(count_new_accounts)
		if count_updated_accounts > 0:
			message += " Updated accounts: " + str(count_updated_accounts)
		self.notify("Accounts synced with server", message)

	def add_account(self, account_id, save_now = True):
		account_guid = self._purple.PurpleAccountGetUsername(account_id) + ':' + self._purple.PurpleAccountGetProtocolId(account_id)

		# skip this event if it is in the list of ignores
		if self._ignore_event.has_key(account_guid) and self._ignore_event[account_guid] > 0:
			self._ignore_event[account_guid] -= 1
			return

		# Skip adding the account if it already exists
		if self._accounts.has_key(account_guid):
			return

		# Retrieve the current status
		status = self._purple.PurpleSavedstatusGetCurrent()

		pidgin_account = PidginAccount()
		pidgin_account.user_id = self._user.id
		pidgin_account.name = str(self._purple.PurpleAccountGetUsername(account_id))
		pidgin_account.password = str(self._purple.PurpleAccountGetPassword(account_id))
		pidgin_account.status = str(self._purple.PurplePrimitiveGetIdFromType(self._purple.PurpleSavedstatusGetType(status)))
		pidgin_account.message = str(self._purple.PurpleSavedstatusGetMessage(status) or "")
		pidgin_account.protocol = str(self._purple.PurpleAccountGetProtocolId(account_id))
		pidgin_account.icon = str(self._purple.PurpleAccountGetBuddyIconPath(account_id) or "")
		if save_now:
			pidgin_account.save()
			pidgin_account = PidginAccount.find(pidgin_account.id, user_id=pidgin_account.user_id)
			self._accounts[account_guid] = pidgin_account
			self.set_newest_timestamp(pidgin_account.updated_timestamp)
		self._accounts[account_guid] = pidgin_account

		if save_now:
			print "Server: Added Pidgin account " + pidgin_account.name + " with the protocol " + pidgin_account.protocol + "."

	def update_account_status(self, account_id, old, new):
		account_guid = self._purple.PurpleAccountGetUsername(account_id) + ':' + self._purple.PurpleAccountGetProtocolId(account_id)

		# skip this event if it is in the list of ignores
		if self._ignore_event.has_key(account_guid) and self._ignore_event[account_guid] > 0:
			self._ignore_event[account_guid] -= 1
			return

		# Skip the account if it does not exist
		if not self._accounts.has_key(account_guid):
			print "no pidgin account with guid: " + account_guid
			return

		# Get the new status
		status = self._purple.PurpleSavedstatusGetCurrent()

		# Save the new status
		pidgin_account = self._accounts[account_guid]
		pidgin_account.status = str(self._purple.PurplePrimitiveGetIdFromType(self._purple.PurpleSavedstatusGetType(status)))
		pidgin_account.message = str(self._purple.PurpleSavedstatusGetMessage(status) or "")

		try:
			pidgin_account.save()
			pidgin_account = PidginAccount.find(pidgin_account.id, user_id=pidgin_account.user_id)
			self._accounts[account_guid] = pidgin_account
			self.set_newest_timestamp(pidgin_account.updated_timestamp)
		except Exception, err:
			if str(err) == "HTTP Error 404: Not Found":
				self._accounts.pop(account_guid)

		print "Server: Changed Pidgin status for account " + pidgin_account.name + " to '" + (pidgin_account.status or '') + \
			"' with the message '" + (pidgin_account.message or '') + "'."

	def remove_account(self, account_id):
		account_guid = self._purple.PurpleAccountGetUsername(account_id) + ':' + self._purple.PurpleAccountGetProtocolId(account_id)

		# skip this event if it is in the list of ignores
		if self._ignore_event.has_key(account_guid) and self._ignore_event[account_guid] > 0:
			self._ignore_event[account_guid] -= 1
			return

		# Just return if it does not exist
		if not self._accounts.has_key(account_guid):
			return

		# Remove the account
		pidgin_account = self._accounts[account_guid]
		try:
			self._accounts.destroy()
		except:
			pass
		self._accounts.pop(account_guid)

		print "Server: Removed Pidgin account " + pidgin_account.name + " with the protocol " + pidgin_account.protocol + "."

	def first_sync(self):
		count_new_accounts = 0
		count_updated_accounts = 0

		# Add all the local pidgin accounts
		for account in self._purple.PurpleAccountsGetAll():
			self.add_account(account, False)

		# Find the pidgin accounts on the server that are newer or updated
		newest_timestamp = self.get_newest_timestamp() or 0
		server_accounts = {}
		for server_account in PidginAccount.get('get_meta', user_id=self._user.id):
			server_account = PidginAccount(server_account)
			server_guid = server_account.name + ':' + server_account.protocol
			server_accounts[server_guid] = server_account

		# Update the pidgin accounts on the server and client
		for server_account in server_accounts.values():
			server_guid = server_account.name + ':' + server_account.protocol
			# Is on server and client ...
			if self._accounts.has_key(server_guid):
				pidgin_account = self._accounts[server_guid]
				# but client's is newer
				if pidgin_account.id and pidgin_account.updated_timestamp > server_account.updated_timestamp:
					pidgin_account.save()
					print "First Sync: Account updated(client newer): " + pidgin_account.name
					count_updated_accounts += 1
				# but server's is newer
				else:
					server_account = PidginAccount.find(server_account.id, user_id=server_account.user_id)
					account_id = self._purple.PurpleAccountsFind(server_account.name, server_account.protocol)
					account_changed = False

					if not self._ignore_event.has_key(server_guid): self._ignore_event[server_guid] = 0
					self._ignore_event[server_guid] += 1

					if pidgin_account.name != server_account.name:
						account_changed = True
						self._purple.PurpleAccountSetUsername(account_id, pidgin_account.name)
					if pidgin_account.password != server_account.password:
						account_changed = True
						self._purple.PurpleAccountSetPassword(account_id, pidgin_account.password)
					if (pidgin_account.status or '') != (server_account.status or '') or \
						(pidgin_account.message or '') != (server_account.message or ''):
						account_changed = True
						status = self._purple.PurpleSavedstatusFind(server_account.status)
						self._purple.PurpleSavedstatusSetMessage(status, server_account.message or "")
					if pidgin_account.protocol != server_account.protocol:
						account_changed = True
						self._purple.PurpleAccountSetProtocolId(account_id, server_account.protocol)
					if (pidgin_account.icon or '') != (server_account.icon or ''):
						account_changed = True
						self._purple.PurpleAccountSetBuddyIconPath(account_id, server_account.icon or "")

					self._accounts[server_guid] = server_account

					if account_changed:
						print "First Sync: Account updated(server newer): " + server_account.name
						count_updated_accounts += 1

		# Save the pidgin accounts that are just on the server
		for server_account in server_accounts.values():
			server_account = PidginAccount.find(server_account.id, user_id=server_account.user_id)
			server_guid = server_account.name + ':' + server_account.protocol

			if not self._accounts.has_key(server_guid):
				if not self._ignore_event.has_key(server_guid): self._ignore_event[server_guid] = 0
				self._ignore_event[server_guid] += 1

				self._accounts[server_guid] = server_account
				account_id = self._purple.PurpleAccountNew(server_account.name, server_account.protocol)
				self._purple.PurpleAccountsAdd(account_id)

				self._purple.PurpleAccountSetRememberPassword(account_id, 1)
				self._purple.PurpleAccountSetPassword(account_id, server_account.password)

				self._purple.PurpleAccountSetEnabled(account_id, "gtk-gaim", 1)

				status = self._purple.PurpleSavedstatusFind(server_account.status)
				self._purple.PurpleSavedstatusSetMessage(status, server_account.message or "")
				if server_account.icon and server_account.icon != '':
					self._purple.PurpleAccountSetBuddyIconPath(account_id, server_account.icon)
				print "First Sync: Account added(new from server): " + server_account.name
				count_new_accounts += 1

		# Save the pidgin accounts that are just on the client
		for pidgin_account in self._accounts.values():
			account_guid = pidgin_account.name + ':' + pidgin_account.protocol
			if not server_accounts.has_key(account_guid):
				pidgin_account.save()
				print "First Sync: Account added(new from client): " + pidgin_account.name
				count_new_accounts += 1

		# Get the updated_timestamp of the newest pidgin account
		for pidgin_account in self._accounts.values():
			self.set_newest_timestamp(pidgin_account.updated_timestamp)

		self.notify_summary(count_new_accounts, count_updated_accounts)

	def normal_sync(self):
		# Find the pidgin accounts on the server that are newer or updated
		newest_timestamp = self.get_newest_timestamp() or 0
		server_accounts = {}
		for server_account in PidginAccount.get('get_newer', newest_timestamp=newest_timestamp, user_id=self._user.id):
			server_account = PidginAccount(server_account)
			server_guid = server_account.name + ':' + server_account.protocol
			server_accounts[server_guid] = server_account

		# Update the pidgin accounts on the server and client
		for server_account in server_accounts.values():
			server_guid = server_account.name + ':' + server_account.protocol
			# Is on server and client ...
			if self._accounts.has_key(server_guid):
				pidgin_account = self._accounts[server_guid]
				# but client's is newer
				if pidgin_account.id and pidgin_account.updated_timestamp > server_account.updated_timestamp:
					pidgin_account.save()
					pidgin_account = PidginAccount.find(pidgin_account.id, user_id=pidgin_account.user_id)
					self._accounts[server_guid] = pidgin_account
					print "Normal Sync: Account updated(client newer): " + pidgin_account.name
				# but server's is newer
				else:
					account_id = self._purple.PurpleAccountsFind(server_account.name, server_account.protocol)
					account_changed = False

					if not self._ignore_event.has_key(server_guid): self._ignore_event[server_guid] = 0
					self._ignore_event[server_guid] += 1

					if pidgin_account.name != server_account.name:
						account_changed = True
						self._purple.PurpleAccountSetUsername(account_id, pidgin_account.name)
					if pidgin_account.password != server_account.password:
						account_changed = True
						self._purple.PurpleAccountSetPassword(account_id, pidgin_account.password)
					if (pidgin_account.status or '') != (server_account.status or '') or \
						(pidgin_account.message or '') != (server_account.message or ''):
						account_changed = True
						status = self._purple.PurpleSavedstatusFind(server_account.status)
						self._purple.PurpleSavedstatusSetMessage(status, server_account.message or "")
					if pidgin_account.protocol != server_account.protocol:
						account_changed = True
						self._purple.PurpleAccountSetProtocolId(account_id, server_account.protocol)
					if (pidgin_account.icon or '') != (server_account.icon or ''):
						account_changed = True
						self._purple.PurpleAccountSetBuddyIconPath(account_id, server_account.icon or "")

					if account_changed:
						print "Normal Sync: Account updated(server newer): " + server_account.name
						self.notify("Updated pidgin account", server_account.name)

				self.set_newest_timestamp(server_account.updated_timestamp)

		# Save the pidgin accounts that are just on the server
		for server_account in server_accounts.values():
			server_guid = server_account.name + ':' + server_account.protocol
			if not self._accounts.has_key(server_guid):
				if not self._ignore_event.has_key(server_guid): self._ignore_event[server_guid] = 0
				self._ignore_event[server_guid] += 1

				self._accounts[server_guid] = server_account
				account_id = self._purple.PurpleAccountNew(server_account.name, server_account.protocol)
				self._purple.PurpleAccountsAdd(account_id)

				self._purple.PurpleAccountSetRememberPassword(account_id, 1)
				self._purple.PurpleAccountSetPassword(account_id, server_account.password)

				self._purple.PurpleAccountSetEnabled(account_id, "gtk-gaim", 1)

				status = self._purple.PurpleSavedstatusFind(server_account.status)
				self._purple.PurpleSavedstatusSetMessage(status, server_account.message or "")
				if server_account.icon and server_account.icon != '':
					self._purple.PurpleAccountSetBuddyIconPath(account_id, server_account.icon)




				self.set_newest_timestamp(server_account.updated_timestamp)
				print "Normal Sync: Account added(new from server): " + server_account.name
				self.notify("Added pidgin account", server_account.name)


class TomboySync(BaseSync):
	def __init__(self, bus, user):
		super(TomboySync, self).__init__('tomboy')
		self._newest_timestamp = None
		self._ignore_event = {}
		self._notes = {}
		self._user = user

		(success, status) = bus.start_service_by_name('org.gnome.Tomboy')

		# Get Tomboy's D-Bus interface
		try:
			obj = bus.get_object("org.gnome.Tomboy", 
								"/org/gnome/Tomboy/RemoteControl")
			self._tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")
		except:
			raise Exception("Please start tomboy first.")


	def notify(self, title, body):
		n = pynotify.Notification(title, body, 
		"file:///usr/share/app-install/icons/tomboy.png")
		n.show()

	def notify_summary(self, count_new_notes, count_updated_notes):
		# If there were no changes
		if count_new_notes + count_updated_notes == 0:
			self.notify("Notes synced with server", "No new notes or updates.")
			return

		# If there were changes show the number
		message = ""
		if count_new_notes > 0:
			message += " New notes: " + str(count_new_notes)
		if count_updated_notes > 0:
			message += " Updated notes: " + str(count_updated_notes)
		self.notify("Notes synced with server", message)

	def add_note(self, note, save_now = True):
		note_guid = str(note).replace("note://tomboy/", "")

		# skip this event if it is in the list of ignores
		if self._ignore_event.has_key(note_guid) and self._ignore_event[note_guid] > 0:
			self._ignore_event[note_guid] -= 1
			return

		# Skip adding the note if it already exists
		if self._notes.has_key(note_guid):
			return

		# Save the note
		tomboy_note = TomboyNote()
		tomboy_note.guid = note_guid
		tomboy_note.user_id = self._user.id
		tomboy_note.name = str(self._tomboy.GetNoteTitle(note))
		tomboy_note.body = base64.b64encode(str(self._tomboy.GetNoteCompleteXml(note)))
		tomboy_note.created_timestamp = None
		tags = []
		for tag in self._tomboy.GetTagsForNote(note):
			tags.append(str(tag))
		tomboy_note.tag = str.join(', ', tags)
		if save_now:
			tomboy_note.save()
			tomboy_note = TomboyNote.find(tomboy_note.id, user_id=tomboy_note.user_id)
			self._notes[tomboy_note.guid] = tomboy_note
			self.set_newest_timestamp(tomboy_note.updated_timestamp)
		self._notes[note_guid] = tomboy_note

		if save_now:
			print "Server: Note added: " + tomboy_note.name

	def update_note(self, note):
		note_guid = str(note).replace("note://tomboy/", "")

		# skip this event if it is in the list of ignores
		if self._ignore_event.has_key(note_guid) and self._ignore_event[note_guid] > 0:
			self._ignore_event[note_guid] -= 1
			return

		# Skip the note if it does not exist
		if not self._notes.has_key(note_guid):
			print "no note with guid: " + note_guid
			return

		# Skip the event if the content has not changed
		new_body = str(self._tomboy.GetNoteCompleteXml(note))
		old_body = base64.b64decode(self._notes[note_guid].body)
		if new_body.split('<note-content')[1].split('</note-content>')[0] == \
			old_body.split('<note-content')[1].split('</note-content>')[0]:
			return

		# Save the changes to the note
		tomboy_note = self._notes[note_guid]
		tomboy_note.name = str(self._tomboy.GetNoteTitle(note))
		tomboy_note.body = base64.b64encode(new_body)
		tags = []
		for tag in self._tomboy.GetTagsForNote(note):
			tags.append(str(tag))
		tomboy_note.tag = str.join(', ', tags)

		try:
			tomboy_note.save()
			tomboy_note = TomboyNote.find(tomboy_note.id, user_id=tomboy_note.user_id)
			self._notes[tomboy_note.guid] = tomboy_note
			self.set_newest_timestamp(tomboy_note.updated_timestamp)
		except Exception, err:
			if str(err) == "HTTP Error 404: Not Found":
				self._tomboy.HideNote(note)
				self._tomboy.DeleteNote(note)
				self._notes.pop(note_guid)

		print "Server: Note updated: " + tomboy_note.name


	def remove_note(self, note):
		note_guid = str(note).replace("note://tomboy/", "")

		# skip this event if it is in the list of ignores
		if self._ignore_event.has_key(note_guid) and self._ignore_event[note_guid] > 0:
			self._ignore_event[note_guid] -= 1
			return

		# Just return if it does not exist
		if not self._notes.has_key(note_guid):
			return

		# Remove the note
		tomboy_note = self._notes[note_guid]
		try:
			tomboy_note.destroy()
		except:
			pass
		self._notes.pop(note_guid)

		print "Server: Note deleted: " + tomboy_note.name

	def first_sync(self):
		count_new_notes = 0
		count_updated_notes = 0

		# Add all the local tomboy notes
		for note in self._tomboy.ListAllNotes():
			self.add_note(note, False)

		# Find the notes on the server that are newer or updated
		newest_timestamp = self.get_newest_timestamp() or 0
		server_notes = {}
		for server_note in TomboyNote.get('get_meta', user_id=self._user.id):
			server_note = TomboyNote(server_note)
			server_notes[server_note.guid] = server_note

		# Update the notes on the server and client
		for server_note in server_notes.values():
			# Is on server and client ...
			if self._notes.has_key(server_note.guid):
				tomboy_note = self._notes[server_note.guid]
				# but client's is newer
				if tomboy_note.id and tomboy_note.updated_timestamp > server_note.updated_timestamp:
					tomboy_note.save()
					print "First Sync: Note updated(client newer): " + tomboy_note.name
					count_updated_notes += 1
				# but server's is newer
				else:
					server_note = TomboyNote.find(server_note.id, user_id=server_note.user_id)
					account_changed = False

					if not self._ignore_event.has_key(tomboy_note.guid): self._ignore_event[tomboy_note.guid] = 0
					self._ignore_event[tomboy_note.guid] += 1

					if tomboy_note.body != server_note.body or tomboy_note.name != server_note.name or tomboy_note.tag != server_note.tag:
						account_changed = True
						self._tomboy.SetNoteCompleteXml("note://tomboy/" + tomboy_note.guid, base64.b64decode(server_note.body))

					self._notes[tomboy_note.guid] = server_note

					if account_changed:
						print "First Sync: Note updated(server newer): " + tomboy_note.name
						count_updated_notes += 1

		# Save the notes that are just on the server
		for server_note in server_notes.values():
			if not self._notes.has_key(server_note.guid):
				if not self._ignore_event.has_key(server_note.guid): self._ignore_event[server_note.guid] = 0
				self._ignore_event[server_note.guid] += 1

				server_note = TomboyNote.find(server_note.id, user_id=server_note.user_id)
				self._notes[server_note.guid] = server_note
				note = self._tomboy.CreateNamedNoteWithUri(server_note.name, "note://tomboy/" + server_note.guid)
				self._tomboy.SetNoteCompleteXml(note, base64.b64decode(server_note.body))
				print "First Sync: Note added(new from server): " + server_note.name
				count_new_notes += 1

		# Save the notes that are just on the client
		for tomboy_note in self._notes.values():
			if not server_notes.has_key(tomboy_note.guid):
				tomboy_note.save()
				print "First Sync: Note added(new from client): " + tomboy_note.name
				count_new_notes += 1

		# Get the updated_timestamp of the newest note
		for tomboy_note in self._notes.values():
			self.set_newest_timestamp(tomboy_note.updated_timestamp)

		self.notify_summary(count_new_notes, count_updated_notes)

	def normal_sync(self):
		# Find the notes on the server that are newer or updated
		newest_timestamp = self.get_newest_timestamp() or 0
		server_notes = {}
		for server_note in TomboyNote.get('get_newer', newest_timestamp=newest_timestamp, user_id=self._user.id):
			server_note = TomboyNote(server_note)
			server_notes[server_note.guid] = server_note

		# Update the notes on the server and client
		for server_note in server_notes.values():
			# Is on server and client ...
			if self._notes.has_key(server_note.guid):
				tomboy_note = self._notes[server_note.guid]
				# but client's is newer
				if tomboy_note.id and tomboy_note.updated_timestamp > server_note.updated_timestamp:
					tomboy_note.save()
					tomboy_note = TomboyNote.find(tomboy_note.id, user_id=tomboy_note.user_id)
					self._notes[tomboy_note.guid] = tomboy_note
					print "Normal Sync: Note updated(client newer): " + tomboy_note.name
				# but server's is newer
				else:
					account_changed = False

					if tomboy_note.body != server_note.body or tomboy_note.name != server_note.name or tomboy_note.tag != server_note.tag:
						if not self._ignore_event.has_key(tomboy_note.guid): self._ignore_event[tomboy_note.guid] = 0
						self._ignore_event[tomboy_note.guid] += 1

						account_changed = True
						tomboy_note = server_note
						self._tomboy.SetNoteCompleteXml("note://tomboy/" + server_note.guid, base64.b64decode(server_note.body))

					self._notes[tomboy_note.guid] = server_note

					if account_changed:
						print "Normal Sync: Note updated(server newer): " + tomboy_note.name
						self.notify("Updated tomboy note", tomboy_note.name)

				self.set_newest_timestamp(tomboy_note.updated_timestamp)

		# Save the notes that are just on the server
		for server_note in server_notes.values():
			if not self._notes.has_key(server_note.guid):
				if not self._ignore_event.has_key(server_note.guid): self._ignore_event[server_note.guid] = 0
				self._ignore_event[server_note.guid] += 1

				self._notes[server_note.guid] = server_note
				note = self._tomboy.CreateNamedNoteWithUri(server_note.name, "note://tomboy/" + server_note.guid)
				self._tomboy.SetNoteCompleteXml(note, base64.b64decode(server_note.body))
				self.set_newest_timestamp(server_note.updated_timestamp)
				print "Normal Sync: Note added(new from server): " + server_note.name
				self.notify("Added tomboy note", server_note.name)

"""
Syncs notes to and from the server
"""
class Syncer(threading.Thread):
	def __init__(self, username, password, email):
		self._needs_first_sync = True

		# Initiate a connection to the Session Bus
		bus = dbus.SessionBus()

		# FIXME: These events should be inside their respective classes
		# Bind the events
		bus.add_signal_receiver(self.onAccountStatusChanged,
								dbus_interface = "im.pidgin.purple.PurpleInterface",
								signal_name = "AccountStatusChanged")

		bus.add_signal_receiver(self.onAccountAdded,
								dbus_interface = "im.pidgin.purple.PurpleInterface",
								signal_name = "AccountAdded")

		bus.add_signal_receiver(self.onAccountRemoved,
								dbus_interface = "im.pidgin.purple.PurpleInterface",
								signal_name = "AccountRemoved")

		bus.add_signal_receiver(self.onNoteSaved,
								dbus_interface = "org.gnome.Tomboy.RemoteControl",
								signal_name = "NoteSaved")

		bus.add_signal_receiver(self.onNoteAdded,
								dbus_interface = "org.gnome.Tomboy.RemoteControl",
								signal_name = "NoteAdded")

		bus.add_signal_receiver(self.onNoteDeleted,
								dbus_interface = "org.gnome.Tomboy.RemoteControl",
								signal_name = "NoteDeleted")

		# Create the user or make sure it exists
		self._user = None
		try:
			User.get('ensure_user_exists', name=username, password=password, email=email)
		except connection.UnauthorizedAccess, err:
			print 'Invalid login.'
			exit()
		except connection.ResourceInvalid, err:
			print "Validation Failed:"
			for error in util.xml_to_dict(err.response.body)['error']:
				print "    " + error
			exit()

		# Get the user from the server
		self._user = User(User.get('get_logged_in_user'))

		self._pidgin_syncer = PidginSync(bus, self._user)
		self._tomboy_syncer = TomboySync(bus, self._user)
		self._watch_file_syncer = WatchFileSync(self._user)
		self._gconf_file_syncer = GConfFileSync(self._user)

		self._stopevent = threading.Event()
		threading.Thread.__init__(self, name='Syncer')

	def run(self):
		self._watch_file_syncer.start()
		self._gconf_file_syncer.start()

		while not self._stopevent.isSet():
			try:
				if self._needs_first_sync:
					self._pidgin_syncer.first_sync()
					self._tomboy_syncer.first_sync()
					self._watch_file_syncer.sync()
					self._gconf_file_syncer.sync()
					self._needs_first_sync = False
				else:
					self._pidgin_syncer.normal_sync()
					self._tomboy_syncer.normal_sync()
					self._watch_file_syncer.sync()
					self._gconf_file_syncer.sync()
				time.sleep(5)

			except Exception:
				traceback.print_exc(file=sys.stdout)
				exit(1)

	def join(self, timeout=None):
		threading.Thread.join(self, timeout)

	def onAccountStatusChanged(self, account_id, old, new):
		if self._needs_first_sync == True: return
		self._pidgin_syncer.update_account_status(account_id, old, new)

	def onAccountAdded(self, account_id):
		if self._needs_first_sync == True: return
		self._pidgin_syncer.add_account(account_id)

	def onAccountRemoved(self, account_id):
		if self._needs_first_sync == True: return
		self._pidgin_syncer.remove_account(account_id)

	def onNoteAdded(self, note):
		if self._needs_first_sync == True: return
		self._tomboy_syncer.add_note(note)

	def onNoteSaved(self, note):
		if self._needs_first_sync == True: return
		self._tomboy_syncer.update_note(note)

	# FIXME: Figure out what the second argument is. There is no documentation
	def onNoteDeleted(self, note, unknown_object):
		if self._needs_first_sync == True: return
		self._tomboy_syncer.remove_note(note)

syncer = Syncer(USERNAME, PASSWORD, EMAIL)
syncer.start()
print "client running ..."

# Wait here and run events
gobject.MainLoop().run()



