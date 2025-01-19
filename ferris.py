# ferris is a write maker, the purpose of this program is to constantly check a folder for new write requests as a form of load balancing
import os
import pickle
import mmap # if it's not used yet, it will be implemented later
import nahcrofDB
import time
from read_config import config
write_location = config["write_folder"]
memory_queue_size_limit = config["memory_queue_size_limit"]

def in_memory_queue(queue: dict) -> None:
    try:
        os.listdir(write_location) # to make sure there is a writes_folder to be opened and checked, in the event that queue method is changed
    except FileNotFoundError:
        os.mkdir(write_location)
        print("made writes folder")
    while True:
        if len(queue) > int(memory_queue_size_limit):
            write_values = {}
            writes_list = list(queue.keys())
            for write in range(int(memory_queue_size_limit)):
                write = writes_list[write]
                try:             
                    write_data = queue[write]
                    location = write_data["location"] 
                    if location in write_values:
                        for key in write_data["data"]:
                            write_values[location][key] = write_data["data"][key]
                    else:
                        write_values[location] = {}
                        for key in write_data["data"]:
                            write_values[location][key] = write_data["data"][key]
                    del queue[write]
                except Exception as e:
                    print(f"ERROR: {e}")
                    time.sleep(0.1)
            for location in write_values:
                nahcrofDB.makeKeys(location, write_values[location])


print("ferris started.")
def file_queue():
    try:
        writes = os.listdir(write_location)
    except FileNotFoundError:
        os.mkdir(write_location)
        print("made writes folder")
    if writes == []:
        pass
    else:
        # convert writes_list into dict to use for nahcrofDB.makeKeys
        write_values = {}
        for write in writes:
            if write.endswith("_ferris"):
                # view every file in writes folder, make each one
                try:             
                    write_data = pickle.load(open(f"{write_location}{write}", "rb"))
                    location = write_data["location"] 
                    if location in write_values:
                        print(f"location: {location}")
                        for key in write_data["data"]:
                            print(key)
                            print(write_data["data"][key])
                            write_values[location][key] = write_data["data"][key]
                    else:
                        write_values[location] = {}
                        print(f"location: {location}")
                        for key in write_data["data"]:
                            print(key)
                            print(write_data["data"][key])
                            write_values[location][key] = write_data["data"][key]
                    os.remove(f"{write_location}{write}")
                except Exception as e:
                    print(f"ERROR: {e}")
                    time.sleep(0.1)
        for location in write_values:
            nahcrofDB.makeKeys(location, write_values[location])

if __name__ == "__main__":
    while True:
        try:
            file_queue()
        except Exception as e:
            print("MAIN Ferris error, waiting 2 seconds")
            time.sleep(2)

