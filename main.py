import alsaaudio
import time
import os
import serial
import random
import json
import urllib2

ser = serial.Serial('/dev/ttyACM0', 9600)
ser.flushInput()

timeHour = int(time.strftime('%H'))

# os.system("mplayer -slave -input file=/tmp/mplayer.fifo /home/pi/ding.mp3 &")
os.system("rm -f /tmp/mplayer.fifo")
os.system("mkfifo /tmp/mplayer.fifo && mplayer -idle -slave -input file=/tmp/mplayer.fifo 1&>/dev/null &")

playTime = 0

playing = False
start = ""
varID = ""

songs = ["/users/u22/stuart/harold.mp3", "/users/u22/henry/harold.mp3", "/users/u22/mbillow/harold.mp3"]
songs.append("/users/u22/henry/harold/selfie.mp3")
songs.append("/users/u22/henry/harold/waka.mp3")
songs.append("/users/u22/henry/harold/topworld.mp3")
songs.append("/users/u22/henry/harold/heybrother.mp3")
songs.append("/users/u22/henry/harold/boomclap.mp3")
songs.append("/users/u22/henry/harold/starships.mp3")
songs.append("/users/u22/henry/harold/domino.mp3")
songs.append("/users/u22/henry/harold/cruise.mp3")

while 1:
    try:
        if not playing:
            varID = ser.readline()
            print(varID)
            if "ready" in varID:
                varID = ""
            os.system("echo \"loadfile /home/pi/ding.mp3\" >/tmp/mplayer.fifo")
    except:
        pass
    if (23 <= timeHour <= 24) or (0 <= timeHour <= 7):
        m = alsaaudio.Mixer(control='PCM')
        m.setvolume(70)
    else:
        m = alsaaudio.Mixer(control='PCM')
        vol = m.getvolume()
        m.setvolume(100)
    if not playing and varID != "":
        try:
            usernameData = json.load(urllib2.urlopen('http://www.csh.rit.edu:56124/?ibutton=' + varID))
        except urllib2.HTTPError, error:
            # Need to check its an 404, 503, 500, 403 etc.
            contents = error.read()
            print(contents)
            username = ""
            dafile = songs[random.randint(0, len(songs)-1)]
        else:
            username = usernameData['username'][0]
            dafile = usernameData['homeDir'][0]
            
        print("New User: '" + username + "'")
        
        if (username != "") and (os.access(dafile + "/harold.mp3", os.R_OK)):
                print("Now playing '" + username + "'...\n")
                os.system("echo \"loadfile " + dafile + "/harold.mp3\" >/tmp/mplayer.fifo")
        else:
            print("Error - not found. Now playing '" + dafile + "'...\n")
            dafile = songs[random.randint(0, len(songs)-1)]
            os.system("echo \"loadfile " + dafile + "\" >/tmp/mplayer.fifo")

        time.sleep(3)
        start = time.strftime("%s")
        playing = True
    elif playing and int(time.strftime("%s")) - int(start) >= 25:
        vol = 100
        while vol > 60:
            m.setvolume(vol)
            time.sleep(0.1)
            vol -= 1 + 1 / 3 * (100 - vol)
        os.system("echo \"stop\" >/tmp/mplayer.fifo")
        playing = False
        ser.flushInput()
        print "Stopped\n"
