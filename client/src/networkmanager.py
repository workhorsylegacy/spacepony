#! /usr/bin/env python

import dbus, dbus.glib
import gobject, time

NM_DEVICE_STATE = [
'UNKNOWN', 'UNMANAGED', 'UNAVAILABLE', 'DISCONNECTED', 
'PREPARE', 'CONFIG', 'NEED_AUTH', 'IP_CONFIG', 
'ACTIVATED', 'FAILED']

NM_DEVICE_STATE_REASON = [
'UNKNOWN', 'NONE', 'NOW_MANAGED', 'NOW_UNMANAGED', 
'CONFIG_FAILED', 'CONFIG_UNAVAILABLE', 'CONFIG_EXPIRED', 
'NO_SECRETS', 'SUPPLICANT_DISCONNECT', 
'SUPPLICANT_CONFIG_FAILED', 'SUPPLICANT_FAILED', 
'SUPPLICANT_TIMEOUT', 'PPP_START_FAILED', 
'PPP_DISCONNECT', 'PPP_FAILED', 'DHCP_START_FAILED', 
'DHCP_ERROR', 'DHCP_FAILED', 'SHARED_START_FAILED', 
'SHARED_FAILED', 'AUTOIP_START_FAILED', 'AUTOIP_ERROR', 
'AUTOIP_FAILED', 'MODEM_BUSY', 'MODEM_NO_DIAL_TONE', 
'MODEM_NO_CARRIER', 'MODEM_DIAL_TIMEOUT', 
'MODEM_DIAL_FAILED', 'MODEM_INIT_FAILED', 
'GSM_APN_FAILED', 'GSM_REGISTRATION_NOT_SEARCHING', 
'GSM_REGISTRATION_DENIED', 'GSM_REGISTRATION_TIMEOUT', 
'GSM_REGISTRATION_FAILED', 'GSM_PIN_CHECK_FAILED', 
'FIRMWARE_MISSING', 'REMOVED', 'SLEEPING', 'CONNECTION_REMOVED', 
'USER_REQUESTED', 'CARRIER']

NM_DEVICE_CAP = [
'NONE', 'NM_SUPPORTED', 'CARRIER_DETECT', 'NM_SUPPORTED & CARRIER_DETECT']

NM_DEVICE_TYPE = [
'UNKNOWN', 'ETHERNET', 'WIRELESS']

NM_STATE = [
'UNKNOWN', 'ASLEEP', 'CONNECTING', 'CONNECTED', 'DISCONNECTED']

bus = dbus.SystemBus()
network_manager = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

#def onDeviceChanged(new_state, old_state, reason):
#	print "device state changed: is " + NM_DEVICE_STATE[new_state] + ' was ' + NM_DEVICE_STATE[old_state] + ' because ' + NM_DEVICE_STATE_REASON[reason]

#def onPropertiesChanged(properties):
#	print "nm properties changed" + NM_STATE[int(properties['State'])]

def onStateChanged(state):
	if NM_STATE[state] != 'CONNECTED':
		print "not connected ..."
		return

	# Sleep for a bit to let the machine settle after getting a net connection
	time.sleep(3)

	# Print the connection info
	print_connection_info()

def print_connection_info():
	devices = network_manager.GetDevices()
	for object_path in devices:
		device = bus.get_object('org.freedesktop.NetworkManager', object_path)
		device_properties = dbus.Interface(device, 'org.freedesktop.DBus.Properties')

		if 'ACTIVATED' != NM_DEVICE_STATE[device_properties.Get('org.freedesktop.NetworkManager.Device', 'State')]:
			continue

		print "Managed: " + str(device_properties.Get('org.freedesktop.NetworkManager.Device', 'Managed'))
		print "Dhcp4Config: " + str(device_properties.Get('org.freedesktop.NetworkManager.Device', 'Dhcp4Config'))
		print "Ip4Config: " + str(device_properties.Get('org.freedesktop.NetworkManager.Device', 'Ip4Config'))
		print "Driver: " + str(device_properties.Get('org.freedesktop.NetworkManager.Device', 'Driver'))
		print "Interface: " + str(device_properties.Get('org.freedesktop.NetworkManager.Device', 'Interface'))
		print "Udi: " + str(device_properties.Get('org.freedesktop.NetworkManager.Device', 'Udi'))
		print "Capabilities: " + NM_DEVICE_CAP[device_properties.Get('org.freedesktop.NetworkManager.Device', 'Capabilities')]
		print "DeviceType: " + NM_DEVICE_TYPE[device_properties.Get('org.freedesktop.NetworkManager.Device', 'DeviceType')]
		print "Ip4Address: " + str(device_properties.Get('org.freedesktop.NetworkManager.Device', 'Ip4Address'))
		print "State: " + NM_DEVICE_STATE[device_properties.Get('org.freedesktop.NetworkManager.Device', 'State')]
		print ""

#bus.add_signal_receiver(onDeviceChanged, 
#					dbus_interface = "org.freedesktop.NetworkManager.Device", 
#					signal_name = "StateChanged")

#bus.add_signal_receiver(onPropertiesChanged,
#						dbus_interface = "org.freedesktop.NetworkManager",
#						signal_name = "PropertiesChanged")

bus.add_signal_receiver(onStateChanged,
						dbus_interface = "org.freedesktop.NetworkManager",
						signal_name = "StateChanged")

gobject.MainLoop().run()


