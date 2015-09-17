#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from harold import Harold
from serial import Serial
from time import gmtime, strftime
import led_control as LED
import logging
import argparse
import os
import subprocess as sp
import sys

MPLAYER_FIFO = "/tmp/mplayer.fifo"

DEBUG_FILE = "error_log.txt"

FNULL = open(os.devnull, 'w')

LED.open_pins()


class MockSerial:

    def __init__(self, fi=sys.stdin):
        self.fi = fi

    def readline(self):
        return self.fi.readline()

    def flushInput(self):
        return self.fi.flush()


def main():
    # Handle some command line arguments
    parser = argparse.ArgumentParser(description="Start Harold system")
    parser.add_argument("--debug", "-d", action="store_true",
                        help="Use debug mode (stdin)")
    parser.add_argument("--serial", "-s",
                        default="/dev/ttyACM0",
                        help="Serial port to use", metavar="PORT")
    parser.add_argument("--rate", "-r",
                        default=9600, type=int,
                        help="Serial BAUD rate to use")
    parser.add_argument("--fifo", "-f",
                        default="/tmp/mplayer.fifo",
                        help="FIFO to communicate to mplayer with")
    parser.add_argument("--nobeep", "-n", action="store_true",
                        help="Disable beep")
    parser.add_argument("--overrides", "-o", default="",
                        help="allow users to be override others")
    parser.add_argument("--blacklist", "-b", default="",
                        help="blacklist certain usernames")
    args = parser.parse_args()
    try:
        os.mkfifo(args.fifo)
    except OSError as e:
        import errno
        if e.errno != errno.EEXIST:
            raise
    cmd = ["mplayer", "-idle", "-slave", "-input", "file="+args.fifo]
    mplayer = sp.Popen(cmd, stdout=sp.PIPE, stderr=FNULL)
    try:
        with open(args.fifo, "w", 0) as mplfifo:
            if args.debug:
                ser = MockSerial()
            else:
                ser = Serial(args.serial, args.rate, timeout = 1)
                ser.flushInput()
            harold = Harold(mplfifo, ser, mplayer.stdout, not args.nobeep,
                    args.overrides.split(","), args.blacklist.split(","))
            while True:
                harold()
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        mplayer.kill()
        os.remove(args.fifo)
        LED.cleanup()

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, filename=DEBUG_FILE)

    #try:
    main()
    #except:
    #    logging.exception(strftime("%d %b %Y %H:%M:%S", gmtime()))
