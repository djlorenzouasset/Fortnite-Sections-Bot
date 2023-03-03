import aiohttp

from datetime import datetime, timedelta
from typing import Optional

from models.enums import EpicAuthToken, FortniteContent, TimelineEndpoint
from models.errors import AuthError
from models.settings import Settings
from models.decorators import is_token_valid

from utils.util import Util


class Requests:
    def __init__(self, util: Util, settings: Settings):
        self.log: Util.log = util.log
        self.util: Util = util
        self.settings: Settings = settings

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.Authorization: str = 'basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE='


    async def get_fortnite_content(self) -> Optional[dict]:
        """
        Get FortniteContent data for sections names.
        """

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

            jsonObject = await fortnite_content.json()
            await self.session.close()

            if fortnite_content.status != 200:
                self.log.error(f"Invalid response from FortniteContent: [BAD({fortnite_content.status})]")
                return None

            return jsonObject
        

        except Exception as e:

            # if there is an error, log it and return None
            self.log.error(f"Error while getting FortniteContent: {e}")
            await self.session.close()

            return None
        

    @is_token_valid
    async def get_timeline(self) -> Optional[dict]:
        """
        Get timeline data for check new sections
        """

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

            jsonObject = await timeline.json()
            await self.session.close()

            if timeline.status != 200:
                if jsonObject.get('errorCode'):
                    self.log.error(f"Invalid response from Timeline: [BAD({timeline.status})]: {jsonObject.get('errorCode')}")

                else:
                    self.log.error(f"Invalid response from Timeline: [BAD({timeline.status})]")
                    
                return None
            
            return jsonObject
        

        except Exception as e:

            self.log.error(f"Error while getting timeline: {e}")
            await self.session.close()

            return None
        

    async def create_token(self) -> None:
        """
        Creates a new access token.
        """

        response = await self.session.request(
            method=EpicAuthToken.METHOD.value,
            url=f'https://{EpicAuthToken.ENDPOINT.value}{EpicAuthToken.PATH.value}',
            headers={
                'Authorization': self.Authorization,
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
            self.log.info('Successfully created a new token.')
            self.settings.auth.expires = datetime.now() + timedelta(seconds=data.get('expires_in'))
            self.settings.auth.access_token = data.get('access_token')
            self.settings.auth.refresh_token = data.get('refresh_token')


        elif 'errorCode' in data:
            text: str = f'[BAD({response.status})] {data.get("errorCode")}: {data.get("errorMessage")}'
            raise AuthError(text)
            

    
    async def refresh_token(self) -> None:
        """
        Refreshes the access token.
        """

        # restart session
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        response = await self.session.request(
            method=EpicAuthToken.METHOD.value,
            url=f'https://{EpicAuthToken.ENDPOINT.value}{EpicAuthToken.PATH.value}',
            headers={
                'Authorization': self.Authorization,
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
            self.log.info('Successfully refreshed access_token.')
            self.settings.auth.expires = datetime.now() + timedelta(seconds=data.get('expires_in'))
            self.settings.auth.access_token = data.get('access_token')
            self.settings.auth.refresh_token = data.get('refresh_token')


        elif 'errorCode' in data:
            text: str = f'[BAD({response.status})] {data.get("errorCode")}: {data.get("errorMessage")}'
            raise AuthError(text)