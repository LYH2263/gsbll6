import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from flights.models import Airline, Airport, Flight


class SeedDataFixture:
    """
    Fixture that creates data consistent with init_data.py seed script.
    This allows integration tests to verify end-to-end behavior matching
    the documented seed data.
    """

    @staticmethod
    def create_seed_data():
        airlines = {
            'CX': Airline.objects.create(name="国泰航空", code="CX"),
            'EK': Airline.objects.create(name="阿联酋航空", code="EK"),
            'BA': Airline.objects.create(name="英国航空", code="BA"),
            'CA': Airline.objects.create(name="中国国际航空", code="CA"),
            'SQ': Airline.objects.create(name="新加坡航空", code="SQ"),
        }

        airports = {
            'HKG': Airport.objects.create(name="香港国际机场", code="HKG", city="香港", country="中国"),
            'LHR': Airport.objects.create(name="伦敦希思罗机场", code="LHR", city="伦敦", country="英国"),
            'PEK': Airport.objects.create(name="北京首都国际机场", code="PEK", city="北京", country="中国"),
            'PVG': Airport.objects.create(name="上海浦东国际机场", code="PVG", city="上海", country="中国"),
            'SIN': Airport.objects.create(name="新加坡樟宜机场", code="SIN", city="新加坡", country="新加坡"),
            'DXB': Airport.objects.create(name="迪拜国际机场", code="DXB", city="迪拜", country="阿联酋"),
        }

        base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        flights_data = [
            {'airline': 'CX', 'flight_number': 'CX123', 'aircraft': '波音777',
             'dep': 'HKG', 'arr': 'LHR', 'dep_hour': 9, 'arr_hour': 21, 'arr_min': 30,
             'price': 8999.00, 'seats': 5, 'direct': True, 'shared': False},
            {'airline': 'EK', 'flight_number': 'EK456', 'aircraft': '空客A380',
             'dep': 'HKG', 'arr': 'LHR', 'dep_hour': 10, 'dep_min': 30, 'arr_hour': 22, 'arr_min': 45,
             'price': 7999.00, 'seats': 8, 'direct': False, 'shared': False},
            {'airline': 'BA', 'flight_number': 'BA789', 'aircraft': '波音787',
             'dep': 'HKG', 'arr': 'LHR', 'dep_hour': 12, 'arr_hour': 20,
             'price': 9499.00, 'seats': 3, 'direct': True, 'shared': False},
            {'airline': 'CA', 'flight_number': 'CA937', 'aircraft': '波音747',
             'dep': 'PEK', 'arr': 'LHR', 'dep_hour': 13, 'arr_hour': 17,
             'price': 9999.00, 'seats': 2, 'direct': True, 'shared': False},
            {'airline': 'BA', 'flight_number': 'BA168', 'aircraft': '波音787',
             'dep': 'PVG', 'arr': 'LHR', 'dep_hour': 11, 'arr_hour': 16,
             'price': 10499.00, 'seats': 4, 'direct': True, 'shared': False},
            {'airline': 'SQ', 'flight_number': 'SQ896', 'aircraft': '空客A350',
             'dep': 'HKG', 'arr': 'SIN', 'dep_hour': 8, 'arr_hour': 12,
             'price': 2999.00, 'seats': 10, 'direct': True, 'shared': False},
        ]

        for fd in flights_data:
            dep_time = base_time + timedelta(hours=fd.get('dep_hour', 0), minutes=fd.get('dep_min', 0))
            arr_time = base_time + timedelta(hours=fd.get('arr_hour', 0), minutes=fd.get('arr_min', 0))
            Flight.objects.create(
                airline=airlines[fd['airline']],
                flight_number=fd['flight_number'],
                aircraft=fd['aircraft'],
                departure_airport=airports[fd['dep']],
                arrival_airport=airports[fd['arr']],
                departure_time=dep_time,
                arrival_time=arr_time,
                price=fd['price'],
                remaining_seats=fd['seats'],
                is_direct=fd['direct'],
                is_shared=fd['shared']
            )

        return airlines, airports


class FlightListIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        SeedDataFixture.create_seed_data()
        self.tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    def test_seed_data_creates_six_flights(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 6)

    def test_hkg_to_lhr_returns_three_flights(self):
        response = self.client.get('/api/flights/?departure_city=香港&arrival_city=伦敦')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 3)
        flight_numbers = sorted([f['flight_number'] for f in data['data']])
        self.assertEqual(flight_numbers, ['BA789', 'CX123', 'EK456'])

    def test_pek_to_lhr_returns_ca937(self):
        response = self.client.get('/api/flights/?departure_city=北京&arrival_city=伦敦')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['flight_number'], 'CA937')
        self.assertEqual(data['data'][0]['price'], 9999.0)

    def test_pvg_to_lhr_returns_ba168(self):
        response = self.client.get('/api/flights/?departure_city=上海&arrival_city=伦敦')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['flight_number'], 'BA168')
        self.assertEqual(data['data'][0]['price'], 10499.0)

    def test_hkg_to_sin_returns_sq896(self):
        response = self.client.get('/api/flights/?departure_city=香港&arrival_city=新加坡')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['flight_number'], 'SQ896')
        self.assertEqual(data['data'][0]['price'], 2999.0)

    def test_cheapest_hkg_lhr_is_ek456(self):
        response = self.client.get('/api/flights/?departure_city=香港&arrival_city=伦敦')
        data = json.loads(response.content)
        prices = {f['flight_number']: f['price'] for f in data['data']}
        self.assertEqual(prices['EK456'], 7999.0)
        self.assertEqual(prices['CX123'], 8999.0)
        self.assertEqual(prices['BA789'], 9499.0)

    def test_filter_by_departure_city_fuzzy(self):
        response = self.client.get('/api/flights/?departure_city=北')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['departure_airport']['city'], '北京')

    def test_filter_by_arrival_city_fuzzy(self):
        response = self.client.get('/api/flights/?arrival_city=伦')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 5)
        for f in data['data']:
            self.assertIn('伦', f['arrival_airport']['city'])

    def test_city_and_date_combined_filter(self):
        response = self.client.get(
            f'/api/flights/?departure_city=香港&arrival_city=伦敦&departure_date={self.tomorrow}'
        )
        data = json.loads(response.content)
        self.assertEqual(data['count'], 3)

    def test_detail_endpoint_matches_list_data(self):
        list_resp = self.client.get('/api/flights/?departure_city=香港&arrival_city=新加坡')
        list_data = json.loads(list_resp.content)
        flight_id = list_data['data'][0]['id']

        detail_resp = self.client.get(f'/api/flights/{flight_id}/')
        detail_data = json.loads(detail_resp.content)

        self.assertEqual(detail_data['data']['flight_number'], 'SQ896')
        self.assertEqual(detail_data['data']['price'], 2999.0)
        self.assertEqual(detail_data['data']['airline'], '新加坡航空')
        self.assertEqual(detail_data['data']['departure_airport']['code'], 'HKG')
        self.assertEqual(detail_data['data']['arrival_airport']['code'], 'SIN')

    def test_detail_contains_country_fields_not_in_list(self):
        list_resp = self.client.get('/api/flights/?departure_city=北京')
        list_data = json.loads(list_resp.content)
        flight_id = list_data['data'][0]['id']

        self.assertNotIn('country', list_data['data'][0]['departure_airport'])

        detail_resp = self.client.get(f'/api/flights/{flight_id}/')
        detail_data = json.loads(detail_resp.content)
        self.assertIn('country', detail_data['data']['departure_airport'])
        self.assertEqual(detail_data['data']['departure_airport']['country'], '中国')
        self.assertEqual(detail_data['data']['arrival_airport']['country'], '英国')

    def test_all_flights_from_hkg(self):
        response = self.client.get('/api/flights/?departure_city=香港')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 4)
        for f in data['data']:
            self.assertEqual(f['departure_airport']['city'], '香港')

    def test_all_flights_to_lhr(self):
        response = self.client.get('/api/flights/?arrival_city=伦敦')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 5)
        for f in data['data']:
            self.assertEqual(f['arrival_airport']['city'], '伦敦')

    def test_ek456_is_transfer_flight(self):
        response = self.client.get('/api/flights/?departure_city=香港&arrival_city=伦敦')
        data = json.loads(response.content)
        ek_flight = [f for f in data['data'] if f['flight_number'] == 'EK456'][0]
        self.assertFalse(ek_flight['is_direct'])

    def test_cx123_is_direct_flight(self):
        response = self.client.get('/api/flights/?departure_city=香港&arrival_city=伦敦')
        data = json.loads(response.content)
        cx_flight = [f for f in data['data'] if f['flight_number'] == 'CX123'][0]
        self.assertTrue(cx_flight['is_direct'])

    def test_remaining_seats_present_in_response(self):
        response = self.client.get('/api/flights/?departure_city=北京')
        data = json.loads(response.content)
        self.assertEqual(data['data'][0]['remaining_seats'], 2)

    def test_aircraft_field_present_in_response(self):
        response = self.client.get('/api/flights/?departure_city=北京')
        data = json.loads(response.content)
        self.assertEqual(data['data'][0]['aircraft'], '波音747')

    def test_response_structure_success(self):
        response = self.client.get('/api/flights/')
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('data', data)
        self.assertIn('count', data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
        self.assertIsInstance(data['count'], int)

    def test_no_flights_to_dubai(self):
        response = self.client.get('/api/flights/?arrival_city=迪拜')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 0)

    def test_no_flights_from_tokyo(self):
        response = self.client.get('/api/flights/?departure_city=东京')
        data = json.loads(response.content)
        self.assertEqual(data['count'], 0)
