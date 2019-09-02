#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##
# Copyright 2017 FIWARE Foundation, e.V.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##

from configparser import ConfigParser, NoSectionError
import logging
from os import environ
from os.path import dirname, join, abspath


__author__ = 'fla'

__version__ = '1.0.0'


"""
Default configuration.

The configuration `cfg_defaults` are loaded from `cfg_filename`, if file exists in
/etc/fiware.d/fiware-sla.ini

Optionally, user can specify the file location manually using an Environment variable
called BACKLOG_SETTINGS_FILE.
"""

name = 'fiware-sla'

cfg_dir = "/etc/fiware.d"

if environ.get("SLA_SETTINGS_FILE"):
    cfg_filename = environ.get("SLA_SETTINGS_FILE")
    cfg_dir = dirname(cfg_filename)

else:
    cfg_filename = join(cfg_dir, '%s.ini' % name)

Config = ConfigParser()

Config.read(cfg_filename)


def check_log_level(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)

    if not isinstance(numeric_level, int):
        print('Invalid log level: {}'.format(loglevel))
        exit()

    return numeric_level


def config_section_map(section):
    dict1 = dict()
    options = list()

    try:
        options = Config.options(section)
    except NoSectionError:
        print("ERROR, no section found: %s" % section)
        exit(1)

    for option in options:
        dict1[option] = Config.get(section, option)

        if dict1[option] == -1:
            print("WARNING, skip: %s" % option)

    return dict1


if Config.sections():
    # Data from Auth section
    auth_section = config_section_map("jira")

    JIRA_USER = auth_section['user']
    JIRA_PASSWORD = auth_section['password']
    JIRA_QUERY = auth_section['query']
    JIRA_URL = auth_section['url']

    # Data from Log section
    log_section = config_section_map("logging")

    LOGGING_LEVEL = check_log_level(log_section['level'])
    LOGGING_FILE = log_section['file']

    # Data from OpenStack section
    openstack_section = config_section_map("openstack")

    OS_PROJECT_ID = openstack_section['os_project_id']
    OS_USERNAME = openstack_section['os_username']
    OS_PASSWORD = openstack_section['os_password']
    OS_AUTH_URL = openstack_section['os_auth_url']
    OS_MONASCA_URL = openstack_section['os_monasca_url']

else:
    msg = '\nERROR: There is not defined SLA_SETTINGS_FILE environment variable ' \
          '\n       pointing to configuration file or there is no fiware-sla.ini file' \
          '\n       in the /etc/fiware.d directory.' \
          '\n\n       Please correct at least one of them to execute the program.'
    exit(msg)

# Settings file is inside Basics directory, therefore I have to go back to the parent directory
# to have the Code Home directory
CODE_HOME = dirname(dirname(abspath(__file__)))
LOGHOME = join(CODE_HOME, 'log')

# Initialize the logging system
from config.config_logging import LoggingConf

LoggingConf()
