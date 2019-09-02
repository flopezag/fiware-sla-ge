#!/usr/bin/env /Users/fernandolopez/Documents/workspace/python/fiware-sla-ge/env/bin/python
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

from core.jiraconnector import Jira
from core.keystone import Keystone
from core.monasca import Monasca
from logging import info, error

__author__ = 'fla'

if __name__ == "__main__":
    jira_instance = Jira()

    issues = jira_instance.get_issues()

    result = map(jira_instance.filter_issue, issues)

    solution_data = jira_instance.calculate_statistics(result)
    '''
    keystone = Keystone()

    token = keystone.get_token()

    monasca = Monasca(token)

    monasca.send_measurements(solution_data)
    '''
    info(solution_data)
