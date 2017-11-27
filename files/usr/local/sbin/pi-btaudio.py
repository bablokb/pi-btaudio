#!/usr/bin/python
# --------------------------------------------------------------------------
# This script implements the pi-btaudio.service. It automatically connects
# with the bluetooth-device defined in /etc/asound.conf
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-btaudio
#
# --------------------------------------------------------------------------

import os, sys, time, signal
import logging, logging.handlers
import dbus, dbus.service, dbus.mainloop.glib
import gobject

LOG_LEVEL = logging.INFO
#LOG_LEVEL = logging.DEBUG
LOG_FILE = "/dev/log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
BLUEZ_DEV = "org.bluez.Device1"

# --- extract MAC of bluetooth-device from /etc/asound.conf   ----------------

def get_audio_mac():
  mac = "xx:xx:xx:xx:xx:xx"
  try:
    asound_conf = open("/etc/asound.conf","r")
    for line in asound_conf:
      if line.startswith("defaults.bluealsa.device"):
        mac = line.split()[1].strip('"\'')
        break
    asound_conf.close()
    return mac
  except Exception as e:
    logger.error("pi-btaudio: unable to parse asound.conf: %" % e.message)
    sys.exit(1)

# --- callback handler for property changes   --------------------------------

def device_property_changed_cb(interface_name,value,path,interface,device_path):
  global bus, audio_mac

  logger.debug("pi-btaudio: interface_name: %s" % interface_name)
  logger.debug("pi-btaudio: device_path  : %s" % device_path)
  logger.debug("pi-btaudio: interface    : %s" % interface)

  # filter only relevant devices
  if interface_name != BLUEZ_DEV:
    return

  # filter only relevant mac addresses
  device_mac = ":".join(device_path.split('/')[-1].split('_')[1:]) 
  logger.debug("pi-btaudio: device mac   : %s" % device_mac)
  if device_mac != audio_mac:
    return

  prop_object = dbus.Interface(bus.get_object("org.bluez", device_path),
                               "org.freedesktop.DBus.Properties")
  properties = prop_object.GetAll(interface_name)

  if properties["Connected"]:
    logger.info("pi-btaudio: device %s has connected" % device_mac)
    dev = dbus.Interface(bus.get_object("org.bluez", device_path),
                         "org.bluez.Device1")
    dev.Connect()
  else:
    logger.info("pi-btaudio: device %s has disconnected" % device_mac)

# --- signal handler   -------------------------------------------------------

def shutdown(signum, frame):
  mainloop.quit()

# --- main program   ---------------------------------------------------------

if __name__ == "__main__":
  # sleep a few seconds to allow bluealsa to settle
  time.sleep(5)

  # shut down on a TERM or INT signals
  signal.signal(signal.SIGTERM, shutdown)
  signal.signal(signal.SIGINT, shutdown)

  # start logging
  logger = logging.getLogger("pi-btaudio")
  logger.setLevel(LOG_LEVEL)
  logger.addHandler(logging.handlers.SysLogHandler(address = "/dev/log"))

  # extract MAC of bluetooth-audio device
  audio_mac = get_audio_mac()
  logger.info("pi-btaudio: starting to monitor %s for auto-connect", audio_mac)

  # Get the system bus
  try:
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
  except Exception as e:
    logger.error("pi-btaudio: unable to get the system dbus: %" % e.message)
    sys.exit(1)

  # listen for signals on the Bluez bus
  bus.add_signal_receiver(device_property_changed_cb,
                          bus_name="org.bluez",
                          signal_name="PropertiesChanged",
                          path_keyword="device_path",
                          interface_keyword="interface")

  try:
    mainloop = gobject.MainLoop()
    mainloop.run()
  except KeyboardInterrupt:
    pass
  except:
    logger.error("pi-btaudio: unable to run the gobject main loop")
    sys.exit(1)

  logger.info("pi-btaudio: terminating")
  sys.exit(0)
