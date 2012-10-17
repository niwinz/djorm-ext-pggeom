# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import force_unicode

class GeometricField(models.Field):
    __metaclass__ = models.SubfieldBase

    def __init__(self, dbtype, *args, **kwargs):
        self._dbtype = dbtype

        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        kwargs.setdefault('default', None)

        super(GeometricField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return self._dbtype.db_type(connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = value if prepared else self.get_prep_value(value)
        return value

    def to_python(self, value):
        return value

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['^djorm_pggeom.fields\.GeometricField$'])
except ImportError:
    pass
