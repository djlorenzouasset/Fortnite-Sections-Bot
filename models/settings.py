from typing import Optional
from datetime import datetime

class Settings:
    def __init__(self, settings: dict):
        self.language: str = settings.get('language', 'en')
        self.seconds: int = settings.get('seconds_per_task', 50)

        self.auth: Auth = Auth(settings.get('auth'))
        self.twitter: Twitter = Twitter(settings.get('twitter'))
        self.sections: Sections = Sections(settings.get('sections'))

class Auth:
    def __init__(self, auth: dict):
        self.expires: Optional[datetime] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

        self.device_id: str = auth.get('device_id', '')
        self.account_id: str = auth.get('account_id', '')
        self.secret: str = auth.get('secret', '')

    @property
    def is_expired(self) -> bool:
        return self.expires < datetime.now()

class Twitter:
    def __init__(self, twitter: dict):
        self.enabled: bool = twitter.get('enabled', False)
        self.apiKey: str = twitter.get('apiKey', '')
        self.apiSecret: str = twitter.get('apiSecret', '')
        self.accessToken: str = twitter.get('accessToken', '')
        self.accessTokenSecret: str = twitter.get('accessTokenSecret', '')

class Sections:
    def __init__(self, sections: dict):
        self.image: Optional[str] = sections.get('image', False)
        self.show_if_one: bool = sections.get('show_if_one', True)
        self.title: str = sections.get('title', 'Today\'s Shop Sections:')
        self.footer: str = sections.get('footer', 'Sections')