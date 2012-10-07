# -*- coding: utf-8 -*-

from django.db import models
from djorm_expressions.models import ExpressionManager as Manager
from djorm_pggeom.fields import GeometricField
from djorm_pggeom.objects import Point, Circle, Box


class SomeObject(models.Model):
    pos = GeometricField(dbtype=Point)
    objects = Manager()


class CircleObjectModel(models.Model):
    carea = GeometricField(dbtype=Circle)
    objects = Manager()


class BoxObjectModel(models.Model):
    barea = GeometricField(dbtype=Box)
    other = models.ForeignKey("CircleObjectModel", related_name="boxes",
        null=True, default=None)

    objects = Manager()
