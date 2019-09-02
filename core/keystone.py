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

from requests import post
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from sys import exit
from config.settings import OS_USERNAME, OS_PASSWORD, OS_AUTH_URL
# from config.log import logger
from logging import info, debug, error

__author__ = 'fla'


class Keystone:
    def __init__(self):
        self.url = OS_AUTH_URL + '/v3/auth/tokens'

        self.payload = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": OS_USERNAME,
                            "password": OS_PASSWORD,
                            "domain": {
                                "name": "default"
                            }
                        }
                    }
                }
            }
        }

        self.headers = {'Content-Type': 'application/json'}

    def get_token(self):
        info('Requesting token to Keytone...')

        r = ''

        try:
            r = post(self.url, json=self.payload, headers=self.headers)

            r.raise_for_status()
        except HTTPError as errh:
            error("Http Error: {}".format(errh))
            exit(1)
        except ConnectionError as errc:
            error("Error Connecting: {}".format(errc))
            exit(1)
        except Timeout as errt:
            error("Timeout Error: {}".format(errt))
            exit(1)
        except RequestException as err:
            error("OOps: Something Else: {}".format(err))
            exit(1)

        new_token = r.headers['X-Subject-Token']

        info('Token obtained, status code: {}'.format(r.status_code))
        debug('Token: {}'.format(new_token))

        return new_token


if __name__ == "__main__":
    keystone = Keystone()

    token = keystone.get_token()

    print(token)
