# -*- coding: utf-8 -*-

"""Generate a default configuration-file section for tanium"""

from __future__ import print_function


def config_section_data():
    """Produce the default configuration section for app.config,
       when called by `resilient-circuits config [-c|-u]`
    """
    return u"""
[tanium]
# user that got permissions to query Tanium via API
tanium_user = 

# user password
tanium_password = 

# FQDN of the tanium server
tanium_server = 

# tcp port the server is listening
tanium_port = 

#e.g. /home/<user_name>/pytan_2.3.3/
tanium_pytan_loc = 
"""
