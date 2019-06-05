#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='tanium',
    version='1.0.2',
    license='MIT',
    author='Jaroslav Brtan',
    author_email='jaroslav.brtan@gmail.com',
    url='',
    description="Resilient Circuits Components for 'tanium'",
    long_description="Suite of functions for querying the Tanium endpoints",
    install_requires=[
        'resilient_circuits>=30.0.0'
    ],
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
    ],
    entry_points={
        "resilient.circuits.components": [
            "TaniumGetAutorunsFunctionComponent = tanium.components.tanium_get_autoruns:FunctionComponent",
            "TaniumGetProcessesFunctionComponent = tanium.components.tanium_get_processes:FunctionComponent",
            "TaniumGetOpenPortsFunctionComponent = tanium.components.tanium_get_open_ports:FunctionComponent",
            "TaniumOnlineCheckFunctionComponent = tanium.components.tanium_online_check:FunctionComponent",
            "TaniumAgentSearchFunctionComponent = tanium.components.tanium_agent_search:FunctionComponent",
            "TaniumSweepForHashFunctionComponent = tanium.components.tanium_sweep_for_hash:FunctionComponent",
            "TaniumGetInstalledAppsFunctionComponent = tanium.components.tanium_get_installed_apps:FunctionComponent",
            "TaniumGetAssetInfoFunctionComponent = tanium.components.tanium_get_asset_info:FunctionComponent",
            "TaniumGetIpConnsFunctionComponent = tanium.components.tanium_get_ip_conns:FunctionComponent"
        ],
        "resilient.circuits.configsection": ["gen_config = tanium.util.config:config_section_data"],
        "resilient.circuits.customize": ["customize = tanium.util.customize:customization_data"],
        "resilient.circuits.selftest": ["selftest = tanium.util.selftest:selftest_function"]
    }
)