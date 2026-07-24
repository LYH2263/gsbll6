#!/usr/bin/env python3
"""
初始化测试数据脚本
"""

import os
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_booking.settings')
django.setup()

from flights.models import Airline, Airport, Flight


def init_data():
    """初始化测试数据"""
    print("开始初始化测试数据...")
    
    # 创建航空公司
    airlines = [
        Airline(name="国泰航空", code="CX"),
        Airline(name="阿联酋航空", code="EK"),
        Airline(name="英国航空", code="BA"),
        Airline(name="中国国际航空", code="CA"),
        Airline(name="新加坡航空", code="SQ")
    ]
    
    for airline in airlines:
        airline.save()
        print(f"创建航空公司: {airline.name}")
    
    # 创建机场
    airports = [
        Airport(name="香港国际机场", code="HKG", city="香港", country="中国"),
        Airport(name="伦敦希思罗机场", code="LHR", city="伦敦", country="英国"),
        Airport(name="北京首都国际机场", code="PEK", city="北京", country="中国"),
        Airport(name="上海浦东国际机场", code="PVG", city="上海", country="中国"),
        Airport(name="新加坡樟宜机场", code="SIN", city="新加坡", country="新加坡"),
        Airport(name="迪拜国际机场", code="DXB", city="迪拜", country="阿联酋")
    ]
    
    for airport in airports:
        airport.save()
        print(f"创建机场: {airport.name}")
    
    # 获取创建的航空公司和机场
    cx = Airline.objects.get(code="CX")
    ek = Airline.objects.get(code="EK")
    ba = Airline.objects.get(code="BA")
    ca = Airline.objects.get(code="CA")
    sq = Airline.objects.get(code="SQ")
    
    hkg = Airport.objects.get(code="HKG")
    lhr = Airport.objects.get(code="LHR")
    pek = Airport.objects.get(code="PEK")
    pvg = Airport.objects.get(code="PVG")
    sin = Airport.objects.get(code="SIN")
    dxb = Airport.objects.get(code="DXB")
    
    # 创建航班数据
    flights = [
        # 香港到伦敦
        Flight(
            airline=cx,
            flight_number="CX123",
            aircraft="波音777",
            departure_airport=hkg,
            arrival_airport=lhr,
            departure_time=datetime.now() + timedelta(days=1, hours=9),
            arrival_time=datetime.now() + timedelta(days=1, hours=21, minutes=30),
            price=8999.00,
            remaining_seats=5,
            is_direct=True,
            is_shared=False
        ),
        Flight(
            airline=ek,
            flight_number="EK456",
            aircraft="空客A380",
            departure_airport=hkg,
            arrival_airport=lhr,
            departure_time=datetime.now() + timedelta(days=1, hours=10, minutes=30),
            arrival_time=datetime.now() + timedelta(days=1, hours=22, minutes=45),
            price=7999.00,
            remaining_seats=8,
            is_direct=False,
            is_shared=False
        ),
        Flight(
            airline=ba,
            flight_number="BA789",
            aircraft="波音787",
            departure_airport=hkg,
            arrival_airport=lhr,
            departure_time=datetime.now() + timedelta(days=1, hours=12),
            arrival_time=datetime.now() + timedelta(days=1, hours=20),
            price=9499.00,
            remaining_seats=3,
            is_direct=True,
            is_shared=False
        ),
        # 北京到伦敦
        Flight(
            airline=ca,
            flight_number="CA937",
            aircraft="波音747",
            departure_airport=pek,
            arrival_airport=lhr,
            departure_time=datetime.now() + timedelta(days=1, hours=13),
            arrival_time=datetime.now() + timedelta(days=1, hours=17),
            price=9999.00,
            remaining_seats=2,
            is_direct=True,
            is_shared=False
        ),
        # 上海到伦敦
        Flight(
            airline=ba,
            flight_number="BA168",
            aircraft="波音787",
            departure_airport=pvg,
            arrival_airport=lhr,
            departure_time=datetime.now() + timedelta(days=1, hours=11),
            arrival_time=datetime.now() + timedelta(days=1, hours=16),
            price=10499.00,
            remaining_seats=4,
            is_direct=True,
            is_shared=False
        ),
        # 香港到新加坡
        Flight(
            airline=sq,
            flight_number="SQ896",
            aircraft="空客A350",
            departure_airport=hkg,
            arrival_airport=sin,
            departure_time=datetime.now() + timedelta(days=1, hours=8),
            arrival_time=datetime.now() + timedelta(days=1, hours=12),
            price=2999.00,
            remaining_seats=10,
            is_direct=True,
            is_shared=False
        )
    ]
    
    for flight in flights:
        flight.save()
        print(f"创建航班: {flight.airline} {flight.flight_number} - {flight.departure_airport.city} to {flight.arrival_airport.city}")
    
    print("测试数据初始化完成!")


if __name__ == "__main__":
    init_data()
