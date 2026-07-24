import axios from 'axios';

/**
 * 航班列表 API 适配层。
 *
 * 之所以从 App.vue 中抽出，是为了在单测里 mock axios 并断言请求参数，
 * 不改变运行时行为：仍然是 GET `${base}/flights/`。
 *
 * @param {Object} params 查询字符串对象
 * @param {string} baseUrl API 基础地址，默认取 VITE_API_URL 或 '/api'
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function fetchFlights(params, baseUrl) {
  const apiBaseUrl = baseUrl ?? (import.meta.env?.VITE_API_URL || '/api');
  return axios.get(`${apiBaseUrl}/flights/`, { params });
}

/**
 * 航班详情 API。
 *
 * @param {number|string} flightId
 * @param {string} baseUrl
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function fetchFlightDetail(flightId, baseUrl) {
  const apiBaseUrl = baseUrl ?? (import.meta.env?.VITE_API_URL || '/api');
  return axios.get(`${apiBaseUrl}/flights/${flightId}/`);
}
