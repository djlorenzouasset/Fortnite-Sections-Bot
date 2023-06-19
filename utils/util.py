import json
import aiofiles
import os 
import aiohttp
import logging

from typing import Union

from models.errors import MissingAuthCredentials, MissingTwitterCredentials, LanguageNotFound
from models.settings import Settings, Twitter

log: logging.Logger = logging.getLogger('FortniteShopSections')

class Util:
    def __init__(self):
        pass

    async def open(
        self, 
        file: str,
        mode: str = 'r', 
        encoding: str = None, 
        is_json: bool = False
    ) -> Union[str, bytes]:
        # open a specified file and return its content
        async with aiofiles.open(file=file, mode=mode, encoding=encoding) as f:
            if is_json:
                # return the file as json object
                return json.loads(await f.read())
            else:
                return await f.read()
        
    async def write(
        self, 
        file: str, 
        content: str, 
        mode: str = 'w', 
        encoding: str = None, 
        is_json: bool = False
    ) -> None:
        # write the content in a specified file
        async with aiofiles.open(file=file, mode=mode, encoding=encoding) as f:
            if is_json:
                # write the file as json
                await f.write(json.dumps(content, indent=4))
            else:
                await f.write(content)

    async def check_settings(self, settings: Settings) -> None:
        if settings.language == '' or settings.language not in ['en', 'it', 'ar', 'de', 'es', 'fr', 'ja', 'ko', 'pl', 'tr', 'pt-BR', 'es-419']:
            raise LanguageNotFound
        
        elif settings.auth.device_id == '' or settings.auth.account_id == '' or settings.auth.secret == '':
            os.open('settings.json')
            raise MissingAuthCredentials

        elif settings.twitter.enabled:
            data: Twitter = settings.twitter
            if not data.apiKey or not data.apiSecret or not data.accessToken or not data.accessTokenSecret:
                os.open('settings.json')
                raise MissingTwitterCredentials
        
    async def check_updates(self) -> None:
        session = aiohttp.ClientSession()

        file_content = await session.request(
            method='GET',
            url=f'https://raw.githubusercontent.com/djlorenzouasset/Fortnite-Sections-Bot/main/version.json'
        )
        if file_content.status == 200:
            file_content = json.loads(await file_content.text())
            local_content = await self.open(file='version.json', is_json=True)
            await session.close()
            if file_content['current'] != local_content['current']:
                # the version is different than the current on github
                # update it if you are seeing this warning
                log.warn(f'There is a new update available. Download it from https://github.com/djlorenzouasset/Fortnite-Sections-Bot.\n\nCurrent version: {local_content["current"]}\nNew version: {file_content["current"]}')
                await self.write(file='version.json', content=file_content, is_json=True)
