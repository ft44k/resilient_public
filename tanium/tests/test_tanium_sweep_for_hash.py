# -*- coding: utf-8 -*-
"""Tests using pytest_resilient_circuits"""

from __future__ import print_function
import pytest
from resilient_circuits.util import get_config_data, get_function_definition
from resilient_circuits import SubmitTestFunction, FunctionResult

PACKAGE_NAME = "tanium"
FUNCTION_NAME = "tanium_sweep_for_hash"

# Read the default configuration-data section from the package
config_data = get_config_data(PACKAGE_NAME)

# Provide a simulation of the Resilient REST API (uncomment to connect to a real appliance)
resilient_mock = "pytest_resilient_circuits.BasicResilientMock"


def call_tanium_sweep_for_hash_function(circuits, function_params, timeout=10):
    # Fire a message to the function
    evt = SubmitTestFunction("tanium_sweep_for_hash", function_params)
    circuits.manager.fire(evt)
    event = circuits.watcher.wait("tanium_sweep_for_hash_result", parent=evt, timeout=timeout)
    assert event
    assert isinstance(event.kwargs["result"], FunctionResult)
    pytest.wait_for(event, "complete", True)
    return event.kwargs["result"].value


class TestTaniumSweepForHash:
    """ Tests for the tanium_sweep_for_hash function"""

    def test_function_definition(self):
        """ Test that the package provides customization_data that defines the function """
        func = get_function_definition(PACKAGE_NAME, FUNCTION_NAME)
        assert func is not None

    @pytest.mark.parametrize("file_hash_md5, incident_id, expected_results", [
        ("text", 123, {"value": "xyz"}),
        ("text", 123, {"value": "xyz"})
    ])
    def test_success(self, circuits_app, file_hash_md5, incident_id, expected_results):
        """ Test calling with sample values for the parameters """
        function_params = { 
            "file_hash_md5": file_hash_md5,
            "incident_id": incident_id
        }
        results = call_tanium_sweep_for_hash_function(circuits_app, function_params)
        assert(expected_results == results)