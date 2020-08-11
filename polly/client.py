import json
import requests


url = 'http://localhost:6000'


def say(text, voice='Joanna', unit='word', queue=True):
    payload = dict(method='say', params=[text, voice, unit, queue], jsonrpc='2.0', id=None)
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    assert 'error' not in response, response
