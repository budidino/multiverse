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

waitTime = 1.0

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
        with open(f, "r") as data_file:
            data = json.load(data_file)

            song = data["song"]
            #data.pop('modifiers', None)
            #data.pop('settings', None)

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
    resultsCompetitionCSV = ""
    for key, value in highscoresList.items():
        if key.lower() == competitionSongName.lower():
            for score in value:
                player = score['player']
                if player not in ignorePlayersList and player not in processedPlayers and len(player) > 1 and "difficulty" in score:
                    resultsCompetition.append(score)
                    processedPlayers.append(player)

                    # TODO: CSV instead of JSON to make google charts easier
                    #_score = score["score"]
                    #resultsCompetitionCSV += f"{player}, {}"

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

    # sort scores by timestamp and display last few    
    latestScores = sorted(latestScores, key=itemgetter('timestamp'), reverse=True)

    # get all scores from today
    resultsLatest = []
    for score in latestScores:
        dateFromTS = datetime.datetime.utcfromtimestamp(score["timestamp"]).strftime('%Y-%m-%d')
        dateToday = datetime.datetime.today().strftime('%Y-%m-%d')
        if dateFromTS == dateToday:
            resultsLatest.append(score)
            # TODO: CSV instead of JSON to make google charts easier

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

    # TODO: push changes if they exist
    
    time.sleep(waitTime)

while True:
    print("-----------------------------------------")
    updateHighScores()
