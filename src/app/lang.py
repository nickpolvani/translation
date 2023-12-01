from enum import Enum
from typing import List

class Language(Enum):
    ENGLISH = 'eng'
    ITALIAN = 'ita'
    FRENCH = 'fra'
    GERMAN = 'deu'
    SPANISH = 'spa'
    PORTUGUESE = 'por'

    def __str__(self):
        # give the complete name when printing
        if self.value == 'eng':
            return 'English'
        elif self.value == 'ita':
            return 'Italian'
        elif self.value == 'fra':
            return 'French'
        elif self.value == 'deu':
            return 'German'
        elif self.value == 'spa':
            return 'Spanish'
        elif self.value == 'por':
            return 'Portuguese'
        else:
            raise ValueError(f"Language {self.value} is not supported.")
        
def get_language_from_name(language:str) -> Language:
    if language == 'English':
        return Language.ENGLISH
    elif language == 'Italian':
        return Language.ITALIAN
    elif language == 'French':
        return Language.FRENCH
    elif language == 'German':
        return Language.GERMAN
    elif language == 'Spanish':
        return Language.SPANISH
    elif language == 'Portuguese':
        return Language.PORTUGUESE
    else:
        raise ValueError(f"Language {language} is not supported.")

def get_language_from_lang_code(language:str) -> Language:
    if language == Language.ENGLISH.value:
        return Language.ENGLISH
    elif language == Language.ITALIAN.value:
        return Language.ITALIAN
    elif language == Language.FRENCH.value:
        return Language.FRENCH
    elif language == Language.GERMAN.value:
        return Language.GERMAN
    elif language == Language.SPANISH.value:
        return Language.SPANISH
    elif language == Language.PORTUGUESE.value:
        return Language.PORTUGUESE
    else:
        raise ValueError(f"Language {language} is not supported.")


def get_available_languages() -> List[Language]:
    """
    Returns a list of the available languages.

    Returns:
        list: The list of available languages.
    """
    return [language for language in Language]