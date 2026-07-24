"""
``flight_list`` 边界单测：

- 城市模糊匹配（大小写无关 icontains）
- 日期解析成功的命中
- 日期解析失败（非法格式）的当前行为（静默忽略，返回未过滤全集）
  ——正确的期望行为见 test_defects.py 中的 xfail 用例，本文件只锁定当前实现
- 空结果（不存在的城市/不存在的日期）
- 非 GET 方法返回 400
"""

from django.test import TestCase
from django.urls import reverse

from .factories import build_flights


class FlightListFilteringTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.flights = build_flights()

    def setUp(self):
        self.url = reverse("flight_list")

    # ---------- 城市模糊匹配 ----------

    def test_filter_by_departure_city_exact(self):
        resp = self.client.get(self.url, {"departure_city": "北京"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["flight_number"], "CA937")

    def test_filter_by_arrival_city_exact(self):
        resp = self.client.get(self.url, {"arrival_city": "新加坡"})
        data = resp.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["flight_number"], "SQ896")

    def test_filter_by_city_partial_match(self):
        # icontains：只给一个字也应能匹配
        resp = self.client.get(self.url, {"departure_city": "香"})
        data = resp.json()["data"]
        # 香港出发：CX123/EK456/BA789/SQ896 共 4 条
        self.assertEqual(len(data), 4)

    def test_filter_by_both_cities(self):
        resp = self.client.get(self.url, {
            "departure_city": "香港",
            "arrival_city": "伦敦",
        })
        data = resp.json()["data"]
        numbers = {f["flight_number"] for f in data}
        self.assertEqual(numbers, {"CX123", "EK456", "BA789"})

    def test_filter_by_city_no_match(self):
        resp = self.client.get(self.url, {"departure_city": "火星"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 0)
        self.assertEqual(resp.json()["data"], [])

    # ---------- 日期 ----------

    def test_filter_by_departure_date_valid(self):
        # 种子航班都在 2026-08-02
        resp = self.client.get(self.url, {"departure_date": "2026-08-02"})
        self.assertEqual(resp.json()["count"], 6)

    def test_filter_by_departure_date_wrong_day_empty(self):
        resp = self.client.get(self.url, {"departure_date": "2026-08-03"})
        self.assertEqual(resp.json()["count"], 0)
        self.assertEqual(resp.json()["data"], [])

    def test_filter_by_date_with_city(self):
        resp = self.client.get(self.url, {
            "departure_city": "香港",
            "arrival_city": "伦敦",
            "departure_date": "2026-08-02",
        })
        self.assertEqual(resp.json()["count"], 3)

    def test_filter_invalid_date_currently_returns_all(self):
        """
        当前实现：非法日期格式触发 ValueError 后 ``pass``，即静默忽略，
        返回未过滤全集。本测试锁定这一既有行为（避免无意回归）。

        期望的正确行为（返回 400 或空结果）在 test_defects.py 以
        @expectedFailure 形式标注。
        """
        resp = self.client.get(self.url, {"departure_date": "not-a-date"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 6)  # 全部 6 条都被返回

    def test_filter_malformed_date_slash_currently_returns_all(self):
        resp = self.client.get(self.url, {"departure_date": "2026/08/02"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 6)

    def test_filter_empty_params_returns_all(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.json()["count"], 6)

    def test_filter_blank_string_params_ignored(self):
        # 空字符串参数应等价于未提供
        resp = self.client.get(self.url, {
            "departure_city": "",
            "arrival_city": "",
            "departure_date": "",
        })
        self.assertEqual(resp.json()["count"], 6)


class FlightListMethodTests(TestCase):
    def setUp(self):
        self.url = reverse("flight_list")

    def test_post_returns_400(self):
        resp = self.client.post(self.url, data={})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["status"], "error")

    def test_put_returns_400(self):
        resp = self.client.put(self.url, data={})
        self.assertEqual(resp.status_code, 400)

    def test_delete_returns_400(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 400)
