# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Agent search Function: 

Tanium keeps track of connected agents for 30d time period. 
So if a hostname is missing on this list, it is very likely the agent
needs to be deployed

input: hostname

output: dict , see the results structure

"""

import logging
from resilient_circuits import (
    ResilientComponent, function, handler, StatusMessage, 
    FunctionResult, FunctionError
    )
import tanium.util.selftest as selftest
import tanium.util.tanium as tanium
import pprint

class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'tanium_agent_search"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get("tanium", {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get("tanium", {})

    @function("tanium_agent_search")
    def _tanium_agent_search_function(self, event, *args, **kwargs):
        """Function: Tanium holds client status for last 30d. 
        This functions checks if given endpoint is on the list. 
        If it is not, we could presume the agent needs to be deployed"""
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
            
            tanium_object = tanium.TaniumWorker(tanium_user, \
            tanium_password, tanium_host, tanium_port, tanium_pytan_loc)
            
            yield StatusMessage("querying Tanium for logged in users...")
            
            agent_check = tanium_object.check_agent(tanium_endpoint)
            
            results = {
              "found" : False,
              "input" : tanium_endpoint
            }
            
            if agent_check:
              results['found'] = True
              results['ipaddr'] = agent_check['ipaddress_client']
              results['last_seen'] = agent_check['last_seen']
              results['hostname'] = agent_check['hostname']
              
            log.debug(pprint.pprint(results))
            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()