# TODO: show highscore in that song

import glob #directory listing
import json
from pprint import pprint #pritty json print
from operator import itemgetter #sorting
import hashlib # hash strings (detect index.html file changes)
import time # so we can sleep
import datetime
from slugify import slugify

# github related imports and settings
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo

oneDriveDir = f'C:/Users/Oculus/OneDrive/'

waitTime = 10.0

competitionSongName = "TestMe"
competitionDateStart = datetime.date(2019, 12, 1)
competitionDateEnd = datetime.date(2019, 12, 31)

winnerPlayers = ["BIT", "YENG", "CHEE KEN", "MAEVE"]
ignorePlayers = ["DINO", "BAN", "BARTENDER", "KING", "PILYO", "KUNG", "JET", "BUDZ"]

renamePlayers = {
    "CHEEKEN": "CHEE KEN"
}

def git_push():
    try:
        repo = Repo(f'{oneDriveDir}githubProject/.git')
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
    files = [f for f in glob.glob(f"{oneDriveDir}scores/*.txt")]

    for f in files:
        try:
            with open(f, "r") as data_file:
                try:
                    data = json.load(data_file) # TODO: maybe write down which file it was in some error log file?
                except Exception as e:
                    print(f"damaged JSON for file: {f} - {e}")
                    continue

            song = data['song']

            latestScores.append(data)
            if song != "#unknown":
                if song in scores:
                    scores[song].append(data)
                else:
                    scores[song] = [data]
            #print(f"end: {f}")

        except FileNotFoundError:
            print("File not found!")
            continue

    # sort all the highscore lists
    for s in scores.keys():
        scores[s] = sorted(scores[s], key=itemgetter('score'), reverse=True)

    # generate HighScore list for competition song
    timeString = datetime.datetime.now().strftime("%B %d").replace(' 0', ' ')
    print(f"{competitionSongName} - {timeString}")
    
    processedPlayers = []
    htmlString = ""
    htmlStringWinners = ""
    rowsStarters = 0
    rowsWinners = 0
    for key, value in scores.items():
        if key.lower() == competitionSongName.lower():
            for score in value:
                player = score['player'].strip()
                if "JR " in player or " JR" in player:
                    player = player.replace(" JR", " ").replace("JR ", "")
                for key, value in renamePlayers.items():
                    if key == player:
                        player = value


                if player not in ignorePlayers and player not in processedPlayers and len(player) > 1:
                    resultDate = datetime.date.fromtimestamp(score['timestamp'])
                    if resultDate < competitionDateStart or resultDate > competitionDateEnd:
                        continue

                    processedPlayers.append(player)
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
                    if player in winnerPlayers:
                        rowsWinners += 1
                        rowNumber = rowsWinners
                    else:
                        rowsStarters += 1
                        rowNumber = rowsStarters

                    classHtml = f"class='row-{rowNumber} "
                    if rowNumber % 2 == 1:
                        classHtml += "row-odd'"
                    else:
                        classHtml += "row-even'"

                    if player in winnerPlayers:
                        htmlStringWinners += f"<tr {classHtml} title='{scoreTime}'><td style='text-align: right'>{rowsWinners}.</td><td><a href='players/{slugify(player)}'>{player}</a></td><td style='text-align: center' title='{good} / {good + bad + miss}'>{bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"
                    else:
                        htmlString += f"<tr {classHtml} title='{scoreTime}'><td style='text-align: right'>{rowsStarters}.</td><td><a href='players/{slugify(player)}'>{player}</a></td><td style='text-align: center' title='{good} / {good + bad + miss}'>{bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"
                    #print(f"{score['score']} {player} ({good} / {good + bad + miss}) - {score['difficulty']}")

    # sort scores by timestamp and display last few    
    htmlStringLatest = ""
    rowNumber = 0
    latestScores = sorted(latestScores, key=itemgetter('timestamp'), reverse=True)
    #print("latest scores")
    for score in latestScores:
        dateFromTS = datetime.datetime.utcfromtimestamp(score["timestamp"]).strftime('%Y-%m-%d')
        dateToday = datetime.datetime.today().strftime('%Y-%m-%d')
        if dateFromTS != dateToday:
            continue

        songName = score['song']
        player = score['player'].strip()
        pcName = '#2'
        if score['computerName'] == "Oculus":
            pcName = '#1'
        if "custom_level" in songName:
            songName = "custom"
        scoreTime = datetime.datetime.fromtimestamp(score['timestamp']).strftime(" %I:%M").replace(' 0', '  ').strip()

        difficulty = "?"
        if "difficulty" in score:
            difficulty = score['difficulty']

        if player == "UNKNOWN":
            player = "?"

        if songName == "#unknown":
            songName = "?"

        status = "OK"
        if score['isFail']:
            status = "FAIL"
        elif score['isQuit']:
            status = "QUIT"
        
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
                    
        duration = int(score['gameStats']['timePlayed'])
        durationHtml = ""
        if duration >= 60*4:
            durationHtml = f"<div class='long'>{duration}</div>"
        else:
            durationHtml = duration
        
        rowNumber += 1
        classHtml = "even"
        if rowNumber % 2 == 1:
            classHtml = "odd"

        #print(f"{pcName} {score['score']} {player} ({good} / {good + bad + miss}) - {difficulty} - {songName}")
        htmlStringLatest += f"<tr class='row-{classHtml}'><td style='text-align: right'>{scoreTime}</td><td style='text-align: center'>{pcName}</td><td style='text-align: center'>{durationHtml}</td><td style='text-align: center'>{status}</td><td><a href='players/{slugify(player)}'>{player}</a></td><td>{songName}</td><td style='text-align: center'>{difficulty}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"

    # generate and save HTML file
    message = """<html>
		<head>
			<title>Multiverse VR</title>
			<meta http-equiv="refresh" content="30" />
            <meta name="format-detection" content="telephone=no">
			<meta name="viewport" content="width=device-width, content=height=device-height, initial-scale=1.0">
			<link rel="stylesheet" type="text/css" href="style.css">
            <script type="text/javascript" src="scripts.js"></script>  
		</head>
		<body>
            <h1 style="color: green;">Multiverse <span style="color: greenyellow;">VR</span> cafe</h1>
            <div class="tab">
                <button class="tablinks" onclick="openTab(event, 'Competition')" id="Competition">Competition</button>
                <button class="tablinks" onclick="openTab(event, 'Leaderboard')" id="Leaderboard">Leaderboard</button>
                <button class="tablinks" onclick="openTab(event, 'Stats')" id="Stats">Stats</button>
                <button class="tablinks" onclick="openTab(event, 'Today')" id="Today">Today</button>
            </div>

            <div id="CompetitionView" class="tabcontent">
                <h1 style="color: green;">""" + datetime.datetime.now().strftime("%B") + """ song: <span style="color: greenyellow;">""" + competitionSongName + """</span></h1>
                <div>
                    <div class="older">
                        <h2>Starters League</h2>
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
                    <div class="younger">
                        <h2>Champions League</h2>
                        <table>
                            <tr>
                                <th style="text-align: center">#</th>
                                <th style="text-align: left">PLAYER</th>
                                <th>MISSES</th>
                                <th>DIFFICULTY</th>
                                <th style="text-align: right">SCORE</th>
                                <th style="text-align: center">MODIFIERS</th>
                            </tr>
                            """ + htmlStringWinners + """
                        </table>
                    </div>
                </div>
            </div>

            <div id="TodayView" class="tabcontent">
                <div class="recents">
                    <table>
                        <tr>
                            <th style="text-align: right">TIME</th>
                            <th>PC</th>
                            <th>SEC</th>
                            <th>STATUS</th>
                            <th style="text-align: left">PLAYER</th>
                            <th style="text-align: left">SONG</th>
                            <th>DIFFICULTY</th>
                            <th style="text-align: right">SCORE</th>
                            <th style="text-align: center">MODIFIERS</th>
                        </tr>
                        """ + htmlStringLatest + """
                    </table>
                </div>
            </div>

            <script type="text/javascript">
                window.onload = loaded;
            </script>

		</body>
	</html>"""

    with open(f'{oneDriveDir}githubProject/index.html', "r") as htmlFile:
        hashObjectOld = hashlib.md5(htmlFile.read().encode('utf-8'))
        hashStringOld = hashObjectOld.hexdigest()
        #print("hash old: " + hashStringOld)

        hashObjectNew = hashlib.md5(message.encode('utf-8'))
        hashStringNew = hashObjectNew.hexdigest()
        #print("hash new: " + hashStringNew)

        if hashStringNew == hashStringOld:
            print("NO UPDATES")
        else:
            print("UPDATING")

    # update index.html file
    if hashStringNew != hashStringOld:
        print("updating index.html and pushing code")
        f = open(f'{oneDriveDir}githubProject/index.html', 'w')
        f.write(message)
        f.close()

        git_push() # push changes to gitHub

    time.sleep(waitTime)

while True:
    updateHighScores()
