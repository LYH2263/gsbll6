// 航班数据映射与格式化纯逻辑
// 从 App.vue 抽离，保持与原实现完全一致的行为，便于单元测试。

/**
 * 计算飞行时长文案，例如 "12h 30m"。
 * @param {Date} departureDateTime 出发时间
 * @param {Date} arrivalDateTime 到达时间
 * @returns {string}
 */
export function formatDuration(departureDateTime, arrivalDateTime) {
  const durationMs = arrivalDateTime - departureDateTime;
  const hours = Math.floor(durationMs / (1000 * 60 * 60));
  const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
  return `${hours}h ${minutes}m`;
}

/**
 * 将后端返回的单条航班数据转换为前端卡片所需结构。
 * 与 App.vue 原始 map 逻辑保持一致。
 * @param {object} flight 后端航班对象
 * @returns {object} 前端航班对象
 */
export function mapFlight(flight) {
  const departureDateTime = new Date(flight.departure_time);
  const arrivalDateTime = new Date(flight.arrival_time);
  const duration = formatDuration(departureDateTime, arrivalDateTime);

  return {
    id: flight.id,
    airline: flight.airline,
    flightNumber: flight.flight_number,
    aircraft: flight.aircraft,
    departureTime: departureDateTime.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    departureAirport: `${flight.departure_airport.name} (${flight.departure_airport.code})`,
    arrivalTime: arrivalDateTime.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    arrivalAirport: `${flight.arrival_airport.name} (${flight.arrival_airport.code})`,
    duration: duration,
    route: flight.is_direct ? '直飞' : '中转',
    price: flight.price,
    remainingSeats: flight.remaining_seats,
    isDirect: flight.is_direct,
    isShared: flight.is_shared
  };
}

/**
 * 批量映射航班列表。
 * @param {Array<object>} flights 后端航班数组
 * @returns {Array<object>}
 */
export function mapFlights(flights) {
  return (flights || []).map(mapFlight);
}
