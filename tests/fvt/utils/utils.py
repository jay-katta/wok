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

"""
This module provide helper methods.
"""

import ConfigParser


def readconfig(self, confile, section, key):
    self.conffile = confile
    self.section = section
    self.value = None

    if self.conffile is None:
        print 'Configuration file required %s' \
              % self.conffile
    else:
        print 'Reading configuration file %s' % self.conffile
        self.params = ConfigParser.ConfigParser()
        self.params.read(self.conffile)
        if self.params.has_section(self.section):
            if self.params.has_option(self.section, key):
                self.value = self.params.get(self.section, key)
                return self.value
        else:
            print "Section %s is not available in the config file " % self.section


def wait_task_status_change(session, task_id, task_uri='/tasks/', task_final_status='finished',
                            task_current_status='running'):
    """
    Wait till task changed its status from task current status
    :param session: session for logging into restful api of the kimchi
    :param task_id: Task Id for which status need to be checked
    :param task_final_status: Final expected status of task
    :param task_current_status: Current status of task
    :return:task_resp: Get response of task id, if task status is other than task_final_status or task_current_status, Raise exception
    """
    session.logging.info(
        '-->utils.wait_task_status_change(), task_id:%s |task_uri:%s |task_final_status:%s |task_current_status:%s ',
        task_id, task_uri, task_final_status, task_current_status)
    counter = 0
    import time

    while True:
        if counter > 10:
            raise Exception('Task status change timed out for task id: %s', str(task_id))

        counter += 1

        task_resp = session.request_get_json(
            task_uri + '/' + task_id)
        task_status = task_resp["status"]
        if task_status == task_current_status:
            time.sleep(2)
            continue
        elif task_status == task_final_status:
            break
        else:
            raise Exception('Task status does not changed to %s. Task Response:%s', task_final_status, task_resp)

    session.logging.debug('task_resp:%s', task_resp)
    session.logging.info('<--utils.wait_task_status_change()')
    return task_resp

def getvalue(response, key):
    """
    Get value of key from response
    :param response: API response
    """
    if response is not None and key is not None:
        return response[key]
