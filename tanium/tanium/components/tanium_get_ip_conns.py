# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Get IP Conns Function

Collects the protocol, local address / port, 
process name, application name, remote port, and connection state
for all active IP connections for given hostname.

input: hostname

output: list

Example: tcp|192.168.95.186:51866|explorer.exe|Windows Explorer|165.254.58.66:80|established

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
    """Component that implements Resilient function 'tanium_get_ip_conns"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get("tanium", {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get("tanium", {})

    @function("tanium_get_ip_conns")
    def _tanium_get_ip_conns_function(self, event, *args, **kwargs):
        """Function: Returns the protocol, local address / port, 
        process name, application name, remote port, and 
        connection state for all active IP connections on an endpoint. 
        Example: tcp|192.168.95.186:51866|explorer.exe|
        Windows Explorer|165.254.58.66:80|established"""
        now = datetime.datetime.now()
        try:
            # Get the function parameters:
            tanium_endpoint = kwargs.get("tanium_endpoint")  # text
            incident_id = kwargs.get("incident_id")  # number
            tanium_user = kwargs.get("tanium_user")  # text
            tanium_password = kwargs.get("tanium_password")  # text
            tanium_host = kwargs.get("tanium_host")  # text
            tanium_port = kwargs.get("tanium_port")  # text
            tanium_pytan_loc = kwargs.get("tanium_pytan_loc")  # text

            log = logging.getLogger(__name__)
            log.info("tanium_endpoint: %s", tanium_endpoint)
            log.info("incident_id: %s", incident_id)
            log.info("tanium_user: %s", tanium_user)
            log.info("tanium_password: %s", tanium_password)
            log.info("tanium_host: %s", tanium_host)
            log.info("tanium_port: %s", tanium_port)
            log.info("tanium_pytan_loc: %s", tanium_pytan_loc)

            yield StatusMessage("starting...")

            tanium_object = tanium.TaniumWorker(tanium_user, \
            tanium_password, tanium_host, tanium_port, tanium_pytan_loc)
            ip_conns = []
            yield StatusMessage("querying Tanium for data...")
            ip_conns = tanium_object.get_ip_connections(tanium_endpoint)

            if ip_conns:
                yield StatusMessage("Tanium returned data...")
                # header, data, file_name, incident_id
                convert.convert_to_csv_and_attach_to_incident(\
                    ["Application","Connection State", \
                    "Local IP and Port", "Process", "Protocol", \
                    "Remote IP and Port"], ip_conns, \
                    now.strftime("%Y-%m-%d_%H:%M")+'-IP_Conns-'+\
                    tanium_endpoint+'.csv', incident_id, self)
            else:
                yield StatusMessage("No data returned")

            results = {
                "ip_conns": ip_conns
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()