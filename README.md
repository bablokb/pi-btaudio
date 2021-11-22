Bluetooth Audio for (headless) Raspbian systems
===============================================

Introduction
------------

Audio on Linux systems has always been rather complicated. ALSA (Advanced
Linux Sound Architecture) is advanced indeed and thus even simple
setups are complicated.

Bluetooth adds another level of complexity. And therefore the forums are
full of posts asking for help on how to connect a Linux system with a
bluetooth speaker or headset. This is no different with Raspbian.

Until Raspbian-Jessie, for bluetooth-devices you additionally needed
PulseAudio, making things even more complicated. With Stretch this has
changed and PulseAudio was replaced with a rather simple helper daemon
called *bluealsa*. Nevertheless, a simple setup is still complicated,
partly because the maintainer of the bluealsa package installed the
daemon only for grafical environments.

With Buster, the setup with bluealsa did not work anymore. The main reason
for this is an outdated version. The package "bluealsa" had been forked
from the upstream "bluez-alsa" and had never been updated. The good
news is, that with Buster the PulseAudio-system also works for headless
systems, so you don't actually need bluealsa/bluez-alsa anymore. But
PulseAudio inflates a Buster-lite image by 50%, so instead of installing
something around 1GB, you need 1,5GB (which also has to be backuped etc.).
Also, PulseAudio always has problems with connecting devices.

Orignially, this project tried to simplify the setup of bluetooth-audio by
providing an optimized configuration for bluealsa. Now, it also
provides a compiled version of a newer upstream version of bluez-alsa
for the Raspberry Pi (see below for details).

After installation all you have to do is to replace a single MAC-address
(of you bluetooth-device) in a single configuration file. There is one
caveat though: the project currently only supports a single device,
but anyhow, this should already cover most of the use-cases.


Prerequisites
-------------

To use bluez-alsa, you first have to manually pair the Pi with your device
and establish a trust. This is done using the program `bluetoothctl`. Note
that you have to add your user (typically `pi`) to the group `bluetooth`
and login again:

    sudo usermod -a -G bluetooth pi

Pairing uses the commands from the following screenshot:
![](images/pairing.png "pairing the device and establishing trust").

You don't have to type all these numbers, just type the first few and then press
the TAB key for autocompletion.

After pairing, note down the MAC address of your bluetooth-device, you will
need it later for configuring ALSA.


Installation
------------

To install all necessary software and the template configuration files, run
the following commands:

    git clone https://github.com/bablokb/pi-btaudio.git
    cd pi-btaudio
    sudo tools/install
    sudo tar -xvzpf misc/bluez-alsa.armhf.tar.gz -C /

The install script will

  - install prerequisite-packages (see list in `tools/install`)
  - unpack a compiled version of bluez-alsa.
    *This is not an installation, you must remove the files manually if
    you decide that you don't want/need bluez-alsa anymore*
  - create a sample `/etc/asound.conf` which will make your bluetooth-device
    the system-wide default audio-device
  - install a watchdog-daemon which will autoconnect to the bluetooth-device
    configured in `/etc/asound.conf`. Note that this is not necessary for
    all bluetooth-devices, but some just don't automatically connect to the Pi.
  - install the utiliy-scripts `btaudio-connect` and `btaudio-disconnect`
    to manually connect and disconnect to the device


Configuration
-------------

After installation, edit the file `/etc/asound.conf` and insert the MAC
address of your bluetooth-device in the line starting with
`defaults.bluealsa.device`:

    pcm.!default "bluealsa"
    ctl.!default "bluealsa"
    defaults.bluealsa.interface "hci0"
    defaults.bluealsa.device "32:54:03:BB:CC:28"
    defaults.bluealsa.profile "a2dp"

That's it for configuration, all scripts and daemons will use this MAC-address.

Now is the time to restart your system. After booting has finished and all
daemons are up and running, your Pi should automatically connect to your
speaker or headset.
