"""
已知缺陷用例集。

本文件中的每个测试都用 ``@unittest.expectedFailure`` 标记。它们断言
**期望的正确行为**，而现有实现并不满足——因此测试会以"预期失败"
（xfail）形式出现在测试报告里，既不会让 CI 变红，又能在文档/报告中
作为可执行的缺陷清单被追踪。

每个测试的 docstring 对应 README "缺陷报告" 表格中的一条。
当修复对应缺陷后，请把相应测试的 ``@expectedFailure`` 去掉，并让它
变绿（避免被"修好了还挂着 xfail"误报为 xpass）。
"""

import unittest
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from flights.models import Airline, Airport, Flight

from .factories import BASE_DATE, build_flights


class InvalidDateDefectTests(TestCase):
    """
    DEFECT-001: ``flight_list`` 对非法 ``departure_date`` 静默忽略。

    视图::

        try:
            date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
            ...
        except ValueError:
            pass

    任意无法解析的字符串都被吞掉，接口照常返回 200 与未过滤全集，
    调用方（前端/调用方）根本感知不到参数错误。期望返回 400 并给出
    错误信息。
    """

    @classmethod
    def setUpTestData(cls):
        build_flights()

    @unittest.expectedFailure
    def test_invalid_date_should_return_400(self):
        resp = self.client.get(reverse("flight_list"), {"departure_date": "not-a-date"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["status"], "error")

    @unittest.expectedFailure
    def test_malformed_slash_date_should_return_400(self):
        resp = self.client.get(reverse("flight_list"), {"departure_date": "2026/08/02"})
        self.assertEqual(resp.status_code, 400)

    @unittest.expectedFailure
    def test_out_of_range_date_should_return_400(self):
        # 2026-13-40 既不是合法日期
        resp = self.client.get(reverse("flight_list"), {"departure_date": "2026-13-40"})
        self.assertEqual(resp.status_code, 400)


class OrderingDefectTests(TestCase):
    """
    DEFECT-002: ``flight_list`` 不处理 ``ordering`` 查询参数。

    前端"价格低到高/时间优先/航空公司"三个排序按钮会发送
    ``ordering=price|departure_time|airline``，但后端从未读取该参数，
    导致前端排序完全失效（默认按主键顺序返回）。期望按参数排序。
    """

    @classmethod
    def setUpTestData(cls):
        build_flights()

    @unittest.expectedFailure
    def test_ordering_price_asc(self):
        resp = self.client.get(reverse("flight_list"), {"ordering": "price"})
        prices = [f["price"] for f in resp.json()["data"]]
        self.assertEqual(prices, sorted(prices))

    @unittest.expectedFailure
    def test_ordering_departure_time(self):
        resp = self.client.get(reverse("flight_list"), {"ordering": "departure_time"})
        times = [f["departure_time"] for f in resp.json()["data"]]
        self.assertEqual(times, sorted(times))

    @unittest.expectedFailure
    def test_ordering_airline(self):
        resp = self.client.get(reverse("flight_list"), {"ordering": "airline"})
        airlines = [f["airline"] for f in resp.json()["data"]]
        self.assertEqual(airlines, sorted(airlines))


class FilterFlagDefectTests(TestCase):
    """
    DEFECT-003: ``flight_list`` 不处理 ``is_direct`` / ``is_shared``。

    前端筛选栏会发送这两个布尔参数，但后端仅按城市/日期过滤，
    "直飞/中转/共享航班"筛选按钮实际无效。期望按布尔标志过滤。
    """

    @classmethod
    def setUpTestData(cls):
        build_flights()
        # 额外构造一条共享航班，便于 is_shared 断言
        cx = Airline.objects.get(code="CX")
        hkg = Airport.objects.get(code="HKG")
        lhr = Airport.objects.get(code="LHR")
        Flight.objects.create(
            airline=cx, flight_number="CX999", aircraft="测试机",
            departure_airport=hkg, arrival_airport=lhr,
            departure_time=BASE_DATE.replace(day=2, hour=14),
            arrival_time=BASE_DATE.replace(day=2, hour=22),
            price=Decimal("5555.00"), remaining_seats=7,
            is_direct=True, is_shared=True,
        )

    @unittest.expectedFailure
    def test_is_direct_true(self):
        resp = self.client.get(reverse("flight_list"), {"is_direct": "true"})
        self.assertTrue(all(f["is_direct"] for f in resp.json()["data"]))

    @unittest.expectedFailure
    def test_is_direct_false_transfer(self):
        resp = self.client.get(reverse("flight_list"), {"is_direct": "false"})
        self.assertTrue(all(not f["is_direct"] for f in resp.json()["data"]))

    @unittest.expectedFailure
    def test_is_shared_true(self):
        resp = self.client.get(reverse("flight_list"), {"is_shared": "true"})
        self.assertTrue(all(f["is_shared"] for f in resp.json()["data"]))
        self.assertEqual(resp.json()["count"], 1)


class ModelConstraintDefectTests(TestCase):
    """
    DEFECT-004: ``Airline.code`` / ``Airport.code`` 无唯一约束，
    允许重复代码，会破坏前端按代码识别航司/机场的假设。

    DEFECT-005: ``Flight`` 缺少业务级约束：
      - 到达时间应晚于起飞时间
      - 价格应 >= 0
      - 剩余座位应 >= 0
      - 出发机场与到达机场不应相同
    """

    @unittest.expectedFailure
    def test_airline_code_should_be_unique(self):
        Airline.objects.create(name="航司A", code="XX")
        with self.assertRaises(IntegrityError):
            Airline.objects.create(name="航司B", code="XX")

    @unittest.expectedFailure
    def test_airport_code_should_be_unique(self):
        Airport.objects.create(name="机场A", code="AAA", city="A城", country="X国")
        with self.assertRaises(IntegrityError):
            Airport.objects.create(name="机场B", code="AAA", city="B城", country="Y国")

    @unittest.expectedFailure
    def test_arrival_should_be_after_departure(self):
        airline = Airline.objects.create(name="航司", code="TS")
        hkg = Airport.objects.create(name="HK", code="HKG", city="香港", country="中国")
        lhr = Airport.objects.create(name="LH", code="LHR", city="伦敦", country="英国")
        with self.assertRaises(Exception):
            Flight.objects.create(
                airline=airline, flight_number="TS1",
                departure_airport=hkg, arrival_airport=lhr,
                departure_time=BASE_DATE.replace(hour=20),
                arrival_time=BASE_DATE.replace(hour=10),  # 早于出发
                price=Decimal("1000.00"), remaining_seats=10,
            )

    @unittest.expectedFailure
    def test_price_should_be_non_negative(self):
        airline = Airline.objects.create(name="航司", code="TS")
        hkg = Airport.objects.create(name="HK", code="HKG", city="香港", country="中国")
        lhr = Airport.objects.create(name="LH", code="LHR", city="伦敦", country="英国")
        with self.assertRaises(Exception):
            Flight.objects.create(
                airline=airline, flight_number="TS2",
                departure_airport=hkg, arrival_airport=lhr,
                departure_time=BASE_DATE.replace(hour=8),
                arrival_time=BASE_DATE.replace(hour=12),
                price=Decimal("-1.00"), remaining_seats=10,
            )

    @unittest.expectedFailure
    def test_remaining_seats_should_be_non_negative(self):
        airline = Airline.objects.create(name="航司", code="TS")
        hkg = Airport.objects.create(name="HK", code="HKG", city="香港", country="中国")
        lhr = Airport.objects.create(name="LH", code="LHR", city="伦敦", country="英国")
        with self.assertRaises(Exception):
            Flight.objects.create(
                airline=airline, flight_number="TS3",
                departure_airport=hkg, arrival_airport=lhr,
                departure_time=BASE_DATE.replace(hour=8),
                arrival_time=BASE_DATE.replace(hour=12),
                price=Decimal("1000.00"), remaining_seats=-1,
            )

    @unittest.expectedFailure
    def test_departure_and_arrival_airport_should_differ(self):
        airline = Airline.objects.create(name="航司", code="TS")
        hkg = Airport.objects.create(name="HK", code="HKG", city="香港", country="中国")
        with self.assertRaises(Exception):
            Flight.objects.create(
                airline=airline, flight_number="TS4",
                departure_airport=hkg, arrival_airport=hkg,
                departure_time=BASE_DATE.replace(hour=8),
                arrival_time=BASE_DATE.replace(hour=12),
                price=Decimal("1000.00"), remaining_seats=10,
            )
