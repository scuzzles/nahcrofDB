
# ferris is a write maker, the purpose of this program is to constantly check a folder for new write requests as a form of load balancing
import os
import pickle
import nahcrofDB
import time
from read_config import config
write_location = config["write_folder"]

def local_log(message):
    print(message)

try:
    os.listdir(write_location)
except FileNotFoundError:
    os.mkdir(write_location)
    print("made writes folder")

print("ferris started.")
def main():
    writes = os.listdir(write_location)
    if writes == []:
        pass
    else:
        for write in writes:
            if write.endswith("_ferris"):
                try:             
                    write_data = pickle.load(open(f"{write_location}{write}", "rb"))
                    location = write_data["location"] 
                    print(f"location: {location}")
                    for key in write_data["data"]:
                        print(key)
                        print(write_data["data"][key])
                        nahcrofDB.makeKey(location, key, write_data["data"][key])
                    os.remove(f"{write_location}{write}")
                except Exception as e:
                    print(f"ERROR: {e}")
                    time.sleep(0.1)

while True:
    try:
        main()
    except Exception as e:
        print("MAIN Ferris error, waiting 2 seconds")
        time.sleep(2)

