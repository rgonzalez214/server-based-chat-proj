import hashlib
import secrets

#a3
def encryptionAlgorithm(key, rand):
    a_string = str(key) + str(rand)
    hashed = hashlib.sha256(a_string.encode('utf-8')).hexdigest()
    return hashed

def a8(rand, K_A):
    combo = str(rand) + str(K_A)
    hashed = hashlib.sha256(combo.encode('utf-8')).hexdigest()
    return hashed

def rand_num():
    nums = secrets.token_hex(16)
    return nums

def getID(data):
    id = data[data.find('(')+1:data.find(')')]
    return id

def findK(ID):
    f1 = open("listofsubscribers.txt","r")
    clients = f1.readlines()
    found = 0
    for clientInfo in clients:
        if ID in clientInfo:
            found = 1
            key = clientInfo
            key = clientInfo[11:-1]
            return int(key,16)
        found = 0
    f1.close()
    if found == 0:
        print("Could not find Key associated to client!!")