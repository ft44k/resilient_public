# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Sweep for hash Function

This script checks if a given MD5 hash is among running processes 
in the environment [Windows OS]. 
Returns a list of hostnames (or empty one if there is no hit)

input: md5 hash

output: list

"""

import logging
from resilient_circuits import (
    ResilientComponent, function, handler, StatusMessage, 
    FunctionResult, FunctionError
    )
import tanium.util.selftest as selftest
import tanium.util.convert_to_csv as convert
import tanium.util.tanium as tanium
import datetime

class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'tanium_sweep_for_hash"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get("tanium", {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get("tanium", {})

    @function("tanium_sweep_for_hash")
    def _tanium_sweep_for_hash_function(self, event, *args, **kwargs):
        """Function: Checks if a given MD5 hash is among running 
        processes in our environment [Windows OS]. 
        Returns a list of hostnames of False"""
        now = datetime.datetime.now()
        try:
            # Get the function parameters:
            incident_id = kwargs.get("incident_id")  # number
            file_hash_md5 = kwargs.get("file_hash_md5")  # text

            # Get Tanium config values
            tanium_user = self.options.get("tanium_user")
            tanium_password = self.options.get("tanium_password")
            tanium_server = self.options.get("tanium_server")
            tanium_port = self.options.get("tanium_port")
            tanium_pytan_loc = self.options.get("tanium_pytan_loc")

            log = logging.getLogger(__name__)
            log.debug("incident_id: %s", incident_id)
            log.debug("file_hash_md5: %s", file_hash_md5)
            log.debug("tanium_user: %s", tanium_user)
            log.debug("tanium_password: %s", tanium_password)
            log.debug("tanium_server: %s", tanium_server)
            log.debug("tanium_port: %s", tanium_port)
            log.debug("tanium_pytan_loc: %s", tanium_pytan_loc)

            yield StatusMessage("starting...")

            tanium_object = tanium.TaniumWorker(tanium_user, \
            tanium_password, tanium_server, tanium_port, tanium_pytan_loc)
            machines_where_hash_was_found = []
            yield StatusMessage("querying Tanium for data...")
            machines_where_hash_was_found = tanium_object.sweep_for_hash(file_hash_md5)
            
            if machines_where_hash_was_found:
                yield StatusMessage("Tanium returned data...")
                # header, data, file_name, incident_id
                convert.convert_to_csv_and_attach_to_incident([ \
                    'Computer Name', 'MD5 Hash', 'Path'], \
                    machines_where_hash_was_found, \
                    now.strftime("%Y-%m-%d_%H:%M")+'-sweep_for_hash-'+ \
                    file_hash_md5+'.csv', incident_id, self)
            else:
                yield StatusMessage("hash not found")

            results = {
                "machines": machines_where_hash_was_found,
                "hash": file_hash_md5
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()