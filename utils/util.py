import json
import aiofiles
import os 
import aiohttp

from models.errors import MissingAuthCredentials, MissingTwitterCredentials, LanguageNotFound
from models.settings import Settings, Twitter

class Util:
    def __init__(self, log):
        self.log = log


    
    async def open(self, file: str, mode: str = 'r', encoding: str = None, is_json: bool = False) -> str:
        """
        Open a file and return the content.

        Parameters:
            file (``str``): 
                The file to open.

            mode (``str``, *optional*): 
                The mode to open the file in. Defaults to 'r'.

            encoding (``str``, *optional*):
                The encoding to use when opening the file. Can be ``None``.

            is_json (``bool``, *optional*):
                Whether the file is a json file. Defaults to ``False``.

        Returns:
            The content of the file.

        """
        
        async with aiofiles.open(file=file, mode=mode, encoding=encoding) as f:
            if is_json:
                return json.loads(await f.read())
            else:
                return await f.read()
            


    async def write(self, file: str, content: str, mode: str = 'w', encoding: str = None, is_json: bool = False) -> None:
        """
        Write to a file.

        Parameters:
            file (``str``): 
                The file to write to.

            content (``str``): 
                The content to write to the file.

            mode (``str``, *optional*): 
                The mode to open the file in. Defaults to 'w'.

            encoding (``str``, *optional*):
                The encoding to use when opening the file. Can be ``None``.

            is_json (``bool``, *optional*):
                Whether the file is a json file. Defaults to ``False``.

        """
        
        async with aiofiles.open(file=file, mode=mode, encoding=encoding) as f:
            if is_json:
                await f.write(json.dumps(content, indent=4))
            else:
                await f.write(content)


    async def check_settings(self, settings: Settings) -> None:
        """
        Check if settings are valid.
        """

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
        """
        Check for updates.
        """

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
                self.log.warn(f'There is a new update available. Download it from https://github.com/djlorenzouasset/Fortnite-Sections-Bot.\n\nCurrent version: {local_content["current"]}\nNew version: {file_content["current"]}')
                await self.write(file='version.json', content=file_content, is_json=True)
