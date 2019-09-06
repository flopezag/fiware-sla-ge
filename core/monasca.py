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

import requests
import sys
import time
from config.settings import OS_MONASCA_URL
# from config.log import logger
from logging import info, debug, error

__author__ = 'fla'


class Monasca:
    def __init__(self, token):
        self.url = OS_MONASCA_URL + '/v2.0/metrics'

        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-Auth-Token': token}

        self.milli_sec = int(round(time.time() * 1000))

    def send_measurements(self, measurements):
        info('Sending measurements to Monasca...')

        measurements['FINAL'] = measurements.apply(lambda row: self.payload_measure([row['% Issues resolved <2d'],
                                                                                     row['% Issues responded <24h'],
                                                                                     row['FIWARE GE'],
                                                                                     row['Number of tickets']
                                                                                     ]), axis=1)

        # need to return a class list with the data
        d = measurements['FINAL'].values.tolist()

        # finally, we need to flatten the results
        flatten_payload = [item for sublist in d for item in sublist]

        debug('Payload: {}'.format(flatten_payload))

        try:
            r = requests.post(self.url, json=flatten_payload,
                              headers=self.headers)

            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            error("Http Error: {}".format(errh))
            sys.exit(1)
        except requests.exceptions.ConnectionError as errc:
            error("Error Connecting: {}".format(errc))
            sys.exit(1)
        except requests.exceptions.Timeout as errt:
            error("Timeout Error: {}".format(errt))
            sys.exit(1)
        except requests.exceptions.RequestException as err:
            error("OOps: Something Else: {}".format(err))
            sys.exit(1)

        info('Measurements sent to Monasca, status code: {}'.format(r.status_code))

    def payload_measure(self, measure):
        """
        Obtain the Monasca JSON measure message for a specific row in a dataframe.
        """
        result = [
            {
                "name": "ge.ticket_response_time",
                "dimensions": {
                    "ge": measure[2],
                    "source": "fiware-ge-sla"
                },
                "timestamp": self.milli_sec,
                "value": measure[1]
            },
            {
                "name": "ge.ticket_resolve_time",
                "dimensions": {
                    "ge": measure[2],
                    "source": "fiware-ge-sla"
                },
                "timestamp": self.milli_sec,
                "value": measure[0]
            },
            {
                "name": "ge.tickets_count",
                "dimensions": {
                    "ge": measure[2],
                    "source": "fiware-ge-sla"
                },
                "timestamp": self.milli_sec,
                "value": measure[3]
            }
        ]

        return result
