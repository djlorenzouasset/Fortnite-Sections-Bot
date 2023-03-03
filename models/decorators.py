from .errors import AuthError

def is_token_valid(func):
    """
    decorator for check token expiration
    """

    async def wrapper(self, *args, **kwargs):
        if self.settings.auth.is_expired:
            try:
                self.log.info('Token expired, refreshing..')
                await self.refresh_token()
                
            except AuthError as e:
                self.log.error(f'An error occurred while refreshing the token: {e}. Please restart the program. If you are having issues, please open an issue on GitHub.')

        return await func(self, *args, **kwargs)
    
    return wrapper