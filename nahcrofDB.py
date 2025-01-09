import sys
import filecmp
import time
import mmap
import os, shutil
import pickle
import random
from read_config import config
utf = "utf-8"
# file_stats.st_size / (1024 * 1024)
default_path = config["default_path"]

# this will log a message to the location/database folder
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

def compare_databases(db1, db2):
    db1 = f"{default_path}{db1}"
    db2 = f"{default_path}{db2}"
    db1_files = os.listdir(db1)
    db2_files = os.listdir(db2)
    for file in db1_files:
        if file in db2_files:
            if not filecmp.cmp(f"{db1}/{file}", f"{db2}/{file}"):
                return False
        else:
            return False
    return True

# view logs and retry if file is being written to
def logmanager(location):
    try:
        logs = pickle.load(open(f"{default_path}{location}/usr.logs", "rb"))
        return logs
    except EOFError:
        return logmanager(location)

# view logs using logmanager, create empty logs file if something goes wrong.
def getLogs(location):
    try:
        return logmanager(location)
    except Exception as e:
        pickle.dump([], open(f"{default_path}{location}/usr.logs", "wb"))
        return getLogs(location)

# returns keys portion of structure file, essentially the location data of each key.
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
        # the code below is commented out temporarily, it causes for imperformant searches, will be implemented again when a more efficient approach is found for searching queued write data.
        """writes_queue = os.listdir(config['write_folder'])
        if writes_queue != []:
            for write in writes_queue:
                try:
                    write_data = pickle.load(open(f"{config['write_folder']}{write}", "rb"))
                    # in this context, write_location is the location (specific database) that the write is assigned to.
                    write_location = write_data['location']
                    if write_location == location:
                        data = write_data["data"]
                        for key in data:
                            keyname = key
                            keyvalue = data[key]
                            if newdata in str(keyvalue):
                                if keyname not in templist:
                                    templist.append(keyname)
                            else:
                                if keyname in templist:
                                    templist.pop(templist.index(keyname))

                except FileNotFoundError:
                    pass # assumes that the write has been written since the search query was made"""
        return templist
    except Exception as e:
        log(location, e)
        return e

def searchNames(location, query, where=None):
    # "where" is where in the name will be searched. if where="end" then the db will search for keys ending with the query
    # if where="start" then the db will search for keys starting with the query     
    # if where=None then the db will search all keys where the keyname contains the query anywhere
    templist = []
    structured_query = str(query).lower()
    st = retrieveStructure(location)
    for key in st["keys"]:
        searchkey = str(key).lower()
        if where != None:
            if where == "end":
                if searchkey.endswith(structured_query):
                    templist.append(key)
            elif where == "start":
                if searchkey.startswith(structured_query):
                    templist.append(key)
            else:
                raise ValueError("Argument \"where\" must be \"end\" \"start\" or None")
        else:
            if structured_query in searchkey:
                templist.append(key)

    writes_queue = os.listdir(config['write_folder'])
    if writes_queue != []:
        for write in writes_queue:
            if write.endswith(f"{location}_ferris"):
                # {key}_{location}_ferris
                keydata = write.split(sep="_")
                keydata.pop(-1)
                keydata.pop(-1)
                keyname = "".join(keydata)

                if keyname not in st["keys"]:
                    searchkey = str(keyname).lower()
                    if where != None:
                        if where == "end":
                            if searchkey.endswith(structured_query):
                                templist.append(keyname)
                        elif where == "start":
                            if searchkey.startswith(structured_query):
                                templist.append(keyname)
                        else:
                            raise ValueError("Argument \"where\" must be \"end\" \"start\" or None")
                    else:
                        if structured_query in searchkey:
                            templist.append(keyname)
    return templist


def retrieveStructure(location):
    # gets the structure file, structure file is a file containing the partition in which each key exists.
    # the structure file also includes useful data like "writes" which is total writes to the database.
    try:
        st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
        return st
    except EOFError:
        log(location, "failed to retrieve structure, retrying")
        return retrieveStructure(location)

def getKey(location, keyname):
    try:
        current_writes = str(os.listdir(config["write_folder"]))
        if f"{keyname}_{location}_ferris" in current_writes:
            try:
                content = pickle.load(open(f"{config['write_folder']}{keyname}_{location}_ferris", "rb"))
                return content["data"][keyname]
            except FileNotFoundError:
                return getKey(location, keyname)
        st = retrieveStructure(location)
        partition = st["keys"][keyname]
        content = pickle.load(open(f"{default_path}{location}/usr_f{partition}.db", "rb"))[keyname]
    except KeyError:
        log(location, f"could not find key: {keyname}")
        content = "Key does not exist, DATABASE erroR"
    return content

def pushKey(location, key, value):
    # puts key in writes_folder to be made by ferris
    random_value = random.randint(100, 100000000000)
    pickle.dump({"data": {key: value}, "location": location}, open(f"{config['write_folder']}{key}_{location}_ferris{random_value}.tmp", "wb"))
    os.replace(f"{config['write_folder']}{key}_{location}_ferris{random_value}.tmp", f"{config['write_folder']}{key}_{location}_ferris")

def makeKey(location, keyname, keycontent):
    # check database size in mb
    try:
        files = os.listdir(f"{default_path}{location}")
        for file in files:
            file_stats = os.stat(f"{default_path}{location}/{file}.db")
            mbs = file_stats.st_size / (1000 * 1000)
    except Exception as e:
        mbs = 0
    # compare database size to size limit
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

    # uhhhhh, make key if it does not exist and update it if it does, in a safe way.
    try:
        st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
        partitions = st["system"]["partitions"]
        print(f"partitions begin: {partitions}")
        if keyname not in st["keys"]:
            file_stats = os.stat(f"{default_path}{location}/usr_f{partitions}.db")
            mbs = file_stats.st_size / (1000 * 1000)
            partition_size = float(config["partition_size"])
            if mbs > partition_size:
                partitions = st["system"]["partitions"] + 1 
                st["system"]["partitions"] = partitions
                st["keys"][keyname] = partitions - 1
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
        # this error message is to say that the database has been deleted, should not happen, hopefully.
        log(location, "If you're seeing this, something probably went very wrong (this database was set empty)")
    finally:
        try:
            structure_check = pickle.load(open(f"{default_path}{location}/usr_st.db","rb"))["keys"]
        except Exception as e:
            log(location, f"error checking DB structure when creating ({keyname}), retrying")
            time.sleep(0.1)
            return makeKey(location, keyname, keycontent)
        if keyname not in structure_check:
            structure_check = [pickle.load(open(f"{default_path}{location}/usr_st.db","rb"))["keys"]]
            encounters = 0
            while keyname not in structure_check[0]:
                structure_check[0] = pickle.load(open(f"{default_path}{location}/usr_st.db","rb"))["keys"]
                encounters += 1
                # sleep to give server time to catch up before remake 
                time.sleep(0.1)
                # retry if key does not exist, implying key was never properly made
                log(location, f"key ({keyname}) not found after creation, encounter: ({encounters}), (retrying)")
                attempt = remakeKey(location, keyname, keycontent)
                if attempt == "success":
                    log(location, f"key ({keyname}) resolved and successfully updated")
                    return "success"
        else:
            return "success"

def remakeKey(location, keyname, keycontent):
    # check database size in mb
    try:
        files = os.listdir(f"{default_path}{location}")
        for file in files:
            file_stats = os.stat(f"{default_path}{location}/{file}.db")
            mbs = file_stats.st_size / (1000 * 1000)
    except Exception as e:
        mbs = 0
    # compare database size to size limit
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

    # uhhhhh, make key if it does not exist and update it if it does, in a safe way.
    try:
        st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))
        partitions = st["system"]["partitions"]
        print(f"partitions begin: {partitions}")
        if keyname not in st["keys"]:
            file_stats = os.stat(f"{default_path}{location}/usr_f{partitions}.db")
            mbs = file_stats.st_size / (1000 * 1000)
            partition_size = float(config["partition_size"])
            if mbs > partition_size:
                partitions = st["system"]["partitions"] + 1 
                st["system"]["partitions"] = partitions
                st["keys"][keyname] = partitions - 1
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
        # this error message is to say that the database has been deleted, should not happen, hopefully.
        log(location, "If you're seeing this, something probably went very wrong (this database was set empty)")
    finally:
        try:
            structure_check = pickle.load(open(f"{default_path}{location}/usr_st.db","rb"))["keys"]
        except Exception as e:
            log(location, f"error checking DB structure when creating ({keyname}), retrying")
            time.sleep(0.1)
            return "STRUCTURE ERROR"
        if keyname not in structure_check:
            time.sleep(0.2)
            # retry if key does not exist, implying key was never properly made
            log(location, f"key ({keyname}) not found after creation, retrying")
            return "KEY NOT MADE"
        else:
            return "success"

def getKeys(location: str, keynames: list):
    tempdict = {}
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

# assume linux is used and use cp command to transfer files
def backupDB(location):
    try:
        os.listdir(f"{default_path}{location}_database_backup")
        deleteDB(f"{default_path}{location}_database_backup")
    except FileNotFoundError:
        os.mkdir(f"{default_path}{location}_database_backup")
    # assume linux
    os.system(f"cp -r {default_path}{location}/. {default_path}{location}_database_backup") 

# same sollution as backupDB, just reverse
def setToBackup(location):
    try:
        os.listdir(f"{default_path}{location}_database_backup")
    except FileNotFoundError:
        print("backup does not exist, good luck!")
        return "failed"
    deleteDB(location)
    os.system(f"cp -r {default_path}{location}_database_backup/. {default_path}{location}")

