# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Get Open Ports Function

Identifies the listening TCP ports, 
including the process listening to the port, the MD5 hash of the process, 
the display name of the process (if available), 
and the listening IP Address and port. 
The Sensor definition can be modified to exclude process 
and IP range

input: hostname

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
    """Component that implements Resilient function 'tanium_get_open_ports"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get("tanium", {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get("tanium", {})

    @function("tanium_get_open_ports")
    def _tanium_get_open_ports_function(self, event, *args, **kwargs):
        """Function: Identifies the listening TCP ports, 
        including the process listening to the port, 
        the MD5 hash of the process, the display name 
        of the process (if available), and the listening IP Address 
        and port. The Sensor definition can be modified to exclude 
        process and IP range."""
        now = datetime.datetime.now()
        try:
            # Get the function parameters:
            tanium_endpoint = kwargs.get("tanium_endpoint")  # text
            incident_id = kwargs.get("incident_id")  # number

            # Get Tanium config values
            tanium_user = self.options.get("tanium_user")
            tanium_password = self.options.get("tanium_password")
            tanium_server = self.options.get("tanium_server")
            tanium_port = self.options.get("tanium_port")
            tanium_pytan_loc = self.options.get("tanium_pytan_loc")
            
            log = logging.getLogger(__name__)
            log.debug("tanium_endpoint: %s", tanium_endpoint)
            log.debug("incident_id: %s", incident_id)
            log.debug("tanium_user: %s", tanium_user)
            log.debug("tanium_password: %s", tanium_password)
            log.debug("tanium_server: %s", tanium_server)
            log.debug("tanium_port: %s", tanium_port)
            log.debug("tanium_pytan_loc: %s", tanium_pytan_loc)

            yield StatusMessage("starting...")

            tanium_object = tanium.TaniumWorker(tanium_user, \
            tanium_password, tanium_server, tanium_port, tanium_pytan_loc)
            open_ports = []
            yield StatusMessage("querying Tanium for data...")
            open_ports = tanium_object.get_open_ports(tanium_endpoint)
            
            if open_ports:
                yield StatusMessage("Tanium returned data...")
                # header, data, file_name, incident_id
                convert.convert_to_csv_and_attach_to_incident(\
                    ['Open Port'], open_ports, \
                    now.strftime("%Y-%m-%d_%H:%M")+'-Open_Ports-' + \
                    tanium_endpoint+'.csv', incident_id, self)
            else:
                yield StatusMessage("No data returned")

            
            results = {
                "open_ports": open_ports
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()