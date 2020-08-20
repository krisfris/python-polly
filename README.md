# python-polly

python-polly is a simple wrapper around AWS's text-to-speech service Polly.

Features are:

* Cache requests to AWS Polly locally
* Tokenize input text into sentences or words in order to maximize usage of cache
* Playback queue for audio output
* Client-server setup to support concurrent output by multiple applications

## Setup

```
pip install --user python-polly[server]
```

Most of the dependencies are only required by the server so I put them in as an extra option.
To get the dependencies for the server use `python-polly[server]` otherwise just `python-polly`.

## Usage

### Server

Start the server. Default port is 6000.

```
polly server
```

### Client

#### CLI

```
polly say "hello world"
```

#### Python

```
import polly.client
polly.client.say('hello world')
```

#### Any other JSON-RPC client e.g. cURL

```
curl -d '{"id": "null", "jsonrpc": "2.0", "method": "say", "params": ["hello", "Joanna", "sentence", true]}' localhost:6000
```

## Links
### Playback
https://people.csail.mit.edu/hubert/pyaudio/docs/#example-callback-mode-audio-i-o  
https://github.com/spatialaudio/python-sounddevice/blob/master/examples/play_long_file.py
