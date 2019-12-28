import glob     # directory listing
import hashlib  # sha1
import json

customSongsDir = 'C:/Program Files (x86)/Steam/steamapps/common/Beat Saber/Beat Saber_Data/CustomLevels/'

folders = [f for f in glob.glob(f"{customSongsDir}*/")]
for folder in folders:
    try:
        with open(f"{folder}info.dat", "r") as infoFileData:
            try:
                test = infoFileData
                data = json.load(infoFileData) # TODO: maybe write down which file it was in some error log file?
                
                subFolders = []
                # _difficultyBeatmapSets
                
                sets = data['_difficultyBeatmapSets']
                for s in sets:
                    beatmaps = s["_difficultyBeatmaps"]
                    for beatmap in beatmaps:
                        subFolders.append(beatmap["_beatmapFilename"])

                hashString = infoFileText
                for sub in subFolders:
                    try:
                        with open(f"{folder}{sub}", "r") as beatmapData:
                            hashString += beatmapData.read()
                    except Exception as e:
                        print(f"failed opening file: {folder}{sub} - {e}")
                        continue

                sha1 = hashlib.sha1(hashString.encode('utf-8')).hexdigest()

                # print(f"song: {data['_songName']} - {sha1}")

                if data['_songName'] == "Overkill":
                    print(f"song: {data['_songName']} - {sha1}")

                # 2FDDB136BDA7F9E29B4CB6621D6D8E0F8A43B126
                
            except Exception as e:
                print(f"damaged JSON for file: {folder} - {e}")
                continue
    except Exception as e:
                print(f"failed opening file: {folder} - {e}")
                continue


#songDir = "1f90 (Overkill - Nuketime)"

#string = "abcdef".encode('utf-8')
#sha1 = hashlib.sha1(string).hexdigest()

#print(sha1)