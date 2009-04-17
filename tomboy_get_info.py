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
#for note in tomboy.ListAllNotes():
#	print tomboy.GetNoteTitle(note)


# Create the User model
User = PyResource.connect("http://localhost:3000", "user")

# Create a user and save it
user = User()
user.name = 'da ass'
user.email = 'da email'
user.password = 'blah blah blah'
user.password_confirmation = 'blah blah blah'
user.save()

# Update the user
user.name = "The Count of Poopicristo"
user.save()

# List all the users
users = User.find_all()
for user in users:
	print 'name: ' + user.name
	print 'email: ' + user.email

exit()

# Get all the users
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

