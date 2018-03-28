import threading
import time
import hashlib
import json
from flask import Flask, jsonify, Response, request

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
    if request.method not in ('GET', 'OPTIONS'):
        return Response('Invalid method', status_code=405)

    global events_data
    m = hashlib.sha1(json.dumps(events_data, ensure_ascii=False).encode('utf8'))
    resp = jsonify(events_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.set_etag(m.hexdigest())

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
