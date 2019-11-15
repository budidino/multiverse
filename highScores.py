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

competitionSongName = "HighHopes"
competitionDateStart = datetime.date(2019, 11, 1)
competitionDateEnd = datetime.date(2019, 11, 30)

winnerPlayers = ["BIT", "YENG", "CHEEKEN"]
ignorePlayers = ["DINO", "BAN", "BARTENDER", "KING", "PILYO", "KUNG", "JET", "BUDZ"]

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

    # sort all the highscore lists
    for s in scores.keys():
        scores[s] = sorted(scores[s], key=itemgetter('score'), reverse=True)

    # generate HighScore list for competition song
    timeString = datetime.datetime.now().strftime("%B %d").replace(' 0', ' ')
    print(f"{competitionSongName} - {timeString}")
    
    processedPlayers = []
    htmlString = ""
    htmlStringWinners = ""
    for key, value in scores.items():
        if key.lower() == competitionSongName.lower():
            for score in value:
                player = score['player']
                if "JR " in player or " JR" in player:
                    player = player.replace(" JR", " ").replace("JR ", "")

                if player not in ignorePlayers and player not in processedPlayers and len(player) > 1:
                    resultDate = datetime.date.fromtimestamp(score['timestamp'])
                    if resultDate < competitionDateStart or resultDate > competitionDateEnd:
                        continue

                    processedPlayers.append(player)
                    good = score['gameStats']['goodCutsCount']
                    bad = score['gameStats']['badCutsCount']
                    miss = score['gameStats']['missedCutsCount']
                    scoreTime = datetime.datetime.fromtimestamp(score['timestamp']).strftime("%b %d - %I:%M")

                    noFail = score['modifiers']['noFail']
                    disappearingArrows = score['modifiers']['disappearingArrows']
                    ghostNotes = score['modifiers']['ghostNotes']
                    fasterSong = score['modifiers']['songSpeed'] == 1
                    
                    modifiersHtmlString = ""
                    if noFail:
                        modifiersHtmlString += "<img src='icons/noFail.png' title='No Fail' style='width:16px; height:16px; filter:invert(100%);'>"
                    if ghostNotes:
                        modifiersHtmlString += "<img src='icons/ghostNotes.png' title='Ghost Notes' style='width:16px; height:16px; filter:invert(100%);'>"
                    if disappearingArrows:
                        modifiersHtmlString += "<img src='icons/disappearingArrows.png' title='Disappearing Arrows' style='width:16px; height:16px; filter:invert(100%);'>"
                    if fasterSong:
                        modifiersHtmlString += "<img src='icons/fasterSong.png' title='Faster Song' style='width:16px; height:16px; filter:invert(100%);'>"
                    
                    if player in winnerPlayers:
                        htmlStringWinners += f"<tr><td style='text-align: right'>{scoreTime}</td><td>{player}</td><td style='text-align: center'>{good} / {good + bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"
                    else:
                        htmlString += f"<tr><td style='text-align: right'>{scoreTime}</td><td>{player}</td><td style='text-align: center'>{good} / {good + bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"
                    #print(f"{score['score']} {player} ({good} / {good + bad + miss}) - {score['difficulty']}")

    # sort scores by timestamp and display last few    
    htmlStringLatest = ""
    latestScores = sorted(latestScores, key=itemgetter('timestamp'), reverse=True)
    #print("latest scores")
    for score in latestScores[:50]:
        dateFromTS = datetime.datetime.utcfromtimestamp(score["timestamp"]).strftime('%Y-%m-%d')
        dateToday = datetime.datetime.today().strftime('%Y-%m-%d')
        #if dateFromTS != dateToday:
        #    continue

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

        noFail = score['modifiers']['noFail']
        disappearingArrows = score['modifiers']['disappearingArrows']
        ghostNotes = score['modifiers']['ghostNotes']
        fasterSong = score['modifiers']['songSpeed'] == 1
        
        modifiersHtmlString = ""
        if noFail:
            modifiersHtmlString += "<img src='icons/noFail.png' title='No Fail' style='width:16px; height:16px; filter:invert(100%);'>"
        if ghostNotes:
            modifiersHtmlString += "<img src='icons/ghostNotes.png' title='Ghost Notes' style='width:16px; height:16px; filter:invert(100%);'>"
        if disappearingArrows:
            modifiersHtmlString += "<img src='icons/disappearingArrows.png' title='Disappearing Arrows' style='width:16px; height:16px; filter:invert(100%);'>"
        if fasterSong:
            modifiersHtmlString += "<img src='icons/fasterSong.png' title='Faster Song' style='width:16px; height:16px; filter:invert(100%);'>"
                    
        duration = int(score['gameStats']['timePlayed'])
        
        #print(f"{pcName} {score['score']} {player} ({good} / {good + bad + miss}) - {difficulty} - {songName}")
        htmlStringLatest += f"<tr><td style='text-align: right'>{scoreTime}</td><td style='text-align: center'>{pcName}</td><td style='text-align: center'>{duration}</td><td style='text-align: center'>{status}</td><td>{player}</td><td>{songName}</td><td style='text-align: center'>{good} / {good + bad + miss}</td><td style='text-align: center'>{difficulty}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"

    # generate and save HTML file
    message = """<html>
		<head>
			<title>Multiverse VR</title>
			<meta http-equiv="refresh" content="30" />
			<meta name="viewport" content="width=device-width, content=height=device-height, initial-scale=1.0">
			<link rel="stylesheet" type="text/css" href="champions.css">
		</head>
		<body>
			<h1>""" + datetime.datetime.now().strftime("%B") + """ Competition - """ + competitionSongName + """</h1>
			<div>
				<div class="older">
					<h2>Starters League</h2>
					<table>
						<tr>
							<th style="text-align: center">TIME</th>
							<th style="text-align: left">PLAYER</th>
							<th>CUTS</th>
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
							<th style="text-align: center">TIME</th>
							<th style="text-align: left">PLAYER</th>
							<th>CUTS</th>
							<th>DIFFICULTY</th>
							<th style="text-align: right">SCORE</th>
                            <th style="text-align: center">MODIFIERS</th>
						</tr>
						""" + htmlStringWinners + """
					</table>
				</div>
			</div>
			<div class="recents">
				<hr>
				<h2>Recent Games</h2>
				<table>
					<tr>
						<th style="text-align: right">TIME</th>
						<th>PC</th>
                        <th>SEC</th>
                        <th>STATUS</th>
						<th style="text-align: left">PLAYER</th>
						<th style="text-align: left">SONG</th>
						<th>CUTS</th>
						<th>DIFFICULTY</th>
						<th style="text-align: right">SCORE</th>
                        <th style="text-align: center">MODIFIERS</th>
					</tr>
					""" + htmlStringLatest + """
				</table>
			</div>
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
