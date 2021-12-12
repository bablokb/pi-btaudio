Bluetooth Audio for (headless) PiOS systems
===========================================

Introduction
------------

Audio on Linux systems has always been rather complicated. ALSA (Advanced
Linux Sound Architecture) is advanced indeed and thus even simple
setups are complicated.

Bluetooth adds another level of complexity. And therefore the forums are
full of posts asking for help on how to connect a Linux system with a
bluetooth speaker or headset. This is no different with PiOs (Raspian).

You have two options: either use PulseAudio (fat, inflates a PiOS-lite
installation by 50%), or [bluez-alsa](https://github.com/Arkq/bluez-alsa).
Don't use "bluesalsa", an early fork of "bluez-alsa" which worked with
Stretch, was broken with Buster and was removed from Bullseye. 

This project aims to simplify the setup of
[bluez-alsa](https://github.com/Arkq/bluez-alsa) for Pi-systems. It
does not support all kinds of configurations, its main aim is to support
single-device setups, i.e. a Pi using a dedicated BT-speaker for audio
output.

Note that functionality and stability of bluez-alsa varies with different
hardware versions and OS-versions. The current status with
bluez-alsa (version 3.1.0-78) for me:

  - Buster   2021-05 works for Pi-Zero-W and Pi3B+
  - Buster   2021-05 fails for Pi4 (BT speaker does not connect)
  - Bullseye 2021-11 works, but BT speaker does not autoconnect


Prerequisites
-------------

To use bluez-alsa, you first have to manually pair the Pi with your device
and establish a trust. This is done using the program `bluetoothctl`. Note
that you have to add your user (typically `pi`) to the group `bluetooth`
if necessary (check with e.g. `id pi`) and login again:

    sudo usermod -a -G bluetooth pi

Pairing uses the commands from the following screenshot:
![](images/pairing.png "pairing the device and establishing trust").

You don't have to type all these numbers, just type the first few and then press
the TAB key for autocompletion.

After pairing, note down the MAC address of your bluetooth-device, you will
need it later for configuring ALSA.


Install bluez-alsa
------------------

Note that Raspbian/PiOS had a package "bluealsa" (removed in Bullseye).
This package is broken, don't install it!

You can install bluez-alsa either from source (recommended),
or using the deb-package provided from this project.

Installation from source is straightforward, the commands are from the
bluez-alsa wiki:

    tools/build-bluez-alsa

The drawback is that installation from source requires many development
packages on your system. They are automatically downloaded but not
everybody likes development tools on productive systems.

You might have to adapt the configure-command in that script, which
currently only does a default build (plus systemd-support).

Installing the deb-package is much simpler, but that package was built for
PiOS buster-lite (version 2021-05) using checkinstall and might or might
not work for you:

    sudo dpkg -i deb/arkq-bluez-alsa_3.1.0-78_armhf.deb
    sudo apt-get -f -y install

The first command will give some errors, which the second command should
fix (hopefully).

As a third alternative, you can build from source on one machine, create
a deb-package and install it on another machine:

    sudo apt-get -y update
    sudo apt-get -y install checkinstall
    tools/build-bluez-alsa deb

This will create the deb-package in the directory `bluez-alsa/build`.


Installation
------------

To install all necessary software and the template configuration files, run
the following commands:

    git clone https://github.com/bablokb/pi-btaudio.git
    cd pi-btaudio
    sudo tools/install

The install script will

  - install prerequisite-packages (see list in `tools/install`)
  - create a sample `/etc/asound.conf` which will make your bluetooth-device
    the system-wide default audio-device
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

Note that you can run

    bluetoothctl devices

which should give you the MAC-address of your bluetooth-speaker.

That's it for configuration, all scripts and daemons will use this MAC-address.

Now is the time to restart your system. After booting has finished and all
daemons are up and running, your Pi should automatically connect to your
speaker or headset. If not, run `btaudio-connect`.
