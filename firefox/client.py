#!/usr/bin/env python

import sys, os, signal
import gobject
import dbus, dbus.service, dbus.glib

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default = True)
gobject.threads_init()
dbus.glib.init_threads()

# Have the program quit when ctrl+c is pressed
def quit_program(signl, frme):
	print "Exiting ..."
	exit(1)
signal.signal(signal.SIGINT, quit_program)

def on_download_complete(title, subject):
	print "Download complete - title:" + title + ' subject:' + subject

def on_bookmark_added(folder, guid, title, uri):
	print "Bookmark added - folder:" + folder + ' title:' + title + ' uri:' + uri

def on_bookmark_removed(guid):
	print "Bookmark removed - guid:" + guid

def on_bookmark_changed(guid, property_name, property_value):
	print "Bookmark changed - guid:" + guid + ' property_name:' + property_name + ' property_value:' + property_value

# Initiate a connection to the Session Bus
bus = dbus.SessionBus()

# Bind the events
bus.add_signal_receiver(on_download_complete,
						dbus_interface = "org.mozilla.firefox.DBus",
						signal_name = "DownloadComplete")

bus.add_signal_receiver(on_bookmark_added,
						dbus_interface = "org.mozilla.firefox.DBus",
						signal_name = "BookmarkAdded")

bus.add_signal_receiver(on_bookmark_removed,
						dbus_interface = "org.mozilla.firefox.DBus",
						signal_name = "BookmarkRemoved")

bus.add_signal_receiver(on_bookmark_changed,
						dbus_interface = "org.mozilla.firefox.DBus",
						signal_name = "BookmarkChanged")

# Loop until manually terminated
try:
	print "client running ..."
	gobject.MainLoop().run()
except KeyboardInterrupt:
	sys.exit(1)

