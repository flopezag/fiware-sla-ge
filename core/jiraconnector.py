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

from jira import JIRA
from dateutil import parser
import pytz
from datetime import datetime
from pandas import DataFrame
import re
from config.settings import JIRA_USER, JIRA_PASSWORD, JIRA_QUERY, JIRA_URL
from logging import info, debug


__author__ = 'fla'


class Jira:
    def __init__(self):
        # By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK
        # (see https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK for details).
        # Override this with the options parameter.
        options = {
            'server': JIRA_URL
        }

        self.jira = JIRA(options, basic_auth=(JIRA_USER, JIRA_PASSWORD))

        # Fetch all fields
        allfields = self.jira.fields()

        # Make a map from field name -> field id
        self.nameMap = {field['name']: field['id'] for field in allfields}

        self.total_issues = list()

    def filter_issue(self, a_issue):
        created = a_issue.fields.created
        resolved = a_issue.fields.resolutiondate
        enabler = getattr(a_issue.fields, self.nameMap['HD-Enabler']).value

        changelog = a_issue.changelog

        progressed = [item.created for item in [history for history in changelog.histories]
                      if (item.items[0].field == 'status'
                          and (
                          (item.items[0].fromString == 'Open' and item.items[0].toString == 'In Progress')
                          or
                          (item.items[0].fromString == 'Open' and item.items[0].toString == 'Answered')
                          or
                          (item.items[0].fromString == 'To Do' and item.items[0].toString == 'In Progress')
                          or
                          (item.items[0].fromString == 'Open' and item.items[0].toString == 'Analysing')
                          or
                          (item.items[0].fromString == 'Open' and item.items[0].toString == 'Closed')
                          ))]

        if len(progressed) == 0:
            # This is the issues that was dismissed, therefore the time should be calculate in a different way
            progressed = [item.created for item in [history for history in changelog.histories]
                          if (len(item.items) == 2
                              and
                              item.items[1].field == 'status'
                              and (
                              (item.items[1].fromString == 'Open' and item.items[1].toString == 'Closed')
                              or
                              (item.items[1].fromString == 'To Do' and item.items[1].toString == 'Done')
                              or
                              (item.items[1].fromString == 'Open' and item.items[1].toString == 'Dismissed')
                              ))]

        t_created = parser.parse(created)

        t_now = pytz.utc.localize(datetime.utcnow())

        try:
            t_progressed = parser.parse(progressed[0])
            # Translate the different to number of days 60*60*24 = 86400
            time_response = (t_progressed - t_created).total_seconds()/86400
        except Exception:
            # Translate the different to number of days 60*60*24 = 86400
            time_response = (t_now - t_created).total_seconds()/86400

        try:
            if resolved is None:
                t_resolved = t_now
            else:
                t_resolved = parser.parse(resolved)

            # Translate the different to number of days 60*60*24 = 86400
            time_resolve = (t_resolved - t_created).total_seconds()/86400
        except Exception:
            # Translate the different to number of days 60*60*24 = 86400
            time_resolve = (t_now - t_created).total_seconds()/86400

        debug("{0} {1:.3f} {2:.3f} {3}"
              .format(a_issue.key, time_response, time_resolve, time_resolve >= time_response))

        return {'enabler': enabler, 'time_response': time_response, 'time_resolve': time_resolve}

    def calculate_statistics(self, a_list):
        solution = list()

        df = DataFrame(a_list)

        requested_enabler = Jira.get_enablers(JIRA_QUERY)

        enablers = df['enabler'].unique()

        enabler_without_tickets = Jira.intersection(requested_enabler, enablers)

        debug('Dimension of the Dataframe: ({}, {})'.format(
            df.shape[0], df.shape[1]))

        for i in range(0, len(enablers)):
            df_aux = df[df['enabler'] == enablers[i]]

            number_of_items = df_aux['time_resolve'].count()

            # I want to obtain the mean of the resolution time and response time
            p_time_resolve = df_aux["time_resolve"].mean()
            p_time_response = df_aux['time_response'].mean()

            info('Enabler: {}, '
                        'time_response_mean (days): {}, '
                        'time_resolve_mean (days): {}, '
                        'number of tickets: {}'
                        .format(enablers[i], p_time_response, p_time_resolve, number_of_items))

            solution_list = {
               'FIWARE GE': enablers[i],
               'Number of tickets': number_of_items,
               '% Issues responded <24h': p_time_response,
               '% Issues resolved <2d': p_time_resolve
            }

            solution.append(solution_list)

        for i in range(0, len(enabler_without_tickets)):
            info('Enabler: {}, '
                        'time_response_mean (days): 0, '
                        'time_resolve_mean (days): 0, '
                        'number of tickets: 0'
                        .format(enabler_without_tickets[i]))

            solution_list = {
               'FIWARE GE': enabler_without_tickets[i],
               'Number of tickets': 0,
               '% Issues responded <24h': 0,
               '% Issues resolved <2d': 0
            }

            solution.append(solution_list)

        solution_df = DataFrame(solution)

        return solution_df

    def get_issues(self):
        block_size = 100
        block_num = 0

        while True:
            start_idx = block_num * block_size

            list_issues = \
                self.jira.search_issues(jql_str=JIRA_QUERY,
                                        startAt=start_idx,
                                        maxResults=block_size,
                                        expand='changelog')

            if len(list_issues) == 0:
                # Retrieve issues until there are no more to come
                break

            self.total_issues = self.total_issues + list_issues

            block_num += 1

            info(
                "Processing block of JIRA issues number: {}".format(block_num))

        info("Total number of JIRA issues: {}".format(
            len(self.total_issues)))

        return self.total_issues

    @staticmethod
    def get_enablers(query):
        pattern = r".*\([ ]?(.*)\).*"

        # matches = re.finditer(regex, query, re.MULTILINE)
        match = re.match(pattern, query)

        new_string = match.group(1).replace("'", "").replace(", ", ",")
        my_list = new_string.split(",")
        return my_list

    @staticmethod
    def intersection(lst1, lst2):
        lst3 = [value for value in lst1 if value not in lst2]
        return lst3
