import requests


def get_json(url, params=None, fallback=None):
    r = requests.get(url, params=params)
    if r.status_code < 200 or r.status_code >= 300:
        print('Unable to get data from {} with params: {}'.format(url, params))
        print(r.text)
        return fallback

    try:
        return r.json()
    except:
        print('Could not parse json response from {} with params: {}'.format(url, params))
        return fallback
