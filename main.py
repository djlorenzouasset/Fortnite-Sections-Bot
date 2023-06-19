import asyncio
import logging
import coloredlogs
import os 

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.util import Util
from utils.twitter import TwitterAPI, TwitterClient
from utils.task import TimelineUpdates
from rest.requests import Requests
from models.settings import Settings, Twitter
from models.errors import MissingAuthCredentials, MissingTwitterCredentials, LanguageNotFound, AuthError

# logger for the program
log: logging.Logger = logging.getLogger('FortniteShopSections')

class Main:
    def __init__(self):
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler()
        self.util: Util = Util()
        self.settings: Settings
        self.twitter: TwitterAPI
        self.tweet: TwitterClient
        self.requests: Requests
        # install the logger colors
        coloredlogs.install(fmt="[%(name)s][%(asctime)s][%(levelname)s] %(message)s", datefmt="%d-%m-%Y %H:%M:%S", logger=log)

    async def start(self):
        os.system('cls')
        os.system(
            'TITLE Fortnite Sections Bot - Made by ᴅᴊʟᴏʀ3xᴢo (@djlorenzouasset)'
        )

        log.info('Loading components..')
        # check if the program is updated
        await self.util.check_updates()

        if not os.path.isfile('utils/config.json'): # check if config file exists, if not the application exit.            
            log.error('Config file not found. The application will now exit.')
            await asyncio.sleep(5)
            exit()

        # initialize settings in a class
        self.settings = Settings(await self.util.open(file='utils/config.json', mode='r', encoding='utf-8', is_json=True))

        try:
            await self.util.check_settings(settings=self.settings) # check settings
            await self.initialize() # initialize the program
        except LanguageNotFound:
            log.error('The language you have selected is not valid.')
            await asyncio.sleep(5)
            exit()
        except MissingAuthCredentials:
            log.error('You have not provided the required Auth credentials, opened the settings file for change your settings.')
            await asyncio.sleep(5)
            exit()
        except MissingTwitterCredentials:
            log.error('You have not provided the required Twitter credentials, opened the settings file for change your settings.')
            await asyncio.sleep(5)
            exit()

    async def initialize(self):
        if self.settings.twitter.enabled:
            data: Twitter = self.settings.twitter
            self.twitter = TwitterAPI(data.apiKey, data.apiSecret, data.accessToken, data.accessTokenSecret)
            self.tweet = TwitterClient(data.apiKey, data.apiSecret, data.accessToken, data.accessTokenSecret)

        # create a new token
        self.requests = Requests(self.util, self.settings)
        try:
            # create the authorization
            # for epic games services
            await self.requests.create_token()
        except AuthError as e:
            log.error(f'An error occurred while creating a new token: {e}. If you are having issues, please open an issue on GitHub.')
            await asyncio.sleep(5)
            exit()
        
        log.info('Want start the checks task? (y/n)')
        choice = input() # empty input for start the task
        if choice.lower() == 'y':
            # start the scheduler
            if self.settings.seconds == 0 or self.settings.seconds == '':
                self.settings.seconds = 50
            elif isinstance(self.settings.seconds, str):
                self.settings.seconds = int(self.settings.seconds)
            
            self.scheduler.add_job(self.timeline_checker, 'interval', seconds=self.settings.seconds) # set how much seconds you want to check for updates
            self.scheduler.start()
            log.info('Scheduler started!')
        else:
            log.info('Exiting..')
            exit()

    async def timeline_checker(self):
        try:
            await TimelineUpdates(self.util, self.settings, self.requests, self.twitter, self.tweet).check_timeline()
        except Exception as e:
            log.error(e)

try:
    loop = asyncio.new_event_loop()
    loop.run_until_complete(Main().start())
    loop.run_forever()
except KeyboardInterrupt:
    pass
