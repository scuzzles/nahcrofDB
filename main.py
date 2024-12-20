import nahcrofDB
from flask import Flask, request, jsonify, render_template, url_for, redirect, session
import pickle
import os
import read_config
import threading
mainpass = read_config.config["password_value"]
admin_password = read_config.config["admin_password"]
# TODO, make visual UI with admin password

write_location = ["ferris"]

# this function is ran at the end of a file in a seperate thread. Allows both ferris and main.py to run within one file
def run_ferris():
    os.system("python3 ferris.py")

app = Flask(__name__)
app.config["SECRET_KEY"] = "verysecret"

@app.route("/status")
def status():
    return "alive"

# this page reverts the database to it's most recent backup, primarily handled at nahcrofDB.setToBackup
@app.route("/to_backup/<database>")
def revert_db(database):
    if "password" in session:
        if session["password"] == admin_password:
            nahcrofDB.setToBackup(database)
            keys = nahcrofDB.keysamount(database)
            size = nahcrofDB.sizeofDB(database)
            writes = nahcrofDB.getWrites(database)
            reads = nahcrofDB.getReads(database)
            logs = nahcrofDB.getLogs(database)
            return render_template("view_database.html", keys=keys, dbsize=size, writes=writes, reads=reads, logs=logs, database=database, message="database reverted")
        else:
            return "no cheating"
    else:
        return redirect("/")

# create an empty database from a form
@app.route("/create_database", methods=["POST", "GET"])
def UI_create_database():
    if request.method == "POST":
        db_name = request.form["database_name"]
        nahcrofDB.emptyDB(db_name)
        return redirect("/dashboard")
    else:
        return render_template("create_database.html")

# backup database using nahcrofDB.backupDB
@app.route("/backup/<database>")
def backup_db(database):
    if "password" in session:
        if session["password"] == admin_password:
            nahcrofDB.backupDB(database)
            keys = nahcrofDB.keysamount(database)
            size = nahcrofDB.sizeofDB(database)
            writes = nahcrofDB.getWrites(database)
            reads = nahcrofDB.getReads(database)
            logs = nahcrofDB.getLogs(database)
            return render_template("view_database.html", keys=keys, dbsize=size, writes=writes, reads=reads, logs=logs, database=database, message="backup made/updated")
        else:
            return "no cheating"
    else:
        return redirect("/")

# delete database using nahcrofDB.deleteDB
@app.route("/delete/<database>")
def delete_DB(database):
    if "password" in session:
        if session["password"] == admin_password:
            nahcrofDB.deleteDB(database)
            return redirect("/dashboard")
        else:
            return "no cheating"
    else:
        return redirect("/")

@app.route("/view_db/<database>")
def view_db(database):
    if "password" in session:
        if session["password"] == admin_password:
            keys = nahcrofDB.keysamount(database)
            size = nahcrofDB.sizeofDB(database)
            writes = nahcrofDB.getWrites(database)
            reads = nahcrofDB.getReads(database)
            logs = nahcrofDB.getLogs(database)

            # check exists
            default_path = read_config.config["default_path"]
            backup_exists = os.path.exists(f"{default_path}{database}_database_backup/usr_st.db")

            # compare
            if backup_exists:
                
                if nahcrofDB.compare_databases(database, f"{database}_database_backup"):
                    message = "database MATCHES the backup"
                else:
                    message = "datasets DO NOT match"
            else:
                message = ""


            return render_template("view_database.html", keys=keys, dbsize=size, writes=writes, reads=reads, logs=logs, database=database, message=message)
        else:
            return "no cheating"
    else:
        return redirect("/")

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == admin_password:
            session["password"] = entered_password
            return redirect("/dashboard")
        else:
            return "wrong password, goober"
    else:
        if "password" not in session:
            return render_template("signin.html")
        else:
            if session["password"] == admin_password:
                return redirect("/dashboard")
            else:
                return "how?"

@app.route("/dashboard")
def dashboard():
    if "password" in session:
        if session["password"] == admin_password:
            try:
                all_folders = os.listdir(read_config.config["default_path"])
                print(all_folders)
                all_folders = sorted(all_folders)
                folders = {}
                for folder in all_folders:
                    reads = nahcrofDB.getReads(folder)
                    writes = nahcrofDB.getWrites(folder)
                    folders[folder] = {"name": folder, "reads": reads, "writes": writes}
                return render_template("dashboard.html", folders=folders)
            except FileNotFoundError:
                os.mkdir(read_config.config["default_path"])
                all_folders = os.listdir(read_config.config["default_path"])
                print(all_folders)
                all_folders = sorted(all_folders)
                folders = {}
                for folder in all_folders:
                    reads = nahcrofDB.getReads(folder)
                    writes = nahcrofDB.getWrites(folder)
                    folders[folder] = {"name": folder, "reads": reads, "writes": writes}
                return render_template("dashboard.html", folders=folders)
        else:
            return "no cheating"
    else:
        return redirect("/")

@app.route("/writes/<location>/<password>/")
def writes(location, password):
    if password == mainpass:
        data = nahcrofDB.getWrites(location)
        return str(data), 200
    else:
        return "no", 403

@app.route("/reads/<location>/<password>/")
def reads(location, password):
    if password == mainpass:
        data = nahcrofDB.getReads(location)
        return str(data), 200
    else:
        return "no", 403

@app.route("/keys/<location>/<password>/")
def keys(location, password):
    if password == mainpass:
        data = str(nahcrofDB.keys(location))
        user_data = {
            "keys": data
        }
        return jsonify(user_data), 200
    else:
        return "no", 403

@app.route("/logs/<location>/<password>/")
def logs(location, password):
    if password == mainpass:
        data = str(nahcrofDB.getLogs(location))
        user_data = {
            "logs": data
        }
        return jsonify(user_data), 200
    else:
        return "no", 403

@app.route("/search/<password>/")
def search(password):
    if password == mainpass:
        location = request.args.get("location")
        data = request.args.get("parameter")
        results = nahcrofDB.search(location, data)
        user_data = {
            "data": results
        }
        return jsonify(user_data), 200
    else:
        return "no", 403    

@app.route("/getKeys/<password>/")
def getKeys(password):
    if password == mainpass:
        location = request.args.get("location")
        templist = []
        keyname_amount = request.args.get("keynamenum")
        keynamenum = int(keyname_amount)
        for n in range(keynamenum):
            key = request.args.get(f"key_{n}")
            templist.append(key)
        newdata = nahcrofDB.getKeys(location, templist)
        user_data = {}
        for key in newdata.keys():
            user_data[key] = newdata[key]
        return jsonify(user_data), 200
    else:
        return "no", 403

@app.route("/getKey/<password>/")
def getKey(password):
    if password == mainpass:
        location = request.args.get("location")
        print(location)
        keyname = request.args.get("keyname")
        newdata = nahcrofDB.getKey(location, keyname)
        user_data = {
            "keycontent": newdata
        }
        return jsonify(user_data), 200
    else:
        return "no", 403

@app.route("/makeKey/<password>/", methods=["POST"])
def makeKey(password):
    if password == mainpass:
        data = request.get_json()
        key = data["keyname"]
        value = data["keycontent"]
        print(key)
        print(value)
        pickle.dump({"data": {key: value}, "location": data["location"]}, open(f"{read_config.config['write_folder']}{key}_{data['location']}_ferris", "wb"))

        return "successful", 201
    else:
        return "no", 403


@app.route("/makeKeys/<password>/", methods=["POST"])
def makeKeys(password):
    if password == mainpass:
        data = request.get_json()
        location = data["location"]
        postdata = dict(data["data"])
        for key, value in postdata.items():
            pickle.dump({"data": {key: value}, "location": data["location"]}, open(f"{read_config.config['write_folder']}{key}_{data['location']}_ferris", "wb"))


            print("successful")
        return "successful", 204
    else:
        return "no", 403


@app.route("/delKey/<password>/", methods=["POST"])
def delKey(password):
    if password == mainpass:
        data = request.get_json()
        attempt = nahcrofDB.delKey(data["location"], data["keyname"])
        if attempt == "success":
            return "successful", 201
        else:
            return "Key not found", 404
    else:
        return "no", 403

@app.route("/databaseSize/<location>/<password>/")
def databaseSize(location, password):
    if password == mainpass:
        data = {"size": nahcrofDB.sizeofDB(location)}
        return jsonify(data)
    else:
        return "no", 403

@app.route("/keynums/<location>/<password>/")
def keynums(location, password):
    if password == mainpass:
        data = {"size": nahcrofDB.keysamount(location)}
        return jsonify(data)
    else:
        return "no", 403

@app.route("/emptyDB/<password>/", methods=["POST"])
def emptyDB(password):
    if password == mainpass:
        data = request.get_json()
        nahcrofDB.emptyDB(data["location"])
        return "success", 201
    else:
        return "no", 403

@app.route("/deleteDB/<password>/", methods=["POST"])
def deleteDB(password):
    if password == mainpass:    
        data = request.get_json()
        nahcrofDB.deleteDB(data["location"])
        return "success", 205
    else:
        return "no", 403

ferris_thread = threading.Thread(target=run_ferris)
ferris_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(read_config.config["port"]))
