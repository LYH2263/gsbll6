import { describe, it, expect } from 'vitest';
import {
  buildBaseParams,
  applyFilterType,
  applySortType,
  buildQueryParams,
  suggestCities,
} from '../../src/utils/searchParams.js';

describe('buildBaseParams', () => {
  it('把 UI 字段翻译成后端 snake_case 参数', () => {
    expect(buildBaseParams({
      departureCity: '香港',
      arrivalCity: '伦敦',
      departureDate: '2026-08-02',
    })).toEqual({
      departure_city: '香港',
      arrival_city: '伦敦',
      departure_date: '2026-08-02',
    });
  });

  it('空字段回退为空字符串而非 undefined', () => {
    const p = buildBaseParams({});
    expect(p.departure_city).toBe('');
    expect(p.arrival_city).toBe('');
    expect(p.departure_date).toBe('');
  });
});

describe('applyFilterType', () => {
  const base = { departure_city: '香港' };

  it('all 不追加任何筛选参数', () => {
    expect(applyFilterType(base, 'all')).toEqual({ departure_city: '香港' });
  });

  it('direct 追加 is_direct=true', () => {
    expect(applyFilterType(base, 'direct')).toEqual({
      departure_city: '香港',
      is_direct: true,
    });
  });

  it('transfer 追加 is_direct=false', () => {
    expect(applyFilterType(base, 'transfer')).toEqual({
      departure_city: '香港',
      is_direct: false,
    });
  });

  it('shared 追加 is_shared=true', () => {
    expect(applyFilterType(base, 'shared')).toEqual({
      departure_city: '香港',
      is_shared: true,
    });
  });

  it('不修改入参（纯函数）', () => {
    const snapshot = { ...base };
    applyFilterType(base, 'direct');
    expect(base).toEqual(snapshot);
  });
});

describe('applySortType', () => {
  const base = { departure_city: '香港' };

  it('price_asc -> ordering=price', () => {
    expect(applySortType(base, 'price_asc').ordering).toBe('price');
  });
  it('time -> ordering=departure_time', () => {
    expect(applySortType(base, 'time').ordering).toBe('departure_time');
  });
  it('airline -> ordering=airline', () => {
    expect(applySortType(base, 'airline').ordering).toBe('airline');
  });
  it('未知/空 sortType 不追加 ordering', () => {
    expect(applySortType(base, null)).not.toHaveProperty('ordering');
    expect(applySortType(base, undefined)).not.toHaveProperty('ordering');
    expect(applySortType(base, 'weird')).not.toHaveProperty('ordering');
  });
});

describe('buildQueryParams', () => {
  it('组合 search/filter/sort 三类参数', () => {
    const params = buildQueryParams({
      searchParams: {
        departureCity: '香港',
        arrivalCity: '伦敦',
        departureDate: '2026-08-02',
      },
      filterType: 'direct',
      sortType: 'price_asc',
    });
    expect(params).toEqual({
      departure_city: '香港',
      arrival_city: '伦敦',
      departure_date: '2026-08-02',
      is_direct: true,
      ordering: 'price',
    });
  });

  it('无 filter/sort 时只返回基础参数', () => {
    const params = buildQueryParams({
      searchParams: { departureCity: '北京' },
    });
    expect(params).toEqual({
      departure_city: '北京',
      arrival_city: '',
      departure_date: '',
    });
  });
});

describe('suggestCities', () => {
  const cities = ['北京', '上海', '香港', '伦敦'];

  it('空关键字返回空数组', () => {
    expect(suggestCities('', cities)).toEqual([]);
  });

  it('按子串匹配', () => {
    expect(suggestCities('香', cities)).toEqual(['香港']);
    expect(suggestCities('伦', cities)).toEqual(['伦敦']);
  });

  it('无匹配返回空数组', () => {
    expect(suggestCities('火星', cities)).toEqual([]);
  });
});
