# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Get Asset info Function: 

Collects asset information including OS version, 
currently logged in users, ip addresses, chasis type, etc 

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
import datetime

class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'tanium_get_asset_info"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get("tanium", {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get("tanium", {})

    @function("tanium_get_asset_info")
    def _tanium_get_asset_info_function(self, event, *args, **kwargs):
        """Function: Returns asset information including the currently
        logged in users to assist in potential asset ownership"""
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
            logged_in_users = []
            yield StatusMessage("querying Tanium for logged in users...")
            logged_in_users = tanium_object.get_logged_in_users(tanium_endpoint)
            
            ip_addresses = []
            yield StatusMessage("querying Tanium for ip addresses...")
            ip_addresses = tanium_object.get_ip_address(tanium_endpoint)
            
            os_info = []
            yield StatusMessage("querying Tanium for OS version...")
            os_info = tanium_object.get_os_info(tanium_endpoint)
            
            cpu_arch = []
            yield StatusMessage("querying Tanium for cpu architecture..")
            cpu_arch = tanium_object.get_cpu_arch(tanium_endpoint)
            
            chassis_type = []
            yield StatusMessage("querying Tanium for chassis type...")
            chassis_type = tanium_object.get_chassis_type(tanium_endpoint)
            
            serial_number = []
            yield StatusMessage("querying Tanium for serial number...")
            serial_number = tanium_object.get_serial_number(tanium_endpoint)
            
            yield StatusMessage("done...")

            results = {
                "hostname": tanium_endpoint,
                "users": logged_in_users,
                "os_info": os_info,
                "ip_addr": ip_addresses,
                "cpu_arch": cpu_arch,
                "chassis_type": chassis_type,
                "serial_number": serial_number
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()