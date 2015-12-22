#!/usr/bin/python
# Project Kimchi
#
# Copyright IBM, Corp. 2015
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301USA

import template_utils
import utils
import warnings

vm_uri = '/vms'
task_uri = '/tasks'
vm_allowed_states = ['running', 'paused', 'shutoff']
support_vm_post_actions = ['start','poweroff','shutdown','reset','connect','clone','suspend','resume']


def delete_vm(session, vm_name='test_vm', expected_status=None):
    """
    Delete specified VM
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the VM to be deleted. Default is test_vm
    :return:http response from restful api of the kimchi
    """
    return session.request_delete(vm_uri + '/' + vm_name, expected_status)

 
def list_vms(session,expected_status=None):
    """
    Return a list of virtual machines
    :param session: session for logging into restful api of the kimchi
    :return: List of virtual machines
    """
    session.logging.info('<--> vm_utils.list_vms()')
    return session.request_get_json(vm_uri,expected_status)


def create_vm(session, vm_name='test_vm', template_name='test', persistent=None, graphics_type=None,
              graphics_listen=None, storagepool=None, expected_status=None):
    """
    Create VM
    :param session: session for logging into restful api of the kimchi
    :param vm_name: Name of VM to be created. Default is test_vm
    :param template_name: Name of Template to be used for VM creation.
    Default is test. If template already exists then will be used for VM creation
    :param persistent : True or False. Default in True
    :param graphics_type : The type of graphics. It can be VNC or spice or None
    :param storagepool : Storage Pool for the new VM
    :param graphics_listen : The network which the vnc/spice server listens on.
    :param expected_status: expected return value from kimchi api
    :return: VM creation response by adding Name of VM.
    """

    session.logging.info('-->vm_utils.create_vm(), vm_name: %s |template_name:%s |persistent:%s|graphics_type:%s |storagepool:%s|listen:%s |expected_status:%s', vm_name, template_name, persistent, graphics_type, storagepool, graphics_listen, expected_status)
    vm_data = {'name': vm_name, 'template': template_utils.template_uri + template_name}
    if persistent is not None:
        vm_data['persistent'] = persistent
    if graphics_type is not None and graphics_type in ['vnc', 'spice']:
        vm_data['graphics[type]'] = graphics_type
    if storagepool is not None:
        vm_data['storagepool'] = storagepool
    if graphics_listen is not None:
        vm_data['graphics[listen]'] = graphics_listen

    created_template = False

    # checking if template exist, otherwise create it
    try:
        template_resp = session.request_get_json(template_utils.template_uri + template_name)
        session.logging.debug('Template already exist. VM will use the same:%s', template_resp)
    except Exception:
        session.logging.debug('Creating new template with name:%s', template_name)
        template_resp = template_utils.create_template(session, name=template_name)
        session.logging.debug('Created new template:%s', template_resp)
        created_template = True  # If template created set this to True

    # Create VM
    try:
        vm_resp = session.request_post_json(vm_uri, vm_data, expected_status)
        vm_resp['name'] = vm_name
    finally:  # Making sure that if Template created above, delete it even VM creation raise exception
        if created_template:
            session.logging.debug('Going to delete the template if create above. template_name:%s', template_name)
            template_utils.delete_template(session, template_name)
            session.logging.debug('Deleted template create above. template_name:%s', template_name)

    task_resp = utils.wait_task_status_change(session, vm_resp['id'])
    session.logging.debug('task response, task_resp:%s', task_resp)

    if task_resp:
        session.logging.info('<--vm_utils.create_vm(), vm_resp:%s', vm_resp)
        return vm_resp


def start_vm(session, vm_name):
    """
    Start a virtual machine
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the vm
    :return:
    """
    session.logging.info('--> vm_utils.start_vm()')
    if not vm_name:
        session.logging.error('VM name cannot be None')
        raise ValueError('VM name cannot be None')

    response = session.request_post_json(vm_uri + '/' + vm_name + '/start')
    warnings.warn("deprecated.", DeprecationWarning)

    session.logging.info('<-- vm_utils.start_vm()')


def poweroff_vm(session, vm_name):
    """
    Power off a virtual machine
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the vm
    :return:
    """
    session.logging.info('--> vm_utils.poweroff_vm()')

    if not vm_name:
        session.logging.error('VM name cannot be None')
        raise ValueError('VM name cannot be None')

    response = session.request_post_json(vm_uri + '/' + vm_name + '/poweroff')
    warnings.warn("deprecated.", DeprecationWarning)

    session.logging.info('<-- vm_utils.poweroff_vm()')


def suspend_vm(session, vm_name):
    """
    Suspend a virtual machine
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the vm
    :return:
    """
    session.logging.info('--> vm_utils.suspend_vm()')
    warnings.warn("deprecated.", DeprecationWarning)

    if not vm_name:
        session.logging.error('VM name cannot be None')
        raise ValueError('VM name cannot be None')

    response = session.request_post_json(vm_uri + '/' + vm_name + '/suspend')

    session.logging.info('<-- vm_utils.suspend_vm()')


def resume_vm(session, vm_name):
    """
    Resume a virtual machine
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the vm
    :return:
    """
    session.logging.info('--> vm_utils.resume_vm()')
    warnings.warn("deprecated.", DeprecationWarning)
    if not vm_name:
        session.logging.error('VM name cannot be None')
        raise ValueError('VM name cannot be None')

    session.logging.info('<--> vm_utils.resume_vm()')
    response = session.request_post_json(vm_uri + '/' + vm_name + '/resume')

    session.logging.info('<-- vm_utils.resume_vm()')


def clone_vm(session, vm_name):
    """
    Clone a virtual machine
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the vm
    :return:
    """
    session.logging.info('--> vm_utils.clone_vm()')
    warnings.warn("deprecated.", DeprecationWarning)
    if not vm_name:
        session.logging.error('VM name cannot be None')
        raise ValueError('VM name cannot be None')

    session.logging.info('<--> vm_utils.clone_vm()')
    response = session.request_post_json(vm_uri + '/' + vm_name + '/clone')
    session.logging.info('<-- vm_utils.clone_vm()')

def perform_action_on_vm(session, vm_name, action, expected_status_values=None):
    """
    Perform supported action on the VM
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the vm
    :param vm_name: action to be perform on VM
    :return:
    """
    session.logging.info('--> vm_utils.perform_action_on_vm().vm_name:%s |action:%s',vm_name, action)

    if not vm_name:
        session.logging.error('VM name cannot be None')
        raise ValueError('VM name cannot be None')

    response = session.request_post_json(vm_uri + '/' + vm_name + '/' + action, expected_status_values=expected_status_values)

    if 'id' in response:
        try:
            task_resp = utils.wait_task_status_change(session, response['id'])
            session.logging.debug('task response, task_resp:%s', task_resp)
        except Exception, err:
            session.logging.debug('VM failed to %s. %s',action, err.message)
            raise Exception('VM failed to start'+err.message)

    session.logging.info('<-- vm_utils.perform_action_on_vm()')
    return response


def list_vms(session, expected_status=None):
    """
    Return a list of virtual machines
    :param session: session for logging into restful api of the kimchi
    :return: List of virtual machines
    [{u'access': u'full',
    u'cpus': 1,
    u'graphics': {u'listen': None,
    u'passwd': None,
    u'passwdValidTo': None,
    u'port': None,
    u'type': u'vnc'},
    u'groups': [],
    u'icon': None,
    u'memory': 2048.0,
    u'name': u'Fedora',
    u'persistent': True,
    u'screenshot': None,
    u'state': u'shutoff',
    u'stats': {u'cpu_utilization': 0,
    u'io_throughput': 0,
    u'io_throughput_peak': 100,
    u'net_throughput': 0,
    u'net_throughput_peak': 100},
    u'users': [],
    u'uuid': u'083114ba-f1ad-5825-48de-7faca1bb3395'}]
    """
    session.logging.info('<--> vm_utils.list_vms()')
    return session.request_get_json(vm_uri, expected_status)


def is_vm_running(session, vm_name):
    """
    Check if the given virtual machine is running or not
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the virtual machine
    :return: True or False
    """
    warnings.warn("deprecated. suggested method is is_vm()", DeprecationWarning)
    is_vm(session, vm_name=vm_name)


def is_vm(session, vm_name, state='running'):
    """
    Check if the given virtual machine is in the state passed as parameter.
    Allowed values are vm_allowed_state = ['running', 'paused', 'shutoff']
    :param session: session for logging into restful api of the kimchi
    :param vm_name: name of the virtual machine
    :param state: state of the virtual machine to check across. Default value is running
    :return: True or False
    """
    session.logging.info('--> vm_utils.is_vm().state:%s', state)

    if not vm_name:
        session.logging.error('VM name cannot be None')
        raise ValueError('VM name cannot be None')

    if state not in vm_allowed_states:
        session.logging.error('state cannot other than %s', vm_allowed_states)
        raise ValueError('state cannot other than %s', vm_allowed_states)

    vms = list_vms(session)
    vm_found = False
    is_running = False

    for vm in vms:
        if vm['name'] == vm_name:
            vm_found = True

            if vm['state'] == state:
                is_running = True
            else:
                is_running = False

            session.logging.debug("VM state :" + str(is_running))

    if not vm_found:
        session.logging.error("VM with name, " + vm_name + " not found.")
        raise ValueError("VM with name, " + vm_name + " not found.")

    session.logging.info('<-- vm_utils.is_vm()')
    return is_running


def is_any_vm(session, state='running'):
    """
    Check if the any virtual machine is in the passed state or not
    Allowed values are vm_allowed_state = ['running', 'paused', 'shutoff']
    :param session: session for logging into restful api of the kimchi
    :param state: state of the virtual machine to check across. Default value is running.
    :return: True or False
    """
    session.logging.info('--> vm_utils.is_any_vm().state:%s', state)

    if state not in vm_allowed_states:
        session.logging.error('state cannot other than %s', vm_allowed_states)
        raise ValueError('state cannot other than %s', vm_allowed_states)

    vms = list_vms(session)

    if vms:
        for vm in vms:
            status = is_vm(vm_name=vm['name'], state=state)
            session.logging.debug('VM:%s found in state:%s', vm['name'], state)
            if status:
                return status
            else:
                continue

    session.logging.debug('No VM in state:%s', state)
    session.logging.info('<-- vm_utils.is_any_vm()')
    return False


def get_vm_by_name(session, vm_name='test_vm', expected_status=None):
    """
    Method to get VM by name
    :param session:session for logging into restful api of the kimchi
    :param vm_name:name of the VM to get details of it.
    :param expected_status:expected return value from kimchi api
    :return: http response from restful api of the kimchi
    """
    return session.request_get_json(vm_uri+ '/' + vm_name)

