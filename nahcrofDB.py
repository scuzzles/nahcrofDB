import sys
import os, shutil
import pickle
import requests
utf = "utf-8"

def makeKey(keyname, keycontent):
    db = pickle.load(open("main.db", "rb"))
    db[keyname] = keycontent
    pickle.dump(db, open("main.db", "wb"))


def getKey(keyname):
    try:
        content = pickle.load(open("main.db", "rb"))[keyname]
    except KeyError:
        content = "Key not found"
    return content

def createDB():
    db = {}
    pickle.dump(db, open("main.db", "wb"))

if __name__ == '__main__':
    args = sys.argv[1:]
    if args:
        if args[0] == "help":
            print("Co4mands:")
            print("createDB - creates a database to load data from")
            print("")
            print("this is currently the only command that exists, more commands will come in the future :)")
    if args[0] == "createDB":
        createDB()



