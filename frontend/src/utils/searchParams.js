// 搜索/筛选/排序请求参数构建纯逻辑
// 从 App.vue 抽离，保持与原实现完全一致的行为，便于单元测试。

/**
 * 构建基础查询参数（出发城市 / 到达城市 / 出发日期）。
 * @param {object} searchParams { departureCity, arrivalCity, departureDate }
 * @returns {{departure_city: string, arrival_city: string, departure_date: string}}
 */
export function buildBaseParams(searchParams) {
  return {
    departure_city: searchParams.departureCity,
    arrival_city: searchParams.arrivalCity,
    departure_date: searchParams.departureDate
  };
}

/**
 * 根据筛选类型补充参数。
 * 注意：这里保留 App.vue 原始映射语义（依赖后端支持 is_direct / is_shared）。
 * @param {object} searchParams
 * @param {'all'|'direct'|'transfer'|'shared'} type
 * @returns {object}
 */
export function buildFilterParams(searchParams, type) {
  const params = buildBaseParams(searchParams);
  if (type === 'direct') {
    params.is_direct = true;
  } else if (type === 'transfer') {
    params.is_direct = false;
  } else if (type === 'shared') {
    params.is_shared = true;
  }
  return params;
}

/**
 * 根据排序类型补充 ordering 参数。
 * 注意：保留 App.vue 原始映射语义（依赖后端支持 ordering）。
 * @param {object} searchParams
 * @param {'price_asc'|'time'|'airline'} sortType
 * @returns {object}
 */
export function buildSortParams(searchParams, sortType) {
  const params = buildBaseParams(searchParams);
  if (sortType === 'price_asc') {
    params.ordering = 'price';
  } else if (sortType === 'time') {
    params.ordering = 'departure_time';
  } else if (sortType === 'airline') {
    params.ordering = 'airline';
  }
  return params;
}

/**
 * 城市自动补全过滤逻辑。
 * @param {Array<string>} cities 城市候选列表
 * @param {string} value 输入值
 * @returns {Array<string>} 匹配的城市（value 为空时返回空数组）
 */
export function filterCitySuggestions(cities, value) {
  if (!value) {
    return [];
  }
  return cities.filter(city => city.includes(value));
}
