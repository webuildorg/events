import config
import os
import meetup
from flask import Flask, jsonify
import threading
import time
import exporters

app = Flask(__name__)
events_data = []
lock = threading.Lock()


def get_events():
    data = meetup.grab_events(config)

    if len(data) > 0:
        lock.acquire()
        global events_data
        events_data = data
        lock.release()


def cron():
    # Check for events every 30mins=1800secs
    time.sleep(1800)
    get_events()


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


@app.route('/cal')
def cal():
    return exporters.events_to_ics(events_data)


if __name__ == "__main__":
    run()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
