#!/usr/bin/env python

import sys, dbus

# Get the args
folder = sys.argv[1] if len(sys.argv) > 1 else 'no folder'
guid = sys.argv[2] if len(sys.argv) > 2 else 'no guid'
title = sys.argv[3] if len(sys.argv) > 3 else 'no title'
uri = sys.argv[4] if len(sys.argv) > 4 else 'no uri'

# Initiate a connection to the Session Bus
bus = dbus.SessionBus()

print "firing bookmark added ..."
remote_object = bus.get_object("org.mozilla.firefox.DBus", "/FireFoxDBus")
remote_object.emitBookmarkAdded(folder, guid, title, uri, dbus_interface="org.mozilla.firefox.DBus")

