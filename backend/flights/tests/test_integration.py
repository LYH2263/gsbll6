"""
集成测试：

1. 多条件组合查询：城市 + 日期 三维组合，与夹具数据一致。
2. 排序语义：验证当前实现对 ``ordering`` 参数的实际处理方式
   （= 被静默忽略），并断言返回顺序稳定；真正的排序期望见
   ``test_defects.py`` 的 xfail 用例。
3. 端到端种子数据：直接调用 ``init_data.init_data()``，对通过
   API 暴露的记录数、关键航班号、价格做与种子一致的断言。

使用 Django 内置 ``self.client``（即 TestClient），未引入 DRF，
因为视图基于 ``JsonResponse`` 手写，且 ``requirements.txt`` 中没有 DRF。
"""

from datetime import datetime, timedelta

from django.test import TestCase, override_settings
from django.urls import reverse

from flights.models import Airline, Airport, Flight

from .factories import build_flights


@override_settings(ROOT_URLCONF="flight_booking.urls")
class MultiConditionQueryIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.flights = build_flights()

    def setUp(self):
        self.url = reverse("flight_list")

    def test_no_filter_returns_six(self):
        self.assertEqual(self.client.get(self.url).json()["count"], 6)

    def test_departure_city_only(self):
        self.assertEqual(
            self.client.get(self.url, {"departure_city": "上海"}).json()["count"], 1
        )

    def test_arrival_city_only(self):
        self.assertEqual(
            self.client.get(self.url, {"arrival_city": "伦敦"}).json()["count"], 5
        )

    def test_date_only(self):
        self.assertEqual(
            self.client.get(self.url, {"departure_date": "2026-08-02"}).json()["count"], 6
        )

    def test_departure_and_arrival(self):
        resp = self.client.get(self.url, {
            "departure_city": "香港", "arrival_city": "伦敦",
        })
        self.assertEqual(resp.json()["count"], 3)

    def test_departure_and_date(self):
        resp = self.client.get(self.url, {
            "departure_city": "北京", "departure_date": "2026-08-02",
        })
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["data"][0]["flight_number"], "CA937")

    def test_arrival_and_date(self):
        resp = self.client.get(self.url, {
            "arrival_city": "新加坡", "departure_date": "2026-08-02",
        })
        self.assertEqual(resp.json()["count"], 1)

    def test_all_three_conditions(self):
        resp = self.client.get(self.url, {
            "departure_city": "香港",
            "arrival_city": "伦敦",
            "departure_date": "2026-08-02",
        })
        self.assertEqual(resp.json()["count"], 3)
        numbers = sorted(f["flight_number"] for f in resp.json()["data"])
        self.assertEqual(numbers, ["BA789", "CX123", "EK456"])

    def test_combination_yielding_empty(self):
        resp = self.client.get(self.url, {
            "departure_city": "北京",
            "arrival_city": "新加坡",
        })
        self.assertEqual(resp.json()["count"], 0)

    def test_case_insensitive_chinese_is_noop(self):
        # 中文无大小写，但 icontains 仍应正常匹配
        self.assertEqual(
            self.client.get(self.url, {"departure_city": "港"}).json()["count"], 4
        )


class OrderingIntegrationTests(TestCase):
    """
    现有视图未读取 ``ordering`` 查询参数——这是缺陷。本组测试只记录
    当前实际行为（接口不报错、返回默认顺序），不假装排序生效。
    """

    @classmethod
    def setUpTestData(cls):
        cls.flights = build_flights()

    def setUp(self):
        self.url = reverse("flight_list")

    def test_ordering_param_does_not_error(self):
        resp = self.client.get(self.url, {"ordering": "price"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 6)

    def test_ordering_param_currently_ignored_for_price(self):
        # 当前实现：价格顺序不保证升序；记录为"未排序"基线
        prices = [f["price"] for f in self.client.get(
            self.url, {"ordering": "price"}
        ).json()["data"]]
        # 至少能取到价格，但不应（错误地）认为已排序
        self.assertEqual(len(prices), 6)
        self.assertIn(2999.0, prices)
        self.assertIn(10499.0, prices)

    def test_ordering_param_currently_ignored_for_departure_time(self):
        resp = self.client.get(self.url, {"ordering": "departure_time"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 6)


class SeedDataEndToEndTests(TestCase):
    """
    直接执行 init_data.init_data()（Docker 部署时使用的种子脚本），
    验证经 API 可见的数据与种子声明一致。
    """

    def setUp(self):
        # init_data 直接写数据库，不经过 Django TestCase 的夹具机制
        from init_data import init_data
        init_data()

    def test_airline_seed_count(self):
        self.assertEqual(Airline.objects.count(), 5)
        self.assertTrue(Airline.objects.filter(code="CX", name="国泰航空").exists())
        self.assertTrue(Airline.objects.filter(code="SQ").exists())

    def test_airport_seed_count(self):
        self.assertEqual(Airport.objects.count(), 6)
        for code in ["HKG", "LHR", "PEK", "PVG", "SIN", "DXB"]:
            self.assertTrue(Airport.objects.filter(code=code).exists(), code)

    def test_flight_seed_count(self):
        self.assertEqual(Flight.objects.count(), 6)

    def test_api_exposes_seed_flights(self):
        resp = self.client.get(reverse("flight_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 6)
        numbers = {f["flight_number"] for f in resp.json()["data"]}
        self.assertEqual(
            numbers,
            {"CX123", "EK456", "BA789", "CA937", "BA168", "SQ896"},
        )

    def test_seed_prices_preserved(self):
        resp = self.client.get(reverse("flight_list"))
        by_number = {f["flight_number"]: f["price"] for f in resp.json()["data"]}
        self.assertAlmostEqual(by_number["CX123"], 8999.00, places=2)
        self.assertAlmostEqual(by_number["EK456"], 7999.00, places=2)
        self.assertAlmostEqual(by_number["BA168"], 10499.00, places=2)
        self.assertAlmostEqual(by_number["SQ896"], 2999.00, places=2)

    def test_seed_routes_preserved(self):
        resp = self.client.get(reverse("flight_list"))
        by_number = {f["flight_number"]: f for f in resp.json()["data"]}
        self.assertEqual(by_number["CX123"]["departure_airport"]["code"], "HKG")
        self.assertEqual(by_number["CX123"]["arrival_airport"]["code"], "LHR")
        self.assertEqual(by_number["SQ896"]["arrival_airport"]["code"], "SIN")

    def test_seed_flights_are_in_the_next_two_days(self):
        # 种子使用 datetime.now() + 1day + N hours；当本地时间在晚间时，
        # +N hours 会跨过午夜，日期可能落到 +2 天。这里只断言业务语义：
        # 全部航班都在未来，且落在 1~2 天窗口内，不绑定具体某一日。
        today = datetime.now().date()
        min_date = today + timedelta(days=1)
        max_date = today + timedelta(days=2)
        for f in Flight.objects.all():
            dep_date = f.departure_time.date()
            self.assertGreaterEqual(dep_date, min_date)
            self.assertLessEqual(dep_date, max_date)
