#!/usr/bin/env python

import sys, dbus

# Get the args
title = sys.argv[1] if len(sys.argv) > 1 else 'no title'
subject = sys.argv[2] if len(sys.argv) > 2 else 'no subject'

# Initiate a connection to the Session Bus
bus = dbus.SessionBus()

print "firing download complete ..."
remote_object = bus.get_object("org.mozilla.firefox.DBus", "/FireFoxDBus")
remote_object.emitDownloadComplete(title, subject, dbus_interface="org.mozilla.firefox.DBus")

