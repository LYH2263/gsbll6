"""flight_detail 视图边界测试：正常、404、字段完整性。"""

import json

from django.test import TestCase, Client
from django.urls import reverse

from .factories import make_flight


class FlightDetailTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.flight = make_flight(flight_number="CX123")

    def _get(self, flight_id):
        resp = self.client.get(reverse("flight_detail", args=[flight_id]))
        return resp, json.loads(resp.content)

    def test_detail_success(self):
        resp, body = self._get(self.flight.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["data"]["id"], self.flight.id)
        self.assertEqual(body["data"]["flight_number"], "CX123")

    def test_detail_not_found_returns_404(self):
        resp, body = self._get(999999)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["message"], "Flight not found")

    def test_detail_includes_airport_country(self):
        """详情视图比列表视图多返回机场 country 字段。"""
        _, body = self._get(self.flight.id)
        self.assertIn("country", body["data"]["departure_airport"])
        self.assertIn("country", body["data"]["arrival_airport"])

    def test_detail_price_is_numeric(self):
        _, body = self._get(self.flight.id)
        self.assertIsInstance(body["data"]["price"], (int, float))
