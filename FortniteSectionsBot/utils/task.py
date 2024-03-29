import os
import logging

from typing import List, Optional
from globals import Globals
from rest.requests import Requests
from .util import Utils
from .twitter import TwitterAPI, TwitterClient

log: logging.Logger = logging.getLogger('FortniteShopSections.Task')

class TimelineUpdates:
    def __init__(
        self, twitter: TwitterAPI = None, tweet: TwitterClient = None
    ):
        self.twitter: Optional[TwitterAPI] = twitter
        self.tweet: Optional[TwitterClient] = tweet

    async def check_timeline(self) -> None:
        log.info('Checking new timeline updates')
        # data getters for the task
        fortnite_content = await Requests.get_fortnite_content()
        timeline = await Requests.get_timeline()

        if fortnite_content and timeline:
            try:
                cache_expire: str = timeline['channels']['client-events']['cacheExpire']
                dailyStoreEnd: str = timeline['channels']['client-events']['states'][1]['state']['dailyStoreEnd']
                sectionsList: dict = timeline['channels']['client-events']['states'][1]['state']['sectionStoreEnds']
                sectionIds: List[dict] = fortnite_content['shopSections']['sectionList']['sections']
            except IndexError:
                return

            try:
                # check if there are new sections
                if await self.diff_expire(cache_expire=cache_expire):
                    if await self.diff_sections(expire=dailyStoreEnd):
                        log.warn(f'New sections detected: {dailyStoreEnd}')
                        # write cache file
                        await Utils.write(file='cache/timeline.json', content=timeline, is_json=True)
                        # make sections list
                        sections = await self.make_sections(sections=sectionsList, sectionIds=sectionIds)
                        sections_names: List[str] = []

                        # make post text
                        for section in sections:
                            if not section: # for some sections, the name is empty, so we skip it
                                continue
                            if sections.count(section) == 1 and not Globals.SETTINGS.sections.show_if_one:
                                # you can choose that if the section is only one, the name will be without the (x1)
                                sections_names.append(f'• {section}')
                            else:
                                sections_names.append(f'• {section} (x{sections.count(section)})')

                        # don't change nothing here. If you have to change the tweet text
                        # just go in the settings.json file and change the title and the footer
                        finished: str = '\n'.join(set(sections_names))
                        text: str = ''

                        # add the title if present
                        if Globals.SETTINGS.sections.title != '':
                            text += f'{Globals.SETTINGS.sections.title}\n'

                        # add sections in the center of the tweet
                        text += f'{finished}'

                        # add the footer if present
                        if Globals.SETTINGS.sections.footer != '':
                            text += f'\n{Globals.SETTINGS.sections.footer}'

                        # post tweet
                        if Globals.SETTINGS.twitter.enabled:
                            # the tweet media can be None
                            have_media = None
                            if Globals.SETTINGS.sections.image:
                                image: str = Globals.SETTINGS.sections.image
                                if os.path.isfile(image):
                                    # upload the media to twitter
                                    have_media = self.twitter.upload(
                                        media=image
                                    )
                                    log.info(f'Uploaded media image from {image}')

                            # post tweet
                            self.tweet.new(
                                text=text,
                                medias=have_media
                            )
                        else:
                            log.info('Twitter is disabled, skipping tweet')

            except Exception as e:
                log.error(f'Error while checking timeline updates: {e}')
                return

    async def diff_expire(self, cache_expire: str) -> Optional[bool]:
        old = await Utils.open(file='cache/timeline.json', mode='r', is_json=True)
        old_cache_expire: str = old['channels']['client-events']['cacheExpire']
        if old_cache_expire != cache_expire:
            return True

    async def diff_sections(self, expire: str) -> Optional[bool]:
        old = await Utils.open(file='cache/timeline.json', mode='r', is_json=True)
        old_expire: str = old['channels']['client-events']['states'][-1]['state']['dailyStoreEnd']
        if old_expire != expire:
            return True

    async def make_sections(
        self, sections: List[dict], sectionIds: List[dict]
    ) -> List[str]:
        localization = await Utils.open(file='utils/localization.json', mode='r', encoding='utf-8', is_json=True)
        sectionsNames: List[dict] = [section for section in sectionIds if "sectionDisplayName" in section]
        actives: List[str] = [section for section in sections]
        display_names: List[str] = [section['sectionDisplayName'] for section in sectionsNames if section['sectionId'] in actives]

        # add some names because epic add only the sectionId for some sections
        if "Featured2" in actives:
            display_names.append(localization["Featured"][Globals.SETTINGS.language])
        if "Featured3" in actives:
            display_names.append(localization["Featured"][Globals.SETTINGS.language])
        if "Featured4" in actives:
            display_names.append(localization["Featured"][Globals.SETTINGS.language])
        if "Daily2" in actives:
            display_names.append(localization["Daily"][Globals.SETTINGS.language])
        if "Special2" in actives:
            display_names.append(localization["Special"][Globals.SETTINGS.language])

        # return the names array
        return display_names