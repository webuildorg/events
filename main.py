import config
import os
from meetup import gatherer, formatter, filters
from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)
events_data = []
lock = threading.Lock()

def get_events():
    data = grab_meetup_events(config)

    if len(data) > 0:
        lock.acquire()
        global events_data
        data = events_data
        lock.release()


def cron():
    # Check for events every 30mins=1800secs
    time.sleep(1800)
    get_events()


def grab_meetup_events(config):
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
    return formatter.format_events(good_events, config.meetup['params']['city'])


def dump_data(events_json):
    import json
    with open('data.json', 'w') as outfile:
        json.dump(events_json, outfile, indent=2)


def run():
    get_events()
    w = threading.Thread(name='worker', target=cron)
    w.start()
    return app


@app.route('/')
def hello():
    return 'Welcome to webuild\'s API'


@app.route('/events')
def events():
    global events_data
    return jsonify(events_data)


if __name__ == "__main__":
    run()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
