export function calculateDuration(departureTime, arrivalTime) {
  const departureDateTime = new Date(departureTime);
  const arrivalDateTime = new Date(arrivalTime);
  const durationMs = arrivalDateTime - departureDateTime;
  const hours = Math.floor(durationMs / (1000 * 60 * 60));
  const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
  return `${hours}h ${minutes}m`;
}

export function formatTime(dateTimeStr) {
  const dateTime = new Date(dateTimeStr);
  return dateTime.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

export function formatAirportName(airport) {
  return `${airport.name} (${airport.code})`;
}

export function adaptFlightFromApi(flight) {
  const duration = calculateDuration(flight.departure_time, flight.arrival_time);
  return {
    id: flight.id,
    airline: flight.airline,
    flightNumber: flight.flight_number,
    aircraft: flight.aircraft,
    departureTime: formatTime(flight.departure_time),
    departureAirport: formatAirportName(flight.departure_airport),
    arrivalTime: formatTime(flight.arrival_time),
    arrivalAirport: formatAirportName(flight.arrival_airport),
    duration: duration,
    route: flight.is_direct ? '直飞' : '中转',
    price: flight.price,
    remainingSeats: flight.remaining_seats,
    isDirect: flight.is_direct,
    isShared: flight.is_shared
  };
}

export function adaptFlightsFromApi(apiFlights) {
  return apiFlights.map(adaptFlightFromApi);
}

export function buildSearchParams(searchParams) {
  return {
    departure_city: searchParams.departureCity || undefined,
    arrival_city: searchParams.arrivalCity || undefined,
    departure_date: searchParams.departureDate || undefined
  };
}

export function buildFilterParams(searchParams, filterType) {
  const params = buildSearchParams(searchParams);
  if (filterType === 'direct') {
    params.is_direct = true;
  } else if (filterType === 'transfer') {
    params.is_direct = false;
  } else if (filterType === 'shared') {
    params.is_shared = true;
  }
  return params;
}

export function buildSortParams(searchParams, sortType) {
  const params = buildSearchParams(searchParams);
  if (sortType === 'price_asc') {
    params.ordering = 'price';
  } else if (sortType === 'time') {
    params.ordering = 'departure_time';
  } else if (sortType === 'airline') {
    params.ordering = 'airline';
  }
  return params;
}
