# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Tanium Class 

Collects asset information including OS version, 
currently logged in users, ip addresses, chasis type, etc 

input: hostname

output: dict , see results structure

"""

import sys
import os
import logging
from datetime import datetime, timedelta
import StringIO
import csv
import time


#this has to point to the pytan folder
#pytan_loc = "/home/resadmin/Integrations/tanium/pytan-2.2.3/"
#pytan_loc = "c:/work/Solutions/Tanium/scripts/L1/pytan-2.2.3/"
recheck_interval	= 10  # script will wait this many seconds before asking again for data


class MyDialect(csv.Dialect):
    """
    This is a helper class
    """
    strict = True
    skipinitialspace = True
    quoting = csv.QUOTE_ALL
    delimiter = ','
    quotechar = '"'
    lineterminator = '\n'

class TaniumWorker(object):
    """
    This class provides methods for quering the Tanium endpoints
    for data

    """
    def __init__(self, name, password, host, port, pytan_loc):
        self.username = name
        self.password = password
        self.host = host
        self.port = port
        self.pytan_loc = pytan_loc
        self.pytan_handler = self.init_pytan()


    def init_pytan(self):

        # disable python from generating a .pyc file
        sys.dont_write_bytecode = True

        # change me to the path of pytan if this script is not running from EXAMPLES/PYTAN_API
        pytan_static_path = os.path.join(os.path.expanduser(self.pytan_loc), 'lib')

        # Determine our script name, script dir
        my_file = os.path.abspath(sys.argv[0])
        my_dir = os.path.dirname(my_file)

        # try to automatically determine the pytan lib directory by assuming it is in '../../lib/'
        parent_dir = os.path.dirname(my_dir)
        pytan_root_dir = os.path.dirname(parent_dir)
        lib_dir = os.path.join(pytan_root_dir, 'lib')

        # add pytan_loc and lib_dir to the PYTHONPATH variable
        path_adds = [lib_dir, pytan_static_path]
        [sys.path.append(aa) for aa in path_adds if aa not in sys.path]

        # import pytan
        import pytan

        # create a dictionary of arguments for the pytan handler
        handler_args = {}

        # establish our connection info for the Tanium Server
        handler_args['username'] = self.username
        handler_args['password'] = self.password
        handler_args['host'] = self.host
        handler_args['port'] = self.port


        # optional, level 0 is no output except warnings/errors
        # level 1 through 12 are more and more verbose
        handler_args['loglevel'] = 0

        # optional, use a debug format for the logging output (uses two lines per log entry)
        handler_args['debugformat'] = False

        # optional, this saves all response objects to handler.session.ALL_REQUESTS_RESPONSES
        # very useful for capturing the full exchange of XML requests and responses
        handler_args['record_all_requests'] = False

        # instantiate a handler using all of the arguments in the handler_args dictionary
        #print "...CALLING: pytan.handler() with args: {}".format(handler_args)
        pytan.utils.get_all_pytan_loggers()["pytan.pollers.QuestionPoller"].disabled = True
        handler = pytan.Handler(**handler_args)

        return handler

    def run_manual_question_for_host(self, sensors, computer_name=0, md5hash=0):

        logger = logging.getLogger(__name__)
        #this is used in the while loop for the timedelta
        #sometimes agents stop responding after the check for online 
        #is done and script ends up running in an infinite loop 
        start = datetime.now()

        function_name = sys._getframe().f_code.co_name
        # setup the arguments for the handler() class
        kwargs = {}

        kwargs["get_results"] = True
        kwargs["sensors"] = sensors
        kwargs["qtype"] = u'manual'
        if sensors == [u'Online']:
            kwargs["override_timeout_secs"] = 90
            kwargs["force_passed_done_count"] = 1

        if [sensors.index(i) for i in sensors if \
        u'Running Processes with MD5 Hash, that' in i]:
            kwargs["question_filters"] = ["Is Windows, that equals: True",\
             "Running Processes with MD5 Hash, that contains:"+md5hash]
            kwargs["complete_pct"] = 98
        else:
            kwargs["question_filters"] = ["Computer Name, \
            that starts with:" + computer_name]
            kwargs["force_passed_done_count"] = 1

        kwargs["refresh_data"] = True

        try:
            response = self.pytan_handler.ask(**kwargs)
        except Exception as e:
            logger.error("ERROR {}: {}\n".format(function_name, str(e)))
            return False
        finally:
            pass

        if response['question_results']:
            results = response['question_results']
            while True:
                # call the export_obj() method to convert response 
                # to CSV and store it in out
                export_kwargs = {}
                export_kwargs['obj'] = results
                export_kwargs['export_format'] = 'csv'
                out = self.pytan_handler.export_obj(**export_kwargs)

                if ("[current result unavailable]" in out or \
                    "[results currently unavailable]" in out):
                    #check for how log we are running, 
                    #if it is more than threshold, exit the loop
                    current = datetime.now()
                    elapsed = current - start
                    if elapsed > timedelta(minutes=5):

                        if sensors != [u'Online']:
                            logging.error("ERROR {}: function is running\
                             more than 5 minutes\n".format(function_name))
                        break
                    else:

                        if sensors != [u'Online']:			
                            logging.debug("{}: Host responded, but data \
                                is not yet available, checking again in \
                                {} seconds..."\
                                .format(function_name, recheck_interval))
                            logging.debug("out: {}".format(out))
                        time.sleep(recheck_interval)
                        kwargs = {}
                        results = self.pytan_handler.get_result_data(\
                            response['question_object'], **kwargs)
                else:
                    break
            logging.debug(out)
            return out

    def parse_the_lines_and_remove_that_number(self, line):
        lineasfile=StringIO.StringIO(line)
        reader=csv.reader(lineasfile,MyDialect())
        values = []
        #ehm there is just one row, I have to check what the above returns
        for row in reader:
            values = row
        values.remove('1')
        return values 

    def check_online(self, hostname):

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        start = datetime.now()

        out = self.run_manual_question_for_host([u"Online"], hostname)
        # This guy here returns string like this 'Online\r\nTrue\r\n'
        # when a machine is offline it returns an empty string
        lines = out.split("\r\n")
        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    if len(line) > 0:
                        lineasfile=StringIO.StringIO(line)
                        reader=csv.reader(lineasfile,MyDialect())
                        values = []
                        #ehm there is just one row, I have to check what the above returns
                        for row in reader:
                            values = row
                        # when the host is online the values contains ['1', 'True']
                        if values[1] == 'True':
                            return True
                        else:
                            return False
                else:
                    saw_header = 1

    def get_running_processes(self, hostname):
        '''
        gathers info about running processes
        returns list
        '''

        #results will be stored here
        running_processes = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Running Processes with MD5 Hash'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        running_processes.append(values)  #md5_hash, process_name
                else:
                    saw_header = 1

        return running_processes

    def get_ip_connections(self, hostname):
        '''
        gathers info about IP connections
        returns list
        '''

        # Application,Connection State,Count,Local IP and Port,Process,Protocol,Remote IP and Port
        #results will be stored here
        ip_connections = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'IP Connections'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        ip_connections.append(values)  #md5_hash, process_name
                else:
                    saw_header = 1
        return ip_connections

    def get_installed_apps(self, hostname):
        '''
        gathers info about installed applications
        returns list
        '''

        # Count,Name,Silent Uninstall String,Uninstallable,Version 
        #results will be stored here
        installed_apps = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Installed Applications'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        installed_apps.append(values)  #md5_hash, process_name
                else:
                    saw_header = 1
        return installed_apps

    def get_autoruns_by_category(self, hostname, hashtype, include_ms_binaries):
        '''
        gathers info about Autoruns
        returns list
        '''

        # Hash,Category,Count,Description,Entry,Entry Location,
        # Image Path,Launch String,Profile,Publisher,Version

        #results will be stored here
        autoruns = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Autoruns by Category{HashAlgorithm='+hashtype+\
            ',ASEPGrp=%s,InclMSPubs='+include_ms_binaries+'}'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        autoruns.append(values)  #md5_hash, process_name
                else:
                    saw_header = 1
        return autoruns

    def sweep_for_hash(self, md5hash):
        '''
        sweeps all windows endpoints for a presence
        of a process with given md5 hash

        returns list
        '''

        # Computer Name,Count,MD5 Hash,Path
        #results will be stored here
        hits = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Computer Name', u'Running Processes with MD5 Hash, \
            that contains:'+md5hash], md5hash=md5hash)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        hits.append(values)  #md5_hash, process_name
                else:
                    saw_header = 1
        return hits

    def get_open_ports(self, hostname):
        '''
        gathers info about IP connections
        returns list
        '''

        # Count,Open Port
        #results will be stored here
        open_ports = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Open Port'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        open_ports.append(values)  #md5_hash, process_name
                else:
                    saw_header = 1
        return open_ports

    def get_logged_in_users(self, hostname):
        '''
        gathers info about logged in users
        returns list
        '''

        # Count,Logged In Users
        #results will be stored here
        logged_in_users = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Logged in Users'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        logged_in_users.append(values[0])  #Logged in Users
                else:
                    saw_header = 1
        return logged_in_users

    def get_ip_address(self, hostname):
        '''
        gathers info about assigned IP addresses
        returns list
        '''

        # count, ip address
        #results will be stored here
        ip_addr = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'IP Address'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        ip_addr.append(values[0])  #ip address
                else:
                    saw_header = 1
        return ip_addr

    def get_os_info(self, hostname):
        '''
        gathers info about OS of the hostname
        returns list
        '''

        # count, Operating System
        #results will be stored here
        os_info = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Operating System'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        os_info = values  #os info
                else:
                    saw_header = 1
        return os_info

    def get_cpu_arch(self, hostname):
        '''
        gathers info about CPU architecture
        returns list
        '''

        # count, Operating System
        #results will be stored here
        cpu_info = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'CPU Architecture'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        cpu_info = values  #os info
                else:
                    saw_header = 1
        return cpu_info

    def get_chassis_type(self, hostname):
        '''
        gathers info about chassis type
        returns list
        '''

        # count, chassis type
        #results will be stored here
        chassis_info = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Chassis Type'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        chassis_info = values  #os info
                else:
                    saw_header = 1
        return chassis_info

    def get_serial_number(self, hostname):
        '''
        gathers info about computer serial number
        returns list
        '''

        # count, serial number
        #results will be stored here
        serial_number = []

        logger = logging.getLogger(__name__)
        function_name = sys._getframe().f_code.co_name

        # DEBUG
        logger.debug("{} called".format(function_name))

        out = self.run_manual_question_for_host(\
            [u'Computer Serial Number'], hostname)
        lines = out.split("\r\n")

        if len(lines) > 1:
            saw_header = 0
            for line in lines:
                if saw_header == 1:
                    #data in a line is delimited by comma
                    if len(line) > 0:
                        values = self.parse_the_lines_and_remove_that_number(line)
                        serial_number = values  #os info
                else:
                    saw_header = 1
        return serial_number