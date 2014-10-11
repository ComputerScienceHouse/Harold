import alsaaudio
import time
import os
import serial
import random

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

songs = ["http://csh.rit.edu/~stuart/harold.mp3", "http://csh.rit.edu/~henry/harold.mp3", "http://csh.rit.edu/~mbillow/harold.mp3"]
songs.append("http://csh.rit.edu/~henry/harold/selfie.mp3")
songs.append("http://csh.rit.edu/~henry/harold/waka.mp3")
songs.append("http://csh.rit.edu/~henry/harold/topworld.mp3")
songs.append("http://csh.rit.edu/~henry/harold/heybrother.mp3")
songs.append("http://csh.rit.edu/~henry/harold/boomclap.mp3")
songs.append("http://csh.rit.edu/~henry/harold/starships.mp3")
songs.append("http://csh.rit.edu/~henry/harold/domino.mp3")
songs.append("http://csh.rit.edu/~henry/harold/cruise.mp3")

while 1:
    try:
        if not playing:
            varID = ser.readline()
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
        print("New ID: '" + varID + "'")
        username = ""
        if "760A0D006D322001" in varID:
            username = "henry"
        elif "FD0A0D00DC223601" in varID:
            username = "stuart"
        else:
            dafile = songs[random.randint(0, len(songs)-1)]

        if username != "":
            print("Now playing '" + username + "'...\n")
            os.system("echo \"loadfile http://csh.rit.edu/~" + username + "/harold.mp3\" >/tmp/mplayer.fifo")
        else:
            print("Now playing '" + dafile + "'...\n")
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
