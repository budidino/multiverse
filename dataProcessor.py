# TODO: show highscore in that song

import glob #directory listing
import json
from pprint import pprint #pritty json print
from operator import itemgetter #sorting
import hashlib # hash strings (detect index.html file changes)
import time # so we can sleep
import datetime
import re # string replace

# github related imports and settings
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo

oneDriveDir = f'C:/Users/Oculus/OneDrive/'

waitTime = 2.0

competitionSongName = "ORIGINS"
ignorePlayersList = ["DINO", "BAN", "BARTENDER", "KING", "PILYO", "KUNG"]

fileHashCompetition = ""
fileHashLatest = ""

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
    global fileHashCompetition
    global fileHashLatest

    # process score files
    highscoresList = {}
    latestScores = []
    files = [f for f in glob.glob(f"{oneDriveDir}scores/*.txt")]

    # TODO: check latest file timestamp - if there are changes continue generating new highscores JSON

    for f in files:
        try:
            data_file = open(f, "r")
        except IOError:
            print('error')
        else:
            with data_file:
                data = json.load(data_file)
                song = data["song"]

                latestScores.append(data)
                if song != "#unknown":
                    if song in highscoresList:
                        highscoresList[song].append(data)
                    else:
                        highscoresList[song] = [data]

    # sort all the highscore lists
    for s in highscoresList.keys():
        highscoresList[s] = sorted(highscoresList[s], key=itemgetter('score'), reverse=True)

    # generate HighScore list for song 'competitionSongName'
    timeString = datetime.datetime.now().strftime("%B %d").replace(' 0', ' ')
    print(f"{competitionSongName} - {timeString}")
    processedPlayers = []
    resultsCompetition = []
    resultsCompetitionCSV = "date, time, player, good cuts, bad cuts, difficuly, score, FC, no fail, dissappearing, ghost, faster, JR\n"
    for key, value in highscoresList.items():
        if key.lower() == competitionSongName.lower():
            for score in value:
                player = score['player']
                if player not in ignorePlayersList and player not in processedPlayers and len(player) > 1 and "difficulty" in score:
                    resultsCompetition.append(score)
                    processedPlayers.append(player)

                    # CSV instead of JSON to make google charts easier
                    cleanPlayer = re.sub(' +', ' ', player.replace(" JR", "").replace("JR ", ""))

                    resultsCompetitionCSV += datetime.datetime.fromtimestamp(score['timestamp']).strftime('%b %d') # date
                    resultsCompetitionCSV += f", {datetime.datetime.fromtimestamp(score['timestamp']).strftime('%I:%M')}" # time
                    resultsCompetitionCSV += f", {cleanPlayer}"
                    resultsCompetitionCSV += f", {score['gameStats']['goodCutsCount']}" # good cuts
                    resultsCompetitionCSV += f", {score['gameStats']['badCutsCount'] + score['gameStats']['missedCutsCount']}" # bad+miss cuts
                    resultsCompetitionCSV += f", {score['difficulty']}" # difficulty
                    resultsCompetitionCSV += f", {score['score']}" # score
                    resultsCompetitionCSV += f", {score['fullCombo']}" # FC
                    resultsCompetitionCSV += f", {score['modifiers']['noFail']}" # no fail
                    resultsCompetitionCSV += f", {score['modifiers']['disappearingArrows']}" # disappearingArrows
                    resultsCompetitionCSV += f", {score['modifiers']['ghostNotes']}" # ghostNotes
                    if score['modifiers']['songSpeed'] == 1:
                        resultsCompetitionCSV += f", {True}" # is faster song
                    else:
                        resultsCompetitionCSV += f", {False}" # not faster song

                    if "JR " in player or " JR" in player:
                        resultsCompetitionCSV += f", {True}" # is junior
                    else:
                        resultsCompetitionCSV += f", {False}" # not junior
                    resultsCompetitionCSV += "\n" # end of line

    # save the highscore if there are scores in it
    if len(resultsCompetition) > 0:
        newFileJson = json.dumps(resultsCompetition, sort_keys = False, indent = 4, ensure_ascii = False)
        hashObject = hashlib.md5(newFileJson.encode('utf-8'))
        hashString = hashObject.hexdigest()

        if fileHashCompetition != hashString:
            print(f"Saving highscores json: {oneDriveDir}githubProject/{competitionSongName.lower()}.json")
            fileHashCompetition = hashString
            with open(f"{oneDriveDir}githubProject/{competitionSongName.lower()}.json", 'w', encoding='utf-8') as f:
                f.write(newFileJson)

            print(f"Saving highscores csv: {oneDriveDir}githubProject/{competitionSongName.lower()}.csv")
            with open(f"{oneDriveDir}githubProject/{competitionSongName.lower()}.csv", 'w', encoding='utf-8') as f:
                f.write(resultsCompetitionCSV)

    # sort scores by timestamp and display last few    
    latestScores = sorted(latestScores, key=itemgetter('timestamp'), reverse=True)

    # get all scores from today
    resultsLatest = []
    resultsLatestCSV = "time, duration, fail, quit, player, pc, song, cuts, difficulty, score, no fail, disappearing, ghost, faster song\n"
    for score in latestScores:
        dateFromTS = datetime.datetime.utcfromtimestamp(score["timestamp"]).strftime('%Y-%m-%d')
        dateToday = datetime.datetime.today().strftime('%Y-%m-%d')
        if dateFromTS == dateToday:
            resultsLatest.append(score)
            
            # CSV instead of JSON to make google charts easier
            player = "UNKNOWN"
            if 'player' in score:
                player = score['player']

            cleanPlayer = re.sub(' +', ' ', player)
            pcName = '#2'
            if score['computerName'] == "Oculus":
                pcName = '#1'

            songName = "#unknown"
            if 'song' in score:
                songName = score['song']
            if "custom_level" in songName:
                songName = "custom"
            
            difficulty = "#unknown"
            if 'difficulty' in score:
                difficulty = score['difficulty']

            resultsLatestCSV += datetime.datetime.fromtimestamp(score['timestamp']).strftime('%I:%M') # time
            resultsLatestCSV += f", {int(score['gameStats']['timePlayed'])}s" # seconds played
            resultsLatestCSV += f", {score['isFail']}"
            resultsLatestCSV += f", {score['isQuit']}"
            resultsLatestCSV += f", {cleanPlayer}"
            resultsLatestCSV += f", {pcName}"
            resultsLatestCSV += f", {songName}"
            resultsLatestCSV += f", {score['gameStats']['goodCutsCount']} / {score['gameStats']['badCutsCount'] + score['gameStats']['missedCutsCount'] + score['gameStats']['goodCutsCount']}" # cuts
            resultsLatestCSV += f", {difficulty}"
            resultsLatestCSV += f", {score['score']}"
            resultsLatestCSV += f", {score['modifiers']['noFail']}" # no fail
            resultsLatestCSV += f", {score['modifiers']['disappearingArrows']}" # disappearingArrows
            resultsLatestCSV += f", {score['modifiers']['ghostNotes']}" # ghostNotes
            if score['modifiers']['songSpeed'] == 1:
                resultsLatestCSV += f", {True}" # is faster song
            else:
                resultsLatestCSV += f", {False}" # not faster song
            resultsLatestCSV += "\n" # end of line

    # save latest if there are any
    if len(resultsLatest) > 0:
        latestJson = json.dumps(resultsLatest, sort_keys = False, indent = 4, ensure_ascii = False)
        latestObject = hashlib.md5(latestJson.encode('utf-8'))
        latestHashString = latestObject.hexdigest()

        if fileHashLatest != latestHashString:
            print(f"Saving latest json: {oneDriveDir}githubProject/latest.json")
            fileHashLatest = latestHashString
            with open(f"{oneDriveDir}githubProject/latest.json", 'w', encoding='utf-8') as f:
                f.write(latestJson)

            print(f"Saving latest csv: {oneDriveDir}githubProject/latest.csv")
            with open(f"{oneDriveDir}githubProject/latest.csv", 'w', encoding='utf-8') as f:
                f.write(resultsLatestCSV)

    # TODO: push changes if they exist
    
    time.sleep(waitTime)

while True:
    print("-----------------------------------------")
    updateHighScores()
