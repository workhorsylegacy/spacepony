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
	print "Download complete: " + title + ' ' + subject

def on_bookmark_added(folder, name, url):
	print "Bookmark added: " + folder + ' ' + name + ' ' + url

def on_bookmark_removed(folder, name, url):
	print "Bookmark removed: " + folder + ' ' + name + ' ' + url

def on_bookmark_changed(folder, name, url):
	print "Bookmark changed: " + folder + ' ' + name + ' ' + url

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

