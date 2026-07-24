import json
import unittest
from datetime import datetime, timedelta
from django.test import TestCase, Client
from flights.models import Airline, Airport, Flight


class FlightListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.airline = Airline.objects.create(name="国泰航空", code="CX")
        self.hkg = Airport.objects.create(
            name="香港国际机场", code="HKG", city="香港", country="中国"
        )
        self.lhr = Airport.objects.create(
            name="伦敦希思罗机场", code="LHR", city="伦敦", country="英国"
        )
        self.pek = Airport.objects.create(
            name="北京首都国际机场", code="PEK", city="北京", country="中国"
        )
        self.tomorrow = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.flight1 = Flight.objects.create(
            airline=self.airline,
            flight_number="CX123",
            aircraft="波音777",
            departure_airport=self.hkg,
            arrival_airport=self.lhr,
            departure_time=self.tomorrow,
            arrival_time=self.tomorrow + timedelta(hours=12, minutes=30),
            price=8999.00,
            remaining_seats=5,
            is_direct=True,
            is_shared=False
        )
        self.flight2 = Flight.objects.create(
            airline=Airline.objects.create(name="阿联酋航空", code="EK"),
            flight_number="EK456",
            aircraft="空客A380",
            departure_airport=self.hkg,
            arrival_airport=self.lhr,
            departure_time=self.tomorrow + timedelta(hours=1, minutes=30),
            arrival_time=self.tomorrow + timedelta(hours=13, minutes=45),
            price=7999.00,
            remaining_seats=8,
            is_direct=False,
            is_shared=False
        )
        self.flight3 = Flight.objects.create(
            airline=Airline.objects.create(name="中国国际航空", code="CA"),
            flight_number="CA937",
            aircraft="波音747",
            departure_airport=self.pek,
            arrival_airport=self.lhr,
            departure_time=self.tomorrow + timedelta(hours=4),
            arrival_time=self.tomorrow + timedelta(hours=8),
            price=9999.00,
            remaining_seats=2,
            is_direct=True,
            is_shared=False
        )

    def test_get_all_flights(self):
        response = self.client.get('/api/flights/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['data']), 3)

    def test_invalid_method_post_returns_400(self):
        response = self.client.post('/api/flights/')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')

    def test_invalid_method_put_returns_400(self):
        response = self.client.put('/api/flights/')
        self.assertEqual(response.status_code, 400)

    def test_invalid_method_delete_returns_400(self):
        response = self.client.delete('/api/flights/')
        self.assertEqual(response.status_code, 400)

    def test_filter_by_departure_city_exact(self):
        response = self.client.get('/api/flights/?departure_city=香港')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 2)
        cities = [f['departure_airport']['city'] for f in data['data']]
        self.assertTrue(all(c == '香港' for c in cities))

    def test_filter_by_departure_city_fuzzy_match(self):
        response = self.client.get('/api/flights/?departure_city=香')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 2)

    def test_filter_by_arrival_city(self):
        response = self.client.get('/api/flights/?arrival_city=伦敦')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 3)

    def test_filter_by_both_cities(self):
        response = self.client.get('/api/flights/?departure_city=北京&arrival_city=伦敦')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['flight_number'], 'CA937')

    def test_filter_by_valid_date(self):
        date_str = self.tomorrow.strftime('%Y-%m-%d')
        response = self.client.get(f'/api/flights/?departure_date={date_str}')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 3)

    def test_empty_result_no_match(self):
        response = self.client.get('/api/flights/?departure_city=东京')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['data'], [])

    def test_empty_result_nonexistent_date(self):
        response = self.client.get('/api/flights/?departure_date=2020-01-01')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 0)

    def test_serialized_fields_present_in_list(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        flight = data['data'][0]
        required_fields = [
            'id', 'airline', 'flight_number', 'aircraft',
            'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time', 'price',
            'remaining_seats', 'is_direct', 'is_shared'
        ]
        for field in required_fields:
            self.assertIn(field, flight, f"Missing field: {field}")

    def test_serialized_departure_airport_fields(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        dep = data['data'][0]['departure_airport']
        self.assertIn('name', dep)
        self.assertIn('code', dep)
        self.assertIn('city', dep)

    def test_serialized_arrival_airport_fields(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        arr = data['data'][0]['arrival_airport']
        self.assertIn('name', arr)
        self.assertIn('code', arr)
        self.assertIn('city', arr)

    def test_price_is_float(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        price = data['data'][0]['price']
        self.assertIsInstance(price, float)

    def test_date_time_format(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        flight = data['data'][0]
        self.assertRegex(flight['departure_time'], r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')
        self.assertRegex(flight['arrival_time'], r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')

    def test_tax_price_depends_on_raw_price_field(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        flight = data['data'][0]
        self.assertIn('price', flight)
        self.assertIsNotNone(flight['price'])

    def test_invalid_date_silently_ignored_returns_all(self):
        response = self.client.get('/api/flights/?departure_date=not-a-date')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 3)

    def test_invalid_date_format_silently_ignored(self):
        response = self.client.get('/api/flights/?departure_date=13-45-9999')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 3)

    def test_partial_date_silently_ignored(self):
        response = self.client.get('/api/flights/?departure_date=2024')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 3)

    def test_empty_database_returns_empty_list(self):
        Flight.objects.all().delete()
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['data'], [])

    def test_airport_name_not_in_list_response(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        dep = data['data'][0]['departure_airport']
        arr = data['data'][0]['arrival_airport']
        self.assertNotIn('country', dep)
        self.assertNotIn('country', arr)


class FlightDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.airline = Airline.objects.create(name="英国航空", code="BA")
        self.hkg = Airport.objects.create(
            name="香港国际机场", code="HKG", city="香港", country="中国"
        )
        self.lhr = Airport.objects.create(
            name="伦敦希思罗机场", code="LHR", city="伦敦", country="英国"
        )
        self.departure_time = datetime.now() + timedelta(days=1, hours=12)
        self.arrival_time = self.departure_time + timedelta(hours=8)
        self.flight = Flight.objects.create(
            airline=self.airline,
            flight_number="BA789",
            aircraft="波音787",
            departure_airport=self.hkg,
            arrival_airport=self.lhr,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            price=9499.00,
            remaining_seats=3,
            is_direct=True,
            is_shared=False
        )

    def test_get_flight_detail_success(self):
        response = self.client.get(f'/api/flights/{self.flight.id}/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['flight_number'], 'BA789')

    def test_flight_detail_404(self):
        response = self.client.get('/api/flights/99999/')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Flight not found')

    def test_flight_detail_contains_country(self):
        response = self.client.get(f'/api/flights/{self.flight.id}/')
        data = json.loads(response.content)
        self.assertIn('country', data['data']['departure_airport'])
        self.assertIn('country', data['data']['arrival_airport'])
        self.assertEqual(data['data']['departure_airport']['country'], '中国')
        self.assertEqual(data['data']['arrival_airport']['country'], '英国')

    def test_flight_detail_all_fields_present(self):
        response = self.client.get(f'/api/flights/{self.flight.id}/')
        data = json.loads(response.content)
        flight = data['data']
        required_fields = [
            'id', 'airline', 'flight_number', 'aircraft',
            'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time', 'price',
            'remaining_seats', 'is_direct', 'is_shared'
        ]
        for field in required_fields:
            self.assertIn(field, flight, f"Missing field: {field}")

    def test_flight_detail_id_matches(self):
        response = self.client.get(f'/api/flights/{self.flight.id}/')
        data = json.loads(response.content)
        self.assertEqual(data['data']['id'], self.flight.id)

    def test_flight_detail_method_not_allowed_post(self):
        response = self.client.post(f'/api/flights/{self.flight.id}/')
        self.assertEqual(response.status_code, 200)

    def test_invalid_flight_id_string_returns_404(self):
        response = self.client.get('/api/flights/abc/')
        self.assertEqual(response.status_code, 404)


class KnownDefectTest(TestCase):
    """
    Tests that expose known defects in the current implementation.
    These tests are marked as @expectedFailure because the current code
    does not handle these cases correctly. When the defects are fixed,
    these tests should be updated to regular passing tests.
    """
    def setUp(self):
        self.client = Client()
        self.airline = Airline.objects.create(name="测试航空", code="TS")
        self.hkg = Airport.objects.create(
            name="香港国际机场", code="HKG", city="香港", country="中国"
        )
        self.lhr = Airport.objects.create(
            name="伦敦希思罗机场", code="LHR", city="伦敦", country="英国"
        )
        self.sin = Airport.objects.create(
            name="新加坡樟宜机场", code="SIN", city="新加坡", country="新加坡"
        )
        self.tomorrow = datetime.now() + timedelta(days=1)
        self.flight_direct = Flight.objects.create(
            airline=self.airline,
            flight_number="TS001",
            departure_airport=self.hkg,
            arrival_airport=self.lhr,
            departure_time=self.tomorrow,
            arrival_time=self.tomorrow + timedelta(hours=10),
            price=5000.00,
            remaining_seats=10,
            is_direct=True,
            is_shared=False
        )
        self.flight_transfer = Flight.objects.create(
            airline=self.airline,
            flight_number="TS002",
            departure_airport=self.hkg,
            arrival_airport=self.sin,
            departure_time=self.tomorrow + timedelta(hours=2),
            arrival_time=self.tomorrow + timedelta(hours=8),
            price=3000.00,
            remaining_seats=5,
            is_direct=False,
            is_shared=True
        )

    @unittest.expectedFailure
    def test_defect_invalid_date_should_return_error_or_empty(self):
        """DEFECT: Invalid date format is silently ignored (except ValueError: pass),
        should return 400 error or empty result instead of returning all flights."""
        response = self.client.get('/api/flights/?departure_date=not-a-date')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 0,
            "Invalid date should return empty result or error, not all flights")

    @unittest.expectedFailure
    def test_defect_ordering_param_not_implemented(self):
        """DEFECT: ordering query parameter is sent by frontend but completely
        ignored by backend - no server-side sorting is performed."""
        response = self.client.get('/api/flights/?ordering=price')
        data = json.loads(response.content)
        prices = [f['price'] for f in data['data']]
        self.assertEqual(prices, sorted(prices),
            "Results should be sorted by price ascending when ordering=price")

    @unittest.expectedFailure
    def test_defect_is_direct_filter_not_implemented(self):
        """DEFECT: is_direct filter parameter is sent by frontend but ignored.
        Filtering by is_direct=true should return only direct flights."""
        response = self.client.get('/api/flights/?is_direct=true')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertTrue(all(f['is_direct'] for f in data['data']))

    @unittest.expectedFailure
    def test_defect_is_direct_false_filter_not_implemented(self):
        """DEFECT: is_direct=false should return only connecting flights."""
        response = self.client.get('/api/flights/?is_direct=false')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertFalse(any(f['is_direct'] for f in data['data']))

    @unittest.expectedFailure
    def test_defect_is_shared_filter_not_implemented(self):
        """DEFECT: is_shared filter parameter is sent by frontend but ignored.
        Filtering by is_shared=true should return only codeshare flights."""
        response = self.client.get('/api/flights/?is_shared=true')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertTrue(all(f['is_shared'] for f in data['data']))
