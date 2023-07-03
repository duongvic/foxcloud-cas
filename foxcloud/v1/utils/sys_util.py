# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import os

from six.moves.urllib import error
from six.moves.urllib import parse
from six.moves.urllib import request

from foxcloud import exceptions as exc


def itersubclasses(cls, _seen=None):
    """Generator over all subclasses of a given class in depth first order."""

    if not isinstance(cls, type):
        raise TypeError("itersubclasses must be called with "
                        "new-style classes, not %.100r" % cls)
    _seen = _seen or set()
    try:
        subs = cls.__subclasses__()
    except TypeError:   # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def find_subclasses(engine=None, base_class=None):
    """Find the class relying on social_type and base class
    """
    for cls in itersubclasses(cls=base_class):
        if getattr(cls, '__engine_type__', None) == engine:
            return cls
    return None


def base_url_for_url(url):
    parsed = parse.urlparse(url)
    parsed_dir = os.path.dirname(parsed.path)
    return parse.urljoin(url, parsed_dir)


def normalise_file_path_to_url(path):
    if parse.urlparse(path).scheme:
        return path
    path = os.path.abspath(path)
    return parse.urljoin('file:', request.pathname2url(path))


def read_url_content(url):
    try:
        # TODO(mordred) Use requests
        content = request.urlopen(url).read()
    except error.URLError:
        raise exc.FoxCloudException(
            'Could not fetch contents for %s' % url)

    if content:
        try:
            content.decode('utf-8')
        except ValueError:
            content = base64.encodestring(content)
    return content

