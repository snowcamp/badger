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

import sys

from oslo_config import cfg

from badger import badge
from badger import barcode
from badger.yurplan import api

CONF = cfg.CONF
cli_opts = [
    cfg.StrOpt('badge_template', default='snowcamp2016.svg.jinja2',
               help='SVG template for badges'),
]

CONF.register_cli_opts(cli_opts)


def main():
    CONF(sys.argv[1:], project='badger', prog='main')
    template_file = CONF.find_file(CONF.badge_template)
    if not template_file:
        raise Exception('file not found')
    yurplan_api = api.YurplanAPI()
    conf_people = yurplan_api.get_badge_info()
    template = badge.SnowCampTemplate(template=template_file)
    for person in conf_people:
        filename = 'temp/qr_temp.png'
        barcode.BarCode(person['token']).save(filename)
        badge.SnowCampBadge(person['firstname'], person['lastname'],
                            filename, template).save()

if __name__ == 'main':
    sys.exit(main())