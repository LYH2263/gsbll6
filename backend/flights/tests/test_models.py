"""模型约束与关联测试：Airline / Airport / Flight。"""

from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from flights.models import Airline, Airport, Flight
from .factories import make_airline, make_airport, make_flight, BASE_TIME


class AirlineModelTest(TestCase):
    def test_str_returns_name(self):
        a = make_airline("国泰航空", "CX")
        self.assertEqual(str(a), "国泰航空")

    def test_logo_optional(self):
        a = make_airline(logo=None)
        self.assertIsNone(a.logo)


class AirportModelTest(TestCase):
    def test_str_includes_code(self):
        ap = make_airport("香港国际机场", "HKG")
        self.assertEqual(str(ap), "香港国际机场 (HKG)")

    def test_fields_persisted(self):
        ap = make_airport("伦敦希思罗机场", "LHR", "伦敦", "英国")
        reloaded = Airport.objects.get(pk=ap.pk)
        self.assertEqual(reloaded.city, "伦敦")
        self.assertEqual(reloaded.country, "英国")


class FlightModelTest(TestCase):
    def test_str_combines_airline_and_number(self):
        f = make_flight(flight_number="CX123")
        self.assertEqual(str(f), "国泰航空 CX123")

    def test_related_names(self):
        """departure_flights / arrival_flights 反向关联可用。"""
        hkg = make_airport("香港国际机场", "HKG", "香港")
        lhr = make_airport("伦敦希思罗机场", "LHR", "伦敦", "英国")
        f = make_flight(departure_airport=hkg, arrival_airport=lhr)
        self.assertIn(f, hkg.departure_flights.all())
        self.assertIn(f, lhr.arrival_flights.all())
        self.assertEqual(hkg.arrival_flights.count(), 0)

    def test_price_is_decimal(self):
        f = make_flight(price="8999.00")
        reloaded = Flight.objects.get(pk=f.pk)
        self.assertEqual(reloaded.price, Decimal("8999.00"))

    def test_defaults(self):
        """is_direct 默认 True，is_shared 默认 False。"""
        hkg = make_airport("香港", "HKG", "香港")
        lhr = make_airport("伦敦", "LHR", "伦敦", "英国")
        f = Flight.objects.create(
            airline=make_airline(),
            flight_number="CX999",
            departure_airport=hkg,
            arrival_airport=lhr,
            departure_time=BASE_TIME,
            arrival_time=BASE_TIME + timedelta(hours=1),
            price="100.00",
            remaining_seats=1,
        )
        self.assertTrue(f.is_direct)
        self.assertFalse(f.is_shared)

    def test_cascade_delete_from_airline(self):
        f = make_flight()
        airline_id = f.airline_id
        Airline.objects.get(pk=airline_id).delete()
        self.assertFalse(Flight.objects.filter(pk=f.pk).exists())

    def test_cascade_delete_from_airport(self):
        f = make_flight()
        dep_id = f.departure_airport_id
        Airport.objects.get(pk=dep_id).delete()
        self.assertFalse(Flight.objects.filter(pk=f.pk).exists())

    def test_required_foreign_keys(self):
        """airline 为必填外键，缺失时应报错。"""
        hkg = make_airport("香港", "HKG", "香港")
        lhr = make_airport("伦敦", "LHR", "伦敦", "英国")
        with self.assertRaises(IntegrityError):
            Flight.objects.create(
                airline=None,
                flight_number="XX000",
                departure_airport=hkg,
                arrival_airport=lhr,
                departure_time=BASE_TIME,
                arrival_time=BASE_TIME + timedelta(hours=1),
                price="100.00",
                remaining_seats=1,
            )
