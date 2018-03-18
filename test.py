import meetup
import config


def dump_data(events_json, filename='data.json'):
    import json
    with open(filename, 'w') as outfile:
        json.dump(events_json, outfile, indent=2)



events = meetup.grab_events(config)
dump_data(events, 'paris_events.json')
