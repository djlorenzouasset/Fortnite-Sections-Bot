import tweepy
from tweepy.models import Media
from typing import Optional, List

class TwitterAPI(tweepy.API):
    def __init__(
        self, apiKey: str, apiSecret: str, accessToken: str, accessTokenSecret: str
    ):
        # v1.1 API - Deprecated, you can only upload media with it
        # https://developer.twitter.com/en/docs/twitter-api/v1

        auth = tweepy.OAuthHandler(apiKey, apiSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        super().__init__(
            auth
        )

    def upload(self, media: str) -> Optional[Media]:
        try:
            # upload the media to twitter 
            # and return the data class 
            # ~tweepy.models.Media
            return super().media_upload(
                media
            )
        except Exception as e:
            raise e
        
class TwitterClient(tweepy.Client):
    def __init__(
        self, apiKey: str, apiSecret: str, accessToken: str, accessTokenSecret: str
    ):
        # v2.0 API - Use this for create tweets only
        # other features are for paying users
        super().__init__(
            consumer_key=apiKey,
            consumer_secret=apiSecret,
            access_token=accessToken,
            access_token_secret=accessTokenSecret
        )

    def new(
        self, text: str = None, media: Media = None   
    ) -> None:
        # twitter want a list of media ids
        media_ids: List[int] = []
        media_ids.append(media.media_id_string)

        # create the tweet
        super().create_tweet(
            text=text,
            media_ids=media_ids
        )