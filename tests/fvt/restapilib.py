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

import ConfigParser
import jsonschema
import json
import requests
import logging
import os

requests.packages.urllib3.disable_warnings()

__all__ = ['APIError', 'APIRequestError', 'APISession', 'SessionParameters']

# DEFAULT_CONNECTION_TIMEOUT = 5  # Default connection timeout, in secs
# DEFAULT_REQUEST_TIMEOUT = 300  # Default request timeout, in secs
DEFAULT_CONF = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'config'

_HTTP_SUCCESS_STATUS_RANGE = range(200, 299)  # All of the 2XX status codes


class APIError(Exception):
    """Base class for exceptions raised by this module."""

    pass


class APISession(object):
    """Represents an API session with the host Web Services API"""

    def __init__(self, conffile=DEFAULT_CONF):
        """ Creates an APISession object for use with the specified Host.
        """
        self._session = None
        self._base_uri = None
        self.username = None
        self.passwd = None
        self.host = None
        self.port = None
        self._session = self.session()  # Holds the session from requests
        self.sessionparams = SessionParameters(conffile=conffile)
        self.logging = self.sessionparams.getlogger()
        # base URI of connected machine
        self._base_uri = self.create_base_uri()

    def session(self):
        """
        Create the session object for API Request if no existing session.
        """
        if self._session is not None:
            raise APIError('Already have a session')

        self._session = requests.Session()
        return self._session

    def auth(self):
        """
        Set authentication to API session.

        \param username
            The username name to use for this session.

        \param password
            The password associated with username.

        """

        if self._session is None:
            self.session()

        self.username, self.passwd = self.sessionparams.getcredentials()

        if self.username is None:
            raise APIError('Username is None')
        if self.passwd is None:
            raise APIError('password is None')
        # Set auth at session level
        self._session.auth = (self.username, self.passwd)

        # set password expiration currently it default value
        # self._session.expires = '1432091741'
        # For now keeping it False to disable SSL verification
        self._session.verify = False
        return

    def create_base_uri(self):
        """
        Create the base URI using host and port.
        if no host is provided _base_uri is None.
        if port is None then _base_uri is just host
        if both is provided then append port to host.
        """

        if self._base_uri is not None:
            return self._base_uri

        self.host, self.port = self.sessionparams.geturlparams()
        if self.host is None:
            return None
        if self.port is None:
            return self.host

        self._base_uri = 'https://' + self.host + ':' + self.port
        return self._base_uri

    def end_session(self):
        """Ends an API session"""

        if self._session is None:
            return None  # Silently ignore
        # The session to be terminated by setting None in session object we
        # have.
        self._session = None
        return

    def request(
            self,
            method,
            uri,
            body=None,
            expected_status_values=None,
            headers=None, ):
        """
        Issue an WS API request and return the response body, if any.

        \param method
            The HTTP method to issue (eg. GET, PUT, POST, DELETE).

        \param uri
            The URI path and query parameter string for the request.

        \param body
        The request body that is input to the request, as a Unicode
            or String, or None if there is no input body.

        \param expected_status_values
            The HTTP status code that is expected on completion of the request.
            If this parameter is specified, the function raises an exception
            if the HTTP status from the request was not exactly as specified.
            Otherwise, it raises an error if the HTTP status is not 2XX.

        \param expected_reason
            The API reason code tha tis expected on completion of the request.
            If this parameter is specified in addition to the
            expected_status_values patameter, this function raises an exception
            if either the status or reason is not as specified.
            Otherwise, the reason code from the request is not considered.

        \param headers
            Request headers for this request, in the form of a Python Dict.
            Optional.  This function automatically augments these headers
            with the headers needed to specify the API session.  Note that if
            input headers are provided, the supplied Dict object will be
            modified by this function.
        """

        # Start with the headers supplied by caller, if any

        if headers is not None:
            hdrs = headers  # Use caller's dict, not a copy
        else:
            hdrs = dict()

        # If no session then throw error.

        if self._session is None:
            raise APIError('You have no session')

        resp = self._session.request(method, uri, data=body, headers=hdrs)

        # If an expected status was specified, check that the status exactly
        # matches wbat was expected, otherwise check that the status is one of
        # the success Statuses.

        if expected_status_values is not None:
            raise_exc = resp.status_code not in expected_status_values
        else:
            raise_exc = resp.status_code not in _HTTP_SUCCESS_STATUS_RANGE

        # Raise an exceptoin if the result is not as intended.

        if raise_exc:

            # If the request fails in some way WEb Services  API response
            # will usually include a standard error response body
            # in JSON format that  includes a more detailed reason
            # code (and message) for the failure.  It provides this data
            # in JSON format even if the request would return some other
            # format if the request had been successful.
            # So if the request  has failed, grab that additional info
            # for use in raising exceptions below.

            failure_reason = 0
            failure_code = None
            # if response.status_code not in _HTTP_SUCCESS_STATUS_RANGE:

            # The API provides the JSON error response in all usual error
            # cases.  But for certain less common errors this does not occur
            # because the error is caught higher in the processing stack.
            # So try to interpret the response as a JSON response body, but
            # just  silently ignore problems if we can't do this.

            try:
                error_resp = json.loads(resp.text)
                failure_reason = error_resp['reason']
                failure_code = error_resp['code']
            except (ValueError, KeyError):
                pass

            raise APIRequestError(resp.status_code, failure_reason,
                                  failure_code)

        # Return the response
        return resp

    def request_octet(
            self,
            method,
            uri,
            body=None,
            expected_status_values=None,
            headers=None,
    ):

        # Start with the request headers the caller supplied if any,
        # otherwise start with an empty set of headers.

        if headers is not None:
            hdrs = headers  # Using caller's dict, not a copy
        else:
            hdrs = dict()

        # If a request body was specified, convert it from its assumed Dict
        # or List form into JSON using the Python JSON library.  Also, add in
        # the required Content-Type HTTP message header to let the API know
        # that we are supplying input in JSON form. (A Content-Length header
        # is also needed to specify the body length, but for not not set.)

        body_json = body
        if body is not None:
            body_json = json.dumps(body)

        # Supply an HTTP Accepts header indicating we accept/expect that any
        # response body be JSON. The Accepts header is optional, and the API
        # will defautl to supplying JSON for any operation defined in API V1.1
        # to return JSON (even if in the future support for other formats would
        # be added). But its a good idea to specify this header as a safeguard
        # in case this function were called for an URI that is not capable of
        # returning JSON, as this function as currently coded would choke on
        # non-JSON responses.

        hdrs['Accept'] = 'application/json'

        # Now issue the request, and retrieve the response object and the
        # response body if provided.

        resp = self.request(
            method,
            uri,
            body=body_json,
            expected_status_values=expected_status_values,
            headers=hdrs,
        )

        return resp

    def request_json(
            self,
            method,
            uri,
            body=None,
            expected_status_values=None,
            headers=None,
    ):
        """
        Issue an WS API request that is defined to take JSON input and
        produce JSON output. (Nearly all WS API requests are like this.)

        Input and output bodies are specified as Python Dict or List objects,
        which are converted to/from JSON by this function.

        \param method
            The HTTP method to issue (eg. GET, PUT, POST, DELETE).

        \param uri
            The URI path and query parameter string for the request.

        \param body
            The request body that is input to the request, in the form of a
            Python Dict or List object.  This object is automatically converted
            to corresponding JSON by this function.  Optional.

        \param expected_status_values
            The HTTP status code that is expected on completion of the request.
        See corresponding parameter on request() method for more details.

        \param expected_reason
            The API reason code that is expected on completion of the request.
            See corresponding parameter on request() method for more details.

        \param headers
            Request headers for this request, in the form of a Python Dict.
            Optional.  This function automatically augments these headers
            with the headers needed to specify the JSON content type for input
            and output, and to specify the API session.  Note that if input
            headers are provided, the supplied Dict object will be modified
            by this function.

        """

        # Start with the request headers the caller supplied if any,
        # otherwise start with an empty set of headers.

        if headers is not None:
            hdrs = headers  # Using caller's dict, not a copy
        else:
            hdrs = dict()

        # If a request body was specified, convert it from its assumed Dict
        # or List form into JSON using the Python JSON library. Also, add in
        # the required Content-Type HTTP message header to let the API know
        # that we are supplying input in JSON form. (A Content-Length header
        # is also needed to specify the body length, but for now have not set.)

        body_json = None
        if body is not None:
            body_json = json.dumps(body)
        hdrs['Content-Type'] = 'application/json'

        # Supply an HTTP Accepts header indicating we accept/expect that any
        # response body be JSON. The Accepts header is optional, and the API
        # will default to supplying JSON for any operation defined in API V1.1
        # to return JSON (even if in the future support for other formats would
        # be added). But its a good idea to specify this header as a safeguard
        # in case this function were called for an URI that is not capable of
        # returning JSON, as this function as currently coded would choke on
        # non-JSON responses.

        hdrs['Accept'] = 'application/json'

        # Now issue the request, and retrieve the response object and the
        # response body if provided.

        response_body = self.request(
            method,
            uri,
            body=body_json,
            expected_status_values=expected_status_values,
            headers=hdrs,
        )

        # If a response body was returned, we presume it is JSON and
        # convert it into a Python dict we will return.

        resp_json = None
        if response_body is not None:
            try:
                resp_json = response_body.json()
            except ValueError, err:
                print 'response_body %s' % response_body
                print 'response_body headers %s' % response_body.headers
                raise APIError('Response body expected to be JSON but is'
                               + 'not valid %s', err)
        return resp_json

    def request_get_json(
            self,
            uri,
            expected_status_values=None,
            headers=None,
    ):
        """Convenience function to do a GET request that returns JSON."""
        if self._base_uri is not None:
            uri = self._base_uri + uri

        return self.request_json('GET', uri,
                                 expected_status_values=expected_status_values,
                                 headers=headers)

    def request_put_json(
            self,
            uri,
            body=None,
            expected_status_values=None,
            headers=None,
    ):
        """Convenience function to do a GET request that returns JSON."""

        if self._base_uri is not None:
            uri = self._base_uri + uri

        return self.request_json(
            'PUT',
            uri,
            body=body,
            expected_status_values=expected_status_values,
            headers=headers,
        )

    def request_post_json(
            self,
            uri,
            body=None,
            expected_status_values=None,
            headers=None,
    ):
        """Convenience function to do a POST request that
           provides/returns JSON."""

        if self._base_uri is not None:
            uri = self._base_uri + uri

        return self.request_json(
            'POST',
            uri,
            body=body,
            expected_status_values=expected_status_values,
            headers=headers,
        )

    def request_delete_json(
            self,
            uri,
            expected_status_values=None,
            headers=None,
    ):
        """Convenience function to do a DELETE request that returns JSON."""

        if self._base_uri is not None:
            uri = self._base_uri + uri

        return self.request_json(
            'DELETE',
            uri,
            expected_status_values=expected_status_values,
            headers=headers,
        )

    def request_get(
            self,
            uri,
            expected_status_values=None,
            headers=None,
    ):
        """Convenience function to do a GET request with header['Accept']
           as application/json that returns the response.
           Does not convert the response to JSON
        """

        if self._base_uri is not None:
            uri = self._base_uri + uri

        if headers is None:
            headers = dict()
        headers['Accept'] = 'application/json'

        return self.request('GET', uri,
                            expected_status_values=expected_status_values,
                            headers=headers)

    def request_put(
            self,
            uri,
            expected_status_values=None,
            headers=None,
    ):
        """Convenience function to do a PUT request with header['Accept']
           as application/json that returns the response.
           Does not convert the response to JSON
        """

        if self._base_uri is not None:
            uri = self._base_uri + uri

        if headers is None:
            headers = dict()
        headers['Accept'] = 'application/json'

        return self.request(
            'PUT',
            uri,
            expected_status_values=expected_status_values,
            headers=headers,
        )

    def request_post(
            self,
            uri,
            body=None,
            expected_status_values=None,
            headers=None,
    ):
        """Convenience function to do a POST request with header['Accept']
           as application/json that returns the response.
           Does not convert the response to JSON
        """

        if self._base_uri is not None:
            uri = self._base_uri + uri

        # If a request body was specified, convert it from its assumed Dict
        # or List form into JSON using the Python JSON library.  Also, add in
        # the required Content-Type HTTP message header to let the API know
        # that we are supplying input in JSON form. (A Content-Length header
        # is also needed to specify the body length, but for now have not set.)

        body_json = None
        if body is not None:
            body_json = json.dumps(body)

        if headers is None:
            headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        return self.request(
            'POST',
            uri,
            body=body_json,
            expected_status_values=expected_status_values,
            headers=headers,
        )

    def request_delete(
            self,
            uri,
            expected_status_values=None,
            headers=None,
    ):
        """Convenience function to do a DELETE request with header['Accept']
           as application/json that returns the response.
           Does not convert the response to JSON
        """

        if self._base_uri is not None:
            uri = self._base_uri + uri

        if headers is None:
            headers = dict()
        headers['Accept'] = 'application/json'

        return self.request(
            'DELETE',
            uri,
            expected_status_values=expected_status_values,
            headers=headers,
        )


class APIRequestError(APIError):
    """
    Raised when an API request ends in error or not as expected.

    Attributes:
        \param status
        HTTP status code from the request

        \param reason
        API reason code from the request

        \param message
        API diagnostic message from the request

        \param stack
        Internal diagnostic info for selected Status 500 errors
    """

    def __init__(
            self,
            status,
            reason=None,
            code=None,
    ):
        self.status = status
        self.reason = reason
        self.code = code

    def __str__(self):
        if self.code is not None:
            s = 'Request ended with status %s-%s (%s)' \
                % (self.status, self.reason, self.code)
        else:
            s = 'Request ended with status %s-%s' % (self.status,
                                                     self.reason)
        return s


class BadJSONResponse(APIError):
    """exceptions raised for Bad Json Response."""

    def __init__(
            self,
            error,
    ):
        self.error = error

    def __str__(self):
        s = 'Bad response: %s' % self.error
        return s


class InvalidInput(APIError):
    """exceptions raised for Invalid Input."""

    def __init__(
            self,
            error,
    ):
        self.error = error

    def __str__(self):
        s = 'Bad response: %s' % self.error
        return s


class SessionParameters(object):
    """
    Represents functionalities that could help in getting the
    session information.
    """

    def __init__(
            self,
            conffile=DEFAULT_CONF):
        """
        Attributes:
            \param conffile
             config file which contains all configuration
             information with sections
        """
        self.conffile = conffile
        self.username = None
        self.passwd = None
        self.host = '127.0.0.1'
        self.port = '8001'
        self.params = 'config'
        self.logfile = 'kimchi-api-test-suite.log'
        self.session_section = 'Session'
        self.logging = logging
        self.loglevel = 'ERROR'
        self.LEVELS = {'INFO': self.logging.INFO,
                       'DEBUG': self.logging.DEBUG,
                       'WARNING': self.logging.WARNING,
                       'ERROR': self.logging.ERROR,
                       'CRITICAL': self.logging.CRITICAL}
        if self.conffile is None:
            print 'Configuration file required %s' \
                  % self.conffile
        else:
            print 'Reading configuration file %s' % self.conffile
            self.params = ConfigParser.ConfigParser()
            print self.params.read(self.conffile)
            if self.params.has_section(self.session_section):
                if self.params.has_option(self.session_section, 'logfile'):
                    self.logfile = self.params.get(
                        self.session_section, 'logfile')

                if self.params.has_option(self.session_section, 'loglevel'):
                    self.loglevel = self.params.get(
                        self.session_section, 'loglevel')
            else:
                print "Section %s is not available in the config file " \
                      % self.session_section

            self.logging.basicConfig(format='%(asctime)s %(levelname)s: \
                                    %(message)s',
                                     datefmt='%m-%d-%Y %I:%M:%S %p',
                                     filename=self.logfile,
                                     level=self.LEVELS[self.loglevel])

    def getcredentials(self):
        """
        Returns user and password details for a session obtained from config
        file
        """
        if self.params.has_section(self.session_section):
            if self.params.has_option(self.session_section, 'user'):
                self.username = self.params.get(self.session_section, 'user')

            if self.params.has_option(self.session_section, 'passwd'):
                self.passwd = self.params.get(self.session_section, 'passwd')
        else:
            print "Section %s is not available in the config file " \
                  % self.session_section
            raise APIError('Session section not present in config')

        return self.username, self.passwd

    def geturlparams(self):
        """
        Returns host and port details for a session obtained from config file
        """
        if self.params.has_section(self.session_section):
            if self.params.has_option(self.session_section, 'host'):
                self.host = self.params.get(self.session_section, 'host')

            if self.params.has_option(self.session_section, 'port'):
                self.port = self.params.get(self.session_section, 'port')
        else:
            print "Section %s is not available in the config file " \
                  % self.session_section

        return self.host, self.port

    def getlogger(self):
        return self.logging


class Validator(object):
    """
    validator class having different validate methods
    """

    def __init__(self, logger=None):
        """
        :param logger:
        :return:
        """
        if logger is not None:
            self.logging = logger

    def validate_json(self, jsn, schma):
        """
        validates json against schema using jsonschema.validate library

        :param jsn: JSON to validate
        :param schma: Schema against which JSON should get validated
        :return:
        """
        if logging is not None:
            self.logging.info('--> validate_json()')
        if logging is not None:
            self.logging.debug(
                'validate_json(): jsn:%s' % jsn)
            self.logging.debug(
                'validate_json(): schma:%s' % schma)
        jsonschema.validate(jsn, schma)
        if logging is not None:
            self.logging.debug(
                'validate_json(): jsn is valid')
        if logging is not None:
            self.logging.info('<-- validate_json()')
