#!/usr/bin/env python

import sys, dbus

# Get the args
a = sys.argv[1] if len(sys.argv) > 1 else 'no a'
b = sys.argv[2] if len(sys.argv) > 2 else 'no b'
c = sys.argv[3] if len(sys.argv) > 3 else 'no c'
d = sys.argv[4] if len(sys.argv) > 4 else 'no d'

# Initiate a connection to the Session Bus
bus = dbus.SessionBus()

print "firing bookmark changed ..."
remote_object = bus.get_object("org.mozilla.firefox.DBus", "/FireFoxDBus")
remote_object.emitBookmarkChanged(a, b, c, d, dbus_interface="org.mozilla.firefox.DBus")

