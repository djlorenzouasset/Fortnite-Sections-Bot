import asyncio
import os
import coloredlogs
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from globals import Globals
from utils.util import Utils
from utils.twitter import TwitterAPI, TwitterClient
from utils.task import TimelineUpdates
from rest.requests import Requests
from models.settings import Settings
from models.errors import MissingAuthCredentials, MissingTwitterCredentials, LanguageNotFound, AuthError

log = logging.getLogger('FortniteShopSections')
coloredlogs.install(fmt="[%(name)s][%(asctime)s][%(levelname)s] %(message)s", datefmt="%d-%m-%Y %H:%M:%S", logger=log)
logging.basicConfig(
    filename=f'utils/log.txt',
    format="[%(name)s][%(asctime)s][%(levelname)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

class Main:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.twitter: TwitterAPI = None
        self.tweet: TwitterClient = None

    async def start(self):
        os.system('cls')
        os.system(
            'TITLE Fortnite Sections Bot - Made by @djlorenzouasset'
        )

        log.info('Loading components')

        # check if config file exists, if not the application exit
        if not os.path.isfile('utils/settings.json'):
            log.error('Config file not found. The application will now exit.')
            await asyncio.sleep(5)
            exit()

        # initialize settings in a class
        Globals.SETTINGS = Settings(
            await Utils.open(
                file='utils/settings.json', mode='r', encoding='utf-8', is_json=True
            )
        )

        try:
            Utils.check_settings(Globals.SETTINGS) # check settings
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
        if Globals.SETTINGS.twitter.enabled:
            data = Globals.SETTINGS.twitter
            self.twitter = TwitterAPI(data.apiKey, data.apiSecret, data.accessToken, data.accessTokenSecret)
            self.tweet = TwitterClient(data.apiKey, data.apiSecret, data.accessToken, data.accessTokenSecret)

        try:
            # create the authorization
            # for epic games services
            await Requests.create_token()
        except AuthError as e:
            log.error(f'An error occurred while creating a new token: {e}. If you are having issues, please open an issue on GitHub.')
            await asyncio.sleep(5)
            exit()

        if Globals.SETTINGS.seconds == 0 or Globals.SETTINGS.seconds == '':
            Globals.SETTINGS.seconds = 50
        elif isinstance(Globals.SETTINGS.seconds, str):
            Globals.SETTINGS.seconds = int(Globals.SETTINGS.seconds)
        
        self.scheduler.add_job(self.check_token, 'interval', seconds=10) # dont touch this schedule
        self.scheduler.add_job(self.timeline_checker, 'interval', seconds=Globals.SETTINGS.seconds) # set how much seconds you want to check for updates
        self.scheduler.start()
        os.system('cls')
        log.info('Scheduler started!')

    async def timeline_checker(self):
        try:
            await TimelineUpdates(self.twitter, self.tweet).check_timeline()
        except Exception as e:
            log.error(e)

    async def check_token(self):
        if Globals.SETTINGS.auth.is_expired:
            try:
                log.warn('Token expired, refreshing..')
                await Requests.refresh_token()
                log.info('Token refreshed.')
            except AuthError as e:
                log.error(f'An error occurred while refreshing the token: {e}. Please restart the program. If you are having issues, please open an issue on GitHub.')

try:
    loop = asyncio.new_event_loop()
    loop.run_until_complete(Main().start())
    loop.run_forever()
except KeyboardInterrupt:
    pass