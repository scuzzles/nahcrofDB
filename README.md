# Introduction
nahcrofDB is an open source, key-value database, designed to be simple, fast, and scalable, even in large datasets.

# Installation
In order to install nahcrofDB, just run 
```
git clone https://github.com/scuzzles/nahcrofDB.git
```
After installing, make sure that you have the required packages installed, the command for this is as follows.
```
pip install flask requests
```
Make sure to look through the config.txt file and update everything.
"admin_password" is the password to acces the UI.
"password_value" is the password used when accessing the database api.
# Using database
in order to interact with the database, use client.py on the server that will be accessing the database server.
If you are trying to directly interact with the database or create a new database you will use the cli on the server.
To create a new database, you wil run...
## Creating a database
```
python3 tools.py create_database DATABASE_NAME_HERE
```
for more commands use the "help" command, here is the output for the help command
```
Welcome to NahcrofDB
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
## Running the database
In order to run nahcrofDB you will run the following command.
```
python3 main.py
```
Please note that as of right now, nahcrofDB will only work in linux.
Running "main.py" will start both the HTTP handler and "ferris."
In short, ferris handles queued write requests.
# Using client.py
client.py is the python api wrapper for nahcrofDB.
To start, you will use the client.init function.
```python
import client
client.init("my_db_name", "url.com", "password_here")
```
## Making Keys
To make one key, you can do this.
```python
client.makeKey("my_key", "my value")
```
To make multiple keys at once (less database strain) you can use the following function.
```python
client.makeKeys({
    "key": "value",
    "key2": "value",
    "testkey": "testvalue"
})
```
## Getting Keys
To get one key, you can use getKey
```python
client.getKey("my_key")
```
OUTPUT:
```
my value
```
NOTE:
if you attempt to use getKey and the key does not exist, the response will be as follows
```
{'error': True, 'message': 'Key (MISSING KEY) does not exist.', 'status': 404}
```
To get multiple keys, you can use getKeys
```python
keys = client.getKeys(["key", "key2"])
```
OUTPUT:
```
{'key': 'value', 'key2': 'value'}
```
## Searching the database
To find keys containing specific data, you can use the .search function
```python
client.search("test")
```
OUTPUT:
```
['testkey']
```
## Incrementing values
In nahcrofDB, there is an incrementKey function. This allows you to increment a key, or a specific value within a key whilst only making one request to the database.
Here is a simple example.
```python
client.makeKey("num", 5)
client.incrementKey(10, "num")
print(client.getKey("num"))
```
OUTPUT:
```
15
```
In this basic example, the key "num" was created and then incremented by 10. Here is a more complex example.
```python
client.makeKey("nums", {
    "inner_values": [10, 23, 42, 8],
    "type": "int",
})
client.incrementKey(2, "nums", "inner_values", 3)
print(client.getKey("nums"))
```
OUTPUT
```
{
    "inner_values": [10, 23, 42, 10],
    "type": "int",
}
```
This change is because nahcrofDB was told to increment a value by 2, the value was in the path nums["inner_values"][3] which was the 4th value in "inner_values", or 8.
# HTTP Docs
## getting a key-value
### GET /v2/key/:key/:database_folder
HEADERS:
```
X-API-Key: api-token-here
```
RESPONSE 200 OK
```json
{
    "error": false,
    "message": null,
    "status": 200,
    "value": "value here"
}
```
## getting multiple key-values
### GET /v2/keys/:database_folder
QUERY PARAMS
```
?key[]=key1&key[]=key2&key[]=key3
```
HEADERS:
```
X-API-Key: api-token-here
```
RESPONSE 200 OK
```json
{
    "key1": "val1"
    "key2": "val2"
    "key3": "val3"
    ...
}
```
## Making key values
### POST /v2/keys/:database_folder
BODY (application/json)
```json
{
    "key": "val1"
    "key2": "val2"
    ...
}
```
RESPONSE 204 NO CONTENT
## Searching your database
### GET /v2/search/:database_folder
QUERY PARAMS
```
?query=Hello%20World
```
HEADERS:
```
X-API-Key: api-token-here
```
RESPONSE 200 OK
```json
[
    "key1",
    "key2",
    ...
]
```
## Incrementing key values
### POST /v2/increment/:database_folder/:path
BODY (application/json)
```json
{
    "amount": 1
}
```
RESPONSE 204 NO CONTENT<br>
example request url: /v2/increment/example_db/nums_list/num1
