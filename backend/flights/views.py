from django.shortcuts import render
from django.http import JsonResponse
from .models import Flight
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime


@csrf_exempt
def flight_list(request):
    if request.method == 'GET':
        # 获取查询参数
        departure_city = request.GET.get('departure_city')
        arrival_city = request.GET.get('arrival_city')
        departure_date = request.GET.get('departure_date')
        
        # 构建查询集
        flights = Flight.objects.all()
        
        # 应用筛选条件
        if departure_city:
            flights = flights.filter(departure_airport__city__icontains=departure_city)
        if arrival_city:
            flights = flights.filter(arrival_airport__city__icontains=arrival_city)
        if departure_date:
            try:
                date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
                # 筛选当天的航班
                flights = flights.filter(
                    departure_time__year=date_obj.year,
                    departure_time__month=date_obj.month,
                    departure_time__day=date_obj.day
                )
            except ValueError:
                pass
        
        # 转换为JSON格式
        flight_data = []
        for flight in flights:
            flight_data.append({
                'id': flight.id,
                'airline': flight.airline.name,
                'flight_number': flight.flight_number,
                'aircraft': flight.aircraft,
                'departure_airport': {
                    'name': flight.departure_airport.name,
                    'code': flight.departure_airport.code,
                    'city': flight.departure_airport.city
                },
                'arrival_airport': {
                    'name': flight.arrival_airport.name,
                    'code': flight.arrival_airport.code,
                    'city': flight.arrival_airport.city
                },
                'departure_time': flight.departure_time.strftime('%Y-%m-%d %H:%M'),
                'arrival_time': flight.arrival_time.strftime('%Y-%m-%d %H:%M'),
                'price': float(flight.price),
                'remaining_seats': flight.remaining_seats,
                'is_direct': flight.is_direct,
                'is_shared': flight.is_shared
            })
        
        return JsonResponse({
            'status': 'success',
            'data': flight_data,
            'count': len(flight_data)
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def flight_detail(request, flight_id):
    try:
        flight = Flight.objects.get(id=flight_id)
        flight_data = {
            'id': flight.id,
            'airline': flight.airline.name,
            'flight_number': flight.flight_number,
            'aircraft': flight.aircraft,
            'departure_airport': {
                'name': flight.departure_airport.name,
                'code': flight.departure_airport.code,
                'city': flight.departure_airport.city,
                'country': flight.departure_airport.country
            },
            'arrival_airport': {
                'name': flight.arrival_airport.name,
                'code': flight.arrival_airport.code,
                'city': flight.arrival_airport.city,
                'country': flight.arrival_airport.country
            },
            'departure_time': flight.departure_time.strftime('%Y-%m-%d %H:%M'),
            'arrival_time': flight.arrival_time.strftime('%Y-%m-%d %H:%M'),
            'price': float(flight.price),
            'remaining_seats': flight.remaining_seats,
            'is_direct': flight.is_direct,
            'is_shared': flight.is_shared
        }
        return JsonResponse({'status': 'success', 'data': flight_data})
    except Flight.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Flight not found'}, status=404)
