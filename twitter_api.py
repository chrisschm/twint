import requests
import config

def create_username_url(username):    
    url = "https://api.twitter.com/2/users/by/username/{}?{}".format(username, config.user_fields)
    return url

def create_usernames_url(usernames):
    usernames = "usernames=" + usernames
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, config.user_fields)
    return url

def create_userid_url(userid):    
    url = "https://api.twitter.com/2/users/{}?{}".format(userid, config.user_fields)
    return url

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {config.bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r

def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    if response.status_code != 200:
        raise ConnectionError(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )
    return response
    