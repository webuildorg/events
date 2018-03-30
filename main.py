import os
import threading
import time
import hashlib
import json
import functools
from io import BytesIO
from gzip import GzipFile
from flask import Flask, jsonify, Response, request, send_from_directory, after_this_request

import config
from events.meetup import Meetup
from events import exporters

class WeBuild:
    def __init__(self, config):
        self.events_data = []
        self.meetup = Meetup(config)
        self.data_hash = ''
        self.last_checked_timestamp = time.time()
        self.lock = threading.Lock()

app = Flask(__name__)
webuild = WeBuild(config)


def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            if ('gzip' not in request.headers.get('Accept-Encoding', '').lower() or
                not 200 <= response.status_code < 300 or
                'Content-Encoding' in response.headers):
                return response

            response.direct_passthrough = False
            gzip_buffer = BytesIO()
            with GzipFile(mode='wb',
                      compresslevel=7,
                      fileobj=gzip_buffer) as gzip_file:
                gzip_file.write(response.get_data())

            response.set_data(gzip_buffer.getvalue())
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response
        return f(*args, **kwargs)
    return view_func


def set_headers(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def set_response_headers(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Cache-Control'] = 'public, max-age=30'
            response.set_etag(webuild.data_hash)
            return response
        return f(*args, **kwargs)
    return view_func


def check_etag(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        @app.before_request
        def check_headers():
            if request.if_none_match and webuild.data_hash in request.if_none_match:
                print('304 response!')
                return Response(status=304)

            if request.method not in ('GET', 'OPTIONS'):
                return Response('Invalid method', status=405)

        return f(*args, **kwargs)
    return decorated_function


def get_events():
    return 'TODO'

    global webuild
    data = webuild.meetup.grab_events()
    m = hashlib.sha1(json.dumps(data, ensure_ascii=False).encode('utf8'))
    data_hash = m.hexdigest()

    if len(data) > 0 and data_hash != webuild.data_hash:
        webuild.lock.acquire()
        webuild.events_data = data
        webuild.data_hash = data_hash
        webuild.lock.release()
    return


def run():
    get_events()
    return app


@app.route('/')
def hello():
    return Response('Welcome to webuild\'s API')


@app.route('/groups')
@check_etag
@set_headers
@gzipped
def groups():
    return Response(
        json.dumps(webuild.meetup.good_groups(), ensure_ascii=False),
        content_type='application/json')


@app.route('/filtered_groups')
@check_etag
@set_headers
@gzipped
def filtered_groups():
    return Response(
        json.dumps(webuild.meetup.bad_groups(), ensure_ascii=False),
        content_type='application/json')


@app.route('/events')
@check_etag
@set_headers
@gzipped
def events():
    if request.if_none_match and webuild.data_hash in request.if_none_match:
        print('304 response!')
        return Response(status=304)

    return Response(
        json.dumps(webuild.events_data, ensure_ascii=False),
        content_type='application/json')


@app.route('/cal')
@check_etag
@set_headers
@gzipped
def cal():
    return Response(
        exporters.events_to_ics(webuild.events_data),
        content_type='text/calendar; charset=utf-8')


@app.route('/cron')
def cron():
    global webuild
    now = time.time()

    if now - webuild.last_checked_timestamp > 300: # 5 mins
        webuild.lock.acquire()
        webuild.last_checked_timestamp = now
        webuild.lock.release()

        w = threading.Thread(name='worker', target=get_events)
        w.start()

    return 'Done at {}'.format(webuild.last_checked_timestamp)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


if __name__ == "__main__":
    app = run()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
