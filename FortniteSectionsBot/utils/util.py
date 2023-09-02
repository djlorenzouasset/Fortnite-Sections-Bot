import json
import aiofiles
import logging

from typing import Union
from globals import Globals
from rest.requests import Requests
from models.settings import Settings
from models.errors import MissingAuthCredentials, MissingTwitterCredentials, LanguageNotFound, AuthError

log = logging.getLogger('FortniteShopSections.Utils')

class Utils:

    async def open(
        file: str, mode: str = 'r', encoding: str = None, is_json: bool = False
    ) -> Union[str, bytes]:
        # open a specified file and return its content
        async with aiofiles.open(file=file, mode=mode, encoding=encoding) as f:
            if is_json:
                return json.loads(await f.read())
            else:
                return await f.read()

    async def write(
        file: str, content: str, mode: str = 'w', encoding: str = None, is_json: bool = False
    ) -> None:
        # write the content in a specified file
        async with aiofiles.open(file=file, mode=mode, encoding=encoding) as f:
            if is_json:
                await f.write(json.dumps(content, indent=4))
            else:
                await f.write(content)

    def check_settings(settings: Settings) -> None:
        if settings.language == '' or settings.language not in Globals.LANGUAGES:
            raise LanguageNotFound
        
        elif settings.auth.device_id == '' or settings.auth.account_id == '' or settings.auth.secret == '':
            raise MissingAuthCredentials
        
        elif settings.twitter.enabled:
            data = settings.twitter
            if not data.apiKey or not data.apiSecret or not data.accessToken or not data.accessTokenSecret:
                raise MissingTwitterCredentials