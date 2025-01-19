import time
import nahcrofDB
import client
import sys
from read_config import config

def console_color(text, color):
    templist = []
    if color == "red":
        templist.append("\033[31m")
    if color == "green":
        templist.append("\033[92m")
    if color == "cyan":
        templist.append("\033[36m")
    if color == "yellow":
        templist.append("\033[33m")
    if color == "purple":
        templist.append("\033[35m")
    templist.append(text)
    templist.append("\033[0m")
    print("".join(templist))

commands = {
    "--help": "Displays this command",
    "--makekey": "Tests making a single key and how long it takes.",
    "--makekeys <amount>": "Tests making \"amount\" keys and displays how long it took",
    "--search <query>": "Tests time to complete generic search query",
    "--searchnames <query> <where>": "Tests time to complete search of key-names, if you're unsure on \"where\" there is further explanation in the github README. set to \"none\" for anywhere",
    "--getkey <keyname>": "Returns the value of a specific keyname, and the time it took to retreive",
}

if __name__ == "__main__":
    args = sys.argv
    args.pop(0)
    database: str = args[0]
    try:
        if database.startswith("--"):
            if database == "--help":
                console_color("Welcome to nahcrofDB testing console", "cyan")
                for command in commands:
                    print(f"{command} - {commands[command]}")
                sys.exit(0)
            else:
                console_color("must input valid database", "red")
        args.pop(0)
    except IndexError:
        raise ValueError("Missing argument, please include desired database or run \"tests.py --help\"")

    client.init(database, f"http://0.0.0.0:{config['port']}/", config["password_value"])
    for arg in args:
        if arg == "--help":
            console_color("Welcome to nahcrofDB testing console", "cyan")
            for command in commands:
                print(f"{command} - {commands[command]}")
            sys.exit(0)
        if arg == "--makekey":
            start = time.time()
            client.makeKey("testkey", "test value")
            end = time.time()
            finaltime = end-start
            print(f"--makekey time: {finaltime}")
            args.pop(0)

        if arg == "--makekeys":
            start = time.time()
            amount = args[1]
            makekeysdata = client.makekeys_test(int(amount))
            end = time.time()
            finaltime = end-start
            print(f"--makekeys ({amount})")
            print(f"time: {makekeysdata['time']}s")
            print(f"speed: {makekeysdata['speed']}/s")
            print(f"keys queued: {makekeysdata['keys made']}")
            args.pop(0)
            args.pop(0)

        if arg == "--search":
            start = time.time()
            query = args[1]
            query_result = client.search(query)
            end = time.time()
            finaltime = end-start
            print(f"--search ({query}) time: {finaltime}")
            print(f"--search ({query}) relatedkeys: {len(query_result)}")
            args.pop(0)
            args.pop(0)

        if arg == "--searchnames":
            start = time.time()
            query = args[1]
            where = args[2]
            if where == "none":
                where = None
            results = client.searchNames(query, where=where)
            end = time.time()
            finaltime = end-start
            print(f"--searchnames ({query}, {where}) time: {finaltime}")
            print(f"--searchnames ({query}, {where}) values returned: {len(results)}")
            args.pop(0)
            args.pop(0)
            args.pop(0)

        if arg == "--getkey":
            start = time.time()
            key = args[1]
            returned_data = client.getKey(key)
            end = time.time()
            finaltime = end-start
            print(f"--getkey ({key}) time: {finaltime}")
            print(f"--getkey ({key}) value returned: {returned_data}")
            args.pop(0)
            args.pop(0)
