import re
import math
import numpy as np
from . import requestor
from .filters import tokenize

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

    for d in groups_data:
        gid = str(d['id'])
        bad_counts = [0] * len(multi_blacklist_tokens)

        # Check the group name for blacklist tokens
        group_name = d['name'].lower()
        for i, tokens in enumerate(multi_blacklist_tokens):
            for token in tokens:
                if token in group_name:
                    bad_counts[i] += 1

        # Add group id to the bad ids if group name was blacklisted
        if max(bad_counts) > 0:
            bad_ids[np.argmax(bad_counts)].append(gid)
            continue

        # Next, check the group description for blacklist tokens
        description = list(tokenize(d['description']))
        for des_token in description:
            for i, blacklist_tokens in enumerate(multi_blacklist_tokens):
                if des_token in blacklist_tokens:
                    bad_counts[i] += 1

        bad_count_idx = np.argmax(bad_counts)
        if max(bad_counts) > blacklist_thresholds[bad_count_idx]:
            bad_ids[bad_count_idx].append(gid)
            continue

        good_ids.append(gid)

    return good_ids, bad_ids


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
