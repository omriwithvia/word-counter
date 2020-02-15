import requests


class ReaderFactory(object):
    @staticmethod
    def produce(request):
        # Assuming input as text is not too big.
        # If required I would go with reading request as a stream, request as raw text (no JSON because I don't know a
        # way to parse a really big JSON "as a stream" without allocating all the memory),
        # identifying input type file:// or http(s):// or nothing alike.
        if request.get('sentence'):
            return StringDataReader(request['sentence'])
        elif request.get('url'):
            # Assuming starts with "http://"
            return HttpDataReader(request['url'])
        elif request.get('filename'):
            # Assuming it fits operation system format - either /home/whatever of C:\dir\filename.ext
            return FileDataReader(request['filename'])

        raise ValueError('Bad request - could not find and valid input source')


class StringDataReader(object):
    def __init__(self, sentence):
        self.data = sentence

    def readlines(self):
        # I could do the same as for http and file, but assuming YAGNI. (create a stream etc but wouldn't have value because of JSON)
        return self.data.split('\n')


class HttpDataReader(object):
    def __init__(self, url):
        self.url = url

    def readlines(self):
        response = requests.get(self.url, stream=True)
        for line in response.iter_lines():
            yield line


class FileDataReader(object):
    def __init__(self, filename):
        self.filename = filename

    def readlines(self):
        # Assuming file exists and we'll crash if not
        # Assuming file not too big
        # TODO(Omri) wrap with better error.
        with open(self.filename, 'r') as f:
            for line in f.readlines():
                yield line
