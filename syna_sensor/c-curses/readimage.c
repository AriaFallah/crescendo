/*
 * This file provides a simple interface to read images from the Hackathon demo
 * board on platforms with the curses library. To build, type "make" into a
 * shell/terminal. You must have the FTDI D2XX driver installed.
 *
 * Because printing the images is so slow, this does not run at the full 80-Hz
 * frame rate. Change the SKIP_FRAMES variable defined below to set the frame
 * rate you want to use.
 */

#include <curses.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "ftd2xx.h"

#define MAX_IMAGE_SIZE 4096
#define MAX_PACKET_LENGTH (MAX_IMAGE_SIZE * 2)

typedef unsigned int uint32;
typedef unsigned short uint16;
typedef int int32;
typedef short int16;

#pragma pack(push, 1)
typedef struct {
  uint32 timeStamp;
  uint32 _0;
  uint16 _1;
  uint16 sequence;
  int16 _2;
  uint16 length;
  uint16 _3;
  uint16 rows;
  uint16 cols;
  uint16 buffer[MAX_IMAGE_SIZE];
} frame_t;

typedef struct {
  uint16 type;
  uint16 packetNumber;
  uint16 totalPackets;
  uint16 bufferSize;
  uint16 offset;
  frame_t frame;
} imagePayload_t;

#pragma pack(pop)

static FT_HANDLE hSensor = NULL;

// The Sensor packet buffer
#define CIRCBUFMASK 0xFFFF
static unsigned char circularBuf[CIRCBUFMASK+1];
static unsigned int bufStart;
static unsigned int bufEnd;

int sensorOpen() {
  FT_STATUS ftStatus;
  if (hSensor != NULL) {
    return 0;
  } else {
    while(1) {
      ftStatus = FT_Open(0,&hSensor);
      if (ftStatus == FT_OK) // FT_Open OK, use ftHandle to access device
        return 0;
      else
        return -1;
    }
  }
}

int sensorClose() {
  if (hSensor != NULL)
  {
    FT_Close(hSensor);
    hSensor = NULL;
  }
  return 0;
}

int copyIntoCircularBuffer(unsigned char *packetBuf, int len) {
  // returns -1 on overflow, otherwise 0
  int i;
  for (i = 0; i < len; i++) {
    circularBuf[bufEnd] = packetBuf[i];
    bufEnd = (bufEnd+1)&CIRCBUFMASK;
    if (bufEnd == bufStart) {
      return -1;
    }
  }
  return 0;
}

void clearCircularBuffer() {
  bufEnd = bufStart = 0;
}

int getCircularBufferLength()
{
  // returns -1 for an empty buffer
  return ((bufEnd - bufStart) & CIRCBUFMASK) - 1;
}

void advanceCircularBufStart(int n) {
  bufStart = (bufStart + n)&CIRCBUFMASK;
}

int readByteFromCircularBuffer(int idx)
{
  if (bufEnd == bufStart)
  {
    return -1;
  }
  return circularBuf[(bufStart + idx) & CIRCBUFMASK];
}

int emptySensorBuffer()
{
  int timeoutCounter = 200;

  FT_STATUS rv;
  DWORD amountInRxQueue,
        amountInTxQueue,
        eventStatus,
    bytesActuallyRead,
    totalBytesRead;
  // this is the maximum size of the buffer. We don't actually
  // expect it to get this large.
  unsigned char packetBuf[32768];

  amountInRxQueue = 0;
  rv = FT_GetStatus(hSensor, &amountInRxQueue, &amountInTxQueue, &eventStatus);
  if (rv != FT_OK)
    return -3;

  // FT_Read should never read less than the number of bytes requested
  // but check just in case
  totalBytesRead = 0;

  if (amountInRxQueue > sizeof(packetBuf))
    amountInRxQueue = sizeof(packetBuf);

  while (amountInRxQueue > 0) {
    rv = FT_Read(hSensor, packetBuf, amountInRxQueue, &bytesActuallyRead);
    if (rv != FT_OK)
      return -3;
    amountInRxQueue -= bytesActuallyRead;
    totalBytesRead += bytesActuallyRead;
  }
  return 0;
}

int readByte(int idx)
{
  int timeoutCounter = 200;

  FT_STATUS rv;
  DWORD amountInRxQueue,
        amountInTxQueue,
        eventStatus,
    bytesActuallyRead,
    totalBytesRead;
  // this is the maximum size of the buffer. We don't actually
  // expect it to get this large.
  unsigned char packetBuf[32768];

  while (getCircularBufferLength() < idx)
  {
    // we need to read more bytes from the sensor
    amountInRxQueue = 0;
    rv = FT_GetStatus(hSensor, &amountInRxQueue, &amountInTxQueue, &eventStatus);
    if (rv != FT_OK)
      return -3;
    if (timeoutCounter <= 0)
      return -4;
    if (amountInRxQueue == 0) {
      struct timespec req = {
        .tv_sec = 0,
	.tv_nsec = 10000000,
      };
      nanosleep(&req, NULL);
      timeoutCounter -= 10;
    }

    // FT_Read should never read less than the number of bytes requested
    // but check just in case
    totalBytesRead = 0;

    if (amountInRxQueue > sizeof(packetBuf))
      amountInRxQueue = sizeof(packetBuf);

    while (amountInRxQueue > 0) {
      rv = FT_Read(hSensor, packetBuf, amountInRxQueue, &bytesActuallyRead);
      if (rv != FT_OK) {
        return -3;
      }
      amountInRxQueue -= bytesActuallyRead;
      totalBytesRead += bytesActuallyRead;
    }

    if (copyIntoCircularBuffer(packetBuf, totalBytesRead) < 0)
      return -2;
  }
  return readByteFromCircularBuffer(idx);
}

static int crc16(int idx, int len)
{
  int i;
  uint16 r = 0;
  for (i = len/2; i > 0; i--) {
    int j;
    int v1 = readByte(idx++);
    int v2 = readByte(idx++);
    int v = v2 | (v1<<8);
    r ^= v;
    if (v1 < 0 || v2 < 0)
      return -1;
    for (j = 16; j > 0; j--) {
      uint16 c = r & 0x8000;
      r <<= 1;
      if (c)
        r ^= 0x1021;
    }
  }
  if (len & 1) {
    int j;
    int v = readByte(idx++);
    if (v < 0)
      return -1;
    r ^= v << 8;
    for (j = 8; j > 0; j--) {
      uint16 c = r & 0x8000;
      r <<= 1;
      if (c)
        r ^= 0x1021;
    }
  }
  return r;
}

// search through the circular buffer until we find eight consecutive
// 8 0xFFs, which is the end-of-packet marker. This returns the
// decoded packet payload.
int getNextPacket(uint16 *packet, int maxlen) {
  int ffidx = 0;
  int beginIdx = 0;
  int ffs = 0;

  // find a string of ffs. This will terminate if the circular buffer
  // overflows without finding an 0xFF
  while(1) {
    int v = readByte(ffidx);
    if (v < 0)
      return -2; // read error or buffer overflow

    if (v == 0xFF) {
      ffs++;
      if (ffs == 7)
        break;
    }
    else
    {
      ffs = 0;
    }
    ffidx++;
  }

  // we found an end-of-packet marker. Now look for the matching
  // 0xA5 and length byte
  beginIdx = 0;
  while(1) {
    for(; beginIdx < ffidx; beginIdx++) {
      int v = readByte(beginIdx);
      if (v < 0)
        return -2;
      if (v != 0xFF && v != 0xA5)
        break;
    }
    if (beginIdx == ffidx) {
      int i;
      // drop this end of packet marker from consideration
      advanceCircularBufStart(ffidx);
      return -1;
    }

    // possible packet found. Check to see if it really is one.
    {
      int readIdx;
      int outIdx = 0;
      int ffs = 0;
      int crc;
      int len;
      int endidx;
      int expectedCrc;
      int v2 = readByte(beginIdx + 0);
      int v3 = readByte(beginIdx + 1);
      int v4 = readByte(beginIdx + 2);
      int v5 = readByte(beginIdx + 3);

      if (v2 < 0 || v3 < 0 || v4 < 0 || v5 < 0)
        return -2;

      len = (((v2 << 8) | v3) & 0x7FFF) - 4;
      expectedCrc = (v4 << 8) | v5;

      if (len > MAX_PACKET_LENGTH*2) {
        beginIdx++;
        continue;
      }
      // check to see if the packet ends at our string of 0xFFs. A
      // packet could end with as many as 4 consecutive 0xFFs before
      // the actual end-of-packet marker, so allow a little slop.
      endidx = ffidx - (beginIdx + 4 + len);
      if (endidx < 2 || endidx > 7) {
        beginIdx++;
        continue;
      }

      crc = crc16(beginIdx + 4, len);
      if (crc < 0)
        return -2;

      if (crc != expectedCrc) {
        // should be zero. So if it's not, then we have a corrupt
        // packet or we didn't actually find one.
        beginIdx++;
        continue;
      }

      // finally, read all this into the packet
      for (readIdx = beginIdx + 4; readIdx < beginIdx + 4 + len; readIdx++) {
        unsigned char b = readByte(readIdx);
        if (ffs == 4) {
          ffs = 0;
          continue;
        }
        if (b == 0xFF)
          ffs++;
        else
          ffs = 0;
        if (outIdx > maxlen*2) {
          // packet too large to fit in the buffer
          advanceCircularBufStart(ffidx);
          return -3;
        }
        if (outIdx&1)
          packet[outIdx/2] |= b;
        else
          packet[outIdx/2] = b << 8;
        outIdx++;
      }
      advanceCircularBufStart(ffidx);

      return outIdx/2;
    }
  }
}


int main(void)
{
  int len;
  int packetType;
  int r, c;
  uint16 packet[MAX_PACKET_LENGTH];
  int rows, cols;
  uint16 baseline[MAX_IMAGE_SIZE];
  uint16 baselineTaken = 0;

  if (sensorOpen() < 0) {
    printf("Could not open sensor device\n");
    return -1;
  }

  printf("Press space to rebaseline, any other key to quit\n");

  // make getch() non-blocking, returning ERR if no key has been pressed
  // since it was last called
  nodelay(stdscr, TRUE);

  for(;;) {
    c = getch();
    if (c == ERR) {
      char c;
      imagePayload_t *p;
      int i;
      // only display every Nth packet or we will get overwhelmed
      // with data.
#ifndef SKIP_FRAMES
#define SKIP_FRAMES 50
#endif
      for (i = 0; i < SKIP_FRAMES; i++) {
        len = getNextPacket(packet, MAX_PACKET_LENGTH);
        if (len < 0) {
          continue;
        }
      }
      packetType = packet[0];
      if (packetType != 2)
        continue;

      p = (imagePayload_t *)&packet;

      printf("Got image:\n");
      printf("  bufferSize = %d\n", p->bufferSize);
      printf("  timeStamp = %u\n", p->frame.timeStamp);
      printf("  sequence = %d\n", p->frame.sequence);
      printf("  length = %d\n", p->frame.length);
      rows = p->frame.rows;
      cols = p->frame.cols;

      if (!baselineTaken) {
        memcpy(baseline, p->frame.buffer, sizeof(p->frame.buffer));
        baselineTaken = 1;
      }
      printf("  rows = %d\n", rows);
      printf("  cols = %d\n", cols);
      printf(" [");
      for (c = 0; c < cols; c++) {
        for (r = 0; r < rows; r++) {
          printf(" % 5d", baseline[r*cols+c] - p->frame.buffer[r*cols+c]);
        }
        printf("\n  ");
      }
      printf(" ]\n");
    } else if (c == ' ') {
      baselineTaken = 0;
    } else {
      break;
    }
  }
  sensorClose();
}
