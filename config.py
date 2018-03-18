import os

blacklist_tokens = frozenset([
  'ethereum', 'blockchain', 'bitcoin', 'ico', 'crypto trading',
  'cryptocurrency', 'cryptocurrencies', 'money', 'gold',
  'business', 'investor', 'entrepreneurs'])

meetup = {
  'groups_url': 'https://api.meetup.com/find/groups',
  'events_url': 'https://api.meetup.com/2/events',
  'max_event_hours': 8,
  'max_meetup_responses': 200,

  'params': {
    'key': os.environ['MEETUP_API_KEY'],
    'country': 'SG',
    'city': 'Singapore',
    'location': 'Singapore',
    'category': 34
  }
}
