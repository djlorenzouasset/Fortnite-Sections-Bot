import aiohttp
import logging 

from datetime import datetime, timedelta
from typing import Optional

from models.enums import EpicAuthToken, FortniteContent, TimelineEndpoint
from models.errors import AuthError
from models.settings import Settings
from models.decorators import is_token_valid
from utils.util import Util

log: logging.Logger = logging.getLogger('FortniteShopSections')

BASIC_TOKEN = 'MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE='

class Requests:
    def __init__(self, util: Util, settings: Settings):
        self.util: Util = util
        self.settings: Settings = settings
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def get_fortnite_content(self) -> Optional[dict]:
        # restart session
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        try:
            fortnite_content = await self.session.request(
                method=FortniteContent.METHOD.value,
                url=f"https://{FortniteContent.ENDPOINT.value}{FortniteContent.PATH.value}",
                params={
                    'lang': self.settings.language
                }
            )
            if fortnite_content.status != 200:
                await self.session.close()
                log.error(f"Invalid response from FortniteContent: [BAD({fortnite_content.status})]")
                return None

            await self.session.close()
            return await fortnite_content.json()
        
        except Exception as e:
            # if there is an error, log it and return None
            log.error(f"Error while getting FortniteContent: {e}")
            await self.session.close()
            return None
        
    @is_token_valid
    async def get_timeline(self) -> Optional[dict]:
        # restart session
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
    
        try:
            timeline = await self.session.request(
                method=TimelineEndpoint.METHOD.value,
                url=f"https://{TimelineEndpoint.ENDPOINT.value}{TimelineEndpoint.PATH.value}",
                headers={
                    "Authorization": f"bearer {self.settings.auth.access_token}"
                }
            )
            await self.session.close()
            jsonObject = await timeline.json()
            
            if timeline.status != 200:
                if jsonObject.get('errorCode'):
                    log.error(f"Invalid response from Timeline: [BAD({timeline.status})]: {jsonObject.get('errorCode')}")
                else:
                    log.error(f"Invalid response from Timeline: [BAD({timeline.status})]")
                return None
            return jsonObject
        
        except Exception as e:
            log.error(f"Error while getting timeline: {e}")
            await self.session.close()
            return None
        
    async def create_token(self) -> None:
        response = await self.session.request(
            method=EpicAuthToken.METHOD.value,
            url=f'https://{EpicAuthToken.ENDPOINT.value}{EpicAuthToken.PATH.value}',
            headers={
                'Authorization': 'Basic ' + BASIC_TOKEN,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': EpicAuthToken.GRANT_TYPE.value,
                'token_type': EpicAuthToken.TOKEN_TYPE.value,
                'account_id': self.settings.auth.account_id,
                'device_id': self.settings.auth.device_id,
                'secret': self.settings.auth.secret
            }
        )
        await self.session.close()
        data = await response.json()
        if response.status == 200:
            log.info('Successfully created a new token.')
            # put the expire 5 minutes before
            # so we can prevent auth errors
            self.settings.auth.expires = datetime.now() + timedelta(seconds=data.get('expires_in')) - timedelta(minutes=5)
            self.settings.auth.access_token = data.get('access_token')
            self.settings.auth.refresh_token = data.get('refresh_token')

        elif 'errorCode' in data:
            # error in the response
            text: str = f'[BAD({response.status})] {data.get("errorCode")}: {data.get("errorMessage")}'
            raise AuthError(text)

    async def refresh_token(self) -> None:
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        response = await self.session.request(
            method=EpicAuthToken.METHOD.value,
            url=f'https://{EpicAuthToken.ENDPOINT.value}{EpicAuthToken.PATH.value}',
            headers={
                'Authorization': 'Basic ' + BASIC_TOKEN,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'refresh_token',
                'token_type': EpicAuthToken.TOKEN_TYPE.value,
                'refresh_token': self.settings.auth.refresh_token
            }
        )
        await self.session.close()
        data = await response.json()
        if response.status == 200:
            log.info('Successfully refreshed access_token.')
            # put the expire 5 minutes before
            # so we can prevent auth errors
            self.settings.auth.expires = datetime.now() + timedelta(seconds=data.get('expires_in')) - timedelta(minutes=5)
            self.settings.auth.access_token = data.get('access_token')
            self.settings.auth.refresh_token = data.get('refresh_token')

        elif 'errorCode' in data:
            # error in the response
            text: str = f'[BAD({response.status})] {data.get("errorCode")}: {data.get("errorMessage")}'
            raise AuthError(text)