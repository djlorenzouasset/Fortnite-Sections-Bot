

class LanguageNotFound(Exception):
    """
    Raised when the user has not provided a valid language.
    """
    pass


class MissingAuthCredentials(Exception):
    """
    Raised when the user has not provided the Fortnite required credentials.
    """
    pass


class MissingTwitterCredentials(Exception):
    """
    Raised when the user has not provided the Twitter required credentials.
    """
    pass


class AuthError(Exception):
    """
    Raised on Epic Games Auth error.
    """
    pass