from enum import Enum

class Language(Enum):
    ENGLISH = 'eng'
    ITALIAN = 'ita'
    FRENCH = 'fra'
    GERMAN = 'deu'
    SPANISH = 'spa'
    PORTUGUESE = 'por'


def get_available_languages() -> list:
    """
    Returns a list of the available languages.

    Returns:
        list: The list of available languages.
    """
    return [language.value for language in Language]