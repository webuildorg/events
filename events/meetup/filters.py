import time
import re
import hashlib
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
    """ Tokenize input text after cleaning up html tags """
    soup = BeautifulSoup(text, 'html.parser')
    cleaned_text = re.sub(URL_REGEX, '', soup.get_text())
    for match in PAT_ALPHABETIC.finditer(cleaned_text.lower()):
        part = match.group()
        if len(part) > 2 and part not in STOPWORDS and part not in ['https']:
            yield part


def unixtimestamp_to_day(unixtime):
    """ Convert unix epoch time in seconds to day string """
    return time.strftime("%y%m%d", time.gmtime(unixtime))


def remove_duplicate_events(events):
    """ Remove duplicates based on the hash of various event strings.
        If 2 same events fall on the same day, take the event with higher rsvp count """
    hashes = {}
    events_id_set = set()
    event_hashes = [[] for e in events]

    for i, event in enumerate(events):
        event_strings = [
            event['description'],
            event['name'] + event['start_time']
        ]

        has_clashed = False
        for estr in event_strings:
            # An event is a duplicate if one of its string clashes with a previous event
            ehash = hashlib.sha1(estr.lower().encode('utf8')).hexdigest()
            event_hashes[i].append(ehash)

            if ehash in hashes:
                has_clashed = True
                clash_index = hashes[ehash]
                clash_event = events[clash_index]
                clash_eday = unixtimestamp_to_day(clash_event['unix_start_time'])
                eday = unixtimestamp_to_day(event['unix_start_time'])

                if eday == clash_eday and event['rsvp_count'] > clash_event['rsvp_count']:
                    # Replace the older duplicate event if the rsvp count is higher
                    clash_hashes = event_hashes[clash_index]
                    for chash in clash_hashes:
                        hashes[chash] = i

                    events_id_set.remove(clash_index)
                    events_id_set.add(i)
                else: # Not adding the new event
                    events_id_set.discard(i)
            elif not has_clashed:
                hashes[ehash] = i
                events_id_set.add(i)

    return (events[idx] for idx in events_id_set)


def is_good_event_name(event, blacklist_tokens):
    return len(blacklist_tokens & frozenset(simple_tokenize(event['name']))) == 0


online_words = ['http', 'online', 'webinar', 'stream']


def is_inperson_venue(venue={}):
    name = venue.get('name', '').lower()
    addr = venue.get('address_1', '').lower()

    return sum([(word in name or word in addr) for word in online_words]) == 0


def is_valid_venue(event, country):
    return ('fee' not in event and 'venue' in event and 'description' in event and
        is_inperson_venue(event.get('venue')) and
        event.get('venue', {}).get('country', '').lower() == country.lower())


def has_valid_duration(event, max_hours=8):
    # Convert duration from milliseconds to hours
    return 0 < event.get('duration', 0) / 3600000 <= max_hours


def is_valid_event(event, blacklist_tokens=frozenset(), country='sg', max_hours=8):
    return (is_good_event_name(event, blacklist_tokens) and
        is_valid_venue(event, country) and
        has_valid_duration(event, max_hours))


def get_good_events(events, blacklist_tokens, country, max_event_hours):
    return filter(lambda e: is_valid_event(e, blacklist_tokens, country, max_event_hours), events)


def get_bad_events(events, blacklist_tokens, country, max_event_hours):
    return filter(lambda e: not is_valid_event(e, blacklist_tokens, country, max_event_hours), events)
