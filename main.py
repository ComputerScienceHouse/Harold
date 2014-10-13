from __future__ import print_function
import alsaaudio
import time
import os
import serial
import random
import json
import urllib2

ser = serial.Serial('/dev/ttyACM0', 9600)
ser.flushInput()

m = alsaaudio.Mixer(control='PCM')

os.remove("/tmp/mplayer.fifo")
os.mkfifo("/tmp/mplayer.fifo")
os.system("mplayer -idle -slave -input file=/tmp/mplayer.fifo 1&>/dev/null &")
mplfifo = open("/tmp/mplayer.fifo", "w", 0)

playTime = 0

playing = False
varID = ""

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
    ".mp3", ".mp4", ".m4a", ".flac", ".ogg"
)

DING_SONG = "/home/pi/ding.mp3"

def get_user_song(username):
    if username:
        homedir = os.path.expanduser("~"+username)
        if os.path.isdir(os.path.join(homedir, "harold")):
            playlist = [f for f in os.listdir(dafile + "/harold")
                        if os.path.isfile(dafile + "/harold/" + f)
                        and f.endswith(SONG_EXTS)]
            return os.path.join(homedir, "harold", random.choice(playlist))
        elif os.path.isfile(os.path.join(homedir, "harold.mp3")):
            return os.path.join(homedir, "harold.mp3")
    return random.choice(DEFAULT_SONGS)

while True:
    if not playing:
        varID = ser.readline()
        print(varID)
        if "ready" in varID:
            varID = ""
        # Mplayer will play any files sent to the FIFO file.
        print("loadfile", DING_SONG, file=mplfifo)
    if (time.localtime().tm_hour + 1) % 24 <= 8:
        # Lower the volume during quiet hours... Don't piss off the RA!
        m.setvolume(85)
    else:
        m.setvolume(100)
    if not playing and varID != "":
        try:
            # Use Nick Depinet's LDAP service!
            usernameData = json.load(urllib2.urlopen('http://www.csh.rit.edu:56124/?ibutton=' + varID))
        except urllib2.HTTPError as error:
            # Need to check its an 404, 503, 500, 403 etc.
            print(error.read())
            username = ""
        else:
            username = usernameData['username'][0]
            
        # Print the user's name (Super handy for debugging...)
        print("New User: '" + username + "'")

        song = get_user_song(username)
        print("Now playing '" + username + "'...\n")
        print("loadfile '" + song.replace("'", "\\'") + "'", file=mplfifo)

        time.sleep(3)
        start = time.time()
        playing = True
    elif playing and time.time() - start >= 25:
        # Fade out the music at the end.
        vol = int(m.getvolume()[0])
        while vol > 60:
            m.setvolume(vol)
            time.sleep(0.1)
            vol -= 1 + 1 / 3 * (100 - vol)
        print("stop", file=mplfifo)
        playing = False
        ser.flushInput()
        print("Stopped\n")
