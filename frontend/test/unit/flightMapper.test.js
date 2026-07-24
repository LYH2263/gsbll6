import { describe, it, expect } from 'vitest';
import {
  computeDuration,
  mapBackendFlight,
  mapBackendFlights,
} from '../../src/utils/flightMapper.js';

describe('computeDuration', () => {
  it('整小时差返回 Xh 0m', () => {
    const dep = '2026-08-02T08:00:00';
    const arr = '2026-08-02T12:00:00';
    expect(computeDuration(dep, arr)).toBe('4h 0m');
  });

  it('带分钟时差返回 Xh Ym', () => {
    const dep = '2026-08-02T09:00:00';
    const arr = '2026-08-02T21:30:00';
    expect(computeDuration(dep, arr)).toBe('12h 30m');
  });

  it('分钟截断而非四舍五入', () => {
    const dep = '2026-08-02T08:00:00';
    const arr = '2026-08-02T09:01:59';
    expect(computeDuration(dep, arr)).toBe('1h 1m');
  });

  it('到达早于出发时返回 0h 0m（防御）', () => {
    const dep = '2026-08-02T12:00:00';
    const arr = '2026-08-02T08:00:00';
    expect(computeDuration(dep, arr)).toBe('0h 0m');
  });

  it('非法日期返回 0h 0m', () => {
    expect(computeDuration('not-a-date', '2026-08-02T08:00:00')).toBe('0h 0m');
  });
});

describe('mapBackendFlight', () => {
  const sample = {
    id: 1,
    airline: '国泰航空',
    flight_number: 'CX123',
    aircraft: '波音777',
    departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
    arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
    departure_time: '2026-08-02T09:00:00',
    arrival_time: '2026-08-02T21:30:00',
    price: 8999.0,
    remaining_seats: 5,
    is_direct: true,
    is_shared: false,
  };

  it('字段名从 snake_case 映射为 camelCase', () => {
    const vm = mapBackendFlight(sample);
    expect(vm.flightNumber).toBe('CX123');
    expect(vm.remainingSeats).toBe(5);
    expect(vm.isDirect).toBe(true);
    expect(vm.isShared).toBe(false);
  });

  it('机场展示为 "名称 (代码)"', () => {
    const vm = mapBackendFlight(sample);
    expect(vm.departureAirport).toBe('香港国际机场 (HKG)');
    expect(vm.arrivalAirport).toBe('伦敦希思罗机场 (LHR)');
  });

  it('route 标志：直飞 -> 直飞，中转 -> 中转', () => {
    expect(mapBackendFlight({ ...sample, is_direct: true }).route).toBe('直飞');
    expect(mapBackendFlight({ ...sample, is_direct: false }).route).toBe('中转');
  });

  it('时长由 departure/arrival 计算', () => {
    const vm = mapBackendFlight(sample);
    expect(vm.duration).toBe('12h 30m');
  });

  it('含税价展示依赖原始 price 字段，原样透传', () => {
    // 模板里 "¥{{ flight.price }}" + "含税"，原始字段必须保留为数字
    const vm = mapBackendFlight(sample);
    expect(vm.price).toBe(8999.0);
    expect(typeof vm.price).toBe('number');
  });

  it('aircraft 为 null 时透传 null', () => {
    const vm = mapBackendFlight({ ...sample, aircraft: null });
    expect(vm.aircraft).toBeNull();
  });

  it('批量映射保持顺序', () => {
    const list = mapBackendFlights([sample, { ...sample, id: 2, flight_number: 'XX' }]);
    expect(list).toHaveLength(2);
    expect(list[0].id).toBe(1);
    expect(list[1].flightNumber).toBe('XX');
  });
});
