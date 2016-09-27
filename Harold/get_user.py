from urllib2 import urlopen, HTTPError
from random import choice
import credentials as login
import sqlite3
import json
import ldap
import os
import stat

# This is a list of sample songs that will randomly play if the
# user is misidentified or does not exist!
DEFAULT_SONGS = map(lambda f: os.path.join("/harold/Harold/random", f),
                    os.listdir("/harold/Harold/random"))

# List of compatible song types.
SONG_EXTS = (
    ".mp3", ".mp4", ".m4a", ".m4p",
    ".flac", ".ogg", ".oga", ".wav",
    ".wma", ".aac"
)


def isgroupreadable(filepath):
    st = os.stat(filepath)
    return bool(st.st_mode & stat.S_IRGRP)


def create_user_dict():
    conn = sqlite3.connect('/harold/Harold/harold_api.db')
    c = conn.cursor()
    user_dict = {}
    for row in c.execute('SELECT * FROM api_users ORDER BY username'):
        user_dict[row[0]] = [row[1], row[2]]
    conn.close()
    return user_dict


def set_played(uid):
    conn = sqlite3.connect('/harold/Harold/harold_api.db')
    c = conn.cursor()
    c.execute('UPDATE api_users SET song_played=1 WHERE username="{uid}"'.format(uid=uid))
    conn.commit()
    conn.close()


def read_ibutton(varID, cache={}):

    ibutton = varID.strip()

    if ibutton in cache:
        return cache[ibutton]
    try:
        conn = ldap.initialize(login.ldap_server, bytes_mode=True)
        conn.simple_bind_s(login.ldap_user, login.ldap_pass)

        ldap_results = conn.search_s('ou=Users,dc=csh,dc=rit,dc=edu', ldap.SCOPE_SUBTREE, "(ibutton=%s)" % ibutton,
                ['uid', 'homeDirectory'])

        return ldap_results[0][1]['uid'][0], ldap_results[0][1]['homeDirectory'][0]
    except:
        return "mbillow", "/users/u22/mbillow"

def get_user_song(homedir, username, random=True, for_api=False):
    '''
    Load one of the following files:
    ~/harold.mp3
    ~/harold/*, of one of the supported file types
    '''
    global playlist
    user_dict = create_user_dict()

    if homedir:
        hdir = os.path.join(homedir, "harold")
        hfile = os.path.join(homedir, "harold.mp3")
        hiddenhdir = os.path.join(homedir, ".harold")
        if os.path.isdir(hdir):
            playlist = [os.path.join(hdir, f)
                        for f in os.listdir(hdir)
                        if os.path.isfile(os.path.join(hdir, f))
                        and f.endswith(SONG_EXTS) and isgroupreadable(os.path.join(hdir, f))]

        elif os.path.isdir(hiddenhdir):
            playlist = [os.path.join(hiddenhdir, f)
                        for f in os.listdir(hiddenhdir)
                        if os.path.isfile(os.path.join(hiddenhdir, f))
                        and f.endswith(SONG_EXTS) and isgroupreadable(os.path.join(hiddenhdir, f))]

        elif os.path.isfile(hfile) and isgroupreadable(os.path.join(hfile)):
            return hfile
        else:
            return choice(DEFAULT_SONGS)

        if random:
                if username in user_dict:
                    if int(user_dict[username][1]) == 0:
                        selected_song = playlist[int(user_dict[username][0])]
                        set_played(username)
                        return selected_song
                    else:
                        return choice(playlist or DEFAULT_SONGS)
                else:
                    return choice(playlist or DEFAULT_SONGS)
        else:
                if not for_api:
                    return playlist
    return choice(DEFAULT_SONGS)
