import { describe, it, expect } from 'vitest';
import {
  calculateDuration,
  formatTime,
  formatAirportName,
  adaptFlightFromApi,
  adaptFlightsFromApi,
  buildSearchParams,
  buildFilterParams,
  buildSortParams
} from '../src/utils/flightAdapter.js';

describe('calculateDuration', () => {
  it('should calculate duration correctly for whole hours', () => {
    const dep = '2024-01-15T09:00:00';
    const arr = '2024-01-15T21:00:00';
    expect(calculateDuration(dep, arr)).toBe('12h 0m');
  });

  it('should calculate duration with hours and minutes', () => {
    const dep = '2024-01-15T09:00:00';
    const arr = '2024-01-15T21:30:00';
    expect(calculateDuration(dep, arr)).toBe('12h 30m');
  });

  it('should handle zero minutes', () => {
    const dep = '2024-01-15T10:00:00';
    const arr = '2024-01-15T12:00:00';
    expect(calculateDuration(dep, arr)).toBe('2h 0m');
  });

  it('should handle less than an hour', () => {
    const dep = '2024-01-15T10:00:00';
    const arr = '2024-01-15T10:45:00';
    expect(calculateDuration(dep, arr)).toBe('0h 45m');
  });
});

describe('formatTime', () => {
  it('should format datetime to HH:MM in zh-CN locale', () => {
    const result = formatTime('2024-01-15T09:30:00');
    expect(result).toMatch(/\d{2}:\d{2}/);
  });
});

describe('formatAirportName', () => {
  it('should format airport with name and code', () => {
    const airport = { name: '香港国际机场', code: 'HKG' };
    expect(formatAirportName(airport)).toBe('香港国际机场 (HKG)');
  });

  it('should handle different airports', () => {
    const airport = { name: '伦敦希思罗机场', code: 'LHR' };
    expect(formatAirportName(airport)).toBe('伦敦希思罗机场 (LHR)');
  });
});

describe('adaptFlightFromApi', () => {
  const apiFlight = {
    id: 1,
    airline: '国泰航空',
    flight_number: 'CX123',
    aircraft: '波音777',
    departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
    arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
    departure_time: '2024-01-15 09:00',
    arrival_time: '2024-01-15 21:30',
    price: 8999.00,
    remaining_seats: 5,
    is_direct: true,
    is_shared: false
  };

  it('should map all fields correctly', () => {
    const result = adaptFlightFromApi(apiFlight);
    expect(result.id).toBe(1);
    expect(result.airline).toBe('国泰航空');
    expect(result.flightNumber).toBe('CX123');
    expect(result.aircraft).toBe('波音777');
    expect(result.price).toBe(8999.00);
    expect(result.remainingSeats).toBe(5);
    expect(result.isDirect).toBe(true);
    expect(result.isShared).toBe(false);
  });

  it('should transform airport names', () => {
    const result = adaptFlightFromApi(apiFlight);
    expect(result.departureAirport).toBe('香港国际机场 (HKG)');
    expect(result.arrivalAirport).toBe('伦敦希思罗机场 (LHR)');
  });

  it('should calculate route type', () => {
    const direct = adaptFlightFromApi(apiFlight);
    expect(direct.route).toBe('直飞');

    const transfer = adaptFlightFromApi({ ...apiFlight, is_direct: false });
    expect(transfer.route).toBe('中转');
  });

  it('should calculate duration', () => {
    const result = adaptFlightFromApi(apiFlight);
    expect(result.duration).toMatch(/^\d+h \d+m$/);
  });

  it('should format time fields', () => {
    const result = adaptFlightFromApi(apiFlight);
    expect(result.departureTime).toMatch(/\d{2}:\d{2}/);
    expect(result.arrivalTime).toMatch(/\d{2}:\d{2}/);
  });

  it('should preserve price as number for tax display', () => {
    const result = adaptFlightFromApi(apiFlight);
    expect(typeof result.price).toBe('number');
    expect(result.price).toBe(8999.00);
  });
});

describe('adaptFlightsFromApi', () => {
  it('should adapt an array of flights', () => {
    const apiFlights = [
      {
        id: 1, airline: '国泰航空', flight_number: 'CX123', aircraft: '波音777',
        departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
        arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
        departure_time: '2024-01-15 09:00', arrival_time: '2024-01-15 21:30',
        price: 8999.00, remaining_seats: 5, is_direct: true, is_shared: false
      },
      {
        id: 2, airline: '阿联酋航空', flight_number: 'EK456', aircraft: '空客A380',
        departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
        arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
        departure_time: '2024-01-15 10:30', arrival_time: '2024-01-15 22:45',
        price: 7999.00, remaining_seats: 8, is_direct: false, is_shared: false
      }
    ];
    const result = adaptFlightsFromApi(apiFlights);
    expect(result).toHaveLength(2);
    expect(result[0].flightNumber).toBe('CX123');
    expect(result[1].flightNumber).toBe('EK456');
  });

  it('should handle empty array', () => {
    expect(adaptFlightsFromApi([])).toEqual([]);
  });
});

describe('buildSearchParams', () => {
  it('should build params from search inputs', () => {
    const searchParams = {
      departureCity: '香港',
      arrivalCity: '伦敦',
      departureDate: '2024-01-15'
    };
    const result = buildSearchParams(searchParams);
    expect(result).toEqual({
      departure_city: '香港',
      arrival_city: '伦敦',
      departure_date: '2024-01-15'
    });
  });

  it('should omit empty values as undefined', () => {
    const searchParams = {
      departureCity: '',
      arrivalCity: '',
      departureDate: ''
    };
    const result = buildSearchParams(searchParams);
    expect(result.departure_city).toBeUndefined();
    expect(result.arrival_city).toBeUndefined();
    expect(result.departure_date).toBeUndefined();
  });

  it('should handle partial inputs', () => {
    const searchParams = {
      departureCity: '北京',
      arrivalCity: '',
      departureDate: ''
    };
    const result = buildSearchParams(searchParams);
    expect(result.departure_city).toBe('北京');
    expect(result.arrival_city).toBeUndefined();
  });
});

describe('buildFilterParams', () => {
  const baseParams = {
    departureCity: '香港',
    arrivalCity: '伦敦',
    departureDate: '2024-01-15'
  };

  it('should add is_direct=true for direct filter', () => {
    const result = buildFilterParams(baseParams, 'direct');
    expect(result.is_direct).toBe(true);
  });

  it('should add is_direct=false for transfer filter', () => {
    const result = buildFilterParams(baseParams, 'transfer');
    expect(result.is_direct).toBe(false);
  });

  it('should add is_shared=true for shared filter', () => {
    const result = buildFilterParams(baseParams, 'shared');
    expect(result.is_shared).toBe(true);
  });

  it('should not add filter params for all', () => {
    const result = buildFilterParams(baseParams, 'all');
    expect(result.is_direct).toBeUndefined();
    expect(result.is_shared).toBeUndefined();
  });
});

describe('buildSortParams', () => {
  const baseParams = {
    departureCity: '香港',
    arrivalCity: '伦敦',
    departureDate: '2024-01-15'
  };

  it('should add ordering=price for price_asc', () => {
    const result = buildSortParams(baseParams, 'price_asc');
    expect(result.ordering).toBe('price');
  });

  it('should add ordering=departure_time for time', () => {
    const result = buildSortParams(baseParams, 'time');
    expect(result.ordering).toBe('departure_time');
  });

  it('should add ordering=airline for airline', () => {
    const result = buildSortParams(baseParams, 'airline');
    expect(result.ordering).toBe('airline');
  });
});
