# -*- coding: utf-8 -*-

from djorm_expressions.base import SqlFunction

class Distance(SqlFunction):
    sql_template = '(%(field)s <-> %%s)'

    def between(self, value):
        self.args.extend([value])
        return self

class Box(SqlFunction):
    sql_function = "box"

class Circle(SqlFunction):
    sql_function = "circle"

class Point(SqlFunction):
    sql_function = "point"

class Area(SqlFunction):
    sql_function = "area"

class Center(SqlFunction):
    sql_function = "center"

class Height(SqlFunction):
    sql_function = "height"

class Diameter(SqlFunction):
    sql_function = "diameter"

class Radius(SqlFunction):
    sql_function = "radius"

class Width(SqlFunction):
    sql_function = "width"

class NPoints(SqlFunction):
    sql_function = "npoints"
