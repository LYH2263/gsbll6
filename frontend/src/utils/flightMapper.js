/**
 * 后端航班 DTO -> 前端展示 ViewModel 的纯函数映射。
 *
 * 从 App.vue 中抽出以便单测。纯函数，相同输入永远相同输出，不依赖
 * Vue / axios / DOM。
 */

/**
 * 计算飞行时长字符串，如 "12h 30m"。
 *
 * @param {string|number|Date} departure ISO 时间字符串或可被 Date 解析的值
 * @param {string|number|Date} arrival
 * @returns {string}
 */
export function computeDuration(departure, arrival) {
  const dep = new Date(departure).getTime();
  const arr = new Date(arrival).getTime();
  const durationMs = arr - dep;
  if (!Number.isFinite(durationMs) || durationMs < 0) {
    return '0h 0m';
  }
  const hours = Math.floor(durationMs / (1000 * 60 * 60));
  const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
  return `${hours}h ${minutes}m`;
}

/**
 * 把后端单条 flight 记录映射成模板里使用的扁平字段。
 * 与原 App.vue 中内联 map 回调的字段完全一致。
 *
 * @param {Object} flight 后端返回的一条 flight JSON
 * @returns {Object} 前端 ViewModel
 */
export function mapBackendFlight(flight) {
  const departureDateTime = new Date(flight.departure_time);
  const arrivalDateTime = new Date(flight.arrival_time);
  return {
    id: flight.id,
    airline: flight.airline,
    flightNumber: flight.flight_number,
    aircraft: flight.aircraft,
    departureTime: departureDateTime.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    }),
    departureAirport: `${flight.departure_airport.name} (${flight.departure_airport.code})`,
    arrivalTime: arrivalDateTime.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    }),
    arrivalAirport: `${flight.arrival_airport.name} (${flight.arrival_airport.code})`,
    duration: computeDuration(flight.departure_time, flight.arrival_time),
    route: flight.is_direct ? '直飞' : '中转',
    price: flight.price,
    remainingSeats: flight.remaining_seats,
    isDirect: flight.is_direct,
    isShared: flight.is_shared,
  };
}

/**
 * 批量映射。
 *
 * @param {Array<Object>} flights
 * @returns {Array<Object>}
 */
export function mapBackendFlights(flights) {
  return flights.map(mapBackendFlight);
}
