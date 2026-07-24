"""
``flight_detail`` 边界单测：命中、404、不同 HTTP 方法。
"""

from django.test import TestCase
from django.urls import reverse

from .factories import build_flights


class FlightDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.flights = build_flights()
        cls.cx123 = cls.flights[0]

    def _url(self, fid):
        return reverse("flight_detail", args=[fid])

    def test_detail_success(self):
        resp = self.client.get(self._url(self.cx123.id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["flight_number"], "CX123")

    def test_detail_not_found_returns_404(self):
        # 不存在的 id
        max_id = max(f.id for f in self.flights)
        resp = self.client.get(self._url(max_id + 999))
        self.assertEqual(resp.status_code, 404)
        payload = resp.json()
        self.assertEqual(payload["status"], "error")
        self.assertIn("not found", payload["message"].lower())

    def test_detail_non_int_returns_404(self):
        # URL 路由 <int:flight_id> 对非数字返回 404（Django 路由）
        resp = self.client.get("/api/flights/abc/")
        self.assertEqual(resp.status_code, 404)

    def test_detail_returns_full_airport_country(self):
        # detail 接口应比 list 多返回 country 字段
        resp = self.client.get(self._url(self.cx123.id))
        data = resp.json()["data"]
        self.assertIn("country", data["departure_airport"])
        self.assertIn("country", data["arrival_airport"])

    def test_detail_each_seed_flight(self):
        for f in self.flights:
            resp = self.client.get(self._url(f.id))
            self.assertEqual(resp.status_code, 200, msg=f"flight {f.flight_number}")
            self.assertEqual(resp.json()["data"]["id"], f.id)
