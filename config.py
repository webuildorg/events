import os

blockchain_blacklist_tokens = frozenset([
  'ethereum', 'blockchain', 'bitcoin', 'ico', 'crypto',
  'cryptocurrency', 'cryptocurrencies', 'money', 'gold'])

business_blacklist_tokens = frozenset([
    'business', 'investor', 'entrepreneurs', 'co-founders'])

multi_blacklist_tokens = [
    blockchain_blacklist_tokens,
    business_blacklist_tokens
]
token_thresholds = [1, 4]

blacklist_tokens = frozenset(list(blockchain_blacklist_tokens) + list(business_blacklist_tokens))

meetup = {
    'groups_url': 'https://api.meetup.com/find/groups',
    'events_url': 'https://api.meetup.com/2/events',
    'max_event_hours': 8,
    'max_meetup_responses': 150,
    'display_time_format': '%d-%b, %a, %I:%M %p',

    'params': {
        'key': os.environ['MEETUP_API_KEY'],
        'country': 'SG',
        'location': 'Singapore',
        'category': 34
    }
}
