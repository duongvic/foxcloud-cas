import sys
import json

import munch
from requests import exceptions as _rex

from foxcloud import log as _log, base
from foxcloud.i18n import _


class FoxCloudException(Exception):

    log_inner_exceptions = False

    def __init__(self, message, extra_data=None, **kwargs):
        args = [message]
        if extra_data:
            if isinstance(extra_data, munch.Munch):
                extra_data = extra_data.toDict()
            args.append("Extra: {0}".format(str(extra_data)))
        super(FoxCloudException, self).__init__(*args)
        self.extra_data = extra_data
        # NOTE(mordred) The next two are not used for anything, but
        # they are public attributes so we keep them around.
        self.inner_exception = sys.exc_info()
        self.orig_message = message

    def log_error(self, logger=None):
        # NOTE(mordred) This method is here for backwards compat. As shade
        # no longer wraps any exceptions, this doesn't do anything.
        pass


class FoxCloudCreateException(FoxCloudException):

    def __init__(self, resource, resource_id, extra_data=None, **kwargs):
        super(FoxCloudCreateException, self).__init__(
            message="Error creating {resource}: {resource_id}".format(
                resource=resource, resource_id=resource_id),
            extra_data=extra_data, **kwargs)
        self.resource_id = resource_id


class FoxCloudTimeout(FoxCloudException):
    pass


class FoxCloudUnavailableExtension(FoxCloudException):
    pass


class FoxCloudUnavailableFeature(FoxCloudException):
    pass


class FoxCloudUnSupportedVersion(FoxCloudException):
    pass


class FoxCloudUnSupportedEngine(FoxCloudException):
    def __init__(self, engine, extra=None, **kwargs):
        msg = _("Not supported engine '%s'. "
                "Expected %s ") % (engine, ' or '.join(e for e in base.SUPPORTED_ENGINES))
        super(FoxCloudUnSupportedEngine, self).__init__(message=msg, extra=extra, **kwargs)
        self.engine = engine


class FoxCloudInvalidUsage(FoxCloudException):
    pass


class FoxCloudVersionNotFoundForAPIMethod(FoxCloudException):
    msg_fmt = "API version '%(vers)s' is not supported on '%(method)s' method."

    def __init__(self, version, method):
        self.version = version
        self.method = method

    def __str__(self):
        return self.msg_fmt % {"vers": self.version, "method": self.method}


class FoxCloudHTTPError(FoxCloudException, _rex.HTTPError):

    def __init__(self, *args, **kwargs):
        FoxCloudException.__init__(self, *args, **kwargs)
        _rex.HTTPError.__init__(self, *args, **kwargs)


class FoxCloudBadRequest(FoxCloudHTTPError):
    """There is something wrong with the request payload.
    Possible reasons can include malformed json or invalid values to parameters
    such as flavorRef to a server create.
    """


class FoxCloudURINotFound(FoxCloudHTTPError):
    pass


# Backwards compat
FoxCloudResourceNotFound = FoxCloudURINotFound


class FoxCloudUnsupportedRequestType(FoxCloudHTTPError):
    pass


class FoxCloudUnsupportedBodyType(FoxCloudHTTPError):
    pass


class FoxCloudFileNotFound(FoxCloudException):
    pass


class FoxCloudBucketNameIsExists(FoxCloudException):
    pass


def _log_response_extras(response):
    # Sometimes we get weird HTML errors. This is usually from load balancers
    # or other things. Log them to a special logger so that they can be
    # toggled indepdently - and at debug level so that a person logging
    # shade.* only gets them at debug.
    if response.headers.get('content-type') != 'text/html':
        return
    try:
        if int(response.headers.get('content-length', 0)) == 0:
            return
    except Exception:
        return
    logger = _log.setup_logging('foxcloud.http')
    if response.reason:
        logger.debug(
            "Non-standard error '{reason}' returned from {url}:".format(
                reason=response.reason,
                url=response.url))
    else:
        logger.debug(
            "Non-standard error returned from {url}:".format(
                url=response.url))
    for response_line in response.text.split('\n'):
        logger.debug(response_line)


# Logic shamelessly stolen from requests
def raise_from_response(response, error_message=None):
    msg = ''
    if 400 <= response.status_code < 500:
        source = "Client"
    elif 500 <= response.status_code < 600:
        source = "Server"
    else:
        return

    remote_error = "Error for url: {url}".format(url=response.url)
    try:
        details = response.json()
        # Nova returns documents that look like
        # {statusname: 'message': message, 'code': code}
        detail_keys = list(details.keys())
        if len(detail_keys) == 1:
            detail_key = detail_keys[0]
            detail_message = details[detail_key].get('message')
            if detail_message:
                remote_error += " {message}".format(message=detail_message)
    except ValueError:
        if response.reason:
            remote_error += " {reason}".format(reason=response.reason)
    except AttributeError:
        if response.reason:
            remote_error += " {reason}".format(reason=response.reason)
        try:
            json_resp = json.loads(details[detail_key])
            fault_string = json_resp.get('faultstring')
            if fault_string:
                remote_error += " {fault}".format(fault=fault_string)
        except Exception:
            pass

    _log_response_extras(response)

    if error_message:
        msg = '{error_message}. ({code}) {source} {remote_error}'.format(
            error_message=error_message,
            source=source,
            code=response.status_code,
            remote_error=remote_error)
    else:
        msg = '({code}) {source} {remote_error}'.format(
            code=response.status_code,
            source=source,
            remote_error=remote_error)

    # Special case 404 since we raised a specific one for services exceptions
    # before
    if response.status_code == 404:
        raise FoxCloudURINotFound(msg, response=response)
    elif response.status_code == 400:
        raise FoxCloudBadRequest(msg, response=response)
    if msg:
        raise FoxCloudHTTPError(msg, response=response)