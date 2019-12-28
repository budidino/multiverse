import hashlib

hash_object = hashlib.sha1('HelWorld')
pbHash = hash_object.hexdigest()
length = len(pbHash.decode("hex"))
print length