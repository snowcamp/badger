#!/usr/bin/env python
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg
import requests

CONF = cfg.CONF

opts = [
    cfg.StrOpt('api_key',
               default='mykey',
               secret=True,
               help='Secret key'),
    cfg.StrOpt('email',
               default='myemail@foo.com',
               secret=True,
               help='Login'),
    cfg.StrOpt('password',
               default='mysupersecret',
               secret=True,
               help='Password'),
]

CONF.register_opts(opts, 'yurplan')


YURPLAN_ENDPOINT = 'http://yurplan.com/api.php'


class YurplanAPI(object):
    def __init__(self):
        self.token = None
        self.auth()

    def auth(self):
        creds = {'email': CONF.yurplan.email,
                 'password': CONF.yurplan.password}
        r = requests.post(YURPLAN_ENDPOINT + '/auth',
                          params={'key': CONF.yurplan.api_key},
                          json=creds)
        if r.ok:
            self.token = r.json()['data']['token']

    def tickets(self, id='6343'):
        if not self.token:
            raise Exception("not authorized")
        r = requests.get(YURPLAN_ENDPOINT + '/events/%s/tickets' % id,
                         params={'key': CONF.yurplan.api_key,
                                 'token': self.token})
        if r.ok:
            return r.json()['data']['tickets']

    def ticket(self, ticket, id='6343'):
        if not self.token:
            raise Exception("not authorized")
        r = requests.get(
            YURPLAN_ENDPOINT + '/events/%(i)s/tickets/%(t)s/show' % {
                'i': id, 't': ticket},
            params={'key': CONF.yurplan.api_key, 'token': self.token,
                    'filter': 'scanv2'})
        if r.ok:
            return r.json()['data']

    def get_badge_info(self, conf_id='11201', speaker_id='12310',
                       sponsor_id='12322',
                       staff_id='12309',
                       exceptions=None,
                       corrections={}):
        """Obtain list of badges from the different ticket types.

        :param exception_list: Dict w/ key == token and value == expected type
        """

        tickets = self.tickets()
        conf_tickets = []
        for ticket in tickets:
            if ticket['type']['id'] == conf_id:
                ticket['_type'] = 'ATTENDEE'
            if ticket['type']['id'] == speaker_id:
                ticket['_type'] = 'SPEAKER'
            if ticket['type']['id'] == sponsor_id:
                ticket['_type'] = 'SPONSOR'
            if ticket['type']['id'] == staff_id:
                ticket['_type'] = 'STAFF'
            if ticket['token'] in exceptions.keys():
                ticket['_type'] = exceptions.get(ticket['token'],
                                                 ticket.get('_type',
                                                            'ATTENDEE'))
            if ticket.get('_type'):
                if ticket['token'] in corrections:
                    (firstname, lastname) = corrections[ticket['token']]
                    ticket['firstname'] = firstname
                    ticket['lastname'] = lastname
                conf_tickets.append(ticket)

        return [{'firstname': t['firstname'],
                 'lastname': t['lastname'],
                 'token': t['token'],
                 'type': t['_type']}
                for t in conf_tickets]
