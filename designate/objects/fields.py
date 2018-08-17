# Copyright 2015 Red Hat, Inc.
# Copyright 2017 Fujitsu Vietnam Ltd.
# All Rights Reserved.
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

from dns import ipv4
import dns.exception
import re
import uuid

from oslo_versionedobjects import fields as ovoo_fields
from oslo_versionedobjects.fields import DateTimeField  # noqa


class IntegerField(ovoo_fields.IntegerField):
    pass


class BooleanField(ovoo_fields.BooleanField):
    pass


class PolymorphicObject(ovoo_fields.Object):
    def coerce(self, obj, attr, value):
        if hasattr(value, '__bases__'):
            check_value = value.__bases__[0]
            super(PolymorphicObject, self).coerce(obj, attr, check_value)
        return value


class PolymorphicObjectField(ovoo_fields.AutoTypedField):
    def __init__(self, objtype, subclasses=False, **kwargs):
        self.AUTO_TYPE = PolymorphicObject(objtype, subclasses)
        self.objname = objtype
        super(PolymorphicObjectField, self).__init__(**kwargs)


class PolymorphicListOfObjectsField(ovoo_fields.AutoTypedField):
    def __init__(self, objtype, subclasses=False, **kwargs):
        self.AUTO_TYPE = ovoo_fields.List(
            PolymorphicObject(objtype, subclasses))
        self.objname = objtype
        super(PolymorphicListOfObjectsField, self).__init__(**kwargs)


class ListOfObjectsField(ovoo_fields.ListOfObjectsField):
    pass


class ObjectFields(ovoo_fields.ObjectField):
    def __init__(self, objtype, subclasses=False, relation=False, **kwargs):
        self.AUTO_TYPE = ovoo_fields.List(
            ovoo_fields.Object(objtype, subclasses))
        self.objname = objtype
        super(ObjectFields, self).__init__(objtype, **kwargs)
        self.relation = relation


class IntegerFields(IntegerField):
    def __init__(self, nullable=False, default=ovoo_fields.UnspecifiedDefault,
                 read_only=False, minimum=0, maximum=None):
        super(IntegerFields, self).__init__(nullable=nullable,
                                            default=default,
                                            read_only=read_only)
        self.min = minimum
        self.max = maximum

    def coerce(self, obj, attr, value):
        value = super(IntegerFields, self).coerce(obj, attr, value)
        if value is None:
            return value
        if value < self.min:
            # return self.min
            raise ValueError('Value must be >= {} for field {}'.format(
                self.min, attr)
            )
        if self.max and value > self.max:
            raise ValueError('Value too high for %s' % attr)
        return value


class StringFields(ovoo_fields.StringField):
    RE_HOSTNAME = r'^(?!.{255,})(?:(?:^\*|(?!\-)[A-Za-z0-9_\-]{1,63})(?<!\-)\.)+\Z'  # noqa
    RE_ZONENAME = r'^(?!.{255,})(?:(?!\-)[A-Za-z0-9_\-]{1,63}(?<!\-)\.)+\Z'
    RE_SRV_HOST_NAME = r'^(?:(?!\-)(?:\_[A-Za-z0-9_\-]{1,63}\.){2})(?!.{255,})'\
                       r'(?:(?!\-)[A-Za-z0-9_\-]{1,63}(?<!\-)\.)+\Z'
    RE_SSHFP_FINGERPRINT = r'^([0-9A-Fa-f]{10,40}|[0-9A-Fa-f]{64})\Z'
    RE_TLDNAME = r'^(?!.{255,})(?:(?!\-)[A-Za-z0-9_\-]{1,63}(?<!\-))' \
                 r'(?:\.(?:(?!\-)[A-Za-z0-9_\-]{1,63}(?<!\-)))*\Z'
    RE_NAPTR_FLAGS = r'^[A-Za-z0-9]*'
    RE_NAPTR_SERVICE = r'^([A-Za-z]([A-Za-z0-9]*)(\+[A-Za-z]([A-Za-z0-9]{0,31}))*)?'  # noqa
#   RE_NAPTR_REGEXP = r'^(([^0-9i\\])(.*)\1((.*)|(\\[1-9]))\1(i?))?'
    RE_NAPTR_REGEXP = r'^.*'

    def __init__(self, nullable=False, read_only=False,
                 default=ovoo_fields.UnspecifiedDefault, description='',
                 maxLength=None):

        super(StringFields, self).__init__(nullable=nullable, default=default,
                                           read_only=read_only)
        self.description = description
        self.maxLength = maxLength

    def coerce(self, obj, attr, value):
        if value is None:
            return self._null(obj, attr)
        else:
            value = super(StringFields, self).coerce(obj, attr, value)
            if self.maxLength and len(value) > self.maxLength:
                raise ValueError('Value too long for %s' % attr)
            return value


class UUID(ovoo_fields.UUID):
    def coerce(self, obj, attr, value):
        try:
            value = int(value)
            uuid.UUID(int=value)
        except ValueError:
            uuid.UUID(hex=value)
        return str(value)


class UUIDFields(ovoo_fields.AutoTypedField):
    AUTO_TYPE = UUID()


class DateTimeField(DateTimeField):
    def __init__(self, tzinfo_aware=False, **kwargs):
        super(DateTimeField, self).__init__(tzinfo_aware, **kwargs)


class ObjectField(ovoo_fields.ObjectField):
    pass


class IPV4AddressField(ovoo_fields.IPV4AddressField):

    def coerce(self, obj, attr, value):
        try:
            # make sure that DNS Python agrees that it is a valid IP address
            ipv4.inet_aton(str(value))
        except dns.exception.SyntaxError:
            raise ValueError()
        value = super(IPV4AddressField, self).coerce(obj, attr, value)
        # we use this field as a string, not need a netaddr.IPAdress
        # as oslo.versionedobjects is using
        return str(value)


class IPV6AddressField(ovoo_fields.IPV6AddressField):

    def coerce(self, obj, attr, value):
        value = super(IPV6AddressField, self).coerce(obj, attr, value)
        # we use this field as a string, not need a netaddr.IPAdress
        # as oslo.versionedobjects is using
        return str(value)


class IPV4AndV6AddressField(ovoo_fields.IPV4AndV6AddressField):

    def coerce(self, obj, attr, value):
        value = super(IPV4AndV6AddressField, self).coerce(obj, attr, value)
        # we use this field as a string, not need a netaddr.IPAdress
        # as oslo.versionedobjects is using
        return str(value)


class Enum(ovoo_fields.Enum):
    def get_schema(self):
        return {
            'enum': self._valid_values,
            'type': 'any'
        }


class EnumField(ovoo_fields.BaseEnumField):
    def __init__(self, valid_values, **kwargs):
        self.AUTO_TYPE = Enum(valid_values=valid_values)
        super(EnumField, self).__init__(**kwargs)


class DomainField(StringFields):
    def __init__(self, **kwargs):
        super(DomainField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(DomainField, self).coerce(obj, attr, value)
        if value is None:
            return
        domain = value.split('.')
        for host in domain:
            if len(host) > 63:
                raise ValueError("Host %s is too long" % host)
        if not value.endswith('.'):
            raise ValueError("Domain %s is not end with a dot" % value)
        if not re.match(self.RE_ZONENAME, value):
            raise ValueError("Domain %s is not match" % value)
        return value


class EmailField(StringFields):
    def __init__(self, **kwargs):
        super(EmailField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(EmailField, self).coerce(obj, attr, value)
        if value.count('@') != 1:
            raise ValueError("%s is not an email" % value)
        email = value.replace('@', '.')
        if not re.match(self.RE_ZONENAME, "%s." % email):
            raise ValueError("Email %s is not match" % value)
        return value


class HostField(StringFields):
    def __init__(self, **kwargs):
        super(HostField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(HostField, self).coerce(obj, attr, value)
        if value is None:
            return
        hostname = value.split('.')
        for host in hostname:
            if len(host) > 63:
                raise ValueError("Host %s is too long" % host)
        if value.endswith('.') is False:
            raise ValueError("Host name %s is not end with a dot" % value)
        if not re.match(self.RE_HOSTNAME, value):
            raise ValueError("Host name %s is not match" % value)
        return value


class SRVField(StringFields):
    def __init__(self, **kwargs):
        super(SRVField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(SRVField, self).coerce(obj, attr, value)
        if value is None:
            return
        srvtype = value.split('.')
        for host in srvtype:
            if len(host) > 63:
                raise ValueError("Host %s is too long" % host)
        if value.endswith('.') is False:
            raise ValueError("Host name %s is not end with a dot" % value)
        if not re.match(self.RE_SRV_HOST_NAME, value):
            raise ValueError("Host name %s is not a SRV record" % value)
        return value


class TxtField(StringFields):
    def __init__(self, **kwargs):
        super(TxtField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(TxtField, self).coerce(obj, attr, value)
        if value.endswith('\\'):
            raise ValueError("Do NOT put '\\' into end of TXT record")
        return value


class Sshfp(StringFields):
    def __init__(self, **kwargs):
        super(Sshfp, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(Sshfp, self).coerce(obj, attr, value)
        if not re.match(self.RE_SSHFP_FINGERPRINT, "%s" % value):
            raise ValueError("Host name %s is not a SSHFP record" % value)
        return value


class TldField(StringFields):
    def __init__(self, **kwargs):
        super(TldField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(TldField, self).coerce(obj, attr, value)
        if not re.match(self.RE_TLDNAME, value):
            raise ValueError("%s is not an TLD" % value)
        return value


class NaptrFlagsField(StringFields):
    def __init__(self, **kwargs):
        super(NaptrFlagsField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(NaptrFlagsField, self).coerce(obj, attr, value)
        if not re.match(self.RE_NAPTR_FLAGS, "%s" % value):
            raise ValueError("%s is not a NAPTR record flag" % value)
        return value


class NaptrServiceField(StringFields):
    def __init__(self, **kwargs):
        super(NaptrServiceField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(NaptrServiceField, self).coerce(obj, attr, value)
        if not re.match(self.RE_NAPTR_SERVICE, "%s" % value):
            raise ValueError("%s is not a NAPTR record service" % value)
        return value


class NaptrRegexpField(StringFields):
    def __init__(self, **kwargs):
        super(NaptrRegexpField, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        value = super(NaptrRegexpField, self).coerce(obj, attr, value)
        if not re.match(self.RE_NAPTR_REGEXP, "%s" % value):
            raise ValueError("%s is not a NAPTR record regexp" % value)
        return value


class Any(ovoo_fields.FieldType):
    @staticmethod
    def coerce(obj, attr, value):
        return value


class AnyField(ovoo_fields.AutoTypedField):
    AUTO_TYPE = Any()


class BaseObject(ovoo_fields.FieldType):
    @staticmethod
    def coerce(obj, attr, value):
        if isinstance(value, object):
            return value
        else:
            raise ValueError("BaseObject valid values are not valid")


class BaseObjectField(ovoo_fields.AutoTypedField):
    AUTO_TYPE = BaseObject()


class IPOrHost(IPV4AndV6AddressField):
    def __init__(self, nullable=False, read_only=False,
                 default=ovoo_fields.UnspecifiedDefault):
        super(IPOrHost, self).__init__(nullable=nullable,
                                       default=default, read_only=read_only)

    def coerce(self, obj, attr, value):
        try:
            value = super(IPOrHost, self).coerce(obj, attr, value)
        except ValueError:
            if not re.match(StringFields.RE_ZONENAME, value):
                raise ValueError("%s is not IP address or host name" % value)
        return value
