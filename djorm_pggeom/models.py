# -*- coding: utf-8 -*-

def register_geometric_types(connection, **kwargs):
    from . import objects

    for objectname in objects.__all__:
        obj_class = getattr(objects, objectname)
        obj_class.register_cast(connection)
        obj_class.register_adapter()
        print "Registering:", obj_class.__name__


from djorm_core.models import connection_handler
connection_handler.attach_handler(register_geometric_types, vendor="postgresql", unique=True)
