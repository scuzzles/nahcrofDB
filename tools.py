import sys
import os
import nahcrofDB
import pickle
from read_config import config
default_path = config["default_path"]
if __name__ == '__main__':
    args = sys.argv[1:]
    if args:

        if args[0] == "help":
            print("HINT: location is in reference to the folder the database is in.")
            print("reset <location> - resets database for specified location (ONLY USE IF COMPLETELY NECESSARY)")
            print("check - check the health of all databases and what keynames they have")
            print("structure <location> - view structure file of given location")
            print("file1 <location> - view first db file of given location")
            print("logs <location> - view log file of given location")
            print("fix_structure <location> - attempts to repair a corrupted structure file")
            print("view <location> - view database data")
            print("queue - view how many write requests are in the queue")
            print("folder <location> - view database folder for individual database")
            print("backup <location> - create a backup of an existing database")
            print("check_backup <location> - compare a database to it's corresponding backup")
            print("set_to_backup <location> - set the database to a pre-existing backup")
            print("create_database <folder_name> - creates empty database within specified folder")

        if args[0] == "reset":
            # VERY SCARY
            user = args[1]
            print("")
            print(f"this will reset the {user} database.") 
            print("are you sure you would like to do this")
            print("")
            danger = input("(y/n)")
            if danger == "y":
                nahcrofDB.deleteDB(user)
                nahcrofDB.emptyDB(user)
                print("deleted")
            elif danger == "n":
                print("canceled deletion")
            else:
                print("invalid input, deletion canceled")

        if args[0] == "check":
            accounts = os.listdir(default_path)
            for user in accounts:
                print(user)
                print(nahcrofDB.search(user, ""))
                print("")
                print("")

        if args[0] == "structure":
            user = args[1]
            data = pickle.load(open(f"{default_path}{user}/usr_st.db", "rb"))
            print(data)

        if args[0] == "file1":
            user = args[1]
            data = pickle.load(open(f"{default_path}{user}/usr_f1.db", "rb"))
            print(data)

        if args[0] == "logs":
            user = args[1]
            data = pickle.load(open(f"{default_path}{user}/usr.logs", "rb"))
            # print(data)
            for x in data:
                print(x)

        if args[0] == "view":
            user = args[1]
            reads = nahcrofDB.getReads(user)
            writes = nahcrofDB.getWrites(user)
            print(f"reads: {reads}")
            print(f"writes: {writes}")
            print(f"database data: {account}")
            print(f"database size: {nahcrofDB.sizeofDB(user)}")


        if args[0] == "fix_structure": 
            user = args[1]
            print("this will (essentially) rewrite every key in the database, are you sure?")
            choice = input("(y/n)")
            if choice == "y":
                data = {"keys": {}, "system": {"partitions": 1, "writes": 0, "reads": 0}}
                loaded = pickle.load(open(f"{default_path}{user}/usr_f1.db", "rb"))
                for key in loaded:
                    data["keys"][key] = 1
                pickle.dump(data, open(f"{default_path}{user}/usr_st.db", "wb"))
                print("done")
            else:
                print("restructure canceled")
                print("")
                print("for more information, contact nahcrof support. You can find this at nahcrof.com")


        if args[0] == "size":
            user = args[1]
            size = nahcrofDB.sizeofDB(user)
            print(f"size: {size}")

        
        if args[0] == "queue":
            print(len(os.listdir(config["write_folder"])))

        if args[0] == "folder":
            user = args[1]
            user_folder = os.listdir(f"{default_path}{user}")
            for file in user_folder:
                print(file)

        if args[0] == "backup":
            user = args[1]
            nahcrofDB.backupDB(user)

        if args[0] == "check_backup":
            user = args[1]
            backup_loc = f"{user}_database_backup"
            keys1 = nahcrofDB.search(user, "")
            keys2 = nahcrofDB.search(backup_loc, "")
            data1 = nahcrofDB.getKeys(user, keys1)
            data2 = nahcrofDB.getKeys(backup_loc, keys2)
            print("mainDB")
            print(nahcrofDB.search(user, ""))
            print("backupDB")
            print(nahcrofDB.search(backup_loc, ""))
            print("")
            if data1 == data2:
                print("database MATCHES the backup")
            else:
                print("datasets DO NOT match")

        if args[0] == "set_to_backup":
            user = args[1]
            print("this will set the current database to a backup, are you sure you would like to do this?")
            choice = input("(y/n)")
            if choice == "y":
                nahcrofDB.setToBackup(user)
            else:
                print("backup canceled")

        if args[0] == "create_database":
            try:
                db_name = args[1]
                nahcrofDB.emptyDB(db_name)
                print("database created!")
            except FileNotFoundError:
                os.mkdir(default_path)
                db_name = args[1]
                nahcrofDB.emptyDB(db_name)
                print("database created!")
                

    else:
        print("you have to run a command, silly")
