import threading
import queue

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

import polly.core


speech_queue = queue.Queue()


def speech_worker():
    while True:
        item = speech_queue.get()
        polly.core.say(*item)
        speech_queue.task_done()


def clear_speech_queue():
    while not speech_queue.empty():
        try:
            speech_queue.get(False)
        except queue.Empty:
            continue
        speech_queue.task_done()


@dispatcher.add_method
def say(text, voice='Joanna', unit='word', queue=True):
    if queue:
        speech_queue.put((text, voice, unit))
    else:
        polly.core.say(text, voice, unit)


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(
        request.get_data(cache=False, as_text=True), dispatcher)
    return Response(response.json, mimetype='application/json')


def run_server(host, port):
    polly.core.setup_db()
    threading.Thread(target=speech_worker, daemon=True).start()
    run_simple(host, port, application)
