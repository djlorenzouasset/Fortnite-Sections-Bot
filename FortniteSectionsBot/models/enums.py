from enum import Enum

class EpicAuthToken(Enum):
    METHOD: str = "Post"
    BASE: str = "account-public-service-prod.ol.epicgames.com"
    ENDPOINT: str = "/account/api/oauth/token"

    # params
    GRANT_TYPE: str = "device_auth"
    TOKEN_TYPE: str = "eg1"

class TimelineEndpoint(Enum):
    METHOD: str = "Get"
    BASE: str = "fortnite-public-service-prod11.ol.epicgames.com"
    ENDPOINT: str = "/fortnite/api/calendar/v1/timeline"

class FortniteContent(Enum):
    METHOD: str = "Get"
    BASE: str = "fortnitecontent-website-prod07.ol.epicgames.com"
    ENDPOINT: str = "/content/api/pages/fortnite-game"