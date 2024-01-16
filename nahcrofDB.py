import requests
import json
import os
token = [0]
username = [0]

# stores token and username to simplify database access
def init(api_token: str, location: str):
    token[0] = api_token
    username[0] = location

# returns a key from the defined database
def getKey(keyname: str):
    if token[0] == 0:
        return "token parameter not set"
    elif username[0] == 0:
        return "username/location parameter not set"
    else:
        r = requests.get(url=f"https://database.nahcrof.com/getKey/?location={username[0]}&keyname={keyname}&token={token[0]}")
        data = r.json()
        return data["keycontent"]

def getKeys(*keynames):
    templist = []
    for keyname in keynames:
        listnum = len(templist)
        keydata = f"&key_{listnum}={keyname}"
        templist.append(keydata)
    keynamenum = len(keynames)
    result = "".join(templist)
    r = requests.get(url=f"https://database.nahcrof.com/getKeys/?location={username[0]}&token={token[0]}&keynamenum={keynamenum}" + result)
    data = r.json()
    return data

# creates a key in the defined database
def makeKey(keyname: str, keycontent):
    if token[0] == 0:
        print("token parameter not set")
    elif username[0] == 0:
        print("username/location parameter not set")
    else:
        payload = {"location": username[0], "keyname": keyname, "keycontent": keycontent, "token": token[0]}
        r1 = requests.post('https://database.nahcrof.com/makeKey', json=payload)
        return r1

# returns all existing keys in defined database
def getAll():
    if token[0] == 0:
        return "token parameter not set"
    elif username[0] == 0:
        return "username/location parameter not set"
    else:
        r = requests.get(url=f"https://database.nahcrof.com/getAll/?location={username[0]}&token={token[0]}")
        data = r.json()
        return data

def delKey(keyname: str):
    if token[0] == 0:
        print("token parameter not set")
    elif username[0] == 0:
        print("username/location parameter not set")
    else:
        payload = {"location": username[0], "keyname": keyname, "token": token[0]}
        r1 = requests.post('https://database.nahcrof.com/delKey', json=payload)
        return r1


# this will reset the defined database to have 0 keys, no backup will be made, DO NOT use this unless you know what you are doing
def resetDB():
    if token[0] == 0:
        print("token parameter not set")
    elif username[0] == 0:
        print("username/location parameter not set")
    else:
        payload = {"location": username[0], "token": token[0]}
        r1 = requests.post('https://database.nahcrof.com/resetDB', json=payload)
        return r1
