import aiohttp
import logging 

from datetime import datetime, timedelta
from typing import Optional
from globals import Globals
from models.errors import AuthError
from models.enums import EpicAuthToken, FortniteContent, TimelineEndpoint

log: logging.Logger = logging.getLogger('FortniteShopSections.Rest')

class Requests:

    async def get_fortnite_content() -> Optional[dict]:
        session = aiohttp.ClientSession()

        try:
            fortnite_content = await session.request(
                method=FortniteContent.METHOD.value,
                url=f"https://{FortniteContent.BASE.value}{FortniteContent.ENDPOINT.value}",
                params={
                    'lang': Globals.SETTINGS.language
                }
            )
            log.info(f'[{fortnite_content.method}] {fortnite_content.reason} ({fortnite_content.status}) {fortnite_content.url}')
            if fortnite_content.status != 200:
                log.error(f"Invalid response from FortniteContent: [BAD({fortnite_content.status})]")
                await session.close()
                return None

            content = await fortnite_content.json()
            await session.close()
            return content
        
        except Exception as e:
            # if there is an error, log it and return None
            log.error(f"Error while getting FortniteContent: {e}")
            await session.close()
            return None

    async def get_timeline() -> Optional[dict]:
        session = aiohttp.ClientSession()

        try:
            timeline = await session.request(
                method=TimelineEndpoint.METHOD.value,
                url=f"https://{TimelineEndpoint.BASE.value}{TimelineEndpoint.ENDPOINT.value}",
                headers={
                    "Authorization": f"bearer {Globals.SETTINGS.auth.access_token}"
                }
            )
            log.info(f'[{timeline.method}] {timeline.reason} ({timeline.status}) {timeline.url}')

            jsonObject = await timeline.json()
            if timeline.status != 200:
                if jsonObject.get('errorCode'):
                    log.error(f"Invalid response from Timeline: [BAD({timeline.status})]: {jsonObject.get('errorCode')}")
                else:
                    log.error(f"Invalid response from Timeline: [BAD({timeline.status})]")
                return None
            
            await session.close()
            return jsonObject
        
        except Exception as e:
            log.error(f"Error while getting timeline: {e}")
            await session.close()
            return None
        
    async def create_token() -> None:
        session = aiohttp.ClientSession()

        response = await session.request(
            method=EpicAuthToken.METHOD.value,
            url=f'https://{EpicAuthToken.BASE.value}{EpicAuthToken.ENDPOINT.value}',
            headers={
                'Authorization': 'Basic ' + Globals.BASIC_TOKEN,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': EpicAuthToken.GRANT_TYPE.value,
                'token_type': EpicAuthToken.TOKEN_TYPE.value,
                'account_id': Globals.SETTINGS.auth.account_id,
                'device_id': Globals.SETTINGS.auth.device_id,
                'secret': Globals.SETTINGS.auth.secret
            }
        )
        log.info(f'[{response.method}] {response.reason} ({response.status}) {response.url}')
        data = await response.json()
        if response.status == 200:
            log.info('Successfully created a new token.')
            # put the expire 5 minutes before
            # so we can prevent auth errors
            Globals.SETTINGS.auth.expires = datetime.now() + timedelta(seconds=data.get('expires_in')) - timedelta(minutes=5)
            Globals.SETTINGS.auth.access_token = data.get('access_token')
            Globals.SETTINGS.auth.refresh_token = data.get('refresh_token')
            await session.close()

        elif 'errorCode' in data:
            # error in the response
            text: str = f'[BAD({response.status})] {data.get("errorCode")}: {data.get("errorMessage")}'
            await session.close()
            raise AuthError(text)

    async def refresh_token() -> None:
        session = aiohttp.ClientSession()

        response = await session.request(
            method=EpicAuthToken.METHOD.value,
            url=f'https://{EpicAuthToken.BASE.value}{EpicAuthToken.ENDPOINT.value}',
            headers={
                'Authorization': 'Basic ' + Globals.BASIC_TOKEN,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'refresh_token',
                'token_type': EpicAuthToken.TOKEN_TYPE.value,
                'refresh_token': Globals.SETTINGS.auth.refresh_token
            }
        )
        log.info(f'[{response.method}] {response.reason} ({response.status}) {response.url}')
        data = await response.json()
        if response.status == 200:
            log.info('Successfully refreshed access_token.')
            # put the expire 5 minutes before
            # so we can prevent auth errors
            Globals.SETTINGS.auth.expires = datetime.now() + timedelta(seconds=data.get('expires_in')) - timedelta(minutes=5)
            Globals.SETTINGS.auth.access_token = data.get('access_token')
            Globals.SETTINGS.auth.refresh_token = data.get('refresh_token')
            await session.close()

        elif 'errorCode' in data:
            # error in the response
            text: str = f'[BAD({response.status})] {data.get("errorCode")}: {data.get("errorMessage")}'
            await session.close()
            raise AuthError(text)