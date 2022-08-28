from pathlib import Path
import sqlite3
import os

### Konstante ####################################################################################

# Twitter API Bearer Token
bearer_token = "YourOwnTokenFrom-https://developer.twitter.com/en"
# Twitter Username to start with (follows.py)
startuser = "TwitterUsername"
# How many steps deep should we go (follows.py)
recursive = 1
# Path and filename of the script itself
absFilePath = os.path.abspath(__file__)
# Split the path and the filename of the script into single variables
ScriptPath, ScriptFilename = os.path.split(absFilePath)
# Path and name of the sqlite database file
# Name of the sqlite database file
DBName = 'users.db'
DBPath = ScriptPath + '\{}'.format(DBName) 
# Wich userfields will we use from Twitter v2 API
user_fields = "user.fields=created_at,description,id,location,name,profile_image_url,protected,username,verified"


### Funktionen ###################################################################################

def create_db():
    fileObj = Path(DBPath) 
    if fileObj.is_file():
        con = sqlite3.connect(DBName)        
        cur = con.cursor()
    else:        
        con = sqlite3.connect(DBName)
        cur = con.cursor()
        cur.execute("CREATE TABLE users(id integer primary key, created_at text, username text, description text, name text, profile_image_url text, protected integer, verified integer)")
        cur.execute("CREATE TABLE follows(id integer NOT NULL, follower integer NOT NULL, foreign key(id) references users(id), primary key(id,follower))")
    cur.close
    con.close
