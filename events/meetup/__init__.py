import itertools
from . import gatherer, formatter, filters


class Meetup(object):
    def __init__(self, config):
        self.config = config
        self.groups = []
        self.good_indexes = []
        self.bad_indexes = []
        self.events_data = []

    def grab_events(self):
        config = self.config
        groups = gatherer.get_groups(config.meetup['groups_url'], config.meetup['params'].copy())
        print('Gathered', len(groups), 'groups')

        good_ids, multi_bad_ids, good_indexes, bad_indexes = gatherer.good_bad_group_ids(
            groups, config.multi_enhanced_blacklist_tokens, config.token_thresholds)
        bad_ids = list(itertools.chain.from_iterable(multi_bad_ids))
        print('Found {} good meetup groups, {} bad meetup groups'.format(len(good_ids), len(bad_ids)))

        events_data = gatherer.get_groups_events(config.meetup['events_url'],
            config.meetup['params'].copy(), good_ids, config.meetup['max_meetup_responses'])
        print('Found {} good meetup events'.format(len(events_data)))

        good_events = list(filters.get_good_events(events_data, config.blacklist_tokens,
                            config.meetup['params']['country'], config.meetup['max_event_hours']))
        print('Filtered {} down to {} good meetup events'.format(len(events_data), len(good_events)))

        good_filtered_events = list(filters.remove_duplicate_events(good_events))
        print('Removed good duplicate events from {} to {}'.format(len(good_events), len(good_filtered_events)))

        self.groups = groups
        self.events_data = events_data
        self.good_indexes = good_indexes
        self.bad_indexes = bad_indexes

        return formatter.format_events(
            good_filtered_events,
            config.meetup['params']['location'],
            config.meetup['display_time_format'])

    def good_groups(self):
        return [formatter.format_group(self.groups[gid]) for gid in self.good_indexes]

    def bad_groups(self):
        return [formatter.format_group(self.groups[gid]) for gid in self.bad_indexes]

    def bad_events(self):
        config = self.config
        bad_events = list(filters.get_bad_events(self.events_data, config.blacklist_tokens,
                            config.meetup['params']['country'], config.meetup['max_event_hours']))
        return formatter.format_events(
            bad_events,
            config.meetup['params']['location'],
            config.meetup['display_time_format'])
