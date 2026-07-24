import { describe, it, expect, vi, beforeEach } from 'vitest';

// mock axios（api 适配层依赖 axios）
vi.mock('axios');
import axios from 'axios';
import { fetchFlights, fetchFlightDetail } from '../src/api/flights.js';

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

beforeEach(() => {
  vi.clearAllMocks();
});

describe('fetchFlights', () => {
  it('成功时映射为前端结构', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: [rawFlight], count: 1 } });
    const res = await fetchFlights({ departure_city: '香港' });
    expect(res.success).toBe(true);
    expect(res.data).toHaveLength(1);
    expect(res.data[0].flightNumber).toBe('CX123');
    // 校验请求参数透传
    expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/flights/'), {
      params: { departure_city: '香港' }
    });
  });

  it('后端返回 error 时返回 success=false 并带 message', async () => {
    axios.get.mockResolvedValue({ data: { status: 'error', message: 'boom' } });
    const res = await fetchFlights({});
    expect(res.success).toBe(false);
    expect(res.data).toEqual([]);
    expect(res.message).toBe('boom');
  });

  it('空结果返回空数组', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: [], count: 0 } });
    const res = await fetchFlights({});
    expect(res.success).toBe(true);
    expect(res.data).toEqual([]);
  });

  it('网络异常向上抛出（由调用方 catch）', async () => {
    axios.get.mockRejectedValue(new Error('network down'));
    await expect(fetchFlights({})).rejects.toThrow('network down');
  });
});

describe('fetchFlightDetail', () => {
  it('成功返回详情数据', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: rawFlight } });
    const res = await fetchFlightDetail(1);
    expect(res.success).toBe(true);
    expect(res.data.id).toBe(1);
    expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/flights/1/'));
  });

  it('404/未找到返回 success=false', async () => {
    axios.get.mockResolvedValue({ data: { status: 'error', message: 'Flight not found' } });
    const res = await fetchFlightDetail(999);
    expect(res.success).toBe(false);
    expect(res.data).toBeNull();
    expect(res.message).toBe('Flight not found');
  });
});
