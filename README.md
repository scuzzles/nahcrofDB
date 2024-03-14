# Introduction 
nahcrofDB is a simple python key-value database designed to make creating and using a database as simple as possible. This GitHub page does not contain instructions on how to setup a database with the website or using languages other than python but you can find that at [database.nahcrof.com/docs](https://database.nahcrof.com/docs)
# Basic Docs
To begin using nahcrofDB, if you are using python then you will need to run the following command:
```
pip install nahcrofDB requests
```
## setting up your project
to add and test your database to project, you will need to paste the following.
```python 
import nahcrofDB
nahcrofDB.init("YOUR_API_KEY_HERE", "YOUR_USERNAME_HERE")
nahcrofDB.makeKey("test", "test value")
print(nahcrofDB.getKey("test"))
```
if set up correctly, you should print "test value" to the console. If you need an api key, visit the [/dashboard](https://database.nahcrof.com/dashboard) page and click "Create Token"
## Resetting the database

after setting up your database and testing some things, you might not want to have the testing keys in your database anymore.
To reset the entire database, do the following.

in your previously set up file, use this function
```python
nahcrofDB.resetDB()
```
this will reset your entire database. Please note that you should NEVER use this under any circumstances in which you have any important information, this is only for when your database is in a testing phase or does not contain any useful information.

## Extra functions

### Get Keys:
if you want to get multiple keys with one request for any reason, you can do that using the "getKeys" function, here is an example.   
```python
nahcrofDB.getKeys("key1", "key2", "key3")
```
This would return the values of key1, key2, and key3 in a dict. To get key2 out of this list would look something like this.
```python
example = nahcrofDB.getKeys("key1", "key2", "key3")
print(example["key2"])
```

### Deleting Keys
to delete a key from your database you will use the "delKey" function.
```python
nahcrofDB.delKey("keyname")
```
