"""轻量测试数据工厂（不引入第三方依赖）。"""

from datetime import datetime, timedelta

from django.utils import timezone

from flights.models import Airline, Airport, Flight

# 固定基准时间，使排序/日期断言可预测（使用带时区的时间避免 USE_TZ 告警）
BASE_TIME = timezone.make_aware(datetime(2026, 8, 1, 9, 0, 0))


def make_airline(name="国泰航空", code="CX", logo=None):
    return Airline.objects.create(name=name, code=code, logo=logo)


def make_airport(name="香港国际机场", code="HKG", city="香港", country="中国"):
    return Airport.objects.create(name=name, code=code, city=city, country=country)


def make_flight(
    airline=None,
    departure_airport=None,
    arrival_airport=None,
    flight_number="CX123",
    aircraft="波音777",
    departure_time=None,
    arrival_time=None,
    price="8999.00",
    remaining_seats=5,
    is_direct=True,
    is_shared=False,
):
    airline = airline or make_airline()
    departure_airport = departure_airport or make_airport()
    arrival_airport = arrival_airport or make_airport(
        name="伦敦希思罗机场", code="LHR", city="伦敦", country="英国"
    )
    departure_time = departure_time or BASE_TIME
    arrival_time = arrival_time or (departure_time + timedelta(hours=12, minutes=30))
    return Flight.objects.create(
        airline=airline,
        flight_number=flight_number,
        aircraft=aircraft,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=departure_time,
        arrival_time=arrival_time,
        price=price,
        remaining_seats=remaining_seats,
        is_direct=is_direct,
        is_shared=is_shared,
    )


def seed_flights():
    """构造一份与 init_data.py 结构一致、但时间/价格可预测的种子数据。

    返回 dict 便于测试引用具体对象。
    """
    cx = make_airline("国泰航空", "CX")
    ek = make_airline("阿联酋航空", "EK")
    ba = make_airline("英国航空", "BA")
    ca = make_airline("中国国际航空", "CA")
    sq = make_airline("新加坡航空", "SQ")

    hkg = make_airport("香港国际机场", "HKG", "香港", "中国")
    lhr = make_airport("伦敦希思罗机场", "LHR", "伦敦", "英国")
    pek = make_airport("北京首都国际机场", "PEK", "北京", "中国")
    pvg = make_airport("上海浦东国际机场", "PVG", "上海", "中国")
    sin = make_airport("新加坡樟宜机场", "SIN", "新加坡", "新加坡")

    flights = {
        "cx_hkg_lhr": make_flight(
            airline=cx, departure_airport=hkg, arrival_airport=lhr,
            flight_number="CX123", price="8999.00", remaining_seats=5,
            is_direct=True, is_shared=False,
            departure_time=BASE_TIME + timedelta(hours=9),
        ),
        "ek_hkg_lhr": make_flight(
            airline=ek, departure_airport=hkg, arrival_airport=lhr,
            flight_number="EK456", price="7999.00", remaining_seats=8,
            is_direct=False, is_shared=False,
            departure_time=BASE_TIME + timedelta(hours=10, minutes=30),
        ),
        "ba_hkg_lhr": make_flight(
            airline=ba, departure_airport=hkg, arrival_airport=lhr,
            flight_number="BA789", price="9499.00", remaining_seats=3,
            is_direct=True, is_shared=True,
            departure_time=BASE_TIME + timedelta(hours=12),
        ),
        "ca_pek_lhr": make_flight(
            airline=ca, departure_airport=pek, arrival_airport=lhr,
            flight_number="CA937", price="9999.00", remaining_seats=2,
            is_direct=True, is_shared=False,
            departure_time=BASE_TIME + timedelta(hours=13),
        ),
        "ba_pvg_lhr": make_flight(
            airline=ba, departure_airport=pvg, arrival_airport=lhr,
            flight_number="BA168", price="10499.00", remaining_seats=4,
            is_direct=True, is_shared=False,
            departure_time=BASE_TIME + timedelta(hours=11),
        ),
        "sq_hkg_sin": make_flight(
            airline=sq, departure_airport=hkg, arrival_airport=sin,
            flight_number="SQ896", price="2999.00", remaining_seats=10,
            is_direct=True, is_shared=False,
            departure_time=BASE_TIME + timedelta(hours=8),
        ),
    }
    return flights
