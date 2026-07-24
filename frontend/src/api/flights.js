// 航班 API 适配层
// 封装 axios 调用与响应解析，便于在测试中 mock axios。

import axios from 'axios';
import { mapFlights } from '../utils/flightMapper.js';

const apiBaseUrl = import.meta.env.VITE_API_URL || '/api';

/**
 * 请求航班列表并解析为前端结构。
 * @param {object} params 查询参数（由 searchParams 构建）
 * @returns {Promise<{success: boolean, data: Array<object>, message?: string}>}
 */
export async function fetchFlights(params) {
  const response = await axios.get(`${apiBaseUrl}/flights/`, { params });
  if (response.data && response.data.status === 'success') {
    return { success: true, data: mapFlights(response.data.data) };
  }
  return {
    success: false,
    data: [],
    message: response.data ? response.data.message : 'unknown error'
  };
}

/**
 * 请求单条航班详情。
 * @param {number|string} flightId
 * @returns {Promise<{success: boolean, data: object|null, message?: string}>}
 */
export async function fetchFlightDetail(flightId) {
  const response = await axios.get(`${apiBaseUrl}/flights/${flightId}/`);
  if (response.data && response.data.status === 'success') {
    return { success: true, data: response.data.data };
  }
  return {
    success: false,
    data: null,
    message: response.data ? response.data.message : 'unknown error'
  };
}

export { apiBaseUrl };
