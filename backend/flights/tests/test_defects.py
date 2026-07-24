"""缺陷暴露用例（expectedFailure）。

每个用例断言「期望的正确行为」。由于现有实现存在缺陷，这些断言会失败，
被 @expectedFailure 标注后在报告中显示为 expected failures，不会让 CI 变红。
修复对应业务代码后去掉 @expectedFailure 即转为回归断言。

按你的要求：未改动任何业务功能，缺陷仅以可执行测试形式标注，
不在本次修改范围内。详见 docs/DEFECTS.md。
"""

import json
import unittest

from django.test import TestCase, Client
from django.urls import reverse

from .factories import seed_flights, make_flight


class DateHandlingDefects(TestCase):
    """缺陷类别 1：非法日期被静默忽略。"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("flight_list")
        self.flights = seed_flights()

    def _get(self, **params):
        resp = self.client.get(self.url, params)
        return resp, json.loads(resp.content)

    @unittest.expectedFailure
    def test_invalid_date_should_not_return_all(self):
        """非法日期 'not-a-date' 当前被 except ValueError: pass 静默忽略，
        导致返回全部航班。期望：应报错或返回空集，而非无声吞掉。"""
        _, body = self._get(departure_date="not-a-date")
        self.assertNotEqual(body["count"], 6)  # 期望不是“返回全部”

    @unittest.expectedFailure
    def test_invalid_date_should_return_400(self):
        """期望：非法日期返回 400 校验错误。当前返回 200。"""
        resp, _ = self._get(departure_date="2026-13-99")
        self.assertEqual(resp.status_code, 400)

    @unittest.expectedFailure
    def test_wrong_date_format_should_be_reported(self):
        """期望：'2026/08/01' 这类格式被识别或报错，而非静默忽略。"""
        _, body = self._get(departure_date="2026/08/01")
        # 期望按当天筛选出 6 条；实际因解析失败被忽略返回全部（这里断言状态字段）
        self.assertEqual(body.get("status"), "error")


class OrderingDefects(TestCase):
    """缺陷类别 2：ordering 排序参数未实现。"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("flight_list")
        self.flights = seed_flights()

    def _numbers(self, **params):
        resp = self.client.get(self.url, params)
        return [i["flight_number"] for i in json.loads(resp.content)["data"]]

    @unittest.expectedFailure
    def test_ordering_by_price_ascending(self):
        """期望 ordering=price 时按价格升序返回。当前忽略该参数。"""
        numbers = self._numbers(ordering="price")
        self.assertEqual(
            numbers,
            ["SQ896", "EK456", "CX123", "BA789", "CA937", "BA168"],
        )

    @unittest.expectedFailure
    def test_ordering_by_departure_time(self):
        """期望 ordering=departure_time 时按出发时间升序。"""
        numbers = self._numbers(ordering="departure_time")
        self.assertEqual(numbers[0], "SQ896")  # 出发最早

    @unittest.expectedFailure
    def test_ordering_by_airline(self):
        """期望 ordering=airline 时按航司排序。"""
        numbers = self._numbers(ordering="airline")
        first = self._numbers()[0]
        self.assertNotEqual(numbers[0], first)


class FilterDefects(TestCase):
    """缺陷类别 3/4：is_direct / is_shared 筛选参数未实现。"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("flight_list")
        self.flights = seed_flights()

    def _get(self, **params):
        resp = self.client.get(self.url, params)
        return json.loads(resp.content)

    @unittest.expectedFailure
    def test_filter_direct_only(self):
        """期望 is_direct=true 只返回直飞。种子中 EK456 为中转，应被排除。"""
        body = self._get(is_direct="true")
        numbers = {i["flight_number"] for i in body["data"]}
        self.assertNotIn("EK456", numbers)

    @unittest.expectedFailure
    def test_filter_transfer_only(self):
        """期望 is_direct=false 只返回中转（仅 EK456）。"""
        body = self._get(is_direct="false")
        self.assertEqual(body["count"], 1)

    @unittest.expectedFailure
    def test_filter_shared_only(self):
        """期望 is_shared=true 只返回共享航班（仅 BA789）。"""
        body = self._get(is_shared="true")
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["data"][0]["flight_number"], "BA789")


class ValidationDefects(TestCase):
    """缺陷类别 5：缺乏输入校验与语义约束。"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("flight_list")

    def _get(self, **params):
        resp = self.client.get(self.url, params)
        return resp, json.loads(resp.content)

    @unittest.expectedFailure
    def test_arrival_equals_departure_should_error(self):
        """期望：出发城市与到达城市相同应报错或返回空。"""
        seed_flights()
        resp, body = self._get(departure_city="香港", arrival_city="香港")
        self.assertEqual(resp.status_code, 400)

    @unittest.expectedFailure
    def test_negative_remaining_seats_rejected(self):
        """期望：模型层禁止负数余票。当前 IntegerField 无约束，可保存负值。"""
        from django.core.exceptions import ValidationError
        f = make_flight(remaining_seats=-5)
        with self.assertRaises(ValidationError):
            f.full_clean()

    @unittest.expectedFailure
    def test_negative_price_rejected(self):
        """期望：价格不允许为负。当前无约束。"""
        from django.core.exceptions import ValidationError
        f = make_flight(price="-100.00")
        with self.assertRaises(ValidationError):
            f.full_clean()

    @unittest.expectedFailure
    def test_arrival_before_departure_rejected(self):
        """期望：到达时间早于出发时间应被拒绝。当前无校验。"""
        from datetime import timedelta
        from django.core.exceptions import ValidationError
        from .factories import BASE_TIME
        f = make_flight(
            departure_time=BASE_TIME,
            arrival_time=BASE_TIME - timedelta(hours=2),
        )
        with self.assertRaises(ValidationError):
            f.full_clean()


class MethodHandlingDefects(TestCase):
    """缺陷类别：详情接口对非法方法/参数处理不完整。"""

    def setUp(self):
        self.client = Client()
        self.flight = make_flight()

    @unittest.expectedFailure
    def test_detail_post_should_be_405(self):
        """期望：detail 对 POST 返回 405（方法不允许）。当前未限制方法。"""
        resp = self.client.post(reverse("flight_detail", args=[self.flight.id]))
        self.assertEqual(resp.status_code, 405)

    @unittest.expectedFailure
    def test_list_should_expose_total_price_with_tax(self):
        """期望：列表返回含税总价字段（如 total_price / tax）。当前仅有裸 price，
        前端仅以静态“含税”文案标注，缺乏真实税费数据。"""
        resp = self.client.get(reverse("flight_list"))
        item = json.loads(resp.content)["data"][0]
        self.assertIn("total_price", item)
