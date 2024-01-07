# Introduction 
nahcrofDB is a key-value database designed to be extremely simple to get running and to use. Please note that at this current time there is no way to host the database, this simply interacts with an existing file

## setup
to setup nahcrofDB you will need to install the "nahcrofDB.py" file. Once this file is installed make sure it is in the same directory as your project. Finally you will need to run the following command to create your database. 

Windows:
```
nahcrofDB.py createDB
```

Linux:
```
python3 nahcrofDB.py createDB
```

# Using nahcrofDB
using nahcrofDB is quite simple and currently only has 2 functions

## creating a key
here is an example of how to create a key with nahcrofDB
```
nahcrofDB.makeKey("keyname", "example key data")
```
your key data can contain any types at all and unless stored incorrectly should not return an error

## getting a key
here is an example of how to get a key with nahcrofDB
```
nahcrofDB.getKey("keyname")
```
RETURNS:
```
example key data
```
if the key requested does not exist the database will simply return "key not found"
