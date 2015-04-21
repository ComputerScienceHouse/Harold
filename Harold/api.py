from get_user import read_ibutton, get_user_song
from flask import Flask, request, jsonify
from ntpath import basename
import sqlite3
import argparse


app = Flask(__name__)


def create_user_dict():
    conn = sqlite3.connect('/harold/Harold/harold_api.db')
    c = conn.cursor()
    user_dict = {}
    for row in c.execute('SELECT * FROM api_users ORDER BY username'):
        user_dict[row[0]] = [row[1], row[2]]
    conn.close()
    return user_dict


def set_song(uid, song_id):
    conn = sqlite3.connect('/harold/Harold/harold_api.db')
    c = conn.cursor()
    c.execute('UPDATE api_users SET song_played=0 WHERE username="{uid}";'.format(uid=uid))
    c.execute('UPDATE api_users SET song_id={song_id}  WHERE username="{uid}";'.format(song_id=song_id, uid=uid))
    conn.commit()
    conn.close()


def create_user(uid, song_id):
    conn = sqlite3.connect('harold_api.db')
    c = conn.cursor()
    c.execute('INSERT INTO api_users VALUES ("{uid}", "{song_id}", 0)'.format(song_id=song_id, uid=uid))
    conn.commit()
    conn.close()


@app.route("/<ibutton>/<song_id>", methods=["GET", "POST"])
def incoming_request(ibutton, song_id):
    inc_req = (ibutton, song_id)
    username, homedir = read_ibutton(inc_req[0])
    song_json = []

    if request.method == "GET":
        song_index = 0
        try:
            song_list = get_user_song(homedir, username, False)
        except:
            song_list = [False]

        try:
            if isinstance(song_list, list):
                for entry in song_list:
                    song_json.append(dict(id=song_index, name=basename(entry)))
                    song_index += 1
            else:
                song_json.append(dict(id=song_index, name=basename(song_list)))

            return jsonify(songs=song_json, user=username, status="true")

        except:
            song_json.append(dict(id=0, name="null"))
            return jsonify(songs=song_json, user=username, status="false")

    if request.method == "POST":
        try:
            user_dict = create_user_dict()
            print("User dict created")
            if username in user_dict:
                print("User found in dictionary!")
                set_song(username, song_id)
                print("Database updated.")
            else:
                print("User created in database.")
                create_user(username, song_id)
                print("Successful")
            return jsonify({"error": False})
        except:
            return jsonify({"error": True})


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test",
                        help="Runs the server in test mode and updates the"
                             " testUsers database.",
                        action="store_true")

    args = parser.parse_args()

    app.run(host='0.0.0.0', port=56125, debug=args.test)


