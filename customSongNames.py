import hashlib

customSongsDir = f'C:\Program Files (x86)\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels'


# overkill test

songDir = "1f90 (Overkill - Nuketime)"

files = [f for f in glob.glob(f"{oneDriveDir}scores/*.txt")]
for f in files:
    try:
        with open(f, "r") as data_file:
            try:
                data = json.load(data_file) # TODO: maybe write down which file it was in some error log file?
            except Exception as e:
                print(f"damaged JSON for file: {f} - {e}")
                continue


string = "abcdef".encode('utf-8')
sha1 = hashlib.sha1(string).hexdigest()

print(sha1)