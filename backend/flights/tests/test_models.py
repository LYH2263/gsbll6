from django.test import TestCase
from django.db import IntegrityError
from datetime import datetime, timedelta
from flights.models import Airline, Airport, Flight


class AirlineModelTest(TestCase):
    def setUp(self):
        self.airline = Airline.objects.create(
            name="国泰航空",
            code="CX",
            logo="https://example.com/logo.png"
        )

    def test_create_airline(self):
        self.assertEqual(self.airline.name, "国泰航空")
        self.assertEqual(self.airline.code, "CX")
        self.assertEqual(self.airline.logo, "https://example.com/logo.png")

    def test_airline_str(self):
        self.assertEqual(str(self.airline), "国泰航空")

    def test_airline_logo_can_be_blank(self):
        airline = Airline.objects.create(name="测试航空", code="TS")
        self.assertIsNone(airline.logo)
        self.assertEqual(str(airline), "测试航空")

    def test_airline_code_max_length(self):
        field = Airline._meta.get_field('code')
        self.assertEqual(field.max_length, 10)

    def test_airline_name_max_length(self):
        field = Airline._meta.get_field('name')
        self.assertEqual(field.max_length, 100)


class AirportModelTest(TestCase):
    def setUp(self):
        self.airport = Airport.objects.create(
            name="香港国际机场",
            code="HKG",
            city="香港",
            country="中国"
        )

    def test_create_airport(self):
        self.assertEqual(self.airport.name, "香港国际机场")
        self.assertEqual(self.airport.code, "HKG")
        self.assertEqual(self.airport.city, "香港")
        self.assertEqual(self.airport.country, "中国")

    def test_airport_str(self):
        self.assertEqual(str(self.airport), "香港国际机场 (HKG)")

    def test_airport_city_max_length(self):
        field = Airport._meta.get_field('city')
        self.assertEqual(field.max_length, 100)

    def test_airport_country_max_length(self):
        field = Airport._meta.get_field('country')
        self.assertEqual(field.max_length, 100)


class FlightModelTest(TestCase):
    def setUp(self):
        self.airline = Airline.objects.create(name="国泰航空", code="CX")
        self.dep_airport = Airport.objects.create(
            name="香港国际机场", code="HKG", city="香港", country="中国"
        )
        self.arr_airport = Airport.objects.create(
            name="伦敦希思罗机场", code="LHR", city="伦敦", country="英国"
        )
        self.departure_time = datetime.now() + timedelta(days=1)
        self.arrival_time = self.departure_time + timedelta(hours=12)
        self.flight = Flight.objects.create(
            airline=self.airline,
            flight_number="CX123",
            aircraft="波音777",
            departure_airport=self.dep_airport,
            arrival_airport=self.arr_airport,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            price=8999.00,
            remaining_seats=5,
            is_direct=True,
            is_shared=False
        )

    def test_create_flight(self):
        self.assertEqual(self.flight.airline, self.airline)
        self.assertEqual(self.flight.flight_number, "CX123")
        self.assertEqual(self.flight.aircraft, "波音777")
        self.assertEqual(self.flight.departure_airport, self.dep_airport)
        self.assertEqual(self.flight.arrival_airport, self.arr_airport)
        self.assertEqual(self.flight.price, 8999.00)
        self.assertEqual(self.flight.remaining_seats, 5)
        self.assertTrue(self.flight.is_direct)
        self.assertFalse(self.flight.is_shared)

    def test_flight_str(self):
        self.assertEqual(str(self.flight), "国泰航空 CX123")

    def test_flight_foreign_key_cascade_delete_airline(self):
        flight_id = self.flight.id
        self.airline.delete()
        self.assertFalse(Flight.objects.filter(id=flight_id).exists())

    def test_flight_foreign_key_cascade_delete_departure_airport(self):
        flight_id = self.flight.id
        self.dep_airport.delete()
        self.assertFalse(Flight.objects.filter(id=flight_id).exists())

    def test_flight_foreign_key_cascade_delete_arrival_airport(self):
        flight_id = self.flight.id
        self.arr_airport.delete()
        self.assertFalse(Flight.objects.filter(id=flight_id).exists())

    def test_flight_aircraft_can_be_blank(self):
        flight = Flight.objects.create(
            airline=self.airline,
            flight_number="CX999",
            departure_airport=self.dep_airport,
            arrival_airport=self.arr_airport,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            price=5000.00,
            remaining_seats=10
        )
        self.assertIsNone(flight.aircraft)

    def test_flight_related_name_departure(self):
        self.assertIn(self.flight, self.dep_airport.departure_flights.all())

    def test_flight_related_name_arrival(self):
        self.assertIn(self.flight, self.arr_airport.arrival_flights.all())

    def test_flight_default_is_direct(self):
        flight = Flight.objects.create(
            airline=self.airline,
            flight_number="CX888",
            departure_airport=self.dep_airport,
            arrival_airport=self.arr_airport,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            price=6000.00,
            remaining_seats=8
        )
        self.assertTrue(flight.is_direct)

    def test_flight_default_is_shared(self):
        flight = Flight.objects.create(
            airline=self.airline,
            flight_number="CX777",
            departure_airport=self.dep_airport,
            arrival_airport=self.arr_airport,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            price=7000.00,
            remaining_seats=3
        )
        self.assertFalse(flight.is_shared)

    def test_price_decimal_precision(self):
        field = Flight._meta.get_field('price')
        self.assertEqual(field.max_digits, 10)
        self.assertEqual(field.decimal_places, 2)
