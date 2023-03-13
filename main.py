import asyncio
import logging
import coloredlogs
import os 

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.util import Util
from utils.twitter import TwitterClient
from utils.task import TimelineUpdates

from rest.requests import Requests
from models.settings import Settings, Twitter
from models.errors import MissingAuthCredentials, MissingTwitterCredentials, LanguageNotFound, AuthError


class Main:
    def __init__(self):
        self.log: logging.Logger = logging.getLogger(__name__)
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler()
        self.util: Util = Util(self.log)

        self.settings: Settings = None
        self.twitter: TwitterClient = None
        self.requests: Requests = None
    
        coloredlogs.install(fmt="[%(asctime)s][%(levelname)s] %(message)s", datefmt="%H:%M:%S", logger=self.log)


    async def start(self):
        """
        Start the program
        """
        
        os.system('cls')
        os.system(
            'TITLE Fortnite Sections Bot - Made by @djlorenzouasset'
        )

        self.log.info('Loading components..')

        if not os.path.isfile('utils/config.json'): # check if config file exists, if not the application exit.            
            self.log.error('Config file not found. The application will now exit. If you are having issues, please open an issue on GitHub.')
            await asyncio.sleep(5)
            exit()


        # initialize settings in a class
        self.settings = Settings(await self.util.open(file='utils/config.json', mode='r', encoding='utf-8', is_json=True))


        try:
            await self.util.check_settings(settings=self.settings) # check settings
            await self.initialize() # initialize the program

        except LanguageNotFound:
            self.log.error('The language you have selected is not valid. If you are having issues, please open an issue on GitHub.')
            await asyncio.sleep(5)
            exit()

        except MissingAuthCredentials:
            self.log.error('You have not provided the required Auth credentials. If you are having issues, please open an issue on GitHub.')
            await asyncio.sleep(5)
            exit()

        except MissingTwitterCredentials:
            self.log.error('You have not provided the required Twitter credentials. If you are having issues, please open an issue on GitHub.')
            await asyncio.sleep(5)
            exit()


    async def initialize(self):
        """
        Initialize the program
        """

        if self.settings.twitter.enabled:
            data: Twitter = self.settings.twitter

            self.twitter = TwitterClient(data.apiKey, data.apiSecret, data.accessToken, data.accessTokenSecret)

        # create a new token
        self.requests = Requests(self.util, self.settings)

        try:
            await self.requests.create_token()
        except AuthError as e:
            self.log.error(f'An error occurred while creating a new token: {e}. If you are having issues, please open an issue on GitHub.')
            await asyncio.sleep(5)
            exit()
        
        self.log.info('Press enter for start the task')
        input() # empty input for start the task

        # start the scheduler
        if self.settings.seconds == 0 or self.settings.seconds == '':
            self.settings.seconds = 50
        elif isinstance(self.settings.seconds, str):
            self.settings.seconds = int(self.settings.seconds)

        self.scheduler.add_job(self.timeline_checker, 'interval', seconds=self.settings.seconds) # set how much seconds you want to check for updates
        self.scheduler.start()
        self.log.info('Scheduler started!')


    async def timeline_checker(self):
        """
        Start the timeline updates task
        """
        try:
            await TimelineUpdates(self.util, self.settings, self.requests, self.twitter).check_timeline()
        except Exception as e:
            print(e)
        

try:
    loop = asyncio.new_event_loop()
    loop.run_until_complete(Main().start())
    loop.run_forever()
except KeyboardInterrupt:
    pass
