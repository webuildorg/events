import re
import math
from . import requestor


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


def good_bad_group_ids(groups_data, blacklist_tokens=[]):
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
      print(group_name)
      bad_ids.append(str(gid))
    else:
      good_ids.append(str(gid))

  return good_ids, bad_ids


def get_groups_events(url, params, gids, max_responses=200):
  num_groups_batch = math.ceil(len(gids) / math.ceil(len(gids) / max_responses))

  i = 0
  offset = 0
  payload = params.copy()
  events_data = []
  while i < len(gids):
    payload['group_id'] = ','.join(gids[i:i+num_groups_batch])
    payload['offset'] = offset
    resp = requestor.get_json(url, payload)

    if not resp:
      continue

    meta = resp['meta']
    if meta['total_count'] > meta['count'] and meta['count'] == max_responses:
      offset += 1
    else:
      offset = 0
      i += num_groups_batch

    #print(meta['count'], meta['total_count'], i, offset)
    events_data += resp['results']

  return events_data
