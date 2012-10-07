# -*- coding: utf-8 -*-

import re
from django.utils import simplejson as json
from django.db import connection
from psycopg2.extensions import adapt, register_adapter, AsIs, new_type, register_type

from .adapt import ADAPT_MAPPER

rx_circle_float = re.compile(r'<\(([\d\.\-]*),([\d\.\-]*)\),([\d\.\-]*)>')
rx_line = re.compile(r'\[\(([\d\.\-]*),\s*([\w\.\-]*)\),\s*\(([\d\.\-]*),\s*([\d\.\+]*)\)\]')
rx_point = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\)')
rx_box = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\),\s*\(([\d\.\-]*),\s*([\d\.\-]*)\)')
rx_path_identify = re.compile(r'^((?:\(|\[))(.*)(?:\)|\])$')

""" SQL->PYTHON CAST """

def cast_point(value, cur):
    if value is None:
        return None

    res = rx_point.search(value)
    if not res:
        raise ValueError("bad point representation: %r" % value)

    return Point.from_tuple([int(x) if "." not in x else float(x) \
        for x in res.groups()])


def cast_circle(value, cur):
    if value is None:
        return None

    rxres = rx_circle_float.search(value)
    if not rxres:
        raise ValueError("bad circle representation: %r" % value)

    return Circle.from_tuple([int(x) if "." not in x else float(x) \
        for x in rxres.groups()])

def cast_lseg(value, cur):
    if value is None:
        return None

    rxres = rx_line.search(value)
    if not rxres:
        raise ValueError("bad lseg representation: %r" % value)

    return Lseg.from_tuple([int(x) if "." not in x else float(x) \
        for x in rxres.groups()])

def cast_box(value, cur):
    if value is None:
        return None

    rxres = rx_box.search(value)
    if not rxres:
        raise ValueError("bad box representation: %r" % value)

    return Box.from_tuple([int(x) if "." not in x else float(x) \
        for x in rxres.groups()])

def cast_path(value, cur):
    if value is None:
        return None

    ident = rx_path_identify.search(value)
    if not ident:
        raise ValueError("bad path representation: %r" % value)

    is_closed = True if "(" == ident.group(1) else False
    points = ident.group(2)
    if not points.strip():
        raise ValueError("bad path representation: %r" % value)

    return Path(*[(
        int(x) if "." not in x else float(x), \
        int(y) if "." not in y else float(y) \
    ) for x, y in rx_point.findall(points)], closed=is_closed)

def cast_polygon(value, cur):
    if value is None:
        return None

    ident = rx_path_identify.search(value)
    if not ident:
        raise ValueError("bad path representation: %r" % value)

    is_closed = True if "(" == ident.group(1) else False
    points = ident.group(2)
    if not points.strip():
        raise ValueError("bad path representation: %r" % value)

    return Polygon(*[(
        int(x) if "." not in x else float(x), \
        int(y) if "." not in y else float(y) \
    ) for x, y in rx_point.findall(points)], closed=is_closed)


CAST_MAPPER = {
    'Point': cast_point,
    'Circle': cast_circle,
    'Box': cast_box,
    'Path': cast_path,
    'Polygon': cast_polygon,
    'Lseg': cast_lseg,
}


class GeometricMeta(type):
    """
    Base meta class for all geometryc types.
    """

    def __init__(cls, name, bases, attrs):
        super(GeometricMeta, cls).__init__(name, bases, attrs)
        cls._registed = False

    #def __call__(cls, *args):
    #    if len(args) > 1:
    #        return super(GeometricMeta, cls).__call__(tuple(args))
    #    elif isinstance(args[0], (list, tuple)):
    #        return super(GeometricMeta, cls).__call__(*args)
    #    raise ValueError("Incorrect parameters")

    def register_cast(cls, connection):
        cast_function = CAST_MAPPER[cls.type_name()]
        cursor = connection.cursor()
        cursor.execute(cls.sql_for_oid())
        oid = cursor.description[0][1]
        cursor.close()

        PGTYPE = new_type((oid,), cls.type_name().upper(), cast_function)
        register_type(PGTYPE)

    def register_adapter(cls):
        adapt_function = ADAPT_MAPPER[cls.type_name()]
        register_adapter(cls, adapt_function)

    def type_name(cls):
        return cls.__name__

    def db_type(cls, connection):
        return cls.type_name().lower()

    def sql_for_oid(cls):
        ntype = cls.type_name().lower()
        return "SELECT NULL::%s" % (ntype)


class Point(object):
    """
    Class that rep resents of geometric point.
    """
    __metaclass__ = GeometricMeta

    def __init__(self, x, y):
        super(Point, self).__init__()
        assert isinstance(x, (int, long, float)), "x must be int or float"
        assert isinstance(y, (int, long, float)), "y must be int or float"

        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return "<Point({0},{1})>".format(self.x, self.y)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_tuple(cls, data):
        if len(data) != 2:
            raise ValueError("Incorrect lenght of data parameter")
        return cls(data[0], data[1])


class Circle(object):
    __metaclass__ = GeometricMeta

    def __init__(self, point, radius):
        super(Circle, self).__init__()
        assert isinstance(point, (list, tuple, Point)), "point must be a list or Point instance"
        assert isinstance(radius, (int, long, float)), "radius must be int or float"

        if isinstance(point, (list, tuple)):
            if len(point) != 2:
                raise ValueError("Incorrect lenght of point parameter")

            self.point = Point(*point)
        else:
            self.point = point

        self.r = radius

    def __repr__(self):
        return "<Circle({0},{1})>".format(self.point, self.r)

    def __iter__(self):
        yield self.point
        yield self.r

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_tuple(cls, data):
        """
        Create circle instance from tuple of three elements.
        """

        if len(data) == 2:
            return cls(data[0], data[1])
        elif len(data) == 3:
            return cls(data[:2], data[2])
        raise ValueError("Incorrect length of data parameter")


class Lseg(object):
    __metaclass__ = GeometricMeta

    def __init__(self, start_point, end_point):
        super(Lseg, self).__init__()
        if isinstance(start_point, (list, tuple)):
            self.start_point = Point.from_tuple(start_point)
        elif isinstance(start_point, Point):
            self.start_point = start_point
        else:
            raise ValueError("start_point must be list, tuple or Point instance")

        if isinstance(end_point, (list, tuple)):
            self.end_point = Point.from_tuple(end_point)
        elif isinstance(end_point, Point):
            self.end_point = end_point
        else:
            raise ValueError("end_point must be list, tuple or Point instance")

    def __repr__(self):
        return "<Lseg({0},{1})>".format(self.start_point, self.end_point)

    def __iter__(self):
        yield self.start_point
        yield self.end_point

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_tuple(cls, data):
        if len(data) == 4:
            return cls(data[2:], data[:2])
        elif len(data) == 2:
            return cls(data[0], data[1])
        raise ValueError("Incorrect length of data parameter")



class Box(object):
    __metaclass__ = GeometricMeta

    def __init__(self, start_point, end_point):
        super(Box, self).__init__()
        if isinstance(start_point, (list, tuple)):
            self.start_point = Point.from_tuple(start_point)
        elif isinstance(start_point, Point):
            self.start_point = start_point
        else:
            raise ValueError("start_point must be list, tuple or Point instance")

        if isinstance(end_point, (list, tuple)):
            self.end_point = Point.from_tuple(end_point)
        elif isinstance(end_point, Point):
            self.end_point = end_point
        else:
            raise ValueError("end_point must be list, tuple or Point instance")

    def __repr__(self):
        return "<Box({0},{1})>".format(self.start_point, self.end_point)

    def __iter__(self):
        yield self.start_point
        yield self.end_point

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_tuple(cls, data):
        if len(data) == 4:
            return cls(data[2:], data[:2])
        elif len(data) == 2:
            return cls(data[0], data[1])
        raise ValueError("Incorrect length of data parameter")


class Path(object):
    __metaclass__ = GeometricMeta

    closed = False

    def __init__(self, *args, **kwargs):
        super(Path, self).__init__()
        self.points = []
        self.closed = kwargs.pop('closed', True)

        if len(args) < 1:
            raise ValueError("Incorrect parameters")

        for item in args:
            if isinstance(item, (tuple, list)):
                self.points.append(Point.from_tuple(item))
            elif isinstance(item, Point):
                self.points.append(item)
            else:
                raise ValueError("invalid content")

    def __repr__(self):
        return "<Path {0}...{1} closed={2} length={3}>".format(
            self.points[0], self.points[-1], self.closed, len(self.points))

    def __iter__(self):
        for item in self.points:
            yield item

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_tuple(self, data):
        return cls(*data)


class Polygon(Path):
    __metaclass__ = GeometricMeta

    def __repr__(self):
        return "<Polygon {0}...{1} closed={2} length={3}>".format(
            self.points[0], self.points[-1], self.closed, len(self.points))


__all__ = ['Polygon', 'Point', 'Box', 'Circle', 'Path', 'Lseg']
