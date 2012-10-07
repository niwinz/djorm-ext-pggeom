# -*- coding: utf-8 -*-

from django.test import TestCase

from djorm_expressions.base import SqlExpression, RawExpression, SqlFunction, AND, OR
from djorm_pggeom.expressions import GeoExpression
from djorm_pggeom.objects import Point, Circle, Box

from .models import SomeObject, CircleObjectModel, BoxObjectModel

class GeometricSearches(TestCase):
    def setUp(self):
        SomeObject.objects.all().delete()
        BoxObjectModel.objects.all().delete()
        CircleObjectModel.objects.all().delete()

    def test_simple_contains(self):
        SomeObject.objects.bulk_create([
            SomeObject(pos=Point(1,1)),
            SomeObject(pos=Point(2,2)),
            SomeObject(pos=Point(1,5)),
            SomeObject(pos=Point(3,4)),
        ])

        # simple sql expresion.
        qs = SomeObject.objects.where(
            SqlExpression("pos", "<@", Box(1,1,4,4))
        )
        self.assertEqual(qs.count(), 3)

        # builtin helper
        qs = SomeObject.objects.where(
            GeoExpression("pos").contained_on(Box(1,1,4,4))
        )
        self.assertEqual(qs.count(), 3)

    def test_simple_overlap(self):
        BoxObjectModel.objects.bulk_create([
            BoxObjectModel(barea=Box(1,1,3,2)),
            BoxObjectModel(barea=Box(2,2,4,7)),
            BoxObjectModel(barea=Box(10,10,20,20)),
            BoxObjectModel(barea=Box(-1,-4, -5, -2)),
        ])

        # simple sql expression
        qs = BoxObjectModel.objects.where(
            SqlExpression("barea", "&&", Box(2,0,5,3))
        )
        self.assertEqual(qs.count(), 2)

        # builtin helper
        qs = BoxObjectModel.objects.where(
            GeoExpression("barea").overlaps(Box(2,0,5,3))
        )
        self.assertEqual(qs.count(), 2)

    def test_join_overlap_circle(self):
        c_instance_0 = CircleObjectModel.objects.create(carea=Circle(1,1,5))
        c_instance_1 = CircleObjectModel.objects.create(carea=Circle(-2, -2, 1))

        BoxObjectModel.objects.bulk_create([
            BoxObjectModel(barea=Box(1,1,3,2), other=c_instance_0),
            BoxObjectModel(barea=Box(2,2,4,7), other=c_instance_0),
            BoxObjectModel(barea=Box(10,10,20,20), other=c_instance_1)
        ])

        qs = BoxObjectModel.objects.where(
            SqlExpression("other__carea", "&&", Circle(2,2,2))
        )
        self.assertEqual(qs.count(), 2)

        """
        -- this automaticaly creates this query with join
        SELECT COUNT(*) FROM "pg_geometric_boxobjectmodel" LEFT OUTER JOIN "pg_geometric_circleobjectmodel" ON
            ("pg_geometric_boxobjectmodel"."other_id" = "pg_geometric_circleobjectmodel"."id") WHERE
            ("pg_geometric_circleobjectmodel"."carea" && circle '<(2,2),2>')
        """

    def test_strict_left_and_right_of(self):
        CircleObjectModel.objects.bulk_create([
            CircleObjectModel(carea=Circle(-2,-2,1)),
            CircleObjectModel(carea=Circle(0,5,1)),
            CircleObjectModel(carea=Circle(10,0,1)),
        ])

        qs = CircleObjectModel.objects.where(
            GeoExpression("carea").is_strictly_left_of(Circle(5,0,1))
        )

        self.assertEqual(qs.count(), 2)

        qs = CircleObjectModel.objects.where(
            GeoExpression("carea").is_strictly_right_of(Circle(0,0,1))
        )

        self.assertEqual(qs.count(), 1)

    def test_does_not_extend(self):
        # box '((0,0),(1,1))' &< box '((0,0),(2,2))'
        # box '((0,0),(3,3))' &> box '((0,0),(2,2))'
        # TODO: improve this test

        BoxObjectModel.objects.bulk_create([
            BoxObjectModel(barea=Box(0,0,1,1)),
            BoxObjectModel(barea=Box(0,0,1,1)),
        ])

        qs = BoxObjectModel.objects.where(
            GeoExpression("barea").does_not_extend_right(Box(0,0,2,2))
        )

        self.assertEqual(qs.count(), 2)

        qs = BoxObjectModel.objects.where(
            GeoExpression("barea").does_not_extend_left(Box(0,0,2,2))
        )

        self.assertEqual(qs.count(), 2)


class PointTests(TestCase):
    def setUp(self):
        self.obj0 = SomeObject.objects.create(pos=Point(1,1))
        self.obj1 = SomeObject.objects.create(pos=Point(2,1))
        self.obj2 = SomeObject.objects.create(pos=Point(5,6))
        self.obj3 = SomeObject.objects.create(pos=Point(4,4))

    def tearDown(self):
        SomeObject.objects.all().delete()

    def test_casting(self):
        self.assertIsInstance(self.obj0.pos, Point)
        self.assertEqual(self.obj0.pos, Point(1,1))

    def test_custom_instance(self):
        self.assertEqual(Point(1,1), Point(1,1))

    def test_incorrect_constructor(self):
        with self.assertRaises(TypeError):
            x = Point(1,2,3)

        with self.assertRaises(TypeError):
            x = Point(1)


class CircleTest(TestCase):
    def setUp(self):
        self.obj0 =  CircleObjectModel.objects\
            .create(carea=Circle([0,0],5))

    def tearDown(self):
        CircleObjectModel.objects.all().delete()

    def test_casting(self):
        self.assertIsInstance(self.obj0.carea, Circle)
        self.assertEqual(self.obj0.carea, Circle([0,0],5))

    def test_custom_instance(self):
        self.assertEqual(Circle([1,1], 1), Circle([1,1], 1))

    def test_incorrect_constructor(self):
        with self.assertRaises(TypeError):
            x = Circle([1,2], 3, 3)

        with self.assertRaises(TypeError):
            x = Circle(1, 2, 3, 2)

        with self.assertRaises(AssertionError):
            x = Circle(1, 2)


class BoxTest(TestCase):
    def setUp(self):
        self.obj0 =  BoxObjectModel.objects\
            .create(barea=Box(0,0,5,5))

    def tearDown(self):
        BoxObjectModel.objects.all().delete()

    def test_casting(self):
        self.assertIsInstance(self.obj0.barea, Box)
        self.assertEqual(self.obj0.barea, Box(0,0,5,5))

    def test_custom_instance(self):
        self.assertEqual(Box(1,1,1,1), Box([1,1,1,1]))

    def test_incorrect_constructor(self):
        with self.assertRaises(ValueError):
            x = Box([1,2,3,5,5])

        with self.assertRaises(ValueError):
            x = Box(1,2,3,2,5)

        with self.assertRaises(ValueError):
            x = Box(1,2,5)
