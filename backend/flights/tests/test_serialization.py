"""序列化字段完整性测试。

重点覆盖含税价展示所依赖的原始字段（price 原样透传、机场 name/code），
以及时间格式化输出。
"""

import json

from django.test import TestCase, Client
from django.urls import reverse

from .factories import make_flight, BASE_TIME


class SerializationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.flight = make_flight(
            flight_number="CX123",
            price="8999.00",
            remaining_seats=5,
            is_direct=True,
            is_shared=False,
        )

    def _list_item(self):
        resp = self.client.get(reverse("flight_list"))
        return json.loads(resp.content)["data"][0]

    def _detail(self):
        resp = self.client.get(reverse("flight_detail", args=[self.flight.id]))
        return json.loads(resp.content)["data"]

    def test_list_item_full_fields(self):
        item = self._list_item()
        expected_keys = {
            "id", "airline", "flight_number", "aircraft",
            "departure_airport", "arrival_airport",
            "departure_time", "arrival_time", "price",
            "remaining_seats", "is_direct", "is_shared",
        }
        self.assertTrue(expected_keys.issubset(set(item.keys())))

    def test_airport_nested_fields_in_list(self):
        item = self._list_item()
        for airport in (item["departure_airport"], item["arrival_airport"]):
            self.assertIn("name", airport)
            self.assertIn("code", airport)
            self.assertIn("city", airport)

    def test_price_original_value_for_tax_display(self):
        """含税价展示依赖 price 原始数值，序列化为 float 且保值。"""
        item = self._list_item()
        self.assertEqual(item["price"], 8999.0)
        self.assertIsInstance(item["price"], float)

    def test_airline_serialized_as_name_string(self):
        item = self._list_item()
        self.assertEqual(item["airline"], "国泰航空")
        self.assertIsInstance(item["airline"], str)

    def test_datetime_format(self):
        """时间序列化为 'YYYY-MM-DD HH:MM'。"""
        item = self._list_item()
        self.assertRegex(item["departure_time"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
        self.assertRegex(item["arrival_time"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

    def test_boolean_flags_are_bool(self):
        item = self._list_item()
        self.assertIsInstance(item["is_direct"], bool)
        self.assertIsInstance(item["is_shared"], bool)

    def test_detail_has_country_but_list_does_not(self):
        detail = self._detail()
        item = self._list_item()
        self.assertIn("country", detail["departure_airport"])
        self.assertNotIn("country", item["departure_airport"])
