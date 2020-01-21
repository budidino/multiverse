# ideas: sync scores across computers (update highscore)
# update LocalDailyLeaderboards.dat to delete lowest score in any list that has 10 songs to make sure we fetch every score
# keep only the best score per user

import getpass #computer name
import time
import datetime
import json
import os
from pprint import pprint #pritty json print

waitTime = 1.0
computerUser = getpass.getuser()
scoresFolderPath = f"C:/Users/{computerUser}/OneDrive/scores/"

previousGameData = {}
previousGameScore = {}
modifiers = {}
settings = {}
isFail = False
isQuit = False
latestFileJson = {}
latestFilename = ""
shouldUpdateLatestFile = False

def fetchAndStoreSettings():
    global previousGameData
    global previousGameScore
    global modifiers
    global settings
    global isFail
    global isQuit
    global latestFileJson
    global latestFilename
    global shouldUpdateLatestFile

    filePlayerData = "C:\\Users\\" + computerUser + "\\AppData\\LocalLow\\Hyperbolic Magnetism\\Beat Saber\\PlayerData.dat"
    with open(filePlayerData, "r") as data_file:
        data = json.load(data_file)

    localPlayers = data["localPlayers"][0]
    modifiers = localPlayers["gameplayModifiers"]
    settings = localPlayers["playerSpecificSettings"]
    stats = localPlayers["playerAllOverallStatsData"]["partyFreePlayOverallStatsData"]

    if previousGameData:
        print("waiting for a game to finish")
        if previousGameData["stats"]["playedLevelsCount"] and stats["playedLevelsCount"]:
            if stats["playedLevelsCount"] - previousGameData["stats"]["playedLevelsCount"] == 1:
                # NEW LEVEL FINISHED
                print("LEVEL FINISHED")
                isFail = False
                isQuit = False

                 # Check if LEVEL NOT COMPLETED
                if previousGameData["stats"]["cleardLevelsCount"] == stats["cleardLevelsCount"]:
                    if previousGameData["stats"]["failedLevelsCount"] != stats["failedLevelsCount"]:
                        # LEVEL FAILED
                        print("by FAILING!")
                        isFail = True
                    else:
                        # LEVEL QUIT
                        print("by QUITTING")
                        isQuit = True
                
                previousGameScore = {
                    "badCutsCount": stats["badCutsCount"] - previousGameData["stats"]["badCutsCount"],
                    "cutScoreWithoutMultiplier": stats["cummulativeCutScoreWithoutMultiplier"] - previousGameData["stats"]["cummulativeCutScoreWithoutMultiplier"],
                    "goodCutsCount": stats["goodCutsCount"] - previousGameData["stats"]["goodCutsCount"],
                    "handDistanceTravelled": stats["handDistanceTravelled"] - previousGameData["stats"]["handDistanceTravelled"],
                    "missedCutsCount": stats["missedCutsCount"] - previousGameData["stats"]["missedCutsCount"],
                    "timePlayed": stats["timePlayed"] - previousGameData["stats"]["timePlayed"],
                    "totalScore": stats["totalScore"] - previousGameData["stats"]["totalScore"]}

                # SAVE BASE DATA
                shouldUpdateLatestFile = True
                timestamp = int(time.time())
                player = "UNKNOWN"
                latestFilename = f"{scoresFolderPath}{str(timestamp)}{computerUser}.txt"
                with open(latestFilename, 'a+') as outfile:
                    latestFileJson = {
                        "timestamp": timestamp,
                        "song": "#unknown",
                        "isFail": isFail,
                        "isQuit": isQuit,
                        "computerName": computerUser,
                        "player": player,
                        "score": previousGameScore["totalScore"],
                        "modifiers": modifiers,
                        "settings": settings,
                        "gameStats": previousGameScore }
                    json.dump(latestFileJson, outfile, sort_keys = False, indent = 4, ensure_ascii = False)
    else:
        print("no previous stats - script just launched")

    # save game info data
    previousGameData = { "modifiers": modifiers, "settings": settings, "stats": stats }

def updateLatestFileIfDataAvailable():
    # TODO: only look for a new score if the leaderboard file was updated after latestFilename vas updated
    fileLocalDailyLeaderboards = "C:\\Users\\" + computerUser + "\\AppData\\LocalLow\\Hyperbolic Magnetism\\Beat Saber\\LocalDailyLeaderboards.dat"
    with open(fileLocalDailyLeaderboards, "r") as data_file:
        data = json.load(data_file)

    leaderboardsData = data["_leaderboardsData"]
    scores = []

    for item in leaderboardsData:
        songId = item['_leaderboardId']
        
        # get difficulty
        difficulty = ""
        if songId.endswith("ExpertPlus"):
            difficulty = "ExpertPlus"
        elif songId.endswith("Expert"):
            difficulty = "Expert"
        elif songId.endswith("Hard"):
            difficulty = "Hard"
        elif songId.endswith("Normal"):
            difficulty = "Normal"
        else: 
            difficulty = "Easy"

        song = songId[: -len(difficulty)]

        # add all scores
        songScores = item["_scores"]
        for s in songScores:
            fullCombo = s["_fullCombo"]
            player = s["_playerName"]
            scoreValue = s["_score"]
            timestamp = s["_timestamp"]
            score = (timestamp, computerUser, player, song, difficulty, scoreValue, fullCombo)
            scores.append(score)

            fileName = f"{scoresFolderPath}{str(timestamp)}{computerUser}.txt"
            if not os.path.exists(fileName):
                if scoreValue == previousGameScore["totalScore"]:
                    #delete latestFilename
                    os.remove(latestFilename)

                    # used to guess who played when fail or quit
                    global latestPlayer
                    latestPlayer = player

                    global latestFileJson
                    with open(fileName, 'a+') as outfile:
                        jsonData = {"timestamp": timestamp,
                                    "computerName": computerUser,
                                    "isFail": latestFileJson["isFail"],
                                    "isQuit": latestFileJson["isQuit"],
                                    "player": player,
                                    "song": song,
                                    "difficulty": difficulty,
                                    "score": scoreValue,
                                    "fullCombo": fullCombo,
                                    "modifiers": modifiers,
                                    "settings": settings,
                                    "gameStats": previousGameScore }
                        json.dump(jsonData, outfile, sort_keys = False, indent = 4, ensure_ascii = False)

                        global shouldUpdateLatestFile
                        shouldUpdateLatestFile = False

    # TODO: delete 10th score on all scoreboards that have 10 scores - and overwrite the local leaderboard file

def fetchAndStoreScores():
    print("-----------------------------------------------")
    print(f"script running - {int(time.time())}")
    fetchAndStoreSettings()

    global shouldUpdateLatestFile

    if shouldUpdateLatestFile:
        updateLatestFileIfDataAvailable()
    
    time.sleep(waitTime)


while True:
    fetchAndStoreScores()
