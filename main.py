#!/usr/bin/env python
from __future__ import print_function
from alsaaudio import Mixer
from random import choice
from serial import Serial
from urllib2 import urlopen
import atexit
import json
import os
import subprocess as sp
import time

# This is a list of sample songs that will randomly play if the
# user is misidentified or does not exist!
DEFAULT_SONGS = [
    "/users/u22/stuart/harold.mp3",
    "/users/u22/henry/harold.mp3",
    "/users/u22/mbillow/harold.mp3"
    "/users/u22/henry/harold/selfie.mp3",
    "/users/u22/henry/harold/waka.mp3",
    "/users/u22/henry/harold/topworld.mp3",
    "/users/u22/henry/harold/heybrother.mp3",
    "/users/u22/henry/harold/boomclap.mp3",
    "/users/u22/henry/harold/starships.mp3",
    "/users/u22/henry/harold/domino.mp3",
    "/users/u22/henry/harold/cruise.mp3"
]

SONG_EXTS = (
    ".mp3", ".mp4", ".m4a", ".flac", ".ogg", ".wav"
)

DING_SONG = "/home/pi/ding.mp3"

MPLAYER_FIFO = "/tmp/mplayer.fifo"

FNULL = open(os.devnull, 'w')


def quiet_hours():
    ' Returns True if the current time is within RIT quiet hours '
    currtime = time.localtime()
    if currtime.tm_wday > 4:
        return (currtime.tm_hour + 23) % 24 < 6
    else:
        return (currtime.tm_hour + 1) % 24 < 8


def read_ibutton(varID):
    '''
    Use Nick Depinet's LDAP service to convert iButtons to usernames
    '''
    try:
        data = urlopen('http://www.csh.rit.edu:56124/?ibutton=' + varID)
        usernameData = json.load(data)
    except urllib2.HTTPError as error:
        # Need to check its an 404, 503, 500, 403 etc.
        print(error.read())
        return ""
    except ValueError as error:
        # Got malformed JSON somehow
        return ""
    else:
        return usernameData['username'][0]


def get_user_song(username):
    '''
    Load one of the following files:
    ~/harold.mp3
    ~/harold/*, of one of the supported file types
    '''
    if username:
        homedir = os.path.expanduser("~" + username)
        hdir = os.path.join(homedir, "harold")
        hfile = os.path.join(homedir, "harold.mp3")
        if os.path.isdir(hdir):
            playlist = [f for f in os.listdir(hdir)
                        if os.path.isfile(os.path.join(hdir, f))
                        and f.endswith(SONG_EXTS)]
            return os.path.join(hdir, choice(playlist))
        elif os.path.isfile(hfile):
            return hfile
    return choice(DEFAULT_SONGS)


class Harold(object):

    def __init__(self, mplfifo):
        self.playing = False
        self.fifo = mplfifo
        self.mixer = Mixer(control='PCM')
        self.ser = Serial('/dev/ttyACM0', 9600)
        self.ser.flushInput()

    def write(self, *args, **kwargs):
        kws = {"file": self.fifo}
        kws.update(kwargs)
        return print(*args, **kws)

    def __call__(self):
        # Lower the volume during quiet hours... Don't piss off the RA!
        self.mixer.setvolume(85 if quiet_hours() else 100)

        if not self.playing:
            varID = self.ser.readline()
            print(varID)
            # mplayer will play any files sent to the FIFO file.
            self.write("loadfile", DING_SONG)
            if "ready" not in varID:
                # Get the username from the ibutton
                username = read_ibutton(varID)

                # Print the user's name (Super handy for debugging...)
                print("New User: '" + username + "'")

                song = get_user_song(username)
                print("Now playing '" + song + "'...\n")
                self.write("loadfile '" + song.replace("'", "\\'") + "'")

                time.sleep(3)
                start = time.time()
                self.playing = True

        elif time.time() - start >= 25:
            # Fade out the music at the end.
            vol = int(self.mixer.getvolume()[0])
            while vol > 60:
                self.mixer.setvolume(vol)
                time.sleep(0.1)
                vol -= 1 + 1 / 3 * (100 - vol)
            self.write("stop")
            self.playing = False
            self.ser.flushInput()
            print("Stopped\n")


def main():
    try:
        os.remove(MPLAYER_FIFO)
    except OSError:
        # This is fine, there just isn't a FIFO there already
        pass
    os.mkfifo(MPLAYER_FIFO)
    cmd = ["mplayer", "-idle", "-slave", "-input", "file="+MPLAYER_FIFO]
    mplayer = sp.Popen(cmd, stdout=FNULL)
    atexit.register(mplayer.kill)
    with open(MPLAYER_FIFO, "w", 0) as mplfifo:
        harold = Harold(mplfifo)
        while True:
            harold()

if __name__ == '__main__':
    main()
