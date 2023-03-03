import tweepy


class TwitterClient(tweepy.API):
    def __init__(self, apiKey: str, apiSecret: str, accessToken: str, accessTokenSecret: str):

        auth = tweepy.OAuthHandler(apiKey, apiSecret)
        auth.set_access_token(accessToken, accessTokenSecret)

        super().__init__(
            auth
        )