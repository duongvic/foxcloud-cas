#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import log as _log
from foxcloud import exceptions as exc


class CASAdapter(object):

    def __init__(self, cas_logger, manager, *args, **kwargs):
        self.cas_logger = cas_logger
        self.manager = manager
        self.request_log = _log.setup_logging('cas.request_ids')

    def _log_request_id(self, response, obj=None):
        # Log the request id and object id in a specific logger. This way
        # someone can turn it on if they're interested in this kind of tracing.
        request_id = response.headers.get('x-openstack-request-id')
        if not request_id:
            return response
        tmpl = "{meth} call to {services} for {url} used request id {req}"
        kwargs = dict(
            meth=response.request.method,
            service=self.service_type,
            url=response.request.url,
            req=request_id)

        if isinstance(obj, dict):
            obj_id = obj.get('id', obj.get('uuid'))
            if obj_id:
                kwargs['obj_id'] = obj_id
                tmpl += " returning object {obj_id}"
        self.request_log.debug(tmpl.format(**kwargs))
        return response

    def _munch_response(self, response, result_key=None, error_message=None):
        exc.raise_from_response(response, error_message=error_message)

        if not response.content:
            # This doens't have any content
            return self._log_request_id(response)

        # Some REST calls do not return json content. Don't decode it.
        if 'application/json' not in response.headers.get('Content-Type'):
            return self._log_request_id(response)

        try:
            result_json = response.json()
            self._log_request_id(response, result_json)
        except Exception:
            return self._log_request_id(response)
        return result_json

    def _version_matches(self, version):
        api_version = self.get_api_major_version()
        if api_version:
            return api_version[0] == version
        return False