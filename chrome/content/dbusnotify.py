#!/usr/bin/env python

import sys,os
import dbus, dbus.service
from dbus.mainloop.glib import DBusGMainLoop

FIREFOX_DBUS_INTERFACE = 'org.mozilla.firefox.DBus'
FIREFOX_DBUS_PATH = '/org/mozilla/firefox/DBus'

class FireFoxDBus(dbus.service.Object):
	def __init__(self, bus_name):
		dbus.service.Object.__init__(self, bus_name, FIREFOX_DBUS_PATH)

	# Will print a message when a download completes
	@dbus.service.signal(dbus_interface=FIREFOX_DBUS_INTERFACE, signature='ss')
	def DownloadComplete(self, title, subject):
		print "download complete: " + title + " - " + subject

title = sys.argv[1] if len(sys.argv) > 1 else 'a'
subject = sys.argv[2] if len(sys.argv) > 2 else 'b'

dbus_loop = DBusGMainLoop()
name = dbus.service.BusName(FIREFOX_DBUS_INTERFACE, bus=dbus.SessionBus(mainloop=dbus_loop))

e = FireFoxDBus(name)
e.DownloadComplete(title, subject)
