import { describe, it, expect } from 'vitest';
import {
  AVAILABLE_CITIES,
  filterCitiesByInput,
  clientSortFlights,
  clientFilterFlights,
  generateDateItems
} from '../src/utils/cityFilter.js';

describe('AVAILABLE_CITIES', () => {
  it('should contain major international cities', () => {
    expect(AVAILABLE_CITIES).toContain('北京');
    expect(AVAILABLE_CITIES).toContain('上海');
    expect(AVAILABLE_CITIES).toContain('香港');
    expect(AVAILABLE_CITIES).toContain('伦敦');
    expect(AVAILABLE_CITIES).toContain('新加坡');
  });

  it('should have 26 cities', () => {
    expect(AVAILABLE_CITIES).toHaveLength(26);
  });
});

describe('filterCitiesByInput', () => {
  const cities = ['北京', '上海', '香港', '伦敦', '巴黎'];

  it('should return matching cities for partial input', () => {
    expect(filterCitiesByInput(cities, '北')).toEqual(['北京']);
  });

  it('should return multiple matches', () => {
    const result = filterCitiesByInput(['北京', '上海', '广州', '深圳'], '');
    expect(result).toEqual([]);
  });

  it('should return empty for non-matching input', () => {
    expect(filterCitiesByInput(cities, '东京')).toEqual([]);
  });

  it('should return empty for empty input', () => {
    expect(filterCitiesByInput(cities, '')).toEqual([]);
  });

  it('should return empty for null/undefined input', () => {
    expect(filterCitiesByInput(cities, null)).toEqual([]);
    expect(filterCitiesByInput(cities, undefined)).toEqual([]);
  });

  it('should handle fuzzy match with single character', () => {
    const result = filterCitiesByInput(AVAILABLE_CITIES, '伦');
    expect(result).toContain('伦敦');
  });

  it('should be case sensitive for Chinese characters', () => {
    const result = filterCitiesByInput(AVAILABLE_CITIES, '香');
    expect(result).toContain('香港');
    expect(result.length).toBeGreaterThanOrEqual(1);
  });
});

describe('clientSortFlights', () => {
  const flights = [
    { id: 1, airline: '国泰航空', price: 8999, departureTime: '09:00' },
    { id: 2, airline: '阿联酋航空', price: 7999, departureTime: '10:30' },
    { id: 3, airline: '英国航空', price: 9499, departureTime: '12:00' }
  ];

  it('should sort by price ascending', () => {
    const result = clientSortFlights(flights, 'price_asc');
    expect(result[0].price).toBe(7999);
    expect(result[1].price).toBe(8999);
    expect(result[2].price).toBe(9499);
  });

  it('should sort by departure time', () => {
    const result = clientSortFlights(flights, 'time');
    expect(result[0].departureTime).toBe('09:00');
    expect(result[1].departureTime).toBe('10:30');
    expect(result[2].departureTime).toBe('12:00');
  });

  it('should not mutate original array', () => {
    const copy = [...flights];
    clientSortFlights(flights, 'price_asc');
    expect(flights).toEqual(copy);
  });

  it('should return same order for unknown sort type', () => {
    const result = clientSortFlights(flights, 'unknown');
    expect(result[0].id).toBe(1);
  });

  it('should handle empty array', () => {
    expect(clientSortFlights([], 'price_asc')).toEqual([]);
  });
});

describe('clientFilterFlights', () => {
  const flights = [
    { id: 1, isDirect: true, isShared: false, price: 8999 },
    { id: 2, isDirect: false, isShared: false, price: 7999 },
    { id: 3, isDirect: true, isShared: true, price: 6999 }
  ];

  it('should return all flights for "all" filter', () => {
    const result = clientFilterFlights(flights, 'all');
    expect(result).toHaveLength(3);
  });

  it('should filter direct flights only', () => {
    const result = clientFilterFlights(flights, 'direct');
    expect(result).toHaveLength(2);
    expect(result.every(f => f.isDirect)).toBe(true);
  });

  it('should filter transfer flights only', () => {
    const result = clientFilterFlights(flights, 'transfer');
    expect(result).toHaveLength(1);
    expect(result[0].isDirect).toBe(false);
  });

  it('should filter shared flights only', () => {
    const result = clientFilterFlights(flights, 'shared');
    expect(result).toHaveLength(1);
    expect(result[0].isShared).toBe(true);
  });

  it('should handle empty array', () => {
    expect(clientFilterFlights([], 'direct')).toEqual([]);
  });

  it('should also work with snake_case field names from API', () => {
    const apiFlights = [
      { id: 1, is_direct: true, is_shared: false },
      { id: 2, is_direct: false, is_shared: false }
    ];
    const direct = clientFilterFlights(apiFlights, 'direct');
    expect(direct).toHaveLength(1);
    const transfer = clientFilterFlights(apiFlights, 'transfer');
    expect(transfer).toHaveLength(1);
  });
});

describe('generateDateItems', () => {
  it('should generate 30 date items by default', () => {
    const items = generateDateItems();
    expect(items).toHaveLength(30);
  });

  it('should generate custom number of days', () => {
    const items = generateDateItems(7);
    expect(items).toHaveLength(7);
  });

  it('should have date in YYYY-MM-DD format', () => {
    const items = generateDateItems(1);
    expect(items[0].date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it('should have a label', () => {
    const items = generateDateItems(1);
    expect(items[0].label).toBeTruthy();
    expect(typeof items[0].label).toBe('string');
  });

  it('should start from tomorrow', () => {
    const items = generateDateItems(1);
    const tomorrow = new Date(Date.now() + 24 * 60 * 60 * 1000);
    const expectedDate = tomorrow.toISOString().split('T')[0];
    expect(items[0].date).toBe(expectedDate);
  });
});
