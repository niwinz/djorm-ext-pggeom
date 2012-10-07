# -*- coding: utf-8 -*-

from djorm_expressions.base import SqlExpression
from . import functions

class SimpleExpression(SqlExpression):
    sql_template = "%(operator)s %(field)s"

class GeoExpression(object):
    """
    Expression generator for postgresql geometric querys:
    PostgreSQL official documentation:
    http://www.postgresql.org/docs/9.1/interactive/functions-geometry.html
    """

    def __init__(self, field):
        self.field = field

    def overlaps(self, value):
        return SqlExpression(self.field, "&&", value)

    def is_strictly_left_of(self, value):
        return SqlExpression(self.field, "<<", value)

    def is_strictly_right_of(self, value):
        return SqlExpression(self.field, ">>", value)

    def does_not_extend_above(self, value):
        return SqlExpression(self.field, "&<|", value)

    def does_not_extend_below(self, value):
        return SqlExpression(self.field, "|&>", value)

    def does_not_extend_right(self, value):
        return SqlExpression(self.field, "&<", value)

    def does_not_extend_left(self, value):
        return SqlExpression(self.field, "&>", value)

    def intersects_with(self, value):
        return SqlExpression(self.field, "?#", value)

    def not_intersects_with(self, value):
        # TODO: actualy not works
        return ~self.intersects(value)

    def contains(self, value):
        return SqlExpression(self.field, "@>", value)

    def contained_on(self, value):
        return SqlExpression(self.field, "<@", value)

    def is_horizontal(self):
        return SimpleExpression(self.field, "?-")

    def is_horizontal_aligned(self, value):
        return SqlExpression(self.field, "?-", value)

    def is_vertical(self):
        return SimpleExpression(self.field, "?|")

    def is_vertical_aligned(self):
        return SqlExpression(self.field, "?|", value)

    def is_perpendicular_to(self, value):
        return SqlExpression(self.field, "?-|", value)

    def is_parallel_to(self, value):
        return SqlExpression(self.field, "?||", value)

    def same_as(self, value):
        return SqlExpression(self.field, "~=", value)
