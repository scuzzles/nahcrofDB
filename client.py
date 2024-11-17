import requests
import json
from urllib.parse import quote
from typing import Any
import os

DB_folder = [0]
DB_pass = [0]
URL = [0]


def init(folder: str, url: str, password: str) -> None: 
    # store important data in globally defined lists.
    DB_folder[0] = folder
    URL[0] = url
    DB_pass[0] = password

def getKey(keyname: str) -> Any:
    r = requests.get(url=f"{URL[0]}/getKey/{DB_pass[0]}/?location={quote(DB_folder[0])}&keyname={quote(keyname)}")
    data = r.json()
    return data["keycontent"]

def search(data: str) -> list[str]: 
    # search database for keys containing specified data.
    r = requests.get(url=f"{URL[0]}/search/{DB_pass[0]}/?location={quote(DB_folder[0])}&parameter={quote(data)}")
    response = r.json()
    return response["data"]

def getKeys(*keynames) -> dict:
    templist = []
    for keyname in keynames:
        listnum = len(templist)
        keydata = f"&key_{listnum}={keyname}"
        templist.append(keydata)
    keynamenum = len(keynames)
    result = "".join(templist)
    r = requests.get(url=f"{URL[0]}/getKeys/{DB_pass[0]}/?location={quote(DB_folder[0])}&keynamenum={keynamenum}" + result)
    data = r.json()
    return data

def getKeysList(keynames: list) -> dict: 
    # get multiple keys with one request using one list parameter.
    templist = []
    for keyname in keynames:
        listnum = len(templist)
        keydata = f"&key_{listnum}={keyname}"
        templist.append(keydata)
    keynamenum = len(keynames)
    result = "".join(templist)
    r = requests.get(url=f"{URL[0]}/getKeys/{DB_pass[0]}/?location={quote(DB_folder[0])}&keynamenum={keynamenum}" + result)
    data = r.json()
    return data

def makeKey(keyname: str, keycontent: Any):
    payload = {"location": DB_folder[0], "keyname": keyname, "keycontent": keycontent}
    r1 = requests.post(f'{URL[0]}/makeKey/{DB_pass[0]}/', json=payload)
    return r1

def makeKeys(data: dict): # make multiple keys with one request containing a dictionary of updates.
    payload = {"location": DB_folder[0], "data": data}
    r1 = requests.post(f'{URL[0]}/makeKeys/{DB_pass[0]}/', json=payload)
    return r1

def delKey(keyname: str):
    payload = {"location": DB_folder[0], "keyname": keyname}
    r1 = requests.post(f'{URL[0]}/delKey/{DB_pass[0]}/', json=payload)
    return r1

def Keys():
    r = requests.get(f"{URL[0]}/keys/{quote(DB_folder[0])}/{DB_pass[0]}/")
    data = r.json()
    return eval(data["keys"]).keys()

def getLogs():
    r = requests.get(f"{URL[0]}/logs/{quote(DB_folder[0])}/{DB_pass[0]}/")
    data = r.json()
    return eval(data["logs"])

def getAll():
    r = requests.get(f"{URL[0]}/keys/{quote(DB_folder[0])}/{DB_pass[0]}/")
    data = r.json()
    return eval(data["keys"])

def getWrites():
    r = requests.get(f"{URL[0]}/writes/{quote(DB_folder[0])}/{DB_pass[0]}/")
    data = r.json()
    return data

def getReads():
    r = requests.get(f"{URL[0]}/reads/{quote(DB_folder[0])}/{DB_pass[0]}/")
    data = r.json()
    return data

def size():
    r = requests.get(url=f"{URL[0]}/databaseSize/{quote(DB_folder[0])}/{DB_pass[0]}/")
    data = r.json()
    return data["size"]

def keynums():
    r = requests.get(url=f"{URL[0]}/keynums/{quote(DB_folder[0])}/{DB_pass[0]}/")
    data = r.json()
    return data["size"]


def emptyDB(): # creates an empty database folder.
    payload = {"location": DB_folder[0]}
    r = requests.post(f'{URL[0]}/emptyDB/{DB_pass[0]}/', json=payload)

def deleteDB():
    payload = {"location": DB_folder[0]}
    r = requests.post(f'{URL[0]}/deleteDB/{DB_pass[0]}/', json=payload)
