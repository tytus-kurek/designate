# Copyright 2018 Canonical Ltd.
#
# Author: Tytus Kurek <tytus.kurek@canonical.com>
#
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

from oslo_log import log as logging
import oslotest.base

from designate import objects

LOG = logging.getLogger(__name__)


def debug(*a, **kw):
    for v in a:
        LOG.debug(repr(v))

    for k in sorted(kw):
        LOG.debug("%s: %s", k, repr(kw[k]))


class NAPTRRecordTest(oslotest.base.BaseTestCase):

    def test_parse_naptr(self):
        naptr_record = objects.NAPTR()
        naptr_record._from_string(
                '0 0 S SIP+D2U !^.*$!sip:customer-service@example.com! _sip._udp.example.com.')  # noqa

        self.assertEqual(0, naptr_record.order)
        self.assertEqual(0, naptr_record.preference)
        self.assertEqual('S', naptr_record.flags)
        self.assertEqual('SIP+D2U', naptr_record.service)
        self.assertEqual('!^.*$!sip:customer-service@example.com!',
                         naptr_record.regexp)
        self.assertEqual('_sip._udp.example.com.', naptr_record.replacement)
