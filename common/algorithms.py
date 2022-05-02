import hashlib
import secrets


def a3(rand, key):
    combo = str(rand) + str(key)
    hashed = hashlib.sha256(combo.encode('utf-8')).hexdigest()
    return hashed


def a8(rand, key):
    combo = str(rand) + str(key)
    hashed = hashlib.md5(combo.encode('utf-8')).hexdigest()
    return hashed

def create_sessionID():
    return secrets.token_hex(5)

def rand_num():
    nums = secrets.token_hex(8)
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
            return clientInfo[11:-1]
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
