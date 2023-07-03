import logging
import requests

from foxcloud import exceptions as fox_exc

try:
    from lxml import etree
except ImportError as e:
    print("Missing required python module: " + str(e))
    exit()

try:
    import json
except ImportError:
    import simplejson as json


class HTTPClient(object):
    def __init__(self, **params):
        """
        Initialize the class, get the necessary parameters
        """
        self.user_agent = 'foxcloud'

        self.params = params
        self.log = self.log_wrapper()

        self.log.debug("Params: {0}".format(str(self.params)))

        self.endpoint = self.params['endpoint']
        if 'timeout' not in self.params:
            self.timeout = None

        self.http = requests.Session()

    def _request(self, url, method, **kwargs):
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.user_agent

        try:
            if kwargs['body'] is 'json':
                kwargs['headers']['Accept'] = 'application/json'
                kwargs['headers']['Content-Type'] = 'application/json'
            elif kwargs['body'] is 'xml':
                kwargs['headers']['Accept'] = 'application/xml'
                kwargs['headers']['Content-Type'] = 'application/xml'
            elif kwargs['body'] is 'text':
                kwargs['headers']['Accept'] = 'text/plain'
                kwargs['headers']['Content-Type'] = 'text/plain'
            elif kwargs['body'] is 'binary':
                kwargs['headers']['Accept'] = 'application/octet-stream'
                kwargs['headers']['Content-Type'] = 'application/octet-stream'
            else:
                raise fox_exc.FoxCloudUnsupportedRequestType()
        except KeyError:
            # Default if body type is unspecified is text/plain
            kwargs['headers']['Accept'] = 'text/plain'
            kwargs['headers']['Content-Type'] = 'text/plain'

        # Optionally verify if requested body type is supported
        try:
            if kwargs['body'] not in kwargs['supported_body_types']:
                raise fox_exc.FoxCloudUnsupportedBodyType()
            else:
                del kwargs['supported_body_types']
        except KeyError:
            pass

        del kwargs['body']

        self.log.debug("{0} URL: {1}{2} - {3}"
                       .format(method, self.endpoint, url, str(kwargs)))

        resp = self.http.request(
            method,
            self.endpoint + url,
            **kwargs)

        if resp.text:
            try:
                if kwargs['headers']['Content-Type'] is 'application/json':
                    body = json.loads(resp.text)
                elif kwargs['headers']['Content-Type'] is 'application/xml':
                    body = etree.XML(resp.text)
                else:
                    body = resp.text
            except ValueError:
                body = None
        else:
            body = None

        return resp, body

    def _get(self, url, **kwargs):
        return self._request(url, 'GET', **kwargs)

    def _post(self, url, **kwargs):
        return self._request(url, 'POST', **kwargs)

    def _put(self, url, **kwargs):
        return self._request(url, 'PUT', **kwargs)

    def _delete(self, url, **kwargs):
        return self._request(url, 'DELETE', **kwargs)

    def log_wrapper(self):
        """
        Wrapper to set logging parameters for output
        """
        log = logging.getLogger('client.py')

        # Set the log format and log level
        try:
            debug = self.params["debug"]
            log.setLevel(logging.DEBUG)
        except KeyError:
            log.setLevel(logging.INFO)

        # Set the log format.
        stream = logging.StreamHandler()
        logformat = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%b %d %H:%M:%S')
        stream.setFormatter(logformat)

        log.addHandler(stream)
        return log
