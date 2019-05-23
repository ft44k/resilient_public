# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""
Takes python dict and column names
    outputs csv

"""

import csv
import tempfile
import os
import logging

csv.register_dialect('myDialect', delimiter = ',', quoting=csv.QUOTE_ALL,skipinitialspace=True)



def convert_to_csv_and_attach_to_incident(header, dict_data, file_name, incident_id, self):

    #csv_columns = ['Path','MD5 Hash']
    log = logging.getLogger(__name__)
    
    
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            #temp_file.write(content)
            writer = csv.DictWriter(temp_file, fieldnames=header, dialect='myDialect')
            writer.writeheader()
            for data in dict_data:
                line = {}
                for index, val in enumerate(data):
                    try:
                        line[header[index]] = val
                    except Exception as e:
                        log.error('index: %i : value: %s' % (index, val)) 
                #writer.writerow({header[0]: data[0], header[1]: data[1]})
                writer.writerow(line)
            temp_file.close()
            # Create a new artifact
            client = self.rest_client()
            attachment_uri = "/incidents/{}/attachments".format(incident_id)
            new_attachment = client.post_attachment(attachment_uri, temp_file.name, filename=file_name, mimetype='text/csv')
        except Exception as e:
            log.error("Something bad happened: %s" % str(e))
            
        finally:
          os.unlink(temp_file.name)
