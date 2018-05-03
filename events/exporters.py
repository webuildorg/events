import datetime
from icalendar import Calendar, Event, vDatetime
from bs4 import BeautifulSoup


def display(cal):
    return cal.to_ical().decode('utf-8').strip().split('\r\n')


ISO8601_format = '%Y-%m-%dT%H:%M:%SZ'
def events_to_ics(events):
    cal = Calendar()
    cal.add('prodid', '-//We Build Org//calendar//EN')
    cal.add('version', '2.0')
    cal.add('name', 'We Build SG')
    cal.add('X-WR-CALNAME', 'We Build SG')
    cal.add('description', 'Free tech events in Singapore')

    for event in events:
        description = event['description']
        soup = BeautifulSoup(description, 'html.parser')
        paragraphs = soup.find_all('p')
        if len(paragraphs) > 0:
            for b in soup.find_all('br'):
                b.replace_with('\n')
            description = '\n\n'.join([p.get_text() for p in paragraphs])
            description += '\n\nRSVP count: {}'.format(event['rsvp_count'])

        start_time = datetime.datetime.strptime(event['start_time'], ISO8601_format)
        start_time += datetime.timedelta(seconds=event['utc_offset'])
        cal_event = Event()
        cal_event['uid'] = event['id']
        cal_event['summary'] = event['name']
        cal_event['dtstamp'] = vDatetime(datetime.datetime.utcnow())
        cal_event['dtstart'] = vDatetime(start_time)
        cal_event['dtend'] = vDatetime(start_time + datetime.timedelta(seconds=event['duration']))
        cal_event['url'] = event['url']
        cal_event['location'] = event['location']
        cal_event['description'] = description
        cal.add_component(cal_event)

    return cal.to_ical()
