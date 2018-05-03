import re
from datetime import datetime

postcode_regex = re.compile('(?<=\D)\d{6}(\D|$)')
address_regex = re.compile('\s{2,}')


def construct_address(venue, city):
    address = ', '.join(filter(lambda x: x != '', [
        re.sub(address_regex, ' ', venue.get('name', '')).strip(' ,'),
        re.sub(address_regex, ' ', venue.get('address_1', '')).strip(' ,'),
        venue.get('address_2', '').strip(' ,')
    ]))

    has_postcode = postcode_regex.search(address)
    if city.lower() not in address.lower() and not has_postcode:
        address += ', ' + venue.get('city', '')

    return address


def format_events(events_data, city, datetime_format):
    results = []

    for event in events_data:
        venue = event.get('venue', {})
        if 'repinned' in venue:
            venue.pop('repinned')

        duration = int(event.get('duration', 0) / 1000)
        start_time = int(event['time'] / 1000)
        utc_offset = int(event['utc_offset'] / 1000)
        row = {
            'id': event['id'],
            'name': event['name'],
            'description': event.get('description'),
            'location': construct_address(venue, city),
            'venue': venue,
            'rsvp_count': event['yes_rsvp_count'],
            'rsvp_limit': event.get('rsvp_limit'),
            'waitlist_count': event.get('waitlist_count'),
            'url': event['event_url'],
            'group_id': event['group']['id'],
            'group_name': event['group']['name'],
            'group_url': 'https://meetup.com/' + event['group']['urlname'],
            'utc_offset': utc_offset,
            'duration': duration,
            'unix_start_time': start_time,
            'start_time': datetime.utcfromtimestamp(start_time).isoformat() + 'Z',
            'end_time': datetime.utcfromtimestamp(start_time + duration).isoformat() + 'Z',
            'formatted_time': datetime.utcfromtimestamp(
                start_time + utc_offset).strftime(datetime_format),
            'platform': 'meetup'
        }

        results.append(row)

    sorted(results, key=lambda x: x['start_time'])
    return results


def format_group(group, other_obj={}):
    return {
        'name': group['name'],
        'url': group['link'],
        **other_obj
    }
