from . import gatherer, formatter, filters

def grab_events(config):
    groups = gatherer.get_groups(config.meetup['groups_url'], config.meetup['params'].copy())
    print('Gathered', len(groups), 'groups')
    good_ids, bad_ids = gatherer.good_bad_group_ids(groups, config.blacklist_tokens)
    print('Found {} good meetup groups, {} bad meetup groups'.format(len(good_ids), len(bad_ids)))
    events_data = gatherer.get_groups_events(config.meetup['events_url'],
      config.meetup['params'].copy(), good_ids, config.meetup['max_meetup_responses'])
    print('Found {} good meetup events'.format(len(events_data)))
    good_events = list(filters.filter_good_events(events_data, config.blacklist_tokens,
                            config.meetup['params']['country'], config.meetup['max_event_hours']))
    print('Filtered {} down to {} good meetup events'.format(len(events_data), len(good_events)))
    return formatter.format_events(good_events, config.meetup['params']['location'])

