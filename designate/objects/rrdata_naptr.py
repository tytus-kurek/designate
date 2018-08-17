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

from designate.objects.record import Record
from designate.objects.record import RecordList
from designate.objects import base
from designate.objects import fields


@base.DesignateRegistry.register
class NAPTR(Record):
    """
    NAPTR Resource Record Type
    Defined in: RFC2915
    """
    fields = {
        'order': fields.IntegerFields(minimum=0, maximum=65535),
        'preference': fields.IntegerFields(minimum=0, maximum=65535),
        'flags': fields.NaptrFlagsField(),
        'service': fields.NaptrServiceField(),
        'regexp': fields.NaptrRegexpField(),
        'replacement': fields.DomainField(maxLength=255)
    }

    def _to_string(self):
        return ("%(order)s %(preference)s %(flags)s %(service)s %(regexp)s "
                "%(replacement)s" % self)

    def _from_string(self, v):
        order, preference, flags, service, regexp, replacement = v.split(' ')
        self.order = int(order)
        self.preference = int(preference)
        self.flags = flags
        self.service = service
        self.regexp = regexp
        self.replacement = replacement

    # The record type is defined in the RFC. This will be used when the record
    # is sent by mini-dns.
    RECORD_TYPE = 35


@base.DesignateRegistry.register
class NAPTRList(RecordList):

    LIST_ITEM_TYPE = NAPTR

    fields = {
        'objects': fields.ListOfObjectsField('NAPTR'),
    }
