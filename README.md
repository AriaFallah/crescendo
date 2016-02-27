# HackTech

HackTech Project

# Data Format

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

```
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
 ```

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
