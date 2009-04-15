#! /usr/bin/env python

import dbus, gobject, dbus.glib
from PyRest import PyRest
from PyRest import PyResource

# Get the D-Bus session bus
bus = dbus.SessionBus()
# Access the Tomboy D-Bus object
obj = bus.get_object("org.gnome.Tomboy",
  "/org/gnome/Tomboy/RemoteControl")
# Access the Tomboy remote control interface
tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")

# Display the Start Here note
#tomboy.DisplayNote(tomboy.FindStartHereNote())

# Display the title of every note
for note in tomboy.ListAllNotes():
	print tomboy.GetNoteTitle(note)


User = PyResource.connect("http://localhost:3000", "user")
user = User()
user.ass = 'da ass'
print user.ass

users = User.find_all()
for user in users:
	print user.name

exit()

# Get all the user
rest = PyRest('http://localhost:3000')
users = rest.get('users.json')

User = PyResource('http://localhost:3000', 'users')
print str(User.find_all())

exit()

# Display the contents of the note called Test
#print tomboy.GetNoteContents(tomboy.FindNote("PSP"))

# Add a tag to the note called Test
#tomboy.AddTagToNote(tomboy.FindNote("PSP"), "games")

# Display the titles of all notes with the tag 'sampletag'
for note in tomboy.GetAllNotesWithTag("awesome"):
	print tomboy.GetNoteTitle(note)

# Print the XML data for the note called Test
#print tomboy.GetNoteCompleteXml(tomboy.FindNote("PSP"))

