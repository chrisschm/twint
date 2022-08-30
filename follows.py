import time
import sqlite3
import requests
import config
import twitter_api

### Variable #####################################################################################

# Ein Zähler um am Laufzeitende auszugeben, wieviele Twitterkonten gelesen wurden
# Benutzer können mehrfach vorkommen, daher sind in der Datenbank am Ende weniger vorhanden
user_counter = int(0)


### Funktionen ###################################################################################



### Recursiv function to get all followers and following accounts of given userid ################
def get_follows(id, recursive_deep):
    url = 'https://api.twitter.com/2/users/{}/followers'.format(id)
    response = twitter_api.connect_to_endpoint(url)   
    json_response = response.json()
    
    try:
        json_data = json_response['data']

        names = ""

        for x in json_data:
            write_db_follows(id,x['id'])
            name = x['username']
            if len(names) == 0:
                names = name
            else:
                names = names + "," + name    
        
        if int(response.headers['x-rate-limit-remaining']) == 0:
            print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            time.sleep(900)

        get_many_users(names, recursive_deep)        

    except KeyError:
        print('No follows for ID={}, skipping this user.'.format(id))
    else:
        if int(response.headers['x-rate-limit-remaining']) == 0:
            print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            time.sleep(900)    

    try:
        while json_response["meta"]["next_token"]:
            time.sleep(2)
            url_next = url + '?pagination_token={}'.format(json_response["meta"]["next_token"])
            response = twitter_api.connect_to_endpoint(url_next)   
            json_response = response.json()
        
            json_data = json_response['data']
            names = ""

            for x in json_data:
                write_db_follows(id,x['id'])
                name = x['username']
                if len(names) == 0:
                    names = name
                else:
                    names = names + "," + name    
        
            if int(response.headers['x-rate-limit-remaining']) == 0:
                print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
                time.sleep(900)

            get_many_users(names, recursive_deep)
    except KeyError:
        pass

    ### Following ###

    url = 'https://api.twitter.com/2/users/{}/following'.format(id)
    response = twitter_api.connect_to_endpoint(url)   
    json_response = response.json()
    
    try:
        json_data = json_response['data']

        names = ""

        for x in json_data:
            write_db_follows(x['id'],id)
            name = x['username']
            if len(names) == 0:
                names = name
            else:
                names = names + "," + name    
        
        if int(response.headers['x-rate-limit-remaining']) == 0:
            print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            time.sleep(900)

        get_many_users(names, recursive_deep)        

    except KeyError:
        print('User ID={} is not following anyone, skip this user.'.format(id))
    else:
        if int(response.headers['x-rate-limit-remaining']) == 0:
            print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            time.sleep(900)    

    try:
        while json_response["meta"]["next_token"]:
            time.sleep(2)
            url_next = url + '?pagination_token={}'.format(json_response["meta"]["next_token"])
            response = twitter_api.connect_to_endpoint(url_next)   
            json_response = response.json()
        
            json_data = json_response['data']
            names = ""

            for x in json_data:
                write_db_follows(id,x['id'])
                name = x['username']
                if len(names) == 0:
                    names = name
                else:
                    names = names + "," + name    
        
            if int(response.headers['x-rate-limit-remaining']) == 0:
                print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
                time.sleep(900)

            get_many_users(names, recursive_deep)
    except KeyError:
        pass


### Function to get attributes of a given list of usernames ######################################
def get_many_users(users, recursive_deep):
    url = twitter_api.create_usernames_url(users)
    response = twitter_api.connect_to_endpoint(url)
    json_response = response.json()
    try:
        json_data = json_response['data']  
            
        if int(response.headers['x-rate-limit-remaining']) == 0:
            print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            time.sleep(900)    
    
        for x in json_data:
            userid = x['id']
            write_db_user(x)                
            if config.recursive > recursive_deep:
                get_follows(userid, recursive_deep + 1)
    except KeyError:
        print('No follows for ID={}, skipping this user.'.format(x['id']))
    else:
        if int(response.headers['x-rate-limit-remaining']) == 0:
            print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            time.sleep(900)       
    

### Function writes one user into the database ###################################################
def write_db_user(user):
    con = sqlite3.connect(config.DBName)
    cur = con.cursor()

    v1 = user['id']
    v2 = user['created_at']
    v3 = user['username']
    v4 = user['description']
    v5 = user['name']
    v6 = user['profile_image_url']
    v7 = user['protected']
    v8 = user['verified']

    cmd = """INSERT INTO users(id, created_at, username, description, name, profile_image_url, protected, verified) VALUES(?,?,?,?,?,?,?,?);"""

    try:
        cur.execute(cmd, (v1,v2,v3,v4,v5,v6,v7,v8))  
    except sqlite3.IntegrityError:
        print('Info: User is already in database (Username:{}, ID:{})'.format(v3,v1))  
    con.commit()
    cur.close()
    con.close()

    global user_counter
    user_counter = user_counter + 1    


### Function writes all followers and following ids of a given user into the database ############
def write_db_follows(user, follower):
    con = sqlite3.connect(config.DBName)
    cur = con.cursor()
    cmd = """INSERT INTO follows(id, follower) VALUES(?,?);"""
    try:
        cur.execute(cmd, (user,follower))  
    except sqlite3.IntegrityError:
        print('Info: Follow is already in database (ID: {} follows ID: {})'.format(user,follower)) 
    con.commit()
    cur.close()
    con.close()


### Main function of the program #################################################################
def main():   
    config.create_db()
    #url = create_start_url()
    url = twitter_api.create_username_url(config.startuser)
    response = twitter_api.connect_to_endpoint(url)
    json_response = response.json()
    json_data = json_response['data']
    userid = json_data['id']
    write_db_user(json_data)
    
    if int(response.headers['x-rate-limit-remaining']) == 0:
        print("{}: Twitter rate-limit exceeded. Waiting for the next window (15 minutes)...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        time.sleep(900)

    get_follows(userid, 1)    
    print('Got {} users from Twitter v2 API. Program endet succesfull.'.format(user_counter))
    

### Programm-Start ###############################################################################
 
if __name__ == "__main__":
    main()

##################################################################################################

