import hashlib

string = "abcdef".encode('utf-8')
sha1 = hashlib.sha1(string).hexdigest()

print(sha1)