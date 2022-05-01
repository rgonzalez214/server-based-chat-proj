import hashlib
import secrets

#a3
def a3(rand, key):
    combo = str(rand) + str(key)
    print(rand, key,"ok", combo)
    hashed = hashlib.sha1(combo.encode('utf-8')).hexdigest()
    return hashed

def a8(rand, key):
    combo = str(rand) + str(key)
    hashed = hashlib.sha256(combo.encode('utf-8')).hexdigest()
    return hashed

def rand_num():
    nums = secrets.token_hex(16)
    return nums

def getID(data):
    id = data[data.find('(')+1:data.find(')')]
    return id

def findSecretKey(clientID):
    f1 = open("listofsubscribers.txt","r")
    clients = f1.readlines()
    Found = False
    for clientInfo in clients:
        if clientID in clientInfo:
            Found = True
            return int(clientInfo[11:-1],16)
    if not Found:
        return -1

def verify(clientID):
    # Verify if a client is on the list of subscribers
    f1 = open("listofsubscribers.txt", "r")
    clients = f1.readlines()
    Verified = False
    for client in clients:
        if clientID == client[0:10]:
            Verified = True
            break
    return Verified
