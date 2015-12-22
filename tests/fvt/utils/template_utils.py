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

from tests.fvt.utils import utils
template_uri = '/templates/'
default_template_name = 'test_template'


# TODO: removed template data and move expected_status to last
def create_template(session, template_data=None, expected_status=None, name=default_template_name, os_distro=None,
                    os_version=None, cpus=None, memory=None, cdrom='iso_remote_path', storagepool=None, networks=None,
                    disks=None, graphics=None, cpu_info=None):
    """
    Method to create a template that can be used while creating VMs
    :param session: session for logging into restful api of the kimchi
    :param template_data: input parameters for creating a template
    :param name: The name of the Template. Default is test_template
    :param os_distro *(optional)*: The operating system distribution
    :param os_version *(optional)*: The version of the operating system distribution
    :param cpus *(optional)*: The number of CPUs assigned to the VM.
    :param memory *(optional)*: The amount of memory assigned to the VM.
    :param cdrom *(optional)*: A volume name or URI to an ISO image. By default value of iso_remote_path from config file
    :param storagepool *(optional)*: URI of the storagepool.Default is '/storagepools/default'
    :param networks *(optional)*: list of networks will be assigned to the new VM.Default is '[default]'
    :param disks *(optional)*: An array of requested disks with the following optional fields
         (either *size* or *volume* must be specified):
           * index: The device index
           * size: The device size in GB
           * base: Base image of this disk
    :param graphics *(optional)*: The graphics paramenters of this template
            * type: The type of graphics. It can be VNC or spice or None.
                * vnc: Graphical display using the Virtual Network
                       Computing protocol
                * spice: Graphical display using the Simple Protocol for
                         Independent Computing Environments
                * null: Graphics is disabled or type not supported
            * listen: The network which the vnc/spice server listens on.
    :param cpu_info *(optional)*: CPU-specific information.
            * topology: Specify sockets, threads, and cores to run the virtual CPU
                threads on.
                All three are required in order to specify cpu topology.
                * sockets - The number of sockets to use.
                * cores   - The number of cores per socket.
                * threads - The number of threads per core.
                If specifying both cpus and CPU topology, make sure cpus is
                equal to the product of sockets, cores, and threads.
    :return: http response from restful api of the kimchi
    """
    
    session.logging.info('-->template_utils.create_template(), name: %s |os_distro:%s |os_version:%s|cpus:%s |memory:%s |cdrom:%s |storagepool:%s |networks:%s |disks:%s |graphics:%s |cpu_info:%s |expected_status:%s'
                         ,name, os_distro,os_version,cpus,memory,cdrom,storagepool,networks,disks,graphics,cpu_info, expected_status)
    
    if cdrom == 'iso_remote_path' or cdrom == 'iso_image_path' or cdrom == 'iso_image_path_no_permission':
        cdrom = utils.readconfig(session,'config', 'Template', cdrom)
        
    if template_data is None:
        template_data = {'name': name, 'cdrom': cdrom}
        if os_distro is not None:
            template_data['os_distro'] = os_distro
        if os_version is not None:
            template_data['os_version'] = os_version
        if cpus is not None:
            template_data['cpus'] = cpus
        if memory is not None:
            template_data['memory'] = memory
        if storagepool is not None:
            template_data['storagepool'] = storagepool
        if networks is not None:
            template_data['networks'] = networks
        if disks is not None:
            template_data['disks'] = disks
        if graphics is not None:
            template_data['graphics'] = graphics
        if cpu_info is not None:
            template_data['cpu_info'] = cpu_info

    response = session.request_post_json(template_uri, template_data, expected_status)
    session.logging.info('<--template_utils.create_template()')
    return response


def delete_template(session, name=default_template_name, expected_status=None):
    """
    Method to delete a template
    :param session: session for logging into restful api of the kimchi
    :param template_name: name of the template that needs to be deleted.
    :return: http response from restful api of the kimchi
    """
    session.logging.info('<-->template_utils.delete_template(), name: %s', default_template_name)
    return session.request_delete(template_uri + '/' + name, expected_status)


def clone_template(session, template_name, expected_status):
    """
    Method to clone a template that can be used while creating VMs
    :param session: session for logging into restful api of the kimchi
    :param template_name: name of the template that needs to be cloned.
    :return: http response from restful api of the kimchi
    """
    return session.request_post_json(template_uri + '/' + template_name + '/clone', expected_status)


def edit_template(session, template_name, update_template_data, expected_status):
    """
    Method to edit a template
    :param session: session for logging into restful api of the kimchi
    :param template_name: name of the template that needs to be edited.
    :param update_template_data : input parameters that can be modified for the template.

            * name: A name for this template
        * folder: A virtual path which can be used to organize Templates in the user
          interface.  The format is an array of path components.
        * icon: A URI to a PNG image representing this template
        * os_distro: The operating system distribution
        * os_version: The version of the operating system distribution
        * cpus: The number of CPUs assigned to the VM
        * memory: The amount of memory assigned to the VM
        * cdrom: A volume name or URI to an ISO image
        * storagepool: URI of the storagepool where template allocates vm storage.
        * networks *(optional)*: list of networks will be assigned to the new VM.
        * disks: An array of requested disks with the following optional fields
          (either *size* or *volume* must be specified):
            * index: The device index
            * size: The device size in GB
            * volume: A volume name that contains the initial disk contents
            * format: Format of the image. Valid formats: bochs, cloop, cow, dmg, qcow, qcow2, qed, raw, vmdk, vpc.
        * graphics *(optional)*: A dict of graphics paramenters of this template
            * type: The type of graphics. It can be VNC or spice or None.
                * vnc: Graphical display using the Virtual Network
                       Computing protocol
                * spice: Graphical display using the Simple Protocol for
                         Independent Computing Environments
                * null: Graphics is disabled or type not supported
            * listen: The network which the vnc/spice server listens on.
    :return: http response from restful api of the kimchi
    """
    return session.request_put_json(template_uri + '/' + template_name, update_template_data, expected_status)


def get_template_by_name(session, template_name=default_template_name, expected_values=None):
    """
    Method to get template by name
    :param session:session for logging into restful api of the kimchi
    :param template_name:name of the template to get details of it.
    :param expected_values:
    :return: http response from restful api of the kimchi
    """
    return session.request_get_json(template_uri + '/' + template_name, expected_values)

