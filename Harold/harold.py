from __future__ import division
from __future__ import print_function
from get_user import read_ibutton, get_user_song
from alsaaudio import Mixer
import led_control as LED
import time

DING_SONG = "/harold/Harold/required/ding.mp3"


def quiet_hours():
    ' Returns True if the current time is within RIT quiet hours '
    currtime = time.localtime()
    if currtime.tm_wday > 4:
        return (currtime.tm_hour + 23) % 24 < 6
    else:
        return (currtime.tm_hour + 1) % 24 < 8


class Harold(object):

    def __init__(self, mplfifo, ser, mpout, beep=True, override = [], blacklist = []):
        self.playing = False
        self.mixer = Mixer(control='PCM')
        self.fifo = mplfifo
        self.ser = ser
        self.mpout = mpout
        self.beep = beep
        self.override = override
        self.blacklist = blacklist
        self.current_user = None

    def write(self, *args, **kwargs):
        delay = kwargs.pop("delay", 0.5)
        kws = {"file": self.fifo}
        kws.update(kwargs)
        print(*args, **kws)
        time.sleep(delay)

    def play(self, override = False):
        varID = self.ser.readline()
        if varID == None or varID == "":
            return
        uid, homedir = read_ibutton(varID)
        if uid in self.blacklist:
            print("user %s is blacklisted, not playing" % uid)
            return
        if not (not override or (override and uid in self.override)) or uid == self.current_user:
            print("user %s is not allowed to override" % uid)
            return
        print("User: '" + uid + "'\n")
        self.current_user = uid
        # mplayer will play any files sent to the FIFO file.
        if self.beep:
            self.write("loadfile", DING_SONG)
        if "ready" not in varID:
            # Turn the LEDs off
            LED.on(False)
            # Get the username from the ibutton
            # uid, homedir = read_ibutton(varID)
            # Print the user's name (Super handy for debugging...)
            song = get_user_song(homedir, uid)
            print("Now playing '" + song + "'...\n")
            varID = varID[:-2]
            self.userlog.write("\n" + time.strftime('%Y/%m/%d %H:%M:%S') + "," + uid + "," + song)
            self.write("loadfile '" + song.replace("'", "\\'") + "'\nget_time_length",
                       delay=0.0)

            line = self.mpout.readline().strip()
            # timeout = time.time() + 5  # Five second time out to wait for song time.

            while not line.startswith("ANS_LENGTH="):
                line = self.mpout.readline().strip()
                if line.startswith("Playing"):  # Check if mplayer can play file.
                    if self.mpout.readline().strip() == "":
                        self.starttime = time.time()
                        self.endtime = time.time()
                        self.playing = True
                        break
                elif line.startswith("ANS_LENGTH="):
                    duration = float(line.strip().split("=")[-1])
                    self.starttime = time.time()
                    self.endtime = time.time() + min(30, duration)
                    self.playing = True
                else:
                    pass

                #self.userlog.close()

    def __call__(self):
        if not self.playing:
            self.userlog = open("/home/pi/logs/user_log.csv", "a")
            # Lower the volume during quiet hours... Don't piss off the RA!
            self.mixer.setvolume(85 if quiet_hours() else 100)
            self.play(False)
        elif self.playing and time.time() < self.endtime:
            self.play(True) # allow a user to override another
        elif self.playing and time.time() >= self.endtime - 2:
            print("fading")
            # Fade out the music at the end.
            vol = int(self.mixer.getvolume()[0])
            while vol > 60:
                vol -= 1 + (100 - vol)/30.
                self.mixer.setvolume(int(vol))
                time.sleep(0.1)
            self.write("stop")
            self.playing = False
            self.current_user = None
            self.ser.flushInput()
            LED.on(True)
            print("Stopped\n")
