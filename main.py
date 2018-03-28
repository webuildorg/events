import threading
import time
from flask import Flask, jsonify, Response

import config
import os
import meetup
import exporters

app = Flask(__name__)
events_data = []
cron_timestamp = time.time()
lock = threading.Lock()


def get_events():
    data = meetup.grab_events(config)

    if len(data) > 0:
        lock.acquire()
        global events_data
        events_data = data
        lock.release()
    return


def run():
    get_events()
    return app


@app.route('/')
def hello():
    return 'Welcome to webuild\'s API'


@app.route('/events')
def events():
    global events_data
    resp = jsonify(events_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/cal')
def cal():
    return Response(exporters.events_to_ics(events_data), content_type='text/calendar; charset=utf-8')


@app.route('/cron')
def cron():
    global cron_timestamp
    now = time.time()

    if now - cron_timestamp > 300: # 5 mins
        cron_timestamp = now
        w = threading.Thread(name='worker', target=get_events)
        w.start()

    return 'Done at {}'.format(cron_timestamp)


if __name__ == "__main__":
    app = run()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
