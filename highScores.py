
import glob #directory listing
import json
from pprint import pprint #pritty json print
from operator import itemgetter #sorting

#import requests
#import base64
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo

scores = {}

files = [f for f in glob.glob("C:/Users/Oculus/OneDrive/scores/*.txt")]

for f in files:
    with open(f, "r") as data_file:
        data = json.load(data_file)
        song = data['song']
        data.pop('modifiers', None)
        data.pop('settings', None)
        if song in scores:
            scores[song].append(data)
            scores[song] = sorted(scores[song], key=itemgetter('score'), reverse=True)
        else:
            scores[song] = [data]
            
#pprint(scores)

print("OVERKILL")
result = {}
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
                if "JR " in player or " JR" in player:
                    playerJR = player.replace(" JR", " ").replace("JR ", "")
                    htmlStringKids += f"<tr><td>{playerJR}</td><td style='text-align: center'>{good} / {good + bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td></tr>"
                else:
                    htmlString += f"<tr><td>{player}</td><td style='text-align: center'>{good} / {good + bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td></tr>"
                print(f"{score['score']} {player} ({good} / {good + bad + miss}) - {score['difficulty']}")


# generate and save HTML file
f = open('index.html', 'w')
message = """<html>
<head></head>
<body style="padding: 40">
    <h1>August Competition - Overkill</h1>

    <h2>15 or older</h2>
    <table style="width: 400px">
        <tr>
            <th style="text-align: left">PLAYER</th>
            <th>CUTS</th>
            <th>DIFFICULTY</th>
            <th style="text-align: right">SCORE</th>
        </tr>
        """ + htmlString + """
    </table>

    <h2>14 or younger</h2>
    <table style="width: 400px">
        <tr>
            <th style="text-align: left">PLAYER</th>
            <th>CUTS</th>
            <th>DIFFICULTY</th>
            <th style="text-align: right">SCORE</th>
        </tr>
        """ + htmlStringKids + """
    </table>
</body>
</html>"""
f.write(message)
f.close()

# push to github

def git_push():
    try:
        repo = Repo('.git')
        repo.git.add(update=True)
        repo.index.commit('update from the python script')
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print('Failed to push with error: '+ str(e))

git_push()
