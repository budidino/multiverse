import glob #directory listing
import json
from pprint import pprint #pritty json print
from operator import itemgetter #sorting
import hashlib # hash strings (detect index.html file changes)
import time # so we can sleep
import datetime

# github related imports and settings
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo

waitTime = 30.0

def git_push():
    try:
        repo = Repo('.git')
        repo.git.add(update=True)
        repo.index.commit('update from the python script')
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print('Failed to push with error: '+ str(e))


def updateHighScores():
    # process score files
    scores = {}
    latestScores = []
    files = [f for f in glob.glob("../scores/*.txt")]

    for f in files:
        with open(f, "r") as data_file:
            data = json.load(data_file)
            song = data['song']
            data.pop('modifiers', None)
            data.pop('settings', None)

            latestScores.append(data)
            if song in scores:
                scores[song].append(data)
                scores[song] = sorted(scores[song], key=itemgetter('score'), reverse=True)
            else:
                scores[song] = [data]

    # generate HighScore list for song 'Overkill'
    timeString = datetime.datetime.now().strftime("%B %d - %I").replace(' 0', ' ')
    print(f"OVERKILL - {timeString}")
    players = ["DINO", "BAN", "BARTENDER"]
    htmlString = ""
    htmlStringKids = ""
    for key, value in scores.items():
        if key == "Overkill":
            for score in value:
                player = score['player']
                if player not in players and len(player) > 1:
                    players.append(player)
                    good = score['gameStats']['goodCutsCount']
                    bad = score['gameStats']['badCutsCount']
                    miss = score['gameStats']['missedCutsCount']
                    scoreTime = datetime.datetime.fromtimestamp(score['timestamp']).strftime("%b %d - %I:%M").replace(' 0', '  ')
                    if "JR " in player or " JR" in player:
                        playerJR = player.replace(" JR", " ").replace("JR ", "")
                        htmlStringKids += f"<tr><td style='text-align: right'>{scoreTime}</td><td>{playerJR}</td><td style='text-align: center'>{good} / {good + bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td></tr>"
                    else:
                        htmlString += f"<tr><td style='text-align: right'>{scoreTime}</td><td>{player}</td><td style='text-align: center'>{good} / {good + bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td></tr>"
                    print(f"{score['score']} {player} ({good} / {good + bad + miss}) - {score['difficulty']}")

    # sort scores by timestamp and display last few
    htmlStringLatest = ""
    latestScores = sorted(latestScores, key=itemgetter('timestamp'), reverse=True)
    print("latest scores")
    for score in latestScores[:10]:
        songName = score['song']
        player = score['player']
        good = score['gameStats']['goodCutsCount']
        bad = score['gameStats']['badCutsCount']
        miss = score['gameStats']['missedCutsCount']
        pcName = '#2'
        if score['computerName'] == "Oculus":
            pcName = '#1'
        if "custom_level" in songName:
            songName = "custom"
        scoreTime = datetime.datetime.fromtimestamp(score['timestamp']).strftime(" %I:%M").replace(' 0', '  ').strip()
        print(f"{pcName} {score['score']} {player} ({good} / {good + bad + miss}) - {score['difficulty']} - {songName}")
        htmlStringLatest += f"<tr><td style='text-align: right'>{scoreTime}</td><td style='text-align: center'>{pcName}</td><td>{player}</td><td>{songName}</td><td style='text-align: center'>{good} / {good + bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td></tr>"

    # generate and save HTML file
    message = """<html>
    <head>
        <title>Multiverse VR</title>
        <meta http-equiv="refresh" content="30" />
        <link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body style="padding: 25">
        <h1>August Competition - Overkill</h1>

        <table style="width: 400px">
            <tr>
                <td valign="top">
                    <h2>15 or older</h2>
                    <table style="width: 400px">
                        <tr>
                            <th style="text-align: right">TIME</th>
                            <th style="text-align: left">PLAYER</th>
                            <th>CUTS</th>
                            <th>DIFFICULTY</th>
                            <th style="text-align: right">SCORE</th>
                        </tr>
                        """ + htmlString + """
                    </table>
                    </td>
                <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
                <td valign="top">
                    <h2>14 or younger</h2>
                    <table style="width: 400px">
                        <tr>
                            <th style="text-align: right">TIME</th>
                            <th style="text-align: left">PLAYER</th>
                            <th>CUTS</th>
                            <th>DIFFICULTY</th>
                            <th style="text-align: right">SCORE</th>
                        </tr>
                        """ + htmlStringKids + """
                    </table>
                </td>
            </tr>
        </table>

        <hr><h2>Recent Games</h2>
        <table style="width: 600px">
            <tr>
                <th style="text-align: right">TIME</th>
                <th>PC</th>
                <th style="text-align: left">PLAYER</th>
                <th style="text-align: left">SONG</th>
                <th>CUTS</th>
                <th>DIFFICULTY</th>
                <th style="text-align: right">SCORE</th>
            </tr>
            """ + htmlStringLatest + """
        </table>
    </body>
    </html>"""

    with open('index.html', "r") as indexFile:
        hashObjectOld = hashlib.md5(indexFile.read().encode('utf-8'))
        hashStringOld = hashObjectOld.hexdigest()
        print("hash old: " + hashStringOld)

        hashObjectNew = hashlib.md5(message.encode('utf-8'))
        hashStringNew = hashObjectNew.hexdigest()
        print("hash new: " + hashStringNew)

    # update index.html file
    if hashStringNew != hashStringOld:
        print("updating index.html and pushing code")
        f = open('index.html', 'w')
        f.write(message)
        f.close()

        git_push() # push changes to gitHub

    time.sleep(waitTime)

while True:
    updateHighScores()
