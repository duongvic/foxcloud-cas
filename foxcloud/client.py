#
# Copyright (c) 2020 FTI-CAS
#

from oslo_utils import importutils

from foxcloud import (base, exceptions as fox_exc, api_versions)
from foxcloud.i18n import _


def Client(version='1', engine='console', services=None, **kwargs):
    """FoxCloud client

    :param version: (str) version supported
    :param engine:
    :param services:
    :param kwargs:
    :return:
    """
    _check_engine(engine=engine)
    api_version = _get_version(version)
    client_class = _get_class('Client', api_version.ver_major)
    if services:
        if isinstance(services, str):
            services = [services]
        elif isinstance(services, list):
            pass
        else:
            msg = "Invalid services of name {}".format(services)
            raise fox_exc.FoxCloudException(msg)

        for service in services:
            if service not in client_class.list_services():
                msg = _("Not found services of name '%s'") % service
                raise fox_exc.FoxCloudException(msg)

    return client_class(api_version=api_version,
                        engine=engine, services=services, **kwargs)


def _get_version(version):
    if not isinstance(version, api_versions.APIVersion):
        version = api_versions.get_api_version(version)
    else:
        api_versions.check_major_version(version)
    if version.is_latest():
        raise fox_exc.FoxCloudUnSupportedVersion(_("The version should be explicit, not latest."))
    return version


def _get_class(name, version):
    module = importutils.import_versioned_module('foxcloud', version, 'client')
    client_class = getattr(module, name)
    return client_class


def _check_engine(engine):
    assert isinstance(engine, str)
    lower_engine = engine.lower()
    if not (lower_engine in base.SUPPORTED_ENGINES):
        raise fox_exc.FoxCloudUnSupportedEngine(engine=engine)


def list_services(version):
    api_version = _get_version(version)
    client_class = _get_class('Client', api_version.ver_major)
    return client_class.list_services()
