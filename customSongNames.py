import hashlib
string = "abcdef".encode('utf-8')
encoded = hashlib.sha1(string).hexdigest()
print(encoded)