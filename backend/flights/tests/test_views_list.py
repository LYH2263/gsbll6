"""flight_list 视图边界测试：城市模糊匹配、日期解析、空结果、请求方法。"""

import json

from django.test import TestCase, Client
from django.urls import reverse

from .factories import seed_flights, make_flight, make_airport, make_airline, BASE_TIME
from datetime import timedelta


class FlightListTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("flight_list")
        self.flights = seed_flights()

    def _get(self, **params):
        resp = self.client.get(self.url, params)
        return resp, json.loads(resp.content)

    def test_returns_all_without_filters(self):
        resp, body = self._get()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["count"], 6)
        self.assertEqual(len(body["data"]), 6)

    def test_filter_by_departure_city(self):
        _, body = self._get(departure_city="香港")
        # HKG 出发：CX/EK/BA(伦敦) + SQ(新加坡) = 4
        self.assertEqual(body["count"], 4)
        for item in body["data"]:
            self.assertEqual(item["departure_airport"]["city"], "香港")

    def test_filter_by_arrival_city(self):
        _, body = self._get(arrival_city="伦敦")
        self.assertEqual(body["count"], 5)

    def test_filter_combined_departure_and_arrival(self):
        _, body = self._get(departure_city="香港", arrival_city="伦敦")
        self.assertEqual(body["count"], 3)

    def test_city_fuzzy_icontains(self):
        """城市为 icontains 模糊匹配：子串应命中。"""
        make_airport(name="首尔仁川机场", code="ICN", city="首尔", country="韩国")
        # 用“伦”匹配“伦敦”
        _, body = self._get(arrival_city="伦")
        self.assertEqual(body["count"], 5)

    def test_empty_result_for_unknown_city(self):
        _, body = self._get(departure_city="火星")
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["count"], 0)
        self.assertEqual(body["data"], [])

    def test_filter_by_valid_date(self):
        """按出发日期筛选当天航班。种子数据出发日均为 2026-08-01。"""
        _, body = self._get(departure_date="2026-08-01")
        self.assertEqual(body["count"], 6)

    def test_valid_date_other_day_empty(self):
        _, body = self._get(departure_date="2026-08-02")
        self.assertEqual(body["count"], 0)

    def test_post_method_rejected(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 400)
        body = json.loads(resp.content)
        self.assertEqual(body["status"], "error")

    def test_response_shape_keys(self):
        _, body = self._get(departure_city="新加坡")
        self.assertEqual(body["count"], 0)
        # SQ 到达新加坡：出发是香港，用到达城市过滤
        _, body = self._get(arrival_city="新加坡")
        self.assertEqual(body["count"], 1)
        item = body["data"][0]
        for key in [
            "id", "airline", "flight_number", "aircraft",
            "departure_airport", "arrival_airport",
            "departure_time", "arrival_time", "price",
            "remaining_seats", "is_direct", "is_shared",
        ]:
            self.assertIn(key, item)
