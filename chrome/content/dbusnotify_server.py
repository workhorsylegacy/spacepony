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
	# Will print a message when a download completes
	@dbus.service.signal(dbus_interface=FIREFOX_DBUS_INTERFACE, signature='ss')
	def DownloadComplete(self, title, subject):
		print "download complete: " + title + " - " + subject

	@dbus.service.method(dbus_interface=FIREFOX_DBUS_INTERFACE)
	def emitDownloadComplete(self, title, subject):
		self.DownloadComplete(title, subject)

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


