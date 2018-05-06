import events.meetup as meetup
import config


def dump_data(events_json, filename='data.json'):
    import json
    with open(filename, 'w') as outfile:
        json.dump(events_json, outfile, indent=2)


m = meetup.Meetup(config)
events = m.grab_events()
dump_data(events, 'sg_events.json')
