import time
import sqlite3
import requests
import config

### Variable #####################################################################################

# Usercounter
user_counter = int(0)

### Funktionen ###################################################################################



# Twitter v2 API App Authorization with Bearer Token
def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {config.bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


# Twitter v2 API query url for a single user
def create_start_url():    
    url = "https://api.twitter.com/2/users/by/username/{}?{}".format(config.startuser, config.user_fields)
    return url

# Twitter v2 API query url for a list of users
def create_users_url(usernames_cs):
    usernames = "usernames=" + usernames_cs
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, config.user_fields)
    return url


# Twitter v2 API query
def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )
    return response


def get_follows(id, recursive_deep):
    url = 'https://api.twitter.com/2/users/{}/followers'.format(id)
    response = connect_to_endpoint(url)   
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
            response = connect_to_endpoint(url_next)   
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
    response = connect_to_endpoint(url)   
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
            response = connect_to_endpoint(url_next)   
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
        print('')


def get_many_users(users, recursive_deep):
    url = create_users_url(users)
    response = connect_to_endpoint(url)
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

 
def main():   
    config.create_db()
    url = create_start_url()
    response = connect_to_endpoint(url)
    json_response = response.json()

    #usr = user(json_response)
    #print(usr.name)

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

