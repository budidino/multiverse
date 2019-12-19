import glob #directory listing
import json
from pprint import pprint #pritty json print
from operator import itemgetter #sorting
import time # so we can sleep
import datetime
from collections import defaultdict
from slugify import slugify

# github related imports and settings
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo

oneDriveDir = f'C:/Users/Oculus/OneDrive/'

waitTime = 60.0 # calculate every minute

competitionWinners = ["BIT"]
competitionSongs = ["TestMe"]

renamePlayers = {
    "CHEEKEN": "CHEE KEN",
    "CHABBYQT": "CHEE KEN"
}

scoresDict = defaultdict()

def git_push():
    try:
        repo = Repo(f'{oneDriveDir}githubProject/.git')
        repo.git.add(update=True)
        for f in repo.untracked_files:
            print(f)
            repo.git.add(f)
        repo.index.commit('update from the python profiles script')
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print('Failed to push with error: '+ str(e))

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
            player = player.strip()
            data['player'] = player

            # store score if valid
            if player != "UNKNOWN" and len(player) > 1:
                if player not in scoresDict.keys():
                    array = [data]
                    scoresDict[player] = array
                else:
                    scoresDict[player].append(data)

        except FileNotFoundError:
            print("File not found!")
            continue

def topScoreHtml(score, rowNumber, attempts):
    song = score['song']
    good = score['gameStats']['goodCutsCount']
    bad = score['gameStats']['badCutsCount']
    miss = score['gameStats']['missedCutsCount']
    scoreTime = datetime.datetime.fromtimestamp(score['timestamp']).strftime("%b %d - %I:%M")
    
    # TODO: only if after August 18
    modifiersHtmlString = ""
    if score['modifiers']['energyType'] == 1:
        modifiersHtmlString += "<img src='../../icons/battery.png' title='Battery Energy' style='width:16px; height:16px;'>"
    if score['modifiers']['noFail']:
        modifiersHtmlString += "<img src='../../icons/noFail.png' title='No Fail' style='width:16px; height:16px;'>"
    if score['modifiers']['instaFail']:
        modifiersHtmlString += "<img src='../../icons/instaFail.png' title='Insta Fail' style='width:16px; height:16px;'>"
    if score['modifiers']['enabledObstacleType'] == 1:
        modifiersHtmlString += "<img src='../../icons/noObstacles.png' title='No Obstacles' style='width:16px; height:16px;'>"
    if score['modifiers']['disappearingArrows']:
        modifiersHtmlString += "<img src='../../icons/disappearingArrows.png' title='Disappearing Arrows' style='width:16px; height:16px;'>"
    if score['modifiers']['ghostNotes']:
        modifiersHtmlString += "<img src='../../icons/ghostNotes.png' title='Ghost Notes' style='width:16px; height:16px;'>"
    if score['modifiers']['noBombs']:
        modifiersHtmlString += "<img src='../../icons/noBombs.png' title='No Bombs' style='width:16px; height:16px;'>"
    if score['modifiers']['songSpeed'] == 1:
        modifiersHtmlString += "<img src='../../icons/fasterSong.png' title='Faster Song' style='width:16px; height:16px;'>"

    classHtml = f"class='row-"
    if rowNumber % 2 == 1:
        classHtml += "odd'"
    else:
        classHtml += "even'"

    return f"<tr {classHtml} title='{scoreTime}'><td style='text-align: center'>{attempts}</td><td style='text-align: right'>{score['score']}</td><td>{song}</td><td style='text-align: center' title='{good} / {good + bad + miss}'>{bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"
    
def processPlayerScores(name, scores):
    songsDict = defaultdict()
    timePlayed = 0
    for score in scores:
        song = score['song']
        timePlayed += score['gameStats']['timePlayed']

        if song not in songsDict:
            songsDict[song] = [score]
        else:
            songsDict[song].append(score)

    sortedSongNames = sorted(songsDict, key = lambda key: len(songsDict[key]), reverse=True)

    rowNumber = 0
    htmlSongs = ""

    for songName in sortedSongNames:
        scoresArray = songsDict[songName]
        rowNumber += 1

        topScore = scoresArray[0]
        for scoreData in scoresArray:
            if scoreData['score'] > topScore['score']:
                topScore = scoreData
        
        htmlSongs += topScoreHtml(topScore, rowNumber, len(scoresArray))

        # TODO: generate new file with all the scores for that song

    htmlStats = ""
    htmlStats += f"<tr class='row-odd'><td style='text-align: left'>Games played</td><td style='text-align: right'>{len(scores)}</td></tr>"
    htmlStats += f"<tr class='row-even'><td style='text-align: left'>Songs played</td><td style='text-align: right'>{len(songsDict)}</td></tr>"
    htmlStats += f"<tr class='row-even'><td style='text-align: left'>Hours played</td><td style='text-align: right'>{str(round(timePlayed/60/60, 2))}</td></tr>"
    # TODO: date of first game on record, date of last game on record, days played, weeks played, accuracy?, tournament wins (which month and song)

    # generate and save HTML file
    html = """<html>
        <head>
            <title>""" + name + """</title>
            <meta name="format-detection" content="telephone=no">
            <meta name="viewport" content="width=device-width, content=height=device-height, initial-scale=1.0">
            <link rel="stylesheet" type="text/css" href="../../style.css">
        </head>
        <body>
            <h1>""" + name + """</h1>
            <div>
                <h2>STATS</h2>
                <table>
                    """ + htmlStats + """
                </table>

                <h2>SONGS</h2>
                <table>
                    <tr>
                        <th style="text-align: center">PLAYS</th>
                        <th style="text-align: right">SCORE</th>
                        <th style="text-align: left">SONG</th>
                        <th>MISSES</th>
                        <th>DIFFICULTY</th>
                        <th style="text-align: center">MODIFIERS</th>
                    </tr>
                    """ + htmlSongs + """
                </table>
            </div>
        </body>
    </html>"""

    # create folder if needed
    folder = f'{oneDriveDir}githubProject/players/{slugify(name)}'
    if not os.path.exists(folder):
        os.makedirs(folder)

    # update player.html file
    f = open(f'{folder}/index.html', 'w')
    f.write(html)
    f.close()

#while True:
getAllScores()

for name, scores in scoresDict.items():
    processPlayerScores(name, scores)

print("pushing changes")
git_push() # push changes to gitHub

#time.sleep(waitTime)
