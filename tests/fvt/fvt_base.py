#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Project Wok
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

import unittest
import os
from restapilib import APISession, APIError, APIRequestError
from restapilib import Validator

DEFAULT_CONF = os.path.dirname(os.path.abspath(__file__)) + 'config'


class TestBase(unittest.TestCase):
    """Represents an API session setup with the host Web Services API"""

    session = None

    def __init__(self, method='runTest'):
        """init with default method as runTest"""
        super(TestBase, self).__init__(method)

    @classmethod
    def setUpClass(cls):
        """
        Hook method for setting up class fixture
        before running tests in the class.
        Create session and set auth to the session
        """
        print '--> TestBase.setUpClass(): Create session '
        cls.session = APISession()
        # Log on to the API.  An exception will be raised if this fails.
        cls.logging = cls.session.logging
        cls.logging.debug('--> TestBase.setUpClass()')
        cls.validator = Validator(cls.logging)
        cls.logging.debug('TestBase.setUpClass(): Setting auth to session')
        try:
            cls.session.auth()
            cls.logging.debug('TestBase.setUpClass(): Auth details set to '
                              'session and base URI created as %s'
                              % cls.session._base_uri)
        except APIError, err:
            print 'ERROR %s' % err
            print err.__str__()
            if cls.session is not None:
                cls.logging.error('TestBase.setUpClass(): Ending session'
                                  ' as API error happened')
                cls.session.end_session()
        finally:
            cls.logging.debug('<-- TestBase.setUpClass()')

    def setUp(self):
        """Hook method for setting up the test fixture before exercising it."""
        pass

    def tearDown(self):
        """Hook method for deconstructing the test fixture after testing it."""
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Hook method for deconstructing the class
        fixture after running all tests in the class.
        """
        if cls.session is not None:
            print 'TestBase.tearDownClass(): Ending session'
            cls.session.end_session()

    def get(self):
        try:
            resp_net = self.session.request_get_json('/')
            print resp_net
        except APIRequestError as err:
            print 'ERROR %s' % err
            print err.__str__()
