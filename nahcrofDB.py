import sys
import time
import os, shutil
import pickle
import requests
from read_config import config
utf = "utf-8"
# file_stats.st_size / (1024 * 1024)
default_path = config["default_path"]

def log(location, message):
    try:
        logs = logmanager(location)
        log_limit = config["logs_per_database"]
        if log_limit != "none":
            if len(logs) > int(log_limit):
                logs.pop(len(logs) - 1)
        logs.append(message)
        pickle.dump(logs, open(f"{default_path}{location}/usr.tmplogs", "wb"))
        os.replace(f"{default_path}{location}/usr.tmplogs", f"{default_path}{location}/usr.logs")
    except Exception as e:
        try:
            pickle.dump([], open(f"{default_path}{location}/usr.logs", "wb"))
            log(location, message)
        except FileNotFoundError:
            print("log file doesn't exist, should make itself so this should be impossible but here we are")
    print(f"MESSAGE TO {location} | {message}")

def logmanager(location):
    try:
        logs = pickle.load(open(f"{default_path}{location}/usr.logs", "rb"))
        return logs
    except EOFError:
        return logmanager(location)


def getLogs(location):
    try:
        return logmanager(location)
    except Exception as e:
        pickle.dump([], open(f"{default_path}{location}/usr.logs", "wb"))
        return getLogs(location)

# {default_path}

def keys(location):
    try:
        content = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))["keys"]
    except Exception as e:
        content = e
        log(location, e)
    return content

def getWrites(location):
    st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
    writes = st["system"]["writes"]
    return writes

def getReads(location):
    st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
    reads = st["system"]["reads"]
    return reads

def search(location, data):
    newdata = str(data).lower()
    templist = []
    try:
        tempdict = {}
        st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
        partitions = st["system"]["partitions"]
        for partition in range(partitions):
            partition = int(partition) + 1
            tempdict[str(partition)] = pickle.load(open(f"{default_path}{location}/usr_f{partition}.db", "rb"))
        existing = st["keys"] 
        for item in existing:
            try:
                checking = str(tempdict[str(st["keys"][item])][item])  
                if newdata in checking:
                    templist.append(item)
            except KeyError:
                log(location, f"SEARCH ERROR: trouble when checking values in ({item})")
        return templist
    except Exception as e:
        log(location, e)
        return e

def retrieveStructure(location):
    try:
        st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
        return st
    except EOFError:
        log(location, "failed to retrieve structure, retrying")
        return retrieveStructure(location)

def getKey(location, keyname):
    try:
        current_writes = str(os.listdir(config["write_folder"]))
        if keyname in current_writes:
            time.sleep(0.1)
            return getKey(location, keyname)
        st = retrieveStructure(location)
        partition = st["keys"][keyname]
        try:
            reads = st["system"]["reads"]
            st["system"]["reads"] = reads + 1
        except KeyError:
            st["system"]["reads"] = 1
        pickle.dump(st, open(f"{default_path}{location}/usr_st.db", "wb"))
        content = pickle.load(open(f"{default_path}{location}/usr_f{partition}.db", "rb"))[keyname]
    except KeyError:
        log(location, f"could not find key: {keyname}")
        content = "Key does not exist, DATABASE erroR"
    return content

def makeKey(location, keyname, keycontent):
    try:
        files = os.listdir(f"{default_path}{location}")
        for file in files:
            file_stats = os.stat(f"{default_path}{location}/{file}.db")
            mbs = file_stats.st_size / (1000 * 1000)
    except Exception as e:
        mbs = 0
    try:
        size_limit = config["database_size_limit"]
        if size_limit == "none":
            pass
        else:
            if mbs > int(size_limit):
                log(location, "database size limit exceeded")
                return "database too large"
    except Exception as e:
        print()


    try:
        st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
        partitions = st["system"]["partitions"]
        print(f"partitions begin: {partitions}")
        if keyname not in st["keys"]:
            file_stats = os.stat(f"{default_path}{location}/usr_f{partitions}.db")
            mbs = file_stats.st_size / (1000 * 1000)
            partition_size = int(config["partition_size"])
            if mbs > partition_size:
                partitions = st["system"]["partitions"] + 1 
                st["system"]["partitions"] = partitions
                st["keys"][keyname] = partitions + 1
                st["system"]["writes"] = st["system"]["writes"] + 1
                pickle.dump(st, open(f"{default_path}{location}/usr_st.tmp", "wb"))
                pickle.dump({}, open(f"{default_path}{location}/usr_f{partitions}.db", "wb"))
            else:
                st["keys"][keyname] = partitions
                st["system"]["writes"] = st["system"]["writes"] + 1
                pickle.dump(st, open(f"{default_path}{location}/usr_st.tmp", "wb"))
            partitions = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))["system"]["partitions"]
            db = pickle.load(open(f"{default_path}{location}/usr_f{partitions}.db", "rb"))
            db[keyname] = keycontent
            pickle.dump(db, open(f"{default_path}{location}/usr_f{partitions}.tmp", "wb"))
            os.replace(f"{default_path}{location}/usr_f{partitions}.tmp", f"{default_path}{location}/usr_f{partitions}.db")
            os.replace(f"{default_path}{location}/usr_st.tmp", f"{default_path}{location}/usr_st.db")

        else:
            correctpartition = st["keys"][keyname]
            st["system"]["writes"] = st["system"]["writes"] + 1
            pickle.dump(st, open(f"{default_path}{location}/usr_st.tmp", "wb"))
            db = pickle.load(open(f"{default_path}{location}/usr_f{correctpartition}.db", "rb"))
            db[keyname] = keycontent
            pickle.dump(db, open(f"{default_path}{location}/usr_f{correctpartition}.tmp", "wb"))
            os.replace(f"{default_path}{location}/usr_f{correctpartition}.tmp", f"{default_path}{location}/usr_f{correctpartition}.db")
            os.replace(f"{default_path}{location}/usr_st.tmp", f"{default_path}{location}/usr_st.db")
    except Exception as e:
        os.mkdir(f"{default_path}{location}")
        db = {keyname: keycontent}
        st = {"keys": {keyname: 1}, "system": {"partitions": 1, "writes": 0}}
        pickle.dump(db, open(f"{default_path}{location}/usr_f1.db", "wb"))
        pickle.dump(st, open(f"{default_path}{location}/usr_st.db", "wb"))
        log(location, "If you're seeing this, something probably went very wrong (this database was set empty)")
    finally:
        try:
            structure_check = pickle.load(open(f"{default_path}{location}/usr_st.db","rb"))["keys"]
        except Exception as e:
            log(location, f"error checking DB structure when creating ({keyname}), retrying")
            time.sleep(0.1)
            return makeKey(location, keyname, keycontent)
        if keyname not in structure_check:
            time.sleep(0.2)
            log(location, f"key ({keyname}) not found after creation, retrying")
            return makeKey(location, keyname, keycontent)
        else:
            return "success"

def getKeys(location: str, keynames: list):
    tempdict = {}
    for keyname in keynames:
        current_writes = str(os.listdir(config["write_folder"]))
        if keyname in current_writes:
            time.sleep(0.1)
            return getKeys(location, keynames)
    try:
        loaded_db = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
        for key in keynames:
            try:
                tempdict[key] = getKey(location, key)
            except KeyError:
                tempdict[key] = "Key does not exist, DATABASE erroR"
    except EOFError:
        log(location, "encountered EOF error, retrying")
        print("encountered EOF error, retrying")
        return getKeys(location, keynames)
    return tempdict


def delKey(location, keyname):
    try:
        st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
        partition = st["keys"][keyname]
        del st["keys"][keyname]
        pickle.dump(st, open(f"{default_path}{location}/usr_st.db", "wb"))
        partitiondata = pickle.load(open(f"{default_path}{location}/usr_f{partition}.db", "rb"))
        del partitiondata[keyname]
    except KeyError:
        log(location, f"could not delete key: {keyname}")
        content = "Key does not exist, DATABASE erroR"

def keysamount(location):
    try:
        amount = len(pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))["keys"])
    except Exception as e:
        log(location, f"AMOUNT ERROR: {e}")
        amount = 0
    return amount



def sizeofDB(location):
    try:
        amount = 0
        files = os.listdir(f"{default_path}{location}")
        for file in files:
            file_stats = os.stat(f"{default_path}{location}/{file}")
            mbs = file_stats.st_size / (1000 * 1000)
            amount += mbs
        return amount
    except Exception as e:
        print(e)
        return f"ERROR: {e}"

def emptyDB(location):
    os.mkdir(f"{default_path}{location}")
    db = {}
    st = {"keys": {}, "system": {"partitions": 1, "writes": 0, "reads": 0}}
    pickle.dump(db, open(f"{default_path}{location}/usr_f1.db", "wb"))
    pickle.dump(st, open(f"{default_path}{location}/usr_st.db", "wb"))

def deleteDB(location):
    os.system(f"rm -r {default_path}{location}")

def backupDB(location):
    try:
        os.listdir(f"{default_path}{location}_database_backup")
    except FileNotFoundError:
        emptyDB(f"{location}_database_backup")
    db = search(location, "")
    alldata = getKeys(location, db)
    for key, value in alldata.items():
        makeKey(f"{location}_database_backup", key, value)
    backupdb = search(f"{location}_database_backup", "")
    backupdata = getKeys(f"{location}_database_backup", backupdb)
    for key in backupdata:
        if key not in db:
            delKey(f"{location}_database_backup", key)


def setToBackup(location):
    try:
        os.listdir(f"{default_path}{location}_database_backup")
    except FileNotFoundError:
        print("backup does not exist, good luck!")
        return "failed"
    backup_loc = f"{location}_database_backup"
    deleteDB(location)
    emptyDB(location)
    db = search(backup_loc, "")
    alldata = getKeys(backup_loc, db)
    for key, value in alldata.items():
        makeKey(location, key, value)


