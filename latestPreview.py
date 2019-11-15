# TODO: show highscore in that song

import csv
from pprint import pprint #pritty json print
from operator import itemgetter #sorting
import datetime
import time # sleep
import re # string replace

competitionSongName = "ORIGINS"
ignorePlayersList = ["DINO", "BAN", "BARTENDER", "KING", "PILYO", "KUNG"]

latestScoresCsvFile = "latest.csv"

waitTime = 5.0

def showLatestScores():
    with open(latestScoresCsvFile, newline='') as csvfile:
        fileReader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in fileReader:
            print(', '.join(row))
    
    time.sleep(waitTime)

while True:
    print("-----------------------------------------")
    showLatestScores()
