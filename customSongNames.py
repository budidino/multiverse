import glob     # directory listing
import hashlib  # sha1
import json
from collections import defaultdict

customSongsDir = 'C:/Program Files (x86)/Steam/steamapps/common/Beat Saber/Beat Saber_Data/CustomLevels/'

songsDict = defaultdict()

folders = [f for f in glob.glob(f"{customSongsDir}*/")]
for folder in folders:
    try:
        with open(f"{folder}info.dat", "r") as infoFileData:
            try:
                test = infoFileData
                data = json.load(infoFileData) # TODO: maybe write down which file it was in some error log file?
                songName = data['_songName']
                hashString = open(f"{folder}info.dat", "r").read()
                
                subFolders = []
                sets = data['_difficultyBeatmapSets']
                for s in sets:
                    beatmaps = s["_difficultyBeatmaps"]
                    for beatmap in beatmaps:
                        subFolders.append(beatmap["_beatmapFilename"])

                for sub in subFolders:
                    try:
                        with open(f"{folder}{sub}", "r") as beatmapData:
                            hashString += beatmapData.read()
                    except Exception as e:
                        print(f"failed opening file: {folder}{sub} - {e}")
                        continue

                
                sha1 = hashlib.sha1(hashString.encode('utf-8')).hexdigest()
                songsDict[sha1] = data['_songName']

                print(f"{} - {sha1}")
                
            except Exception as e:
                print(f"damaged JSON for file: {folder} - {e}")
                continue
    except Exception as e:
                print(f"failed opening file: {folder} - {e}")
                continue


with open('customSongNames.json', 'w') as fp:
    json.dump(sample, fp)
