import { describe, it, expect } from 'vitest';
import { formatDuration, mapFlight, mapFlights } from '../src/utils/flightMapper.js';

const rawFlight = {
  id: 1,
  airline: '国泰航空',
  flight_number: 'CX123',
  aircraft: '波音777',
  departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
  arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
  departure_time: '2026-08-01 09:00',
  arrival_time: '2026-08-01 21:30',
  price: 8999.0,
  remaining_seats: 5,
  is_direct: true,
  is_shared: false
};

describe('formatDuration', () => {
  it('计算小时与分钟差（时区无关）', () => {
    const dep = new Date('2026-08-01T09:00:00');
    const arr = new Date('2026-08-01T21:30:00');
    expect(formatDuration(dep, arr)).toBe('12h 30m');
  });
  it('跨天时长', () => {
    const dep = new Date('2026-08-01T22:00:00');
    const arr = new Date('2026-08-02T01:15:00');
    expect(formatDuration(dep, arr)).toBe('3h 15m');
  });
});

describe('mapFlight', () => {
  const mapped = mapFlight(rawFlight);
  it('保留 id / 航司 / 机型', () => {
    expect(mapped.id).toBe(1);
    expect(mapped.airline).toBe('国泰航空');
    expect(mapped.aircraft).toBe('波音777');
  });
  it('snake_case 转 camelCase 字段', () => {
    expect(mapped.flightNumber).toBe('CX123');
    expect(mapped.remainingSeats).toBe(5);
    expect(mapped.isDirect).toBe(true);
    expect(mapped.isShared).toBe(false);
  });
  it('机场拼接 名称+代码', () => {
    expect(mapped.departureAirport).toBe('香港国际机场 (HKG)');
    expect(mapped.arrivalAirport).toBe('伦敦希思罗机场 (LHR)');
  });
  it('直飞/中转文案', () => {
    expect(mapped.route).toBe('直飞');
    expect(mapFlight({ ...rawFlight, is_direct: false }).route).toBe('中转');
  });
  it('保留原始含税价字段（用于 ¥{amount} 含税 展示）', () => {
    // price 原样透传，供含税价展示依赖
    expect(mapped.price).toBe(8999.0);
  });
  it('时长字段存在且为 h/m 文案', () => {
    expect(mapped.duration).toMatch(/^\d+h \d+m$/);
  });
});

describe('mapFlights', () => {
  it('批量映射', () => {
    expect(mapFlights([rawFlight, { ...rawFlight, id: 2 }])).toHaveLength(2);
  });
  it('空/undefined 安全返回空数组', () => {
    expect(mapFlights([])).toEqual([]);
    expect(mapFlights(undefined)).toEqual([]);
  });
});
