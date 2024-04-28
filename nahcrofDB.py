import requests
import json
from urllib.parse import quote
import os
usertoken = ["0"]
myurl = "https://database.nahcrof.com"

def init(token):
    usertoken[0] = token

def getKey(key):
    headers = {'X-API-Key': usertoken[0]}
    r = requests.get(url=f"{myurl}/v2/key/{quote(key)}", headers=headers).json()
    try:
        return r["value"]
    except KeyError:
        return r

def getKeys(*keys):
    templist = []
    headers = {'X-API-Key': usertoken[0]}
    templist.append(f"?key[]={quote(str(keys[0]))}")
    if len(keys) > 1:
        for key in keys:
            if f"?key[]={key}" in templist:
                pass
            else:
                templist.append(f"&key[]={quote(str(key))}")
    result = "".join(templist)
    return requests.get(url=f"{myurl}/v2/keys/{result}", headers=headers).json()

def resetDB():
    headers = {'X-API-Key': usertoken[0]}
    return requests.delete(url=f"{myurl}/v2/reset/", headers=headers).json()

def makeKey(key, value):
    payload = {key: value}
    headers = {'X-API-Key': usertoken[0]}
    return requests.post(url=f"{myurl}/v2/keys/", headers=headers, json=payload)

def delKey(key):
    payload = [key]
    headers = {'X-API-Key': usertoken[0]}
    return requests.delete(url=f"{myurl}/v2/keys/", headers=headers, json=payload)

def search(query):
    headers = {'X-API-Key': usertoken[0]}
    r = requests.get(url=f"{myurl}/v2/search/?query={quote(query)}", headers=headers).json()
    return r
