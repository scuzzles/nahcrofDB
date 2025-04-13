import sys
import filecmp
import time
import json
import mmap
import os, shutil
import pickle
import random
from tools import console_color
from read_config import config
utf = "utf-8"
# file_stats.st_size / (1024 * 1024)
default_path = config["default_path"]
st_type = ["file"]
structure_data = {} 

def build_st() -> None:
    st_type[0] = "memory"
    build_start = time.time()
    console_color("building structures...", "yellow")
    all_databases = os.listdir(default_path)
    for location in all_databases:
        structure_data[location] = {}
        with open(f"{default_path}{location}/st.db") as db_st:
            for line in db_st:
                line_json = json.loads(line)
                keyname = list(line_json.keys())[0]
                key_location = line_json[keyname]
                if key_location != 0:
                    structure_data[location][keyname] = key_location 
                if key_location == 0:
                    if keyname in structure_data[location]:
                        del structure_data[location][keyname]
    build_end = time.time()
    build_time = build_end-build_start
    console_color(f"structures built! Took ({build_time})s", "purple")
    structures_memory_space = sys.getsizeof(structure_data)
    console_color(f"Memory taken by structures: {structures_memory_space}", "cyan") 

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
    return "getWrites function is deprecated"

def getReads(location):
    return "getReads function is deprecated"

def search(location, data):
    newdata = str(data).lower()
    dict_alt = {} # gonna be honest, copied code from searchwithqueue, to lazy to fix
    try:
        tempdict = {}
        partitions = pickle.load(open(f"{default_path}{location}/partitions.db"))
        existing = {}
        with open(f"{default_path}{location}/st.db") as st:
            for line in st:
                json_data = json.loads(line)
                key = list(json_data.keys())[0]
                existing[key] = json_data[key]
        for partition in range(partitions):
            partition = int(partition) + 1
            tempdict[str(partition)] = pickle.load(open(f"{default_path}{location}/usr_f{partition}.db", "rb"))
        for item in existing:
                try:
                    checking = str(tempdict[str(existing[item])])  
                    if newdata in checking:
                        dict_alt[item] = ""
                except KeyError as e:
                    log(location, f"SEARCH ERROR: trouble when checking values in ({item}) key: {key}")
        
        return list(dict_alt.keys())
    except Exception as e:
        log(location, e)
        return e


def find_key_from_structure(location, key: str):
    if st_type[0] == "memory":
        try:
            structure_data[location]
        except KeyError:
            build_st()
        try:
            return structure_data[location][key]
        except KeyError:
            raise KeyError("Could not find key within structure")
    else:
        found = [0]
        with open(f"{default_path}{location}/st.db") as st:
            for line in st:
                
                if line.startswith("{" + f'"{key}"'):
                    json_value = json.loads(line)
                    found[0] = json_value[key]
        if found[0] == 0:
            raise KeyError("Could not find key within structure")
        else:
            return found[0]

def find_keys_from_structure(location, keys: dict) -> dict:
    find_start = time.time()
    tempdict = {}
    if st_type[0] == "memory":
        print("using memory st")
        try:
            structure_data[location]
        except KeyError:
            build_st()
        for key in keys:

            try:
                tempdict[key] = structure_data[location][key]
            except KeyError:
                pass
    else:
        with open(f"{default_path}{location}/st.db") as st:
            for line in st:
                line_json = json.loads(line)
                line_keyname = list(line_json.keys())[0]
                if line_keyname in keys:
                    if line_keyname in tempdict:
                        if line_json[line_keyname] == 0:
                            del tempdict[line_keyname]
                    else:
                        tempdict[line_keyname] = line_json[line_keyname]
    return tempdict

def searchwithqueue(location, data, queue):
    newdata = str(data).lower()
    dict_alt = {} # replaces templist, ~150x faster than searching list
    for item in queue:
        if newdata in str(queue).lower():
            dict_alt[item] = ""

    try:
        tempdict = {}
        partitions = pickle.load(open(f"{default_path}{location}/partitions.db", "rb"))
        existing = {}
        if st_type[0] == "memory":
            print("MEMORY")
            for x in structure_data[location]:
                existing[x] = structure_data[location][x]
            print("memory done")
        if st_type[0] == "file":
            with open(f"{default_path}{location}/st.db") as st:
                for line in st:
                    try:
                        json_data = json.loads(line)
                        key = list(json_data.keys())[0]
                        existing[key] = json_data[key]
                    except Exception as e:
                        log(location, f"JSON ERROR: {e}")
        print("PARTITIONS")
        for partition in range(partitions):
            partition = int(partition) + 1
            tempdict[str(partition)] = pickle.load(open(f"{default_path}{location}/usr_f{partition}.db", "rb"))
        print("partitions done")
        print("SEARCH")
        for item in existing:
            if item not in dict_alt:
                try:
                    checking = str(tempdict[str(existing[item])])  
                    if newdata in checking:
                        dict_alt[item] = ""
                except KeyError as e:
                    log(location, f"SEARCH ERROR: trouble when checking values in ({item}) key: {key}")
        print("search done")
        
        return list(dict_alt.keys())
    except Exception as e:
        log(location, e)
        return e



def searchNames(location, query, where=None):
    # "where" is where in the name will be searched. if where="end" then the db will search for keys ending with the query
    # if where="start" then the db will search for keys starting with the query     
    # if where=None then the db will search all keys where the keyname contains the query anywhere
    templist = []
    structured_query = str(query).lower()
    with open(f"{default_path}{location}/st.db") as st:
        for line in st:
            linejson = json.loads(line)
            key = list(linejson.keys())[0]
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
    
    return templist

def searchNameswithqueue(location, query, where=None, queue=None):
    # "where" is where in the name will be searched. if where="end" then the db will search for keys ending with the query
    # if where="start" then the db will search for keys starting with the query     
    # if where=None then the db will search all keys where the keyname contains the query anywhere
    tempdict = {} # dictionary used because it is ~150x faster than a list
    if st_type[0] == "memory":
        try:
            structure_data[location]
        except KeyError:
            build_st()
    structured_query = str(query).lower()
    if st_type[0] == "memory":
        if where == "start":
            tempdict = {k: "" for k in structure_data[location] if str(k).lower().startswith(structured_query)}
        if where == "end":
            tempdict = {k: "" for k in structure_data[location] if str(k).lower().endswith(structured_query)}
            print(location)
        if where == None:
            tempdict = {k: "" for k in structure_data[location] if structured_query in str(k).lower()}
    if queue:
        for key in queue:
            if queue[key]["location"] == location:
                if key not in tempdict:
                    searchkey = str(key).lower()
                    if where != None:
                        if where == "end":
                            if searchkey.endswith(structured_query):
                                tempdict[key] = ""
                        elif where == "start":
                            if searchkey.startswith(structured_query):
                                tempdict[key] = ""
                        else:
                            raise ValueError("Argument \"where\" must be \"end\" \"start\" or None")
                    else:
                        if structured_query in searchkey:
                            tempdict[key] = ""

    if st_type[0] == "file":
        with open(f"{default_path}{location}/st.db") as st:
            for line in st:
                linejson = json.loads(line)
                key = list(linejson.keys())[0]
                if key not in tempdict:
                    searchkey = str(key).lower()
                    if where != None:
                        if where == "end":
                            if searchkey.endswith(structured_query):
                                tempdict[key] = ""
                        elif where == "start":
                            if searchkey.startswith(structured_query):
                                tempdict[key] = ""
                        else:
                            raise ValueError("Argument \"where\" must be \"end\" \"start\" or None")
                    else:
                        if structured_query in searchkey:
                            tempdict[key] = ""
    final = list(tempdict.keys())
    return final

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
        st_data = find_key_from_structure(location, keyname)
        partition = st_data
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

def makeKeys(location, keyvalues):
    if st_type[0] == "memory":
        try:
            structure_data[location]
        except KeyError:
            build_st()
    st_file = open(f"{default_path}{location}/st.db", "a")
    # check database size in mb
    tempnumber = random.randint(0, 10000000000) # prevents one tempfile from being used multiple times (ideally)
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
        pass

    try:
        found = find_keys_from_structure(location, keyvalues)
        partitions = pickle.load(open(f"{default_path}{location}/partitions.db", "rb"))
        file_stats = os.stat(f"{default_path}{location}/usr_f{partitions}.db")
        mbs = file_stats.st_size / (1000 * 1000)
        partition_size = float(config["partition_size"])
        updated_partitions = {} # data of partitions that will be updated
        smaller_partition_size = partition_size * 0.75
        if mbs > smaller_partition_size: # accounts for the amount of keys being causing partition to go over 1, makes new partition early.
            partitions = partitions + 1 
            pickle.dump({}, open(f"{default_path}{location}/usr_f{partitions}.db", "wb"))
            pickle.dump(partitions, open(f"{default_path}{location}/partitions.db", "wb"))
        for key in keyvalues:
            keycontent = keyvalues[key]
            if key not in found:
                keyjson = {key: partitions}
                st_file.write(json.dumps(keyjson) + "\n")
                if st_type[0] == "memory":
                    structure_data[location][key] = partitions
                if partitions in updated_partitions:
                    updated_partitions[partitions][key] = keycontent
                else: 
                    thispartition = pickle.load(open(f"{default_path}{location}/usr_f{partitions}.db", "rb"))
                    updated_partitions[partitions] = thispartition 
                    updated_partitions[partitions][key] = keycontent

            else:
                correctpartition = found[key]
                if correctpartition in updated_partitions:
                    updated_partitions[correctpartition][key] = keycontent
                else: 
                    thispartition = pickle.load(open(f"{default_path}{location}/usr_f{correctpartition}.db", "rb"))
                    updated_partitions[correctpartition] = dict(thispartition) 
                    updated_partitions[correctpartition][key] = keycontent
                

        for partition in updated_partitions:
            pickle.dump(updated_partitions[partition], open(f"{default_path}{location}/usr_f{partition}.tmp", "wb"))
            os.replace(f"{default_path}{location}/usr_f{partition}.tmp", f"{default_path}{location}/usr_f{partition}.db")
    except Exception as e:
        emptyDB(location)
        # this will create a new database, this looks scary but it will error if the dir exists, only sets db empty if db doesn't exist
        log(location, "If you're seeing this, something probably went very wrong (this database was set empty)")
    finally:
        st_file.close()
        return "success"

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
        try:
            key_location = find_key_from_structure(keyname) # key-value partition
        except KeyError:
            key_location = False
        partitions = pickle.load(open(f"{default_path}{location}/partitions.db", "rb"))
        print(f"partitions begin: {partitions}")
        if not key_location:
            file_stats = os.stat(f"{default_path}{location}/usr_f{partitions}.db")
            mbs = file_stats.st_size / (1000 * 1000)
            partition_size = float(config["partition_size"])
            if mbs > partition_size:
                partitions = partitions + 1 
                pickle.dump(partitions, open(f"{default_path}{location}/partitions.db", "wb"))

                st = open(f"{default_path}{location}/st.db", "a")
                stdata = {keyname: partitions}
                st.write(json.dumps(stdata) + "\n")
                if st_type[0] == "memory":
                    structure_data[location][key] = partitions
                st.close()

                pickle.dump({}, open(f"{default_path}{location}/usr_f{partitions}.db", "wb"))
            else:
                
                st = open(f"{default_path}{location}/st.db", "a")
                stdata = {keyname: partitions}
                st.write(json.dumps(stdata) + "\n")
                if st_type[0] == "memory":
                    structure_data[location][key] = partitions
                st.close()

            db = pickle.load(open(f"{default_path}{location}/usr_f{partitions}.db", "rb"))
            db[keyname] = keycontent
            pickle.dump(db, open(f"{default_path}{location}/usr_f{partitions}.tmp", "wb"))
            os.replace(f"{default_path}{location}/usr_f{partitions}.tmp", f"{default_path}{location}/usr_f{partitions}.db")

        else:
            correctpartition = key_location
            partitions = pickle.load(open(f"{default_path}{location}/partitions.db", "rb"))
            db = pickle.load(open(f"{default_path}{location}/usr_f{correctpartition}.db", "rb"))
            db[keyname] = keycontent
            pickle.dump(db, open(f"{default_path}{location}/usr_f{correctpartition}.tmp", "wb"))
            os.replace(f"{default_path}{location}/usr_f{correctpartition}.tmp", f"{default_path}{location}/usr_f{correctpartition}.db")
    except Exception as e:
        emptyDB(location)
        makeKey(location, keyname, keycontent)
        # this error message is to say that the database has been deleted, should not happen, hopefully.
        log(location, "If you're seeing this, something probably went very wrong (this database was set empty)")
        return "initial write failed"
    finally:
        return "success"

def getKeys(location: str, keynames: list):
    found = find_keys_from_structure(location, keynames)
    tempdict = {}
    loaded_partitions = {}
    try:
        for key in keynames:
            try:
                partition = found[key]
                if partition not in loaded_partitions:
                    loaded_partitions[partition] = pickle.load(open(f"{default_path}{location}/usr_f{partition}.db", "rb"))
                key_value = loaded_partitions[partition][key]
                tempdict[key] = key_value
            except KeyError:
                tempdict[key] = "Key does not exist, DATABASE erroR"
    except EOFError:
        log(location, "encountered EOF error, retrying")
        print("encountered EOF error, retrying")
        return getKeys(location, keynames)
    return tempdict


def delKey(location, keyname):

    if st_type[0] == "memory":
        try:
            structure_data[location]
        except KeyError:
            build_st()
        del structure_data[location][keyname]
    st = open(f"{default_path}{location}/st.db", "a")
    json_data = {keyname: 0}
    st.write(json.dumps(json_data) + "\n")
    st.close()
    

def keysamount(location):
    tempdict = {}
    if st_type[0] == "memory":
        try:
            structure_data[location]
        except KeyError:
            build_st()
        amount = len(structure_data[location])
    if st_type[0] == "file":
        with open(f"{default_path}{location}/st.db") as st:
            for line in st:
                data = json.loads(line)
                key = list(data.keys())[0]
                value = data[key]
                if key not in tempdict:
                    if value != 0:
                        tempdict[key] = value
                if key in tempdict:
                    if value == 0:
                        del tempdict[key]
        amount = len(list(tempdict.keys()))
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

def structuresize(location):
    try:
        file_stats = os.stat(f"{default_path}{location}/st.db")
        mbs = file_stats.st_size / (1000 * 1000)
        return mbs
    except Exception as e:
        print(e)
        return f"ERROR: {e}"

def emptyDB(location):
    os.mkdir(f"{default_path}{location}")
    db = {}
    st = {"keys": {}, "system": {"partitions": 1, "writes": 0, "reads": 0}}
    pickle.dump(db, open(f"{default_path}{location}/usr_f1.db", "wb"))
    pickle.dump(1, open(f"{default_path}{location}/partitions.db", "wb"))
    open(f"{default_path}{location}/st.db", "w").close()

def deleteDB(location):
    if st_type[0] == "memory":
        try:
            del structure_data[location]
        except KeyError:
            pass
    os.system(f"rm -r {default_path}{location}")

def convert_old_st(location):
    #try:
        open(f"{default_path}{location}/st.db", "w")
        st_file = open(f"{default_path}{location}/st.db", "a")
        old_st = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))["keys"]
        partitions = pickle.load(open(f"{default_path}{location}/usr_st.db", "rb"))["system"]["partitions"]
        pickle.dump(partitions, open(f"{default_path}{location}/partitions.db", "wb"))
        for key in old_st:
            value = old_st[key]
            json_data = {key: value}
            st_file.write(json.dumps(json_data) + "\n")
        st_file.close()
    #except Exception as e:
    #    print("Could not convert st file")
    #    print(f"error: {e}")


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
