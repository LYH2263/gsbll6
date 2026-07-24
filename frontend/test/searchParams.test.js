import { describe, it, expect } from 'vitest';
import {
  buildBaseParams,
  buildFilterParams,
  buildSortParams,
  filterCitySuggestions
} from '../src/utils/searchParams.js';

const search = {
  departureCity: '香港',
  arrivalCity: '伦敦',
  departureDate: '2026-08-01'
};

describe('buildBaseParams', () => {
  it('映射基础查询字段', () => {
    expect(buildBaseParams(search)).toEqual({
      departure_city: '香港',
      arrival_city: '伦敦',
      departure_date: '2026-08-01'
    });
  });
});

describe('buildFilterParams', () => {
  it('direct 追加 is_direct=true', () => {
    expect(buildFilterParams(search, 'direct')).toMatchObject({ is_direct: true });
  });
  it('transfer 追加 is_direct=false', () => {
    expect(buildFilterParams(search, 'transfer')).toMatchObject({ is_direct: false });
  });
  it('shared 追加 is_shared=true', () => {
    expect(buildFilterParams(search, 'shared')).toMatchObject({ is_shared: true });
  });
  it('all 不追加筛选字段', () => {
    const params = buildFilterParams(search, 'all');
    expect(params).not.toHaveProperty('is_direct');
    expect(params).not.toHaveProperty('is_shared');
  });
});

describe('buildSortParams', () => {
  it('price_asc -> ordering=price', () => {
    expect(buildSortParams(search, 'price_asc').ordering).toBe('price');
  });
  it('time -> ordering=departure_time', () => {
    expect(buildSortParams(search, 'time').ordering).toBe('departure_time');
  });
  it('airline -> ordering=airline', () => {
    expect(buildSortParams(search, 'airline').ordering).toBe('airline');
  });
  it('未知排序不追加 ordering', () => {
    expect(buildSortParams(search, 'unknown')).not.toHaveProperty('ordering');
  });
});

describe('filterCitySuggestions', () => {
  const cities = ['北京', '上海', '香港', '南京', '东京'];
  it('空输入返回空数组', () => {
    expect(filterCitySuggestions(cities, '')).toEqual([]);
  });
  it('按子串匹配（"京" 命中多城市）', () => {
    expect(filterCitySuggestions(cities, '京')).toEqual(['北京', '南京', '东京']);
  });
  it('无匹配返回空数组', () => {
    expect(filterCitySuggestions(cities, '巴黎')).toEqual([]);
  });
});
