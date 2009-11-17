#!/usr/bin/env python

import sys, dbus

# Get the args
guid = sys.argv[1] if len(sys.argv) > 1 else 'no guid'
property_name = sys.argv[2] if len(sys.argv) > 2 else 'no property_name'
property_value = sys.argv[3] if len(sys.argv) > 3 else 'no property_value'

# Initiate a connection to the Session Bus
bus = dbus.SessionBus()

print "firing bookmark changed ..."
remote_object = bus.get_object("org.mozilla.firefox.DBus", "/FireFoxDBus")
remote_object.emitBookmarkChanged(guid, property_name, property_value, dbus_interface="org.mozilla.firefox.DBus")

