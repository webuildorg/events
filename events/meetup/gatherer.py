import re
import math
import numpy as np
from . import requestor
from .filters import tokenize, simple_tokenize


def get_groups(url, params={}):
    data = []
    resp = [0]
    i = 0

    while len(resp) != 0:
        params['offset'] = i
        resp = requestor.get_json(url, params, [])
        data += resp
        i += 1

    return data


# Separate meetup groups ids into good and bad based on blacklist tokens
# Currently not in use. See function below
def simple_good_bad_group_ids(groups_data, blacklist_tokens=[]):
    good_ids = []
    bad_ids = []

    for d in groups_data:
        bad = 0
        gid = d['id']
        group_name = d['name'].lower()
        for token in blacklist_tokens:
            if token in group_name:
                bad += 1

        if bad > 0:
            # print(group_name)
            bad_ids.append(str(gid))
        else:
            good_ids.append(str(gid))

    return good_ids, bad_ids


# Separate meetup groups ids into good and bad based on multiple blacklist tokens
def good_bad_group_ids(groups_data, multi_blacklist_tokens=[], blacklist_thresholds=[]):
    good_ids = []
    bad_ids = [[] for i in range(len(multi_blacklist_tokens))]
    good_indexes = []
    bad_indexes = []

    for group_idx, group in enumerate(groups_data):
        gid = str(group['id'])
        bad_counts = [0] * len(multi_blacklist_tokens)

        # Check the group topics for blacklist tokens
        for topic in group['topics']:
            for name in topic['name'].lower().split(' '):
                for i, blacklist_tokens in enumerate(multi_blacklist_tokens):
                    if name in blacklist_tokens:
                        bad_counts[i] += 1

        # Add to the bad ids if no. of word topics exceed blacklist threshold
        bad_count_idx = np.argmax(bad_counts)
        if bad_counts[bad_count_idx] > blacklist_thresholds[bad_count_idx]:
            bad_ids[np.argmax(bad_counts)].append(gid)
            bad_indexes.append(group_idx)
            continue

        # Reset the counts for the name and description checking
        bad_counts = [0] * len(multi_blacklist_tokens)
        # Check the group name + audience for blacklist tokens
        group_name = group['name'].lower() + ' ' + group['who'].lower()

        for name_token in simple_tokenize(group_name):
            for i, blacklist_tokens in enumerate(multi_blacklist_tokens):
                if name_token in blacklist_tokens:
                    bad_counts[i] += 1

        # Add group id to the bad ids if group name was blacklisted
        if max(bad_counts) > 0:
            bad_ids[np.argmax(bad_counts)].append(gid)
            bad_indexes.append(group_idx)
            continue

        # Next, check the group description for blacklist tokens
        description = list(tokenize(group['description']))
        for des_token in description:
            for i, blacklist_tokens in enumerate(multi_blacklist_tokens):
                if des_token in blacklist_tokens:
                    bad_counts[i] += 1

        # Add to the bad ids if no. of description tokens exceed blacklist threshold
        bad_count_idx = np.argmax(bad_counts)
        if bad_counts[bad_count_idx] > blacklist_thresholds[bad_count_idx]:
            bad_ids[bad_count_idx].append(gid)
            bad_indexes.append(group_idx)
            continue

        good_ids.append(gid)
        good_indexes.append(group_idx)

    return good_ids, bad_ids, good_indexes, bad_indexes


def get_groups_events(url, params, gids, max_responses=200):
    if len(gids) == 0:
        print('No group ids supplied')
        return []

    num_groups_batch = math.ceil(len(gids) / math.ceil(len(gids) / max_responses))

    i = 0
    offset = 0
    cur_count = 0
    payload = params.copy()
    events_data = []
    while i < len(gids):
        payload['group_id'] = ','.join(gids[i:i + num_groups_batch])
        payload['offset'] = offset
        resp = requestor.get_json(url, payload)

        if not resp:
            continue

        meta = resp['meta']
        cur_count += meta['count']
        # print(meta['count'], cur_count, meta['total_count'], i, offset)

        if meta['total_count'] > cur_count:
            offset += 1
        else:
            offset = 0
            cur_count = 0
            i += num_groups_batch

        events_data += resp['results']

    return events_data
