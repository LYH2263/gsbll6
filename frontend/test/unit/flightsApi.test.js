import { describe, it, expect, vi, beforeEach } from 'vitest';

// Note: 必须在 import 被测模块前 mock axios
vi.mock('axios', () => {
  const get = vi.fn();
  return {
    default: { get },
    get,
  };
});

import axios from 'axios';
import { fetchFlights, fetchFlightDetail } from '../../src/api/flights.js';

describe('fetchFlights', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('GET /flights/ 并透传 params', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: [] } });
    const params = { departure_city: '香港' };
    await fetchFlights(params, 'http://example.com/api');
    expect(axios.get).toHaveBeenCalledWith(
      'http://example.com/api/flights/',
      { params },
    );
  });

  it('未提供 baseUrl 时回退到 VITE_API_URL 或 /api', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: [] } });
    await fetchFlights({});
    const url = axios.get.mock.calls[0][0];
    expect(url.endsWith('/flights/')).toBe(true);
  });

  it('请求失败时把异常向上抛（由组件层 catch 处理 alert）', async () => {
    const boom = new Error('network');
    axios.get.mockRejectedValue(boom);
    await expect(fetchFlights({}, 'http://x')).rejects.toThrow('network');
  });
});

describe('fetchFlightDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('GET /flights/:id/', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: { id: 1 } } });
    await fetchFlightDetail(42, 'http://example.com/api');
    expect(axios.get).toHaveBeenCalledWith(
      'http://example.com/api/flights/42/',
    );
  });
});
