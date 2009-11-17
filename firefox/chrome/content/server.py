#!/usr/bin/env python

import sys, os, signal
import gobject
import dbus, dbus.service, dbus.glib
from dbus.mainloop.glib import DBusGMainLoop

# Have the program quit when ctrl+c is pressed
def quit_program(signl, frme):
	print "Exiting ..."
	exit(1)
signal.signal(signal.SIGINT, quit_program)

FIREFOX_DBUS_INTERFACE = 'org.mozilla.firefox.DBus'
FIREFOX_DBUS_PATH = '/org/mozilla/firefox/DBus'

class FireFoxDBus(dbus.service.Object):
	# Events
	@dbus.service.signal(dbus_interface=FIREFOX_DBUS_INTERFACE, signature='ss')
	def DownloadComplete(self, title, subject):
		print "download complete: " + title + " - " + subject

	@dbus.service.signal(dbus_interface=FIREFOX_DBUS_INTERFACE, signature='ssss')
	def BookmarkAdded(self, folder, guid, title, uri):
		print "bookmark added: " + folder + " - " + title + " - " + uri

	@dbus.service.signal(dbus_interface=FIREFOX_DBUS_INTERFACE, signature='s')
	def BookmarkRemoved(self, guid):
		print "bookmark removed: " + guid

	@dbus.service.signal(dbus_interface=FIREFOX_DBUS_INTERFACE, signature='sss')
	def BookmarkChanged(self, guid, property_name, property_value):
		print "bookmark changed: " + guid + " - " + property_name + " - " + property_value

	# Event emitters
	@dbus.service.method(dbus_interface=FIREFOX_DBUS_INTERFACE, in_signature='ss', out_signature='')
	def emitDownloadComplete(self, title, subject):
		self.DownloadComplete(title, subject)

	@dbus.service.method(dbus_interface=FIREFOX_DBUS_INTERFACE, in_signature='ssss', out_signature='')
	def emitBookmarkAdded(self, folder, guid, title, uri):
		self.BookmarkAdded(folder, guid, title, uri)

	@dbus.service.method(dbus_interface=FIREFOX_DBUS_INTERFACE, in_signature='s', out_signature='')
	def emitBookmarkRemoved(self, guid):
		self.BookmarkRemoved(guid)

	@dbus.service.method(dbus_interface=FIREFOX_DBUS_INTERFACE, in_signature='sss', out_signature='')
	def emitBookmarkChanged(self, guid, property_name, property_value):
		self.BookmarkChanged(guid, property_name, property_value)

DBusGMainLoop(set_as_default = True)
gobject.threads_init()
dbus.glib.init_threads()

session_bus = dbus.SessionBus()
name = dbus.service.BusName(FIREFOX_DBUS_INTERFACE, session_bus)
object = FireFoxDBus(session_bus, '/FireFoxDBus')

# Loop until manually terminated
try:
	print "server running ..."
	gobject.MainLoop().run()
except KeyboardInterrupt:
	sys.exit(1)


