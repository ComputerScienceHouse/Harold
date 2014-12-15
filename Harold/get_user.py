from urllib2 import urlopen, HTTPError
from random import choice
import json
import os


# This is a list of sample songs that will randomly play if the
# user is misidentified or does not exist!
DEFAULT_SONGS = map(lambda f: os.path.join("/harold/Harold/random", f),
                    os.listdir("/harold/Harold/random"))

# List of compatible song types.
SONG_EXTS = (
    ".mp3", ".mp4", ".m4a", ".m4p",
    ".flac", ".ogg", ".oga", ".wav",
    ".wma"
)


def read_ibutton(varID, cache={}):
    '''
    Use Nick Depinet's LDAP service to convert iButtons to usernames

    Caches values when possible (iButtons don't really change)
    '''
    if varID in cache:
        return cache[varID]
    try:
        data = urlopen('http://www.csh.rit.edu:56124/?ibutton=' + varID)
        uidData = json.load(data)
    except HTTPError as error:
        # Need to check its an 404, 503, 500, 403 etc.
        print(error.read())
    except ValueError as error:
        # Got malformed JSON somehow
        print(error)
    else:
        cache[varID] = uidData['uid'], uidData['homeDir']
        return cache[varID]
    return "", ""


def get_user_song(homedir):
    '''
    Load one of the following files:
    ~/harold.mp3
    ~/harold/*, of one of the supported file types
    '''
    if homedir:
        print("Home:", homedir)
        hdir = os.path.join(homedir, "harold")
        hfile = os.path.join(homedir, "harold.mp3")
        hiddenhdir = os.path.join(homedir, ".harold")
        if os.path.isdir(hdir):
            playlist = [os.path.join(hdir, f)
                        for f in os.listdir(hdir)
                        if os.path.isfile(os.path.join(hdir, f))
                        and f.endswith(SONG_EXTS)]
            return choice(playlist or DEFAULT_SONGS)
        elif os.path.isdir(hiddenhdir):
            playlist = [os.path.join(hiddenhdir, f)
                        for f in os.listdir(hiddenhdir)
                        if os.path.isfile(os.path.join(hiddenhdir, f))
                        and f.endswith(SONG_EXTS)]
            return choice(playlist or DEFAULT_SONGS)
        elif os.path.isfile(hfile):
            return hfile
    return choice(DEFAULT_SONGS)
