from enum import Enum

class EpicAuthToken(Enum):
    METHOD: str = "POST"
    GRANT_TYPE: str = "device_auth"
    TOKEN_TYPE: str = "eg1"

    ENDPOINT: str = "account-public-service-prod.ol.epicgames.com"
    PATH: str = "/account/api/oauth/token"

class TimelineEndpoint(Enum):
    METHOD: str = "GET"
    ENDPOINT: str = "fortnite-public-service-prod11.ol.epicgames.com"
    PATH: str = "/fortnite/api/calendar/v1/timeline"

class FortniteContent(Enum):
    METHOD: str = "GET"
    ENDPOINT: str = "fortnitecontent-website-prod07.ol.epicgames.com"
    PATH: str = "/content/api/pages/fortnite-game"