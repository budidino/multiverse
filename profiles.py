# TODO: show highscore in that song

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

oneDriveDir = f'C:/Users/Oculus/OneDrive/'

waitTime = 10.0

competitionWinners = ["BIT"]
competitionSongs = ["TestMe"]

renamePlayers = {
    "CHEEKEN": "CHEE KEN"
}

scores = []
players = set()

def git_push():
    try:
        repo = Repo(f'{oneDriveDir}githubProject/.git')
        repo.git.add(update=True)
        repo.index.commit('update from the python profiles script')
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print('Failed to push with error: '+ str(e))
    
def process(player):
    htmlString = ""
    rowCount = 0
    for score in scores:
        name = score['player']
        if name != "BIT":
            continue

        good = score['gameStats']['goodCutsCount']
        bad = score['gameStats']['badCutsCount']
        miss = score['gameStats']['missedCutsCount']
        scoreTime = datetime.datetime.fromtimestamp(score['timestamp']).strftime("%b %d - %I:%M")
        
        modifiersHtmlString = ""
        if score['modifiers']['energyType'] == 1:
            modifiersHtmlString += "<img src='icons/battery.png' title='Battery Energy' style='width:16px; height:16px;'>"
        if score['modifiers']['noFail']:
            modifiersHtmlString += "<img src='icons/noFail.png' title='No Fail' style='width:16px; height:16px;'>"
        if score['modifiers']['instaFail']:
            modifiersHtmlString += "<img src='icons/instaFail.png' title='Insta Fail' style='width:16px; height:16px;'>"
        if score['modifiers']['enabledObstacleType'] == 1:
            modifiersHtmlString += "<img src='icons/noObstacles.png' title='No Obstacles' style='width:16px; height:16px;'>"
        if score['modifiers']['disappearingArrows']:
            modifiersHtmlString += "<img src='icons/disappearingArrows.png' title='Disappearing Arrows' style='width:16px; height:16px;'>"
        if score['modifiers']['ghostNotes']:
            modifiersHtmlString += "<img src='icons/ghostNotes.png' title='Ghost Notes' style='width:16px; height:16px;'>"
        if score['modifiers']['noBombs']:
            modifiersHtmlString += "<img src='icons/noBombs.png' title='No Bombs' style='width:16px; height:16px;'>"
        if score['modifiers']['songSpeed'] == 1:
            modifiersHtmlString += "<img src='icons/fasterSong.png' title='Faster Song' style='width:16px; height:16px;'>"
        
        #calculate row number and odd/even
        rowNumber = 1

        rowCount += 1

        classHtml = f"class='row-{rowNumber} "
        if rowNumber % 2 == 1:
            classHtml += "row-odd'"
        else:
            classHtml += "row-even'"

        htmlString += f"<tr {classHtml} title='{scoreTime}'><td style='text-align: right'>{rowCount}.</td><td>{name}</td><td style='text-align: center' title='{good} / {good + bad + miss}'>{bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"
        #print(f"{score['score']} {player} ({good} / {good + bad + miss}) - {score['difficulty']}")

        # generate and save HTML file
        message = """<html>
            <head>
                <title>""" + player + """</title>
                <meta http-equiv="refresh" content="30" />
                <meta name="format-detection" content="telephone=no">
                <meta name="viewport" content="width=device-width, content=height=device-height, initial-scale=1.0">
                <link rel="stylesheet" type="text/css" href="../../style.css">
            </head>
            <body>
                <h1>""" + player + """</h1>
                <div>
                    <div class="older">
                        <table>
                            <tr>
                                <th style="text-align: center">#</th>
                                <th style="text-align: left">PLAYER</th>
                                <th>MISSES</th>
                                <th>DIFFICULTY</th>
                                <th style="text-align: right">SCORE</th>
                                <th style="text-align: center">MODIFIERS</th>
                            </tr>
                            """ + htmlString + """
                        </table>
                    </div>
                </div>
            </body>
        </html>"""

    # create folder if needed
    folder = f'{oneDriveDir}githubProject/players/{player}'
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(f'{folder}/index.html', "w+") as htmlFile:
        hashObjectOld = hashlib.md5(htmlFile.read().encode('utf-8'))
        hashStringOld = hashObjectOld.hexdigest()

        hashObjectNew = hashlib.md5(message.encode('utf-8'))
        hashStringNew = hashObjectNew.hexdigest()

        if hashStringNew == hashStringOld:
            print("NO UPDATES")
        else:
            print("UPDATING")

    # update player.html file
    if hashStringNew != hashStringOld:
        print(f"updating {player}.html and pushing code")
        f = open(f'{folder}/index.html', 'w')
        f.write(message)
        f.close()

        git_push() # push changes to gitHub

def getAllScores():
    files = [f for f in glob.glob(f"{oneDriveDir}scores/*.txt")]

    for f in files:
        try:
            with open(f, "r") as data_file:
                try:
                    data = json.load(data_file) # TODO: maybe write down which file it was in some error log file?
                except Exception as e:
                    print(f"damaged JSON for file: {f} - {e}")
                    continue

            # get and update player name
            player = data['player']
            if "JR " in player or " JR" in player:
                player = player.replace(" JR", " ").replace("JR ", "")
            for key, value in renamePlayers.items():
                if key == player:
                    player = value
            data['player'] = player

            # store score if valid
            if player != "UNKNOWN" and len(player) > 1:
                scores.append(data)

        except FileNotFoundError:
            print("File not found!")
            continue

    #time.sleep(waitTime)

#while True:
getAllScores()
process("BIT")
