# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Online Check Function

This script checks if given hostname is online and running the Tanium agent 

input: hostname

output: boolean

"""

import logging
from resilient_circuits import (
    ResilientComponent, function, handler, StatusMessage,
    FunctionResult, FunctionError
    )
import tanium.util.selftest as selftest
import tanium.util.tanium as tanium

class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'tanium_online_check"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get("tanium", {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get("tanium", {})

    @function("tanium_online_check")
    def _tanium_online_check_function(self, event, *args, **kwargs):
        """Function: Checks if a given hostname is online 
        (running the Tanium agent)"""
        try:
            # Get the function parameters:
            tanium_endpoint = kwargs.get("tanium_endpoint")  # text

            # Get Tanium config values
            tanium_user = self.options.get("tanium_user")
            tanium_password = self.options.get("tanium_password")
            tanium_server = self.options.get("tanium_server")
            tanium_port = self.options.get("tanium_port")
            tanium_pytan_loc = self.options.get("tanium_pytan_loc")
            
            log = logging.getLogger(__name__)
            log.debug("tanium_endpoint: %s", tanium_endpoint)
            log.debug("tanium_user: %s", tanium_user)
            log.debug("tanium_password: %s", tanium_password)
            log.debug("tanium_server: %s", tanium_server)
            log.debug("tanium_port: %s", tanium_port)
            log.debug("tanium_pytan_loc: %s", tanium_pytan_loc)

            yield StatusMessage("starting...")
            
            is_endpoint_online = False
            tanium_object = tanium.TaniumWorker(tanium_user, \
            tanium_password, tanium_server, tanium_port, tanium_pytan_loc)
            yield StatusMessage("querying Tanium for data...")
            is_endpoint_online = tanium_object.check_online(tanium_endpoint)
            yield StatusMessage("done...")
            
            results = {
                "check": is_endpoint_online,
                "hostname": tanium_endpoint
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()