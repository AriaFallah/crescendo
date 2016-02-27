====================
 Sensor Data Server
====================

:Author: Joel Jordan
:Date: 8/28/2015

Requirements
============

Windows
-------

  - Python 2.7 or 3.4 (only 32-bit versions tested) (http://www.python.org/)
	Python/Windows-python-2.7.10.msi
	or Python/Windows-python-2.7.10.amd64.msi

  - PyWin32 (http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/)
	Python/Windows-pywin32-219.win32-py2.7.exe
	or Python/Windows-pywin32-219.win-amd64-py2.7.exe

  - FTDI D2XX driver (http://www.ftdichip.com/Drivers/D2XX.htm)
	FTDI/Windows CDM v2.12.06 WHQL Certified.zip
	

Mac OS X
--------

Tested on 10.10, using system Python (2.7.6) (http://www.python.org/)
	Python/MAC_OS_X-python-2.7.9-macosx10.5.pkg
	or Python/MAC_OS_X-python-2.7.9-macosx10.6.pkg

Install the FTDI D2XX driver. (http://www.ftdichip.com/)
	FTDI/Mac_OS_X-D2XX1.2.2.dmg

Follow instructions in section 3.3 of:

  http://www.ftdichip.com/Support/Documents/AppNotes/AN_134_FTDI_Drivers_Installation_Guide_for_MAC_OSX.pdf

If you have 10.9 or 10.10, follow instructions in section 7 to disable
Apple's FTDI virtual COM port driver.

What worked for me was to run:

  sudo kextunload /System/Library/Extensions/IOUSBFamily.kext/Contents/PlugIns/AppleUSBFTDI.kext/

Linux
-----

Tested on Ubuntu 15.04 amd64 with Python 2.7 and 3.4

Copy ftdi_d2xx.rules to /etc/udev/rules.d (you may have to restart udev). Plug in the development kit USB cable after this file has been copied.

Optional: Install the FTDI D2XX driver. Download the appropriate version from
  http://www.ftdichip.com/Drivers/D2XX.htm

follow installation instructions in:
  http://www.ftdichip.com/Drivers/D2XX/Linux/ReadMe-linux.txt

Or, to manually set up the device (after it has been plugged in), open a terminal and type:

  sudo rmmod ftdi_sio
  sudo rmmod usbserial
  lsusb -d 0403:6010
  # replace <bus> and <device> with the numbers listed by lsusb
  chmod 0666 /dev/bus/usb/<bus>/<device>

It may also be possible to avoid setup by running programs that access the Synaptics hackathon hardware as root.

Sample Programs
===============

Python
------

This distribution includes both C and Python example code for reading
images from the sensor using FTDI's D2XX driver.

The Python code can be run with

  cd python
  python server.py

This creates a web server listening on port 8080. See the source code
for more details.

The demo web site at http://127.0.0.1:8080 is known to work with
Firefox and Safari but not with Internet Explorer.

The python code uses a modified version of the ftd2xx Python module
available from https://pypi.python.org/pypi/ftd2xx, found in the
ftd2xx directory. This version is modified to work with Python 2 and 3
on Windows, Mac OS X, and Linux.

C
----------------

The C code is in c-windows/readimage.c for Microsoft Windows and c-curses/readimage.c for other platforms.

For Windows, type "nmake" into a Visual Studio command prompt
For 64-bit builds, you can also use:
  cl readimage.c /Zi -I./ftdi ./ftdi/win64/ftd2xx.lib
For 32-bit builds, you can use:
  cl readimage.c /Zi -I./ftdi ./ftdi/win32/ftd2xx.lib

For other platforms, you may first have to install gcc, make and curses.
Ubuntu:
  sudo apt-get install gcc make ncurses-dev
To build, just run make:
  make
For platforms other than 64-bit linux, find the appropriate ftd2xx.a or alternative from the FTDI installer.

Data Format
===========

If you want to write your own interface, feel free! The format is
fairly simple but has some quirks that you will have to work around.

Images are sent in variable-length packets. The beginning of a packet
is denoted by a string of at least 7 0xFF characters followed by an
0xA5.

Packets are sent in 16-bit words, high byte first. The first 16 bits
are the length of the packet in bytes. The second two bytes are a
CRC-16 checksum, performed on the rest of the packet after the
checksum. If you want to use my checksum code, you can borrow it from
server.py or readimage.c.

The next two bytes are the packet type. Type 2 is an image. Packets of
other types can be ignored.

Because a long string of 0xFF characters is used to mark the beginning
of a packet, strings of more than four consecutive 0xFF characters are
transformed inside the payload of the packet (after the CRC word) by
adding a 0x00 byte after each group of 4 0xFFs. So when reading a
packet, if you see four 0xFF bytes in a row, discard the next byte if
it's 0x00. However, these extra zero bytes are included in the length
and CRC-16 calculations.

However, if you see a string of 7 or more consecutive 0xFF characters
in a packet, that packet is corrupt and you should drop it. I
recommend starting over at the next 0xA5 after the 0xFFs.

The image packets have the following format::

Word    Contents
  0     Length in bytes
  1     CRC-16
  2     Type (always 2)
  3     Ignore
  4     Ignore
  5     Ignore
  6     Ignore
  7     Time Stamp (microseconds), low word
  8     Time Stamp (microseconds), high word
  9     Ignore
 10     Ignore
 11     Ignore
 12     Sequence Number
 13     Ignore
 14     Length of image data in words (should be 3312)
 15     Ignore
 16     Number of rows
 17     Number of columns
 18...  Image buffer

The image buffer will be a 2D array of 16-bit words, with the
indicated number of columns and rows, stored in row-major order (like
in C). So for a 46-row by 72-column sensor, image buffer index 0 is
row 0, column 0, index 1 is row 0, column 1, and index 72 is row 1,
column 0.

You must read the buffer frequently or it will fill up and you'll lose
packets. The USB-serial converter has a small buffer than can store
only a few full images before it fills up. When this happens, you will
see long strings of 0xFF in the data, indicating that the buffer
overflowed.

The easiest thing to do is to write your code to read the entire
buffer and scan it for complete image packets.
