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

# This is a list of sample songs that will randomly play if the user is misidentified or does not exist!
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
            os.system("echo \"loadfile /home/pi/ding.mp3\" >/tmp/mplayer.fifo")  # Mplayer will play any files sent to the FIFO file.
    except:
        pass
    if (23 <= timeHour <= 24) or (0 <= timeHour <= 7):  # Lower the volume during quite hours... Don't piss off the RA!
        m = alsaaudio.Mixer(control='PCM')
        m.setvolume(85)
    else:
        m = alsaaudio.Mixer(control='PCM')
        vol = m.getvolume()
        m.setvolume(100)
    if not playing and varID != "":
        try:
            usernameData = json.load(urllib2.urlopen('http://www.csh.rit.edu:56124/?ibutton=' + varID))  # Use Nick Depinet's LDAP service!
        except urllib2.HTTPError, error:
            # Need to check its an 404, 503, 500, 403 etc.
            contents = error.read()
            print(contents)
            username = ""
            dafile = songs[random.randint(0, len(songs)-1)]
        else:
            username = usernameData['username'][0]
            dafile = usernameData['homeDir'][0]
            
        print("New User: '" + username + "'")  # Print the user's name (Super handy for debugging...)

        if (username != "") and (os.path.isdir(dafile + "/harold")):  #

            playlistFiles = [f for f in os.listdir(dafile + "/harold") if os.path.isfile(dafile + "/harold/" + f) and f.endswith(".mp3") ]  # Makes list of files excluding directories.
            shuffleSong = playlistFiles[random.randint(0, len(playlistFiles)-1)]  # Pick a random song from the list!
            os.system("echo \"loadfile '" + dafile + "/harold/" + shuffleSong.replace("'", "\\'") + "'\" >/tmp/mplayer.fifo")  # Play dat funky music white boy!
            #os.system("bash scrapemp3.sh '" + dafile + "/harold'")

        elif (username != "") and (os.access(dafile + "/harold.mp3", os.R_OK)) and not (os.path.isdir(dafile + "/harold")):  # User only has one song, well PLAY IT!
            print("Now playing '" + username + "'...\n")
            os.system("echo \"loadfile " + dafile + "/harold.mp3\" >/tmp/mplayer.fifo")

        else:
            print("Error - not found. Now playing '" + dafile + "'...\n")  # User doesn't have ANYTHING?! (or doesn't exist...) Welp, play something from the list.
            dafile = songs[random.randint(0, len(songs)-1)]
            os.system("echo \"loadfile " + dafile + "\" >/tmp/mplayer.fifo")

        time.sleep(3)
        start = time.strftime("%s")
        playing = True
    elif playing and int(time.strftime("%s")) - int(start) >= 25:
        vol = int(m.getvolume()[0])  # Fade out the music at the end.
        while vol > 60:
            m.setvolume(vol)
            time.sleep(0.1)
            vol -= 1 + 1 / 3 * (100 - vol)
        os.system("echo \"stop\" >/tmp/mplayer.fifo")
        playing = False
        ser.flushInput()
        print "Stopped\n"
