# Introduction
nahcrofDB is an open source key-value database designed to be simple, fast, and scalable.

# Installation
In order to install nahcrofDB, just run 
```
git clone https://github.com/scuzzles/nahcrofDB.git
```
Running the database is also fairly simple, you will need to have two simultaneous terminals--or whatever your method of running python programs--and run both "main.py" and "ferris.py"
Make sure to look through the config.txt file and update everything.
# Using database
in order to interact with the database, use client.py on the server that will be accessing the database server.
If you are trying to directly interact with the database or create a new database you will use the cli on the server.
To create a new database, you wil run...
```
python3 tools.py create_database DATABASE_NAME_HERE
```
for more commands use the "help" command, here is the output for the help command
```
HINT: location is in reference to the folder the database is in.
reset <location> - resets database for specified location (ONLY USE IF COMPLETELY NECESSARY)
check - check the health of all databases and what keynames they have
structure <location> - view structure file of given location
file1 <location> - view first db file of given location
logs <location> - view log file of given location
fix_structure <location> - attempts to repair a corrupted structure file
view <location> - view database data
queue - view how many write requests are in the queue
folder <location> - view database folder for individual database
backup <location> - create a backup of an existing database
check_backup <location> - compare a database to it's corresponding backup
set_to_backup <location> - set the database to a pre-existing backup
create_database <folder_name> - creates empty database within specified folder
```
# Using client.py
client.py is the python api wrapper for nahcrofDB.
To start, you will use the nahcrofDB.init function.
```python
nahcrofDB.init("my_db_name", "url.com", "password_here")
```
## Making Keys
To make one key, you can do this.
```python
nahcrofDB.makeKey("my_key", "my value")
```
To make multiple keys at once (less database strain) you can use the following function.
```python
nahcrofDB.makeKeys({
    "key": "value",
    "key2": "value",
    "testkey": "testvalue"
})
```
## Getting Keys
To get one key, you can use getKey
```python
nahcrofDB.getKey("my_key")
```
OUTPUT:
```
my value
```
To get multiple keys, you can use getKeys
```python
keys = nahcrofDB.getKeys(["key", "key2"])
```
OUTPUT:
```
{'key': 'value', 'key2': 'value'}
```
## Searching the database
To find keys containing specific data, you can use the .search function
```python
nahcrofDB.search("test")
```
OUTPUT:
```
['testkey']
```
# HTTP Docs
this section is a work in progress (sorry). We plan to have this finished within a month (for reference, that's 11/11 since I'm writing this on 10/11).