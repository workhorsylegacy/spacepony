#!/usr/bin/env python

import sys, dbus

# Get the args
guid = sys.argv[1] if len(sys.argv) > 1 else 'no guid'

# Initiate a connection to the Session Bus
bus = dbus.SessionBus()

print "firing bookmark removed ..."
remote_object = bus.get_object("org.mozilla.firefox.DBus", "/FireFoxDBus")
remote_object.emitBookmarkRemoved(guid, dbus_interface="org.mozilla.firefox.DBus")

