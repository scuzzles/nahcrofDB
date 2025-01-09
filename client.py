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

def getKey(key: str) -> Any:
    headers = {'X-API-Key': DB_pass[0]}
    r = requests.get(url=f"{URL[0]}/v2/key/{quote(key)}/{quote(DB_folder[0])}", headers=headers).json()
    try:
        return r["value"]
    except KeyError:
        return r

def search(data: str) -> list[str]: 
    # search database for keys containing specified data.
    r = requests.get(url=f"{URL[0]}/search/{DB_pass[0]}/?location={quote(DB_folder[0])}&parameter={quote(data)}")
    response = r.json()
    return response["data"]

def searchNames(data: str, where=None) -> list[str]: 
    # search database for keys containing specified data.
    if where == None:
        where = "null"
    r = requests.get(url=f"{URL[0]}/search/{DB_pass[0]}/?location={quote(DB_folder[0])}&parameter={quote(data)}&where={quote(where)}")
    response = r.json()
    return response["data"]

def getKeys(*keys) -> dict:
    templist = []
    headers = {'X-API-Key': DB_pass[0]}
    templist.append(f"?key[]={quote(str(keys[0]))}")
    if len(keys) > 1:
        for key in keys:
            if f"?key[]={key}" in templist:
                pass
            else:
                templist.append(f"&key[]={quote(str(key))}")
    result = "".join(templist)
    return requests.get(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/{result}", headers=headers).json()

def getKeysList(keys: list) -> dict:
    templist = []
    headers = {'X-API-Key': DB_pass[0]}
    templist.append(f"?key[]={quote(str(keys[0]))}")
    if len(keys) > 1:
        for key in keys:
            if f"?key[]={key}" in templist:
                pass
            else:
                templist.append(f"&key[]={quote(str(key))}")
    result = "".join(templist)
    return requests.get(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/{result}", headers=headers).json()

def makeKey(key: str, value: Any):
    payload = {key: value}
    headers = {'X-API-Key': DB_pass[0]}
    return requests.post(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=payload)

def makeKeys(data: dict):
    headers = {'X-API-Key': DB_pass[0]}
    return requests.post(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=data)

def delKey(key: str):
    payload = [key]
    headers = {'X-API-Key': DB_pass[0]}
    return requests.delete(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=payload)

def incrementKey(amount, *pathtokey):
    payload = {"amount": amount}
    headers = {'X-API-Key': DB_pass[0]}
    templist = []
    for value in pathtokey:
        templist.append(f"{value}/")
    finalpath = "".join(templist)
    return requests.post(url=f"{URL[0]}/v2/increment/{quote(DB_folder[0])}/{finalpath}", headers=headers, json=payload)
