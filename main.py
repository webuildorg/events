import config
from meetup import gatherer, formatter, filters
from flask import Flask, jsonify

app = Flask(__name__)

def grab_meetup_events(config):
  groups = gatherer.get_groups(config.meetup['groups_url'], config.meetup['params'].copy())
  print('Gathered', len(groups), 'groups')
  good_ids, bad_ids = gatherer.good_bad_group_ids(groups, config.blacklist_tokens)
  print('Found {} good meetup groups, {} bad meetup groups'.format(len(good_ids), len(bad_ids)))
  events_data = gatherer.get_groups_events(config.meetup['events_url'], config.meetup['params'].copy(), good_ids, config.meetup['max_meetup_responses'])
  print('Found {} good meetup events'.format(len(events_data)))
  good_events_data = list(filters.filter_good_events(events_data, config.blacklist_tokens, config.meetup['params']['country'], config.meetup['max_event_hours']))
  print('Filtered {} down to {} good meetup events'.format(len(events_data), len(good_events_data)))
  return formatter.format_events(good_events_data, config.meetup['params']['city'])


def dump_data(events_json):
  import json
  with open('data.json', 'w') as outfile:
    json.dump(events_json, outfile, indent=2)


@app.route('/')
def hello():
  return 'Welcome to webuild\'s API'


@app.route('/events')
def events():
  events = grab_meetup_events(config)
  return jsonify(events)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
