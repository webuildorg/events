import os
from events import spellchecker

blockchain_blacklist_tokens = frozenset([
    'ethereum', 'blockchain', 'bitcoin', 'ico', 'ledger',
    'crypto', 'cryptocurrency', 'money', 'gold'])

business_blacklist_tokens = frozenset([
    'business', 'enterprise', 'entrepreneur', 'entrepreneurship',
    'executive', 'founder', 'investor'])


multi_blacklist_tokens = [
    blockchain_blacklist_tokens,
    business_blacklist_tokens
]

# Enhance the blacklist tokens by expanding the set with possible typos
enhanced_blockchain_blacklist_tokens = set()
for token in blockchain_blacklist_tokens:
    if len(token) < 6:
        enhanced_blockchain_blacklist_tokens.add(token)
    else:
        enhanced_blockchain_blacklist_tokens = enhanced_blockchain_blacklist_tokens.union(
            spellchecker.typos(token))

enhanced_business_blacklist_tokens = set()
for token in business_blacklist_tokens:
    enhanced_business_blacklist_tokens = enhanced_business_blacklist_tokens.union(
        spellchecker.typos(token))

multi_enhanced_blacklist_tokens = [
    enhanced_blockchain_blacklist_tokens,
    enhanced_business_blacklist_tokens
]

print('{} blacklist tokens'.format(
    len(enhanced_blockchain_blacklist_tokens) + len(enhanced_business_blacklist_tokens)))

# Minimum number of tokens to blacklist a group or event in each topic [blockchain, bussines]
token_thresholds = [1, 4]

blacklist_tokens = frozenset(list(blockchain_blacklist_tokens) + list(business_blacklist_tokens))

meetup = {
    'groups_url': 'https://api.meetup.com/find/groups',
    'events_url': 'https://api.meetup.com/2/events',
    'max_event_hours': 12,
    'max_meetup_responses': 150,
    'display_time_format': '%d-%b, %a, %I:%M %p',

    'params': {
        'key': os.environ['MEETUP_API_KEY'],
        'country': 'SG',
        'location': 'Singapore',
        'category': 34
    }
}
