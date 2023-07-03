#
# Copyright (c) 2020 FTI-CAS
#

"""
Heat template and stack management
"""

from __future__ import absolute_import

import datetime
import getpass
import socket
import tempfile
import time

from oslo_serialization import jsonutils
from heatclient import client as heat_client
from heatclient import exc as heat_exc
from foxcloud import exceptions as fox_exc

from foxcloud.v1.utils import event_util, template_format
from foxcloud.v1.utils import template_util


class HeatStack(object):
    """Represents a Heat stack (deployed template)"""

    def __init__(self, name_or_id, session=None, tags=None):
        """Initialize Heat stack

        :param name_or_id: (str) Name or ID of stack.
        :param session: (keystone.Session) keystone session
        :param tags: (list) tags
        """
        self.name_or_id = name_or_id
        self.outputs = {}
        self._client = heat_client.Client(version='1', session=session)
        self._stack = None
        self._tags = tags

    def get_stack(self):
        """Get a stack being created
        :return:
        :raises: ``FoxCloudException`` if something goes wrong during the
            OpenStack API call or if multiple matches are found.
        """
        try:
            stack = self._client.stacks.get(stack_id=self.name_or_id, resolve_outputs=True)
            self._stack = stack
        except heat_exc.HTTPException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def _update_stack_tracking(self):
        """Update the output of stack
        :return:
        """
        outputs = self._stack.outputs
        self.outputs = {output['output_key']: output['output_value'] for output
                        in outputs}

    def get(self):
        """Retrieves an existing stack from the target cloud
        Returns a bool indicating whether the stack exists in the target cloud
        If the stack exists, it will be stored as self._stack

        :return
        """
        try:
            self._stack = self._client.stacks.get(stack_id=self.name_or_id, resolve_outputs=True)
            if not self._stack:
                return False

            self._update_stack_tracking()
            return True
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def create(self, template, heat_parameters, wait, timeout, rollback=True, **kwargs):
        """Creates an OpenStack stack from a template

        :param template:
        :param heat_parameters:
        :param wait:
        :param timeout:
        :param rollback:
        :return:
        """

        def _create_stack(tags=None, template_file=None,
                          template_url=None, template_object=None,
                          files=None, environment_files=None,
                          **parameters):
            if timeout:
                timeout_mins = timeout // 60
            else:
                timeout_mins = 2

            envfiles, env = template_util.process_multiple_environments_and_files(env_paths=environment_files)
            tpl_files, template_ = template_util.get_template_contents(
                template_file=template_file,
                template_url=template_url,
                template_object=template_object,
                files=files)

            params = dict(
                stack_name=self.name_or_id,
                tags=tags,
                disable_rollback=not rollback,
                parameters=parameters,
                template=template_,
                files=dict(list(tpl_files.items()) + list(envfiles.items())),
                environment=env,
                timeout_mins=timeout_mins,
            )
            self._client.stacks.create(**params)
            if wait:
                status, msg = event_util.poll_for_events(self._client,
                                                         stack_name=self.name_or_id,
                                                         action='CREATE')
                if status:
                    pass
            return self._client.stacks.get(stack_id=self.name_or_id)

        try:
            with tempfile.NamedTemporaryFile('wb', delete=False) as template_file:
                template_file.write(jsonutils.dump_as_bytes(template))
                template_file.close()
                self._stack = _create_stack(tags=self._tags,
                                            template_file=template_file.name,
                                            **heat_parameters)
            self._update_stack_tracking()
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def update(self, template, heat_parameters, wait, timeout, rollback=True):
        """
        Update an OpenStack stack being created
        :param template:
        :param heat_parameters:
        :param wait:
        :param timeout:
        :param rollback:
        :return:
        """
        def _update_stack(tags=None,
                          template_file=None, template_url=None,
                          template_object=None, files=None,
                          environment_files=None,
                          **parameters):

            if timeout:
                timeout_mins = timeout // 60
            else:
                timeout_mins = 2

            envfiles, env = template_util.process_multiple_environments_and_files(env_paths=environment_files)
            tpl_files, template = template_util.get_template_contents(
                template_file=template_file,
                template_url=template_url,
                template_object=template_object,
                files=files)

            params = dict(
                tags=tags,
                disable_rollback=not rollback,
                parameters=parameters,
                template=template,
                files=dict(list(tpl_files.items()) + list(envfiles.items())),
                environment=env,
                timeout_mins=timeout_mins,
            )
            if wait:
                events = event_util.get_events(
                    self, self.name_or_id, event_args={'sort_dir': 'desc', 'limit': 1})
                marker = events[0].id if events else None

            self._stack = self._client.stacks.update(stack_id=self.name_or_id, **params)
            if wait:
                event_util.poll_for_events(self._client, stack_name=self.name_or_id,
                                           action='UPDATE')
            return self._client.stacks.get(stack_id=self.name_or_id)

        try:
            with tempfile.NamedTemporaryFile('wb', delete=False) as template_file:
                template_file.write(jsonutils.dump_as_bytes(template))
                template_file.close()
                self._stack = _update_stack(name=self.name_or_id, tags=self._tags,
                                            template_file=template_file.name,
                                            **heat_parameters)
            self._update_stack_tracking()
        except Exception as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def delete(self, wait=True):
        """Delete an OpenStack stack being created

        :param wait: If True , waits for stack to be deleted
        :return:
        """
        def _delete_stack():
            try:
                stack = self._client.stacks.get(stack_id=self.name_or_id, resolve_outputs=False)
                if not stack:
                    raise fox_exc.FoxCloudBadRequest("Stack %s not found for deleting", self.name_or_id)

                if wait:
                    events = event_util.get_events(
                        self, self.name_or_id, event_args={'sort_dir': 'desc', 'limit': 1})
                    marker = events[0].id if events else None

                self._stack = self._client.stacks.delete(stack_id=self.name_or_id)

                if wait:
                    event_util.poll_for_events(self._client, stack_name=self.name_or_id,
                                               action='DELETE', marker=marker)

                    self._client.stacks.get(stack_id=self.name_or_id, resolve_outputs=False)
                    if stack and stack.stack_status == 'DELETE_FAILED':
                        raise fox_exc.FoxCloudBadRequest(
                            "Failed to delete stack {id}: {reason}".format(
                                id=self.name_or_id, reason=stack['stack_status_reason']))

            except heat_exc.HTTPException as e:
                raise fox_exc.FoxCloudException(e)

        return _delete_stack()

    def abandon(self, wait=True):
        """
        Abandon a stack.
        :return:
        """
        try:
            return self._client.stacks.abandon(self.name_or_id)
        except heat_exc.HTTPException as e:
            raise fox_exc.FoxCloudException(e)

    def get_failures(self):
        """Get failures when deploying stack

        :return:
        """
        return event_util.get_events(self._stack.id,
                                     event_args={'resource_status': 'FAILED'})

    @property
    def status(self):
        """
        Retrieve the current stack status
        :return:
        """
        if self._stack:
            return self._stack.status

    @property
    def uuid(self):
        """Retrieve the current stack ID

        :return:
        """
        if self._stack:
            return self._stack.id


HEAT_TEMPLATE_VERSIONS = ["2.10", "2.11", "2.12", "3.0", "3.1", "3.2", "3.3", "8.0"]


class HeatTemplate(object):
    """Represents a Heat stack (deployed template)
    Refer: https://docs.openstack.org/heat/latest/template_guide/index.html
    """

    DESCRIPTION_TEMPLATE = """
        Stack built by the cas framework for %s on host %s %s.
        All referred generated resources are prefixed with the template
        name (i.e. %s).
        """
    HEAT_WAIT_LOOP_INTERVAL = 2
    HEAT_STATUS_COMPLETE = 'COMPLETE'

    def __init__(self, name, template_file=None, heat_parameters=None, session=None):
        default_version = HEAT_TEMPLATE_VERSIONS[0]

        self.name = name
        self.heat_parameters = {}
        self.parameter_groups = {}
        self.conditions = {}
        self._session = session or {}
        self.resources = {}
        self.outputs = {}

        if heat_parameters:
            assert isinstance(heat_parameters, dict)
            self.heat_parameters = heat_parameters

        if template_file:
            with open(template_file) as stream:
                # LOG.info('Parsing external template: %s', template_file)
                template_str = stream.read()
            self._template = template_format.parse(template_str)
            self._parameters = heat_parameters
        else:
            self._init_template()

        # LOG.debug("Template object '%s' created", name)

    def _init_template(self):
        """Init a new heat template

        :return:
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._template = {
            'heat_template_version': '2018-08-31',
            'description': self.DESCRIPTION_TEMPLATE % (
                getpass.getuser(),
                socket.gethostname(),
                timestamp,
                self.name,
            ),
            'resources': {},
            'outputs': {}
        }
        self.resources = self._template['resources']
        self.outputs = self._template['outputs']

    def load_existed_template(self, template):
        """Load a stack template being created

        :param template
        :return
        """
        self._template = {
            'heat_template_version': template['heat_template_version'],  # rocky version
            'description': template['description'],
            'resources': {},
            'outputs': {},
        }

        self.resources = template.get('resources')
        self.outputs = template.get('outputs')

    def get_id(self, obj):
        """
        :param obj:
        :return:
        """
        if getattr(obj, 'uuid', None):
            return obj.uuid
        else:
            return getattr(obj, 'id', obj)

    def create(self, block=True, timeout=3600):
        """Creates a stack in the target based on the stored template
        Subclass may be override this method

        :param block: (bool) Wait for Heat create to finish
        :param timeout: (int) Timeout in seconds for Heat create,
               default 3600s
        :return A dict with the requested output values from the template
        """
        start_time = time.time()
        stack = HeatStack(self.name, session=self._session)
        stack.create(self._template, self.heat_parameters, block, timeout, rollback=True)
        if not block:
            print("Creating stack '%s' DONE in %d secs", self.name, time.time() - start_time)
            return stack

        if stack.status != self.HEAT_STATUS_COMPLETE:
            raise fox_exc.FoxCloudException('Error in Heat during the creation of the'
                                            ' OpenStack stack {}'.format(self.name))
        # stack.abandon(wait=True)
        print("Creating stack '%s' DONE in %d secs", self.name, time.time() - start_time)
        return stack

    def update(self, block=True, timeout=3600):
        """Update a stack in the target based on the stored template
        Subclass may be override this method

        :param block: (bool) Wait for Heat create to finish
        :param timeout: (int) Timeout in seconds for Heat create,
               default 3600s
        :return A dict with the requested output values from the template
        """
        start_time = time.time()
        stack = HeatStack(self.name, session=self._session)
        stack.update(self._template, self.heat_parameters, block, timeout, rollback=True)
        if not block:
            print("Updating stack '%s' DONE in %d secs", self.name, time.time() - start_time)
            return stack

        if stack.status != self.HEAT_STATUS_COMPLETE:
            raise fox_exc.FoxCloudException('Error in Heat during the update of the'
                                            ' OpenStack stack {}'.format(self.name))

        return stack
