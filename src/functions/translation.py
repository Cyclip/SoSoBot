import os
import dotenv
from mezmorize import Cache
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import clipboard, json

dotenv.load_dotenv()
API_KEY = os.getenv("TRANSLATION_API")
URL = os.getenv("TRANSLATION_URL")
CHAR_LIMIT = 100

cache = Cache(CACHE_TYPE="filesystem", CACHE_DIR="translationCache")

authenticator = IAMAuthenticator(f'{API_KEY}')
lt = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticator
)

lt.set_service_url(f'{URL}')


@cache.memoize(150)
def translate(text, fromCode, toCode):
    text = text[:CHAR_LIMIT]
    t = lt.translate(text=text, model_id=f'{fromCode}-{toCode}').get_result()
    clipboard.copy(json.dumps(t, indent=2))
    return t['translations'][0]['translation']


@cache.memoize(60)
def identifyLanguage(text):
    text = text[:CHAR_LIMIT]
    identified = lt.identify('This is a language').get_result()
    return identified['languages'][0]['language']


@cache.memoize(60)
def getLanguages():
    lang = lt.list_languages().get_result()

    langDict = {}
    for i in lang['languages']:
        langDict[i['language']] = i['language_name']
    return langDict
