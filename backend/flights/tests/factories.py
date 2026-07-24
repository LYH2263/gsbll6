"""
测试夹具（fixtures）与工厂函数。

刻意使用固定的日期时间（而非 ``datetime.now()``），保证断言稳定、可重复。
数据与 ``init_data.py`` 的种子结构一一对应（5 家航司 / 6 个机场 / 6 个航班），
方便在集成测中对种子数据做端到端断言。
"""

from datetime import datetime

from flights.models import Airline, Airport, Flight


# 固定基准日：2026-08-01（未来日期，避免与"过去航班"业务语义冲突）
BASE_DATE = datetime(2026, 8, 1, 0, 0, 0)


AIRLINES_DATA = [
    {"name": "国泰航空", "code": "CX"},
    {"name": "阿联酋航空", "code": "EK"},
    {"name": "英国航空", "code": "BA"},
    {"name": "中国国际航空", "code": "CA"},
    {"name": "新加坡航空", "code": "SQ"},
]

AIRPORTS_DATA = [
    {"name": "香港国际机场", "code": "HKG", "city": "香港", "country": "中国"},
    {"name": "伦敦希思罗机场", "code": "LHR", "city": "伦敦", "country": "英国"},
    {"name": "北京首都国际机场", "code": "PEK", "city": "北京", "country": "中国"},
    {"name": "上海浦东国际机场", "code": "PVG", "city": "上海", "country": "中国"},
    {"name": "新加坡樟宜机场", "code": "SIN", "city": "新加坡", "country": "新加坡"},
    {"name": "迪拜国际机场", "code": "DXB", "city": "迪拜", "country": "阿联酋"},
]


def build_airlines():
    return [Airline.objects.create(**a) for a in AIRLINES_DATA]


def build_airports():
    return [Airport.objects.create(**a) for a in AIRPORTS_DATA]


def build_flights():
    """
    与 init_data.py 同构的 6 条航班，但起飞日期固定为 2026-08-02，
    价格、余票、直飞标志与种子数据完全一致。
    """
    airlines = {a.code: a for a in build_airlines()}
    airports = {a.code: a for a in build_airports()}

    flights_spec = [
        # 香港 -> 伦敦
        ("CX", "CX123", "波音777", "HKG", "LHR", (9, 0), (21, 30), 8999.00, 5, True, False),
        ("EK", "EK456", "空客A380", "HKG", "LHR", (10, 30), (22, 45), 7999.00, 8, False, False),
        ("BA", "BA789", "波音787", "HKG", "LHR", (12, 0), (20, 0), 9499.00, 3, True, False),
        # 北京 -> 伦敦
        ("CA", "CA937", "波音747", "PEK", "LHR", (13, 0), (17, 0), 9999.00, 2, True, False),
        # 上海 -> 伦敦
        ("BA", "BA168", "波音787", "PVG", "LHR", (11, 0), (16, 0), 10499.00, 4, True, False),
        # 香港 -> 新加坡
        ("SQ", "SQ896", "空客A350", "HKG", "SIN", (8, 0), (12, 0), 2999.00, 10, True, False),
    ]

    objs = []
    for (
        airline_code, flight_number, aircraft, dep_code, arr_code,
        dep_hm, arr_hm, price, seats, is_direct, is_shared,
    ) in flights_spec:
        dep_dt = BASE_DATE.replace(day=2, hour=dep_hm[0], minute=dep_hm[1])
        arr_dt = BASE_DATE.replace(day=2, hour=arr_hm[0], minute=arr_hm[1])
        objs.append(Flight.objects.create(
            airline=airlines[airline_code],
            flight_number=flight_number,
            aircraft=aircraft,
            departure_airport=airports[dep_code],
            arrival_airport=airports[arr_code],
            departure_time=dep_dt,
            arrival_time=arr_dt,
            price=price,
            remaining_seats=seats,
            is_direct=is_direct,
            is_shared=is_shared,
        ))
    return objs
