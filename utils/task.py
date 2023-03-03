import os

from typing import List, Optional

from models.settings import Settings, Auth
from rest.requests import Requests

from .util import Util
from .twitter import TwitterClient


class TimelineUpdates:
    def __init__(self, util: Util, settings: Settings, requests: Requests, twitter: TwitterClient):
        """
        Task for check timeline updates.
        """
        self.util: Util = util
        self.settings: Settings = settings
        self.auth: Auth = settings.auth
        self.log: Util.log = util.log
        self.requests: Requests = requests
        self.twitter: TwitterClient = twitter


    async def check_timeline(self) -> None:
        """
        Check timeline and FortniteContent
        """
        self.log.info('Checking new timeline updates')

        fortnite_content = await self.requests.get_fortnite_content()
        timeline = await self.requests.get_timeline()


        if fortnite_content and timeline:
            try:
                cache_expire: str = timeline['channels']['client-events']['cacheExpire']
                dailyStoreEnd: str = timeline['channels']['client-events']['states'][-1]['state']['dailyStoreEnd']
                sectionsList: dict = timeline['channels']['client-events']['states'][-1]['state']['sectionStoreEnds']
                sectionIds: List[dict] = fortnite_content['shopSections']['sectionList']['sections']


                # check if there are new sections
                if await self.diff_expire(cache_expire=cache_expire):
                    if await self.diff_sections(expire=dailyStoreEnd):
                        self.log.warn(f'New sections detected: {dailyStoreEnd}')
                        await self.util.write(file='cache/timeline.json', content=timeline, is_json=True)

                        sections = await self.make_sections(sections=sectionsList, sectionIds=sectionIds)
                        sections_names: List[str] = []

                        for section in sections:
                            if not section: # for some sections, the name is empty, so we skip it
                                continue

                            if sections.count(section) == 1 and not self.settings.sections.show_if_one: # you can choose that if the section is only one, the name will be without the (x1)
                                sections_names.append(f'• {section}')
                            else:
                                sections_names.append(f'• {section} (x{sections.count(section)})')


                        finished: str = '\n'.join(set(sections_names))
                        text: str = ''

                        if self.settings.sections.title != '':
                            text += f'{self.settings.sections.title}\n'

                        text += f'{finished}' # add it in the center of the tweet

                        if self.settings.sections.footer != '':
                            text += f'\n{self.settings.sections.footer}'


                        # post tweet
                        if self.settings.twitter.enabled:
                            if self.settings.sections.image:
                                image: str = self.settings.sections.image

                                if os.path.isfile(image):
                                    self.twitter.update_status_with_media(
                                        status=text,
                                        filename=image
                                    )
                                    self.log.info('Tweeted new sections')

                                else:
                                    self.log.error(f'Image {image} not found, posting without image')
                                    self.twitter.update_status(status=text)

                            else:
                                self.twitter.update_status(status=text)
                                self.log.info('Tweeted new sections')
            
                        else:
                            self.log.info('Twitter is disabled, skipping tweet')


            except IndexError:
                pass


            except Exception as e:
                self.log.error(f'Error while checking timeline updates: {e}')
                return 



    async def diff_expire(self, cache_expire: str) -> Optional[bool]:
        """
        Check if cacheExpire is different from the last one.
        """

        old = await self.util.open(file='cache/timeline.json', mode='r', is_json=True)

        old_cache_expire: str = old['channels']['client-events']['cacheExpire']

        if old_cache_expire != cache_expire:
            return True
        


    async def diff_sections(self, expire: str) -> Optional[bool]:
        """
        Check if dailyStoreEnd is different from the old one.
        """

        old = await self.util.open(file='cache/timeline.json', mode='r', is_json=True)

        old_expire: str = old['channels']['client-events']['states'][-1]['state']['dailyStoreEnd']

        if old_expire != expire:
            return True
    

    async def make_sections(self, sections: List[dict], sectionIds: List[dict]) -> List[str]:
        """ 
        make the sections list 

        return a list of sections names

        """

        localization = await self.util.open(file='utils/localization.json', mode='r', encoding='utf-8', is_json=True)

        sectionsNames: List[dict] = [section for section in sectionIds if "sectionDisplayName" in section]
        actives: List[str] = [section for section in sections]
        display_names: List[str] = [section['sectionDisplayName'] for section in sectionsNames if section['sectionId'] in actives]


        # add some names because epic add only the sectionId for some sections

        if "Featured2" in actives:
            display_names.append(localization["Featured"][self.settings.language])
        if "Featured3" in actives:
            display_names.append(localization["Featured"][self.settings.language])
        if "Featured4" in actives:
            display_names.append(localization["Featured"][self.settings.language])
        if "Daily2" in actives:
            display_names.append(localization["Daily"][self.settings.language])
        if "Special2" in actives:
            display_names.append(localization["Special"][self.settings.language])

        return display_names