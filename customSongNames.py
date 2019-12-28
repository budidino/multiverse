import hashlib

customSongsDir = f'C:\Program Files (x86)\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels'

string = "abcdef".encode('utf-8')
sha1 = hashlib.sha1(string).hexdigest()

print(sha1)