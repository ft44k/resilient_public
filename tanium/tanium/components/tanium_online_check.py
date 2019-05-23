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
            tanium_user = kwargs.get("tanium_user")  # text
            tanium_password = kwargs.get("tanium_password")  # text
            tanium_host = kwargs.get("tanium_host")  # text
            tanium_port = kwargs.get("tanium_port")  # text
            tanium_pytan_loc = kwargs.get("tanium_pytan_loc")  # text

            log = logging.getLogger(__name__)
            log.info("tanium_endpoint: %s", tanium_endpoint)
            log.info("tanium_user: %s", tanium_user)
            log.info("tanium_password: %s", tanium_password)
            log.info("tanium_host: %s", tanium_host)
            log.info("tanium_port: %s", tanium_port)
            log.info("tanium_pytan_loc: %s", tanium_pytan_loc)

            yield StatusMessage("starting...")
            
            is_endpoint_online = False
            tanium_object = tanium.TaniumWorker(tanium_user, \
            tanium_password, tanium_host, tanium_port, tanium_pytan_loc)
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