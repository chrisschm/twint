import twitter_api

class user:

    def __init__(self,userid=0,username=""):
        if (userid==0) and (username==""):
            raise ValueError(
                "Missing identification of the user to create object. To build a new reference of the user object it will need to give userid OR username."
            )
        self.__userid = userid
        self.__username = username
        if (userid==0):
            __url = twitter_api.create_username_url(username)
        else:
            __url = twitter_api.create_userid_url(userid)
        
        __response = twitter_api.connect_to_endpoint(__url)
        __json_response = __response.json()
        __json_data = __json_response['data']

        self.__created_at = __json_data['created_at']
        self.__description = __json_data['description']
        self.__location = __json_data['location']
        self.__userid = __json_data['id']
        self.__name = __json_data['name']
        self.__profile_image_url = __json_data['profile_image_url']
        self.__protected = __json_data['protected']
        self.__username = __json_data['username']
        self.__verified = __json_data['verified']



    ### Eigenschaften ############################################################################

    @property
    def created_at(self):
        return self.__created_at

    @property
    def description(self):
        return self.__description

    @property
    def location(self):
        return self.__location    

    @property
    def id(self):
        return self.__userid

    @property
    def name(self):
        return self.__name

    @property
    def profile_image_url(self):
        return self.__profile_image_url

    @property
    def protected(self):
        return self.__protected

    @property
    def username(self):
        return self.__username

    @property
    def verified(self):
        return self.__verified
  