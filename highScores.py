# TODO: show highscore in that song

import glob #directory listing
import json
from pprint import pprint #pritty json print
from operator import itemgetter #sorting
import hashlib # hash strings (detect index.html file changes)
import time # so we can sleep
import datetime
from collections import defaultdict
from slugify import slugify

# github related imports and settings
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo

oneDriveDir = f'C:/Users/Oculus/OneDrive/'

waitTime = 30

longSongDuration: int = 60 * 5

competitionSongName = "TestMe"
competitionDateStart = datetime.date(2019, 12, 1)
competitionDateEnd = datetime.date(2019, 12, 31)

winnerPlayers = ["BIT", "YENG", "CHEE KEN", "MAEVE"]
ignorePlayers = ["DINO", "BAN", "BARTENDER", "KING", "PILYO", "KUNG", "JET", "BUDZ"]
ignoreSongs = ["custom_level", "OneSaber", "NoArrows", "360Degree", "90Degree"]

renamePlayers = {
    "CHEEKEN": "CHEE KEN",
    "CHABBYQT": "CHEE KEN",
    "QT": "CHEE KEN"
}

class Song():
    data = {}
    playersPlayed: int
    gamesPlayed: int
    hoursPlayed: str

class Player():
    name: str
    gold: int
    silver: int
    bronze: int
    score: int

scoresSongsDict = defaultdict()
scoresPlayersDict = defaultdict()
htmlStringLeaderboard = ""
leaderboard: [Song] = []
leaderboardPlayers = defaultdict()

def git_push():
    try:
        repo = Repo(f'{oneDriveDir}githubProject/.git')
        repo.git.add(update=True)
        for f in repo.untracked_files:
            repo.git.add(f)
        repo.index.commit('update from the python script')
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print('Failed to push with error: '+ str(e))

# profiles and leaderboard
def getAllScores():
    scoresSongsDict.clear()
    scoresPlayersDict.clear()
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

            # store player score if valid
            if player != "UNKNOWN" and len(player) > 1:
                if player not in scoresPlayersDict.keys():
                    array = [data]
                    scoresPlayersDict[player] = array
                else:
                    scoresPlayersDict[player].append(data)
            
            # store song scores if valid # ignore custom levels for now
            songName = data['song']
            skipSong = False
            for ignore in ignoreSongs:
                if ignore in songName:
                    skipSong = True

            if player != "UNKNOWN" and len(player) > 1 and not skipSong:
                if songName not in scoresSongsDict.keys():
                    array = [data]
                    scoresSongsDict[songName] = array
                else:
                    scoresSongsDict[songName].append(data)

        except FileNotFoundError:
            print("File not found!")
            continue

def topScoreHtml(score, rowNumber, attempts, name, isPlayer = True):
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

    linkedName = f"<a href='../../players/{slugify(name)}'>{name}</a>"
    if not isPlayer:
        linkedName = f"<a href='../../songs/{slugify(name)}'>{name}</a>"

    return f"<tr {classHtml} title='{scoreTime}'><td style='text-align: center'>{attempts}</td><td style='text-align: right'>{score['score']}</td><td>{linkedName}</td><td style='text-align: center' title='{good} / {good + bad + miss}'>{bad + miss}</td><td style='text-align: center'>{score['difficulty']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"

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
        
        htmlSongs += topScoreHtml(topScore, rowNumber, len(scoresArray), topScore['song'], False)

    htmlStats = ""
    htmlStats += f"<tr class='row-odd'><td style='text-align: left'>Games played</td><td style='text-align: right'>{len(scores)}</td></tr>"
    htmlStats += f"<tr class='row-even'><td style='text-align: left'>Songs played</td><td style='text-align: right'>{len(songsDict)}</td></tr>"
    htmlStats += f"<tr class='row-even'><td style='text-align: left'>Hours played</td><td style='text-align: right'>{str(round(timePlayed/60/60, 2))}</td></tr>"
    # TODO: 
    # date of first game on record
    # date of last game on record
    # unique days played
    # unique weeks played
    # accuracy?
    # leaderboard stats (1, 2, 3 places)
    # tournament wins (which month and song)

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
    try:
        f = open(f'{folder}/index.html', 'w')
        f.write(html)
        f.close()
    except Exception as e:
        print(f"failed to write file to folder: {folder} - {e}")
        # TODO: maybe call the same function again?

def processLeaderboardScores(name, scores):
    playersTopScore = defaultdict()
    playersScore = defaultdict()
    playerAttempts = defaultdict()
    timePlayed = 0
    for score in scores:
        timePlayed += score['gameStats']['timePlayed']
        player = score['player']

        if player not in playerAttempts:
            playerAttempts[player] = 1
            playersScore[player] = score
            playersTopScore[player] = score['score']
        else:
            playerAttempts[player] += 1
            newScore = score['score']
            if newScore > playersTopScore[player]:
                playersTopScore[player] = newScore
                playersScore[player] = score

    sortedPlayerNames = sorted(playersScore, key = lambda k: playersTopScore[k], reverse=True)

    rowNumber = 0
    htmlSongs = ""

    for player in sortedPlayerNames:
        rowNumber += 1
        pScore = playersScore[player]
        pAttempts = playerAttempts[player]
        
        htmlSongs += topScoreHtml(pScore, rowNumber, pAttempts, player)

        if rowNumber == 1:
            song = Song()
            song.data = pScore
            song.gamesPlayed = len(scores)
            song.playersPlayed = len(playersScore)
            song.hoursPlayed = str(round(timePlayed/60/60, 2))
            leaderboard.append(song)

        if rowNumber <= 3:
            if player not in leaderboardPlayers:
                p = Player()
                p.name = player
                p.gold = 0
                p.silver = 0
                p.bronze = 0
                p.score = 0
                leaderboardPlayers[player] = p
            
            p = leaderboardPlayers[player]
            if rowNumber == 1:
                p.gold += 1
                p.score += 3
            elif rowNumber == 2:
                p.silver += 1
                p.score += 2
            elif rowNumber == 3:
                p.bronze += 1
                p.score += 1

    htmlStats = ""
    htmlStats += f"<tr class='row-odd'><td style='text-align: left'>Players played</td><td style='text-align: right'>{len(playersScore)}</td></tr>"
    htmlStats += f"<tr class='row-even'><td style='text-align: left'>Games played</td><td style='text-align: right'>{len(scores)}</td></tr>"
    htmlStats += f"<tr class='row-odd'><td style='text-align: left'>Hours played</td><td style='text-align: right'>{str(round(timePlayed/60/60, 2))}</td></tr>"

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
                <h2>LEADERBOARD</h2>
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
    folder = f'{oneDriveDir}githubProject/songs/{slugify(name)}'
    if not os.path.exists(folder):
        os.makedirs(folder)

    # update player.html file
    try:
        f = open(f'{folder}/index.html', 'w')
        f.write(html)
        f.close()
    except Exception as e:
        print(f"failed to write file to folder: {folder} - {e}")
        # TODO: maybe call the same function again?

def generateLeaderboardHtml():
    html = ""
    rowNumber = 0
    sortedLeaderboard = sorted(leaderboard, key=lambda x: x.playersPlayed, reverse=True)
    for song in sortedLeaderboard:
        good = song.data['gameStats']['goodCutsCount']
        bad = song.data['gameStats']['badCutsCount']
        miss = song.data['gameStats']['missedCutsCount']
        scoreTime = datetime.datetime.fromtimestamp(song.data['timestamp']).strftime("%b %d - %I:%M")
        
        modifiersHtmlString = ""
        if song.data['modifiers']['energyType'] == 1:
            modifiersHtmlString += "<img src='icons/battery.png' title='Battery Energy' style='width:16px; height:16px;'>"
        if song.data['modifiers']['noFail']:
            modifiersHtmlString += "<img src='icons/noFail.png' title='No Fail' style='width:16px; height:16px;'>"
        if song.data['modifiers']['instaFail']:
            modifiersHtmlString += "<img src='icons/instaFail.png' title='Insta Fail' style='width:16px; height:16px;'>"
        if song.data['modifiers']['enabledObstacleType'] == 1:
            modifiersHtmlString += "<img src='icons/noObstacles.png' title='No Obstacles' style='width:16px; height:16px;'>"
        if song.data['modifiers']['disappearingArrows']:
            modifiersHtmlString += "<img src='icons/disappearingArrows.png' title='Disappearing Arrows' style='width:16px; height:16px;'>"
        if song.data['modifiers']['ghostNotes']:
            modifiersHtmlString += "<img src='icons/ghostNotes.png' title='Ghost Notes' style='width:16px; height:16px;'>"
        if song.data['modifiers']['noBombs']:
            modifiersHtmlString += "<img src='icons/noBombs.png' title='No Bombs' style='width:16px; height:16px;'>"
        if song.data['modifiers']['songSpeed'] == 1:
            modifiersHtmlString += "<img src='icons/fasterSong.png' title='Faster Song' style='width:16px; height:16px;'>"
        
        #calculate row number and odd/even
        rowNumber += 1
        classHtml = "class='row-even'"
        if rowNumber % 2 == 1:
            classHtml = "class='row-odd'"

        songName = song.data['song']
        player = song.data['player']
        html += f"<tr {classHtml} title='{scoreTime}'><td style='text-align: center'>{song.playersPlayed}</td><td style='text-align: center'>{song.gamesPlayed}</td><td><a href='songs/{slugify(songName)}'>{songName}</a></td><td><a href='players/{slugify(player)}'>{player}</a></td><td style='text-align: center' title='{good} / {good + bad + miss}'>{bad + miss}</td><td style='text-align: center'>{song.data['difficulty']}</td><td style='text-align: right'>{song.data['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"

    playersHtml = ""
    sortedLeaderboardPlayers = sorted(leaderboardPlayers.values(), key=lambda x: x.score, reverse=True)
    rowNumber = 0
    for p in sortedLeaderboardPlayers:
        rowNumber += 1
        classHtml = f"class='row-{rowNumber} "
        if rowNumber % 2 == 1:
            classHtml += "row-odd'"
        else:
            classHtml += "row-even'"
        playersHtml += f"<tr {classHtml} title='{scoreTime}'><td style='text-align: right'>{p.score}</td><td style='text-align: left'><a href='players/{slugify(p.name)}'>{p.name}</a></td><td style='text-align: center'>{p.gold}</td><td style='text-align: center'>{p.silver}</td><td style='text-align: center'>{p.bronze}</td></tr>"

    global htmlStringLeaderboard
    htmlStringLeaderboard = """
        <h2>PLAYERS</h2>
        <table>
            <tr>
            <th style="text-align: right">SCORE</th>
                <th style="text-align: left">PLAYER</th>
                <th style="text-align: center">GOLD</th>
                <th style="text-align: center">SILVER</th>
                <th style="text-align: center">BRONZE</th>
            </tr>
            """ + playersHtml + """
        </table>

        <h2 style:"padding-top: 20px">SONGS</h2>
        <table>
            <tr>
                <th style="text-align: center">PLAYERS</th>
                <th style="text-align: center">GAMES</th>
                <th style="text-align: left">SONG</th>
                <th style="text-align: left">PLAYER</th>
                <th>MISSES</th>
                <th>DIFFICULTY</th>
                <th style="text-align: right">SCORE</th>
                <th style="text-align: center">MODIFIERS</th>
            </tr>
            """ + html + """
        </table>"""

# competition

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
    #print(f"{competitionSongName} - {timeString}")
    
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
    htmlStringLatestPC1 = ""
    htmlStringLatestPC2 = ""
    rowNumberPC1 = 0
    rowNumberPC2 = 0
    latestScores = sorted(latestScores, key=itemgetter('timestamp'), reverse=True)
    #print("latest scores")

    todayGamesPlayed = 0
    todaySecondsPlayed = 0
    todayPlayers = set()

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
        if duration >= longSongDuration:
            durationHtml = f"<div class='long'>{duration}</div>"
        else:
            durationHtml = duration

        # stats
        todaySecondsPlayed += duration
        todayGamesPlayed += 1
        if player != "?":
            todayPlayers.add(player)

        #print(f"{pcName} {score['score']} {player} ({good} / {good + bad + miss}) - {difficulty} - {songName}")
        if pcName == "#1":
            rowNumberPC1 += 1
            classHtml = "even"
            if rowNumberPC1 % 2 == 1:
                classHtml = "odd"

            htmlStringLatestPC1 += f"<tr class='row-{classHtml}'><td style='text-align: right'>{scoreTime}</td><td style='text-align: center'>{durationHtml}</td><td style='text-align: center'>{status}</td><td><a href='players/{slugify(player)}'>{player}</a></td><td><a href='songs/{slugify(songName)}'>{songName}</a></td><td style='text-align: center'>{difficulty}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"
        else:
            rowNumberPC2 += 1
            classHtml = "even"
            if rowNumberPC2 % 2 == 1:
                classHtml = "odd"
            htmlStringLatestPC2 += f"<tr class='row-{classHtml}'><td style='text-align: right'>{scoreTime}</td><td style='text-align: center'>{durationHtml}</td><td style='text-align: center'>{status}</td><td><a href='players/{slugify(player)}'>{player}</a></td><td><a href='songs/{slugify(songName)}'>{songName}</a></td><td style='text-align: center'>{difficulty}</td><td style='text-align: right'>{score['score']}</td><td style='text-align: center'>{modifiersHtmlString}</td></tr>"

    htmlStats = ""
    htmlStats += f"<tr class='row-odd'><td style='text-align: left'>Players played</td><td style='text-align: right'>{len(todayPlayers)}</td></tr>"
    htmlStats += f"<tr class='row-even'><td style='text-align: left'>Games played</td><td style='text-align: right'>{todayGamesPlayed}</td></tr>"
    htmlStats += f"<tr class='row-odd'><td style='text-align: left'>Hours played</td><td style='text-align: right'>{str(round(todaySecondsPlayed/60/60, 2))}</td></tr>"

    htmlToday = """
        <div class="recents">
            <h2>STATS</h2>
            <table>
                """ + htmlStats + """
            </table>

            <h2 style="padding-top: 20px">PC 2</h2>
            <table>
                <tr>
                    <th style="text-align: right">TIME</th>
                    <th>SEC</th>
                    <th>STATUS</th>
                    <th style="text-align: left">PLAYER</th>
                    <th style="text-align: left">SONG</th>
                    <th>DIFFICULTY</th>
                    <th style="text-align: right">SCORE</th>
                    <th style="text-align: center">MODIF</th>
                </tr>
                """ + htmlStringLatestPC2 + """
            </table>

            <h2 style="padding-top: 20px">PC 1</h2>
            <table style="margin-bottom: 30px">
                <tr>
                    <th style="text-align: right">TIME</th>
                    <th>SEC</th>
                    <th>STATUS</th>
                    <th style="text-align: left">PLAYER</th>
                    <th style="text-align: left">SONG</th>
                    <th>DIFFICULTY</th>
                    <th style="text-align: right">SCORE</th>
                    <th style="text-align: center">MODIF</th>
                </tr>
                """ + htmlStringLatestPC1 + """
            </table>
        </div>
        """

    global htmlStringLeaderboard

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
                <button class="tablinks" onclick="openTab(event, 'Today')" id="Today">Today</button>
            </div>

            <div id="LeaderboardView" class="tabcontent">
                """+ htmlStringLeaderboard +"""
            </div>

            <div id="CompetitionView" class="tabcontent">
                <h2 style="color: white;">""" + datetime.datetime.now().strftime("%B") + """ song: <span style="color: greenyellow;">""" + competitionSongName + """</span></h2>
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
                """ + htmlToday + """
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
        try:
            fileName = f'{oneDriveDir}githubProject/index.html'
            f = open(fileName, 'w')
            f.write(message)
            f.close()
        except Exception as e:
            print(f"failed to write main index file: {fileName} - {e}")
            # TODO: maybe call the same function again?

    for i in range(waitTime):
        timeLeft = waitTime - i
        if timeLeft <= 3:
            print(f"{timeLeft, end="", flush=True)
        else:
            print(".", end="", flush=True)
        time.sleep(1)

def updateLeaderboardAndProfiles():
    getAllScores()

    for name, scores in scoresPlayersDict.items():
        processPlayerScores(name, scores)

    leaderboard.clear()
    leaderboardPlayers.clear()
    for name, scores in scoresSongsDict.items():
        processLeaderboardScores(name, scores)
    
    generateLeaderboardHtml()

while True:
    updateLeaderboardAndProfiles()
    updateHighScores()
    git_push() # push changes to gitHub
