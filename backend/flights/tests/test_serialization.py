"""
序列化/响应字段完整性单测。

前端"含税价"展示直接依赖后端返回的原始字段 ``price``（前端在该字段旁
渲染"含税"字样），因此需要保证 list / detail 两个接口都返回该字段，
且返回类型为 JSON 可序列化的 float。同时校验机场嵌套对象、时间格式化
字符串、直飞/共享标志等字段完整不缺。
"""

from django.test import TestCase
from django.urls import reverse

from .factories import build_flights


# list 响应中每条航班应包含的顶层字段
LIST_ITEM_FIELDS = {
    "id", "airline", "flight_number", "aircraft",
    "departure_airport", "arrival_airport",
    "departure_time", "arrival_time",
    "price", "remaining_seats", "is_direct", "is_shared",
}

# 机场嵌套对象字段（list 中不含 country）
LIST_AIRPORT_FIELDS = {"name", "code", "city"}

# detail 中机场嵌套对象字段（含 country）
DETAIL_AIRPORT_FIELDS = {"name", "code", "city", "country"}


class FlightListSerializationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.flights = build_flights()

    def setUp(self):
        self.url = reverse("flight_list")

    def test_list_envelope_and_count(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["status"], "success")
        self.assertIn("data", payload)
        self.assertIn("count", payload)
        self.assertEqual(payload["count"], len(payload["data"]))
        self.assertEqual(payload["count"], 6)

    def test_list_item_field_completeness(self):
        resp = self.client.get(self.url)
        for item in resp.json()["data"]:
            self.assertEqual(set(item.keys()), LIST_ITEM_FIELDS)

    def test_list_airport_nested_fields(self):
        for item in self.client.get(self.url).json()["data"]:
            self.assertEqual(set(item["departure_airport"].keys()), LIST_AIRPORT_FIELDS)
            self.assertEqual(set(item["arrival_airport"].keys()), LIST_AIRPORT_FIELDS)

    def test_list_price_is_float_and_positive(self):
        # 含税价展示依赖的原始字段 price 必须存在且为 float
        for item in self.client.get(self.url).json()["data"]:
            self.assertIsInstance(item["price"], float)
            self.assertGreater(item["price"], 0)

    def test_list_time_format_string(self):
        # 视图使用 '%Y-%m-%d %H:%M' 格式
        item = self.client.get(self.url).json()["data"][0]
        self.assertRegex(item["departure_time"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
        self.assertRegex(item["arrival_time"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

    def test_list_airline_name_rendered_not_id(self):
        # 响应中 airline 字段应为航司名称字符串，而非主键
        item = self.client.get(self.url).json()["data"][0]
        self.assertIsInstance(item["airline"], str)
        self.assertIn(item["airline"], {"国泰航空", "阿联酋航空", "英国航空",
                                        "中国国际航空", "新加坡航空"})

    def test_list_boolean_flags_present(self):
        for item in self.client.get(self.url).json()["data"]:
            self.assertIsInstance(item["is_direct"], bool)
            self.assertIsInstance(item["is_shared"], bool)

    def test_list_aircraft_nullable_field_present(self):
        # aircraft 可能为 None，但字段必须存在
        for item in self.client.get(self.url).json()["data"]:
            self.assertIn("aircraft", item)


class FlightDetailSerializationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.flights = build_flights()
        cls.cx123 = cls.flights[0]

    def _detail(self, flight_id):
        return self.client.get(reverse("flight_detail", args=[flight_id]))

    def test_detail_envelope_and_field_completeness(self):
        resp = self._detail(self.cx123.id)
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["status"], "success")
        item = payload["data"]
        self.assertEqual(set(item.keys()), LIST_ITEM_FIELDS)

    def test_detail_airport_includes_country(self):
        item = self._detail(self.cx123.id).json()["data"]
        self.assertEqual(set(item["departure_airport"].keys()), DETAIL_AIRPORT_FIELDS)
        self.assertEqual(set(item["arrival_airport"].keys()), DETAIL_AIRPORT_FIELDS)

    def test_detail_price_float(self):
        item = self._detail(self.cx123.id).json()["data"]
        self.assertIsInstance(item["price"], float)
        self.assertAlmostEqual(item["price"], 8999.00, places=2)

    def test_detail_values_match_seed(self):
        item = self._detail(self.cx123.id).json()["data"]
        self.assertEqual(item["flight_number"], "CX123")
        self.assertEqual(item["airline"], "国泰航空")
        self.assertEqual(item["aircraft"], "波音777")
        self.assertEqual(item["departure_airport"]["code"], "HKG")
        self.assertEqual(item["arrival_airport"]["code"], "LHR")
        self.assertEqual(item["departure_airport"]["country"], "中国")
        self.assertEqual(item["arrival_airport"]["country"], "英国")
        self.assertEqual(item["remaining_seats"], 5)
        self.assertTrue(item["is_direct"])
        self.assertFalse(item["is_shared"])
