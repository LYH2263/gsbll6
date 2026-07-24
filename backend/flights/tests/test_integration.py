"""集成测试：多条件组合查询、与种子数据一致的端到端断言、排序语义现状。

说明：当前后端 flight_list 未实现 ordering / is_direct / is_shared 查询参数，
因此这里断言的是「现有真实行为」（参数被忽略、返回默认顺序）。
对应的“应支持却未支持”的缺陷在 test_defects.py 中以 expectedFailure 标注。
"""

import json

from django.test import TestCase, Client
from django.urls import reverse

from .factories import seed_flights


class MultiConditionQueryTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("flight_list")
        self.flights = seed_flights()

    def _get(self, **params):
        resp = self.client.get(self.url, params)
        return json.loads(resp.content)

    def test_hkg_to_lhr_on_date(self):
        body = self._get(departure_city="香港", arrival_city="伦敦", departure_date="2026-08-01")
        self.assertEqual(body["count"], 3)
        numbers = {i["flight_number"] for i in body["data"]}
        self.assertEqual(numbers, {"CX123", "EK456", "BA789"})

    def test_combined_no_match(self):
        body = self._get(departure_city="北京", arrival_city="新加坡")
        self.assertEqual(body["count"], 0)

    def test_seed_data_consistency_prices(self):
        """端到端：返回的价格与种子数据一致。"""
        body = self._get(arrival_city="伦敦")
        by_number = {i["flight_number"]: i for i in body["data"]}
        self.assertEqual(by_number["CX123"]["price"], 8999.0)
        self.assertEqual(by_number["CA937"]["price"], 9999.0)
        self.assertEqual(by_number["BA168"]["price"], 10499.0)

    def test_seed_data_consistency_remaining_seats(self):
        body = self._get(departure_city="香港", arrival_city="新加坡")
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["data"][0]["remaining_seats"], 10)
        self.assertEqual(body["data"][0]["flight_number"], "SQ896")


class SortingSemanticsCurrentBehaviorTest(TestCase):
    """记录排序参数的当前真实行为：被忽略，返回默认（主键/插入）顺序。"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("flight_list")
        self.flights = seed_flights()

    def _numbers(self, **params):
        resp = self.client.get(self.url, params)
        return [i["flight_number"] for i in json.loads(resp.content)["data"]]

    def test_ordering_param_is_ignored(self):
        """带 ordering=price 与不带参数返回顺序一致（说明参数被忽略）。"""
        with_order = self._numbers(ordering="price")
        without_order = self._numbers()
        self.assertEqual(with_order, without_order)

    def test_default_order_is_insertion_order(self):
        """默认顺序即种子插入顺序。"""
        numbers = self._numbers()
        self.assertEqual(
            numbers,
            ["CX123", "EK456", "BA789", "CA937", "BA168", "SQ896"],
        )

    def test_client_side_sort_by_price_matches_seed(self):
        """在客户端对返回结果按价格排序应得到确定序列（验证数据正确性）。"""
        resp = self.client.get(self.url)
        data = json.loads(resp.content)["data"]
        prices = sorted(i["price"] for i in data)
        self.assertEqual(
            prices,
            [2999.0, 7999.0, 8999.0, 9499.0, 9999.0, 10499.0],
        )
