import re

PAT_ALPHABETIC = re.compile(r'(((?![\d])\w)+)', re.UNICODE)


def tokenize(text):
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
  for match in PAT_ALPHABETIC.finditer(text):
    yield match.group()


def is_good_event_name(event, blacklist_tokens):
    return len(blacklist_tokens & frozenset(tokenize(event['name']))) == 0


def is_valid_venue(event, country):
    return ('fee' not in event and 'venue' in event and 'description' in event
        and event.get('venue', {}).get('country', '').lower() == country.lower())


def has_valid_duration(event, max_hours=8):
  # Convert duration from milliseconds to hours
  return event.get('duration', 0) / 3600000 < max_hours


def is_valid_event(event, blacklist_tokens=frozenset(), country='sg', max_hours=8):
  return (is_good_event_name(event, blacklist_tokens)
    and is_valid_venue(event, country)
    and has_valid_duration(event, max_hours))


def filter_good_events(events, blacklist_tokens, country, max_event_hours):
  return filter(lambda event: is_valid_event(event, blacklist_tokens, country, max_event_hours), events)
