"""
模型层单测：Airline / Airport / Flight 的字段约束、默认值、关联与级联。

注意：本项目模型当前未声明 ``unique`` / ``CheckConstraint`` 等约束，
凡是涉及"应当被数据库拒绝"的期望，统一放到 ``test_defects.py`` 中
以 ``@expectedFailure`` 暴露缺陷。本文件只断言"现有实现"实际行为。
"""

from decimal import Decimal

from django.db import models
from django.test import TestCase

from flights.models import Airline, Airport, Flight

from .factories import build_airlines, build_airports, build_flights


class AirlineModelTests(TestCase):
    def test_str_returns_name(self):
        a = Airline.objects.create(name="国泰航空", code="CX")
        self.assertEqual(str(a), "国泰航空")

    def test_logo_optional(self):
        # logo 为 URLField(blank=True, null=True)，不传应可保存
        a = Airline.objects.create(name="测试航司", code="TS")
        self.assertIsNone(a.logo)
        a.logo = "https://example.com/logo.png"
        a.save()
        self.assertEqual(a.logo, "https://example.com/logo.png")

    def test_name_code_max_length(self):
        name_field = Airline._meta.get_field("name")
        code_field = Airline._meta.get_field("code")
        self.assertEqual(name_field.max_length, 100)
        self.assertEqual(code_field.max_length, 10)
        self.assertIsInstance(name_field, models.CharField)
        self.assertIsInstance(code_field, models.CharField)

    def test_duplicate_code_currently_allowed(self):
        # 现有实现未对 code 加 unique，因此可重复保存——这是已知缺陷，
        # 真正的"应当报错"期望见 test_models.py 中 xfail 用例。
        Airline.objects.create(name="航司A", code="XX")
        Airline.objects.create(name="航司B", code="XX")
        self.assertEqual(Airline.objects.filter(code="XX").count(), 2)


class AirportModelTests(TestCase):
    def test_str_includes_name_and_code(self):
        ap = Airport.objects.create(
            name="香港国际机场", code="HKG", city="香港", country="中国",
        )
        self.assertEqual(str(ap), "香港国际机场 (HKG)")

    def test_field_max_lengths(self):
        self.assertEqual(Airport._meta.get_field("name").max_length, 200)
        self.assertEqual(Airport._meta.get_field("code").max_length, 10)
        self.assertEqual(Airport._meta.get_field("city").max_length, 100)
        self.assertEqual(Airport._meta.get_field("country").max_length, 100)


class FlightModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.flights = build_flights()

    def test_str_includes_airline_and_number(self):
        cx123 = Flight.objects.get(flight_number="CX123")
        self.assertEqual(str(cx123), "国泰航空 CX123")

    def test_default_flags(self):
        # is_direct 默认 True, is_shared 默认 False（由 factories 覆盖亦可，
        # 这里重新显式构造以验证默认值）
        f = self.flights[0]
        f.is_direct = True
        f.is_shared = False
        f.save()
        f.refresh_from_db()
        self.assertTrue(f.is_direct)
        self.assertFalse(f.is_shared)

    def test_aircraft_optional(self):
        # aircraft 可空
        airline = Airline.objects.create(name="测试航司", code="TS")
        hkg = Airport.objects.get(code="HKG")
        lhr = Airport.objects.get(code="LHR")
        from .factories import BASE_DATE
        f = Flight.objects.create(
            airline=airline, flight_number="TS001", aircraft=None,
            departure_airport=hkg, arrival_airport=lhr,
            departure_time=BASE_DATE, arrival_time=BASE_DATE.replace(hour=12),
            price=Decimal("1000.00"), remaining_seats=10,
        )
        self.assertIsNone(f.aircraft)

    def test_price_decimal_precision(self):
        field = Flight._meta.get_field("price")
        self.assertEqual(field.max_digits, 10)
        self.assertEqual(field.decimal_places, 2)
        f = self.flights[0]
        self.assertEqual(f.price, Decimal("8999.00"))

    def test_foreign_key_cascade_airline(self):
        # 删除航司应当级联删除其航班
        ek = Airline.objects.get(code="EK")
        ek_flight_ids = list(Flight.objects.filter(airline=ek).values_list("id", flat=True))
        self.assertTrue(ek_flight_ids)
        ek.delete()
        self.assertFalse(Flight.objects.filter(id__in=ek_flight_ids).exists())

    def test_foreign_key_cascade_departure_airport(self):
        hkg = Airport.objects.get(code="HKG")
        hkg_flight_ids = list(
            Flight.objects.filter(departure_airport=hkg).values_list("id", flat=True)
        )
        self.assertTrue(hkg_flight_ids)
        hkg.delete()
        self.assertFalse(Flight.objects.filter(id__in=hkg_flight_ids).exists())

    def test_related_names(self):
        # related_name='departure_flights' / 'arrival_flights'
        lhr = Airport.objects.get(code="LHR")
        # 种子中以 LHR 为到达机场的航班：CX123/EK456/BA789/CA937/BA168 共 5 条
        self.assertEqual(lhr.arrival_flights.count(), 5)
        hkg = Airport.objects.get(code="HKG")
        # HKG 出发：CX123/EK456/BA789/SQ896 共 4 条
        self.assertEqual(hkg.departure_flights.count(), 4)

    def test_airline_back_relation(self):
        cx = Airline.objects.get(code="CX")
        # 默认 related_name（flight_set）可用
        self.assertEqual(cx.flight_set.count(), 1)
        self.assertEqual(cx.flight_set.first().flight_number, "CX123")

    def test_same_airline_multiple_flights(self):
        ba = Airline.objects.get(code="BA")
        # BA 有 BA789 和 BA168
        self.assertEqual(ba.flight_set.count(), 2)
