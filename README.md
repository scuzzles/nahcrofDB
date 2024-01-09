# Introduction 
nahcrofDB is a simple python key-value database designed to make creating and using a database as simple as possible. This GitHub page does not contain instructions on how to setup a database with the website and api but you can find that at [database.nahcrof.com/docs](https://database.nahcrof.com/docs)

## setup
to setup a local database you will need to install the "localDB.py" file. Once this file is installed make sure it is in the same directory as your project. Finally you will need to run the following command to create your database. 

Windows:
```
localDB.py createDB
```

Linux:
```
python3 localDB.py createDB
```

# Using localDB 
using a localDB is quite simple and currently only has 2 functions

## creating a key
here is an example of how to create a key with the localDB 
```
localDB.makeKey("keyname", "example key data")
```
your key data can contain any types at all and unless stored incorrectly should not return an error

## getting a key
here is an example of how to get a key with a localDB 
```
localDB.getKey("keyname")
```
RETURNS:
```
example key data
```
if the key requested does not exist the database will simply return "key not found"
