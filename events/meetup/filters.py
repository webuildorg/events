import re
from bs4 import BeautifulSoup
from gensim.parsing.preprocessing import STOPWORDS

PAT_ALPHABETIC = re.compile(r'(((?![\d])\w)+)', re.UNICODE)
URL_REGEX = re.compile(r'https?:\/\/.*\.\w{2,10}', re.UNICODE)


def simple_tokenize(text):
    """Tokenize input test using :const:`gensim.utils.PAT_ALPHABETIC`.
    Parameters
    ----------
    text : str
        Input text.
    Yields
    ------
    str
        Tokens from `text`.
    """
    for match in PAT_ALPHABETIC.finditer(text.lower()):
        yield match.group()


def tokenize(text):
    """Tokenize input test after cleaning up html tags
    """
    soup = BeautifulSoup(text, 'html.parser')
    cleaned_text = re.sub(URL_REGEX, '', soup.get_text())
    for match in PAT_ALPHABETIC.finditer(cleaned_text.lower()):
        part = match.group()
        if len(part) > 2 and part not in STOPWORDS and part not in ['https']:
            yield part


def is_good_event_name(event, blacklist_tokens):
    return len(blacklist_tokens & frozenset(simple_tokenize(event['name']))) == 0


def is_valid_venue(event, country):
    return ('fee' not in event and 'venue' in event and 'description' in event and
        event.get('venue', {}).get('country', '').lower() == country.lower())


def has_valid_duration(event, max_hours=8):
    # Convert duration from milliseconds to hours
    return event.get('duration', 0) / 3600000 <= max_hours


def is_valid_event(event, blacklist_tokens=frozenset(), country='sg', max_hours=8):
    return (is_good_event_name(event, blacklist_tokens) and
        is_valid_venue(event, country) and
        has_valid_duration(event, max_hours))


def get_good_events(events, blacklist_tokens, country, max_event_hours):
    return filter(lambda e: is_valid_event(e, blacklist_tokens, country, max_event_hours), events)


def get_bad_events(events, blacklist_tokens, country, max_event_hours):
    return filter(lambda e: not is_valid_event(e, blacklist_tokens, country, max_event_hours), events)
