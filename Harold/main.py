#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from alsaaudio import Mixer
from serial import Serial
from get_user import read_ibutton, get_user_song
import led_control as LED
import argparse
import os
import subprocess as sp
import sys
import time

DING_SONG = "/home/pi/ding.mp3"

MPLAYER_FIFO = "/tmp/mplayer.fifo"

FNULL = open(os.devnull, 'w')

LED.open_pins()

class MockSerial:

    def __init__(self, fi=sys.stdin):
        self.fi = fi

    def readline(self):
        return self.fi.readline()

    def flushInput(self):
        return self.fi.flush()


def quiet_hours():
    ' Returns True if the current time is within RIT quiet hours '
    currtime = time.localtime()
    if currtime.tm_wday > 4:
        return (currtime.tm_hour + 23) % 24 < 6
    else:
        return (currtime.tm_hour + 1) % 24 < 8


class Harold(object):

    def __init__(self, mplfifo, ser, mpout, beep=True):
        self.playing = False
        self.mixer = Mixer(control='PCM')
        self.fifo = mplfifo
        self.ser = ser
        self.mpout = mpout
        self.beep = beep

    def write(self, *args, **kwargs):
        delay = kwargs.pop("delay", 0.5)
        kws = {"file": self.fifo}
        kws.update(kwargs)
        print(*args, **kws)
        time.sleep(delay)

    def __call__(self):
        if not self.playing:
            userlog = open("/home/pi/logs/user_log.csv", "a")
            # Lower the volume during quiet hours... Don't piss off the RA!
            self.mixer.setvolume(85 if quiet_hours() else 100)
            varID = self.ser.readline()
            print(varID)
            # mplayer will play any files sent to the FIFO file.
            if self.beep:
                self.write("loadfile", DING_SONG)
            if "ready" not in varID:
                # Turn the LEDs off
                LED.on(False)
                LED.on(False)
                # Get the username from the ibutton
                uid, homedir = read_ibutton(varID)
                # Print the user's name (Super handy for debugging...)
                print("User: '" + uid + "'\n")
                song = get_user_song(homedir)
                print("Now playing '" + song + "'...\n")
                varID = varID[:-2]
                userlog.write("\n" + time.strftime('%Y/%m/%d %H:%M:%S') + "," + varID + "," + uid + "," + song)
                self.write("loadfile '" + song.replace("'", "\\'") + "'\nget_time_length",
                           delay=0.0)

                line = self.mpout.readline()
                while not line.startswith("ANS_LENGTH="):
                    line = self.mpout.readline()
                duration = float(line.strip().split("=")[-1])

                self.starttime = time.time()
                self.endtime = time.time() + min(30, duration)
                self.playing = True
                userlog.close()
        elif time.time() >= self.endtime:
            self.write("stop")
            self.playing = False
            self.ser.flushInput()
            LED.on(True)
            LED.on(True)
            print("Stopped\n")

        elif time.time() >= self.starttime+28:
            # Fade out the music at the end.
            vol = int(self.mixer.getvolume()[0])
            while vol > 60:
                vol -= 1 + (100 - vol)/30.
                self.mixer.setvolume(int(vol))
                time.sleep(0.1)


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
                ser = Serial(args.serial, args.rate)
                ser.flushInput()
            harold = Harold(mplfifo, ser, mplayer.stdout, not args.nobeep)
            while True:
                harold()
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        mplayer.kill()
        os.remove(args.fifo)
        LED.cleanup()

if __name__ == '__main__':
    main()
