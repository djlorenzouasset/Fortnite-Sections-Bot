from typing import Union, Optional
from datetime import datetime


class Settings:
    def __init__(self, settings: dict):
        """
        Settings class: This class is used to store the settings data.

        Parameters:
            settings (``dict``): The settings config file.

        Attributes:
            language (``str``): 
                The language for the program.

            auth (:obj:`Auth`): 
                The auth class.

            twitter (:obj:`Twitter`): 
                The twitter class.

            sections (:obj:`Sections`): 
                The sections class.

        """

        self.language: str = settings.get('language', 'en')
        self.seconds: int = settings.get('seconds_per_task', 50)

        self.auth: Auth = Auth(settings.get('auth'))
        self.twitter: Twitter = Twitter(settings.get('twitter'))
        self.sections: Sections = Sections(settings.get('sections'))



class Auth:
    def __init__(self, auth: dict):
        """
        Auth class: This class is used to store the auth data.

        Parameters:
            auth (``dict``): 
                The auth config file.

        Attributes:

            expires (``datetime``, **Optional**):
                The expires time of the access token.

            access_token (``str``, **Optional**):
                The access token for the authorization.

            device_id (``str``, **Optional**):
                The device id for auth.

            account_id (``str``, **Optional**):
                The account id for auth.

            secret (``str``, **Optional**):
                The secret key for auth.

        """

        self.expires: Optional[datetime] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

        self.device_id: str = auth.get('device_id', '')
        self.account_id: str = auth.get('account_id', '')
        self.secret: str = auth.get('secret', '')


    @property
    def is_expired(self) -> bool:
        """
        Check if the access token is expired or not.

        Returns:
            ``bool``: If the access token is expired or not.
        """

        return self.expires < datetime.now()



class Twitter:
    def __init__(self, twitter: dict):
        """
        Twitter class: This class is used to store the tweet data

        Parameters:
            twitter (``dict``): The twitter config file.

        Attributes:
            enabled (``bool``):
                If the twitter feature is enabled or not.

            api_key (``str``):
                The api key for the twitter api.

            api_secret (``str``):
                The api secret for the twitter api.

            accessToken (``str``):
                The access token for the twitter api.

            accessTokenSecret (``str``):
                The access token secret for the twitter api.

        """

        self.enabled: bool = twitter.get('enabled', False)
        self.apiKey: str = twitter.get('apiKey', '')
        self.apiSecret: str = twitter.get('apiSecret', '')
        self.accessToken: str = twitter.get('accessToken', '')
        self.accessTokenSecret: str = twitter.get('accessTokenSecret', '')


class Sections:
    def __init__(self, sections: dict):
        """
        Sections class: This class is used to store the tweet data
        for the sections post.

        Parameters:
            sections (``dict``): 
                The sections config file.

        Attributes:
            text (``str``): 
                The text for the sections post.

            image (``str``): 
                The image for the sections post. Can be None, if it the program will post sections as a text post.

        """

        self.image: Optional[str] = sections.get('image', False)
        self.show_if_one: bool = sections.get('show_if_one', True)
        self.title: str = sections.get('title', 'Today\'s Shop Sections:')
        self.footer: str = sections.get('footer', 'Sections')