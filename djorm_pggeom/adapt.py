# -*- coding: utf-8 -*-

from psycopg2.extensions import adapt, AsIs


""" PYTHON->SQL ADAPTATION """

def adapt_point(point):
    return AsIs(u"point '(%s, %s)'" % (adapt(point.x), adapt(point.y)))

def adapt_circle(c):
    return AsIs(u"circle '<(%s,%s),%s>'" % \
        (adapt(c.point.x), adapt(c.point.y), adapt(c.r)))

def adapt_lseg(l):
    return AsIs(u"'[(%s,%s), (%s,%s)]'::lseg" % (\
        adapt(l.start_point.x),
        adapt(l.start_point.y),
        adapt(l.end_point.x),
        adapt(l.end_point.y)
    ))

def adapt_box(box):
    return AsIs("'(%s,%s),(%s,%s)'::box" % (
        adapt(box.start_point.x),
        adapt(box.start_point.y),
        adapt(box.end_point.x),
        adapt(box.end_point.y)
    ))

def adapt_path(path):
    container = "'[%s]'::path"
    if path.closed:
        container = "'(%s)'::path"

    points = ["(%s,%s)" % (x, y) \
        for x, y in path]
    return AsIs(container % (",".join(points)))


def adapt_polygon(path):
    container = "'(%s)'::polygon"

    points = ["(%s,%s)" % (x, y) \
        for x, y in path]

    return AsIs(container % (",".join(points)))


ADAPT_MAPPER = {
    'Point': adapt_point,
    'Circle': adapt_circle,
    'Box': adapt_box,
    'Path': adapt_path,
    'Polygon': adapt_polygon,
    'Lseg': adapt_lseg,
}

