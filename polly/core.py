"""Speech synthesis with AWS Polly.

Text is chunked into sentences or even words which are cached individually.
This way, this script can be used offline once all sentences/words are cached.

This will happen faster when using words, since words can be recombined
to support other sentences as well.

On the other hand, chunking into sentences will produce better results,
as passing entire sentences to AWS enables it to produce results
with the correct sentence intonation and word spacing.

PCM format is used so that content can be assembled from various (cached) files easily.

The PCM data returned from AWS is in a signed 16-bit, 1 channel, little-endian format.

On Linux, if ffmpeg is installed these pcm files can be played with:
> ffplay -f s16le -ar 16000 -ac 1 file.pcm

On ubuntu, to use pyaudio you might have to install portaudio19-dev.
"""

import os
import sys
import unicodedata
import uuid
import boto3
import time
import sqlite3
import appdirs
import logging
import datetime
import nltk
import pyaudio


logger = logging.getLogger(__name__)

data_dir = appdirs.user_data_dir('python-polly')

download_dir = os.path.join(data_dir, 'download')
os.makedirs(download_dir, exist_ok=True)

db_path = os.path.join(data_dir, 'polly.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)


polly_client = boto3.Session().client('polly')

punctuation = ''.join(chr(i) for i in range(sys.maxunicode)
                      if unicodedata.category(chr(i)).startswith('P'))


def get_db():
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db


def ensure_requests_table():
    sql = """create table if not exists polly_requests (
                 id integer primary key,
                 voice text,
                 format text,
                 text text,
                 date text,
                 path text
             )
    """
    with get_db() as db:
        db.execute(sql)


def setup_db():
    ensure_requests_table()


def save_stream(s, filename):
    with open(filename, 'wb') as f:
        f.write(s.read())


def synthesize_with_aws(text, voice, format):
    response = polly_client.synthesize_speech(VoiceId=voice, OutputFormat=format,
                                              Text=text)
    return response['AudioStream']


def find_request(text, voice, format):
    db = get_db()
    return db.execute("""select path from polly_requests
                      where voice = ? and format = ? and text = ?""",
                      (voice, format, text)).fetchone()


def save_request(text, voice, format, path):
    with get_db() as db:
        db.execute("""insert into polly_requests (voice, format, text, path, date)
                      values (?, ?, ?, ?, ?)""",
                   (voice, format, text, path, datetime.datetime.utcnow().isoformat()))


def cache_stream(stream, text, voice, format):
    path = os.path.join(download_dir, str(uuid.uuid4()))
    save_stream(stream, path)
    save_request(text, voice, format, path)
    return path


def remove_double_quotation_marks(s):
    return s.translate(str.maketrans(dict.fromkeys(['\u201C', '\u201D', '\u0022'])))


def synthesize_cached(text, voice, format):
    data = find_request(text, voice, format)
    if data is None:
        stream = synthesize_with_aws(text, voice, format)
        return cache_stream(stream, text, voice, format)
    else:
        return data['path']


def preprocess(text):
    return ' '.join(x.strip(punctuation).lower() for x in text.split())


def synthesize_by_words(stream, text, voice):
    for sent in nltk.tokenize.sent_tokenize(remove_double_quotation_marks(text)):
        for token in nltk.tokenize.word_tokenize(preprocess(sent)):
            src_path = synthesize_cached(token, voice, 'pcm')
            with open(src_path, 'rb') as ff:
                stream.write(ff.read())


def synthesize_by_sentences(stream, text, voice):
    sents = nltk.tokenize.sent_tokenize(remove_double_quotation_marks(text))
    for sent in sents:
        src_path = synthesize_cached(sent, voice, 'pcm')
        with open(src_path, 'rb') as ff:
            stream.write(ff.read())


class UnrecognizedUnit(Exception):
    pass


def synthesize_to_stream(stream, text, voice, unit):
    if unit == 'word':
        synthesize_by_words(stream, text, voice)
    elif unit == 'sentence':
        synthesize_by_sentences(stream, text, voice)
    else:
        raise UnrecognizedUnit(unit)


def synthesize(text, path, voice='Joanna', unit='word'):
    with open(path, 'wb') as f:
        synthesize_to_stream(f, text, voice, unit)


def say(text, voice='Joanna', unit='word'):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    synthesize_to_stream(stream, text, voice, unit)
    time.sleep(1)
    stream.stop_stream()
    stream.close()
    p.terminate()
