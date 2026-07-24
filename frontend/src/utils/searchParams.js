/**
 * 把前端 UI 状态（searchParams / filterType / sortType）翻译成后端
 * 查询参数对象。纯函数，便于单测。
 *
 * 这些逻辑原本散落在 App.vue 的 searchFlights / filterFlights /
 * sortFlights 三个方法中，行为完全保持一致：
 *   - 基础参数：departure_city / arrival_city / departure_date
 *   - 筛选：direct -> is_direct=true，transfer -> is_direct=false，
 *           shared -> is_shared=true，all -> 不加任何参数
 *   - 排序：price_asc -> ordering=price，time -> ordering=departure_time，
 *           airline -> ordering=airline
 */

/**
 * 构造基础查询参数。
 *
 * @param {{departureCity?:string, arrivalCity?:string, departureDate?:string}} searchParams
 * @returns {Object}
 */
export function buildBaseParams(searchParams) {
  return {
    departure_city: searchParams.departureCity ?? '',
    arrival_city: searchParams.arrivalCity ?? '',
    departure_date: searchParams.departureDate ?? '',
  };
}

/**
 * 根据筛选类型追加布尔筛选参数。
 *
 * @param {Object} base 基础参数对象（会被浅拷贝，不修改入参）
 * @param {'all'|'direct'|'transfer'|'shared'} filterType
 * @returns {Object}
 */
export function applyFilterType(base, filterType) {
  const params = { ...base };
  if (filterType === 'direct') {
    params.is_direct = true;
  } else if (filterType === 'transfer') {
    params.is_direct = false;
  } else if (filterType === 'shared') {
    params.is_shared = true;
  }
  return params;
}

/**
 * 根据排序类型追加 ordering 参数。
 *
 * @param {Object} base
 * @param {'price_asc'|'time'|'airline'|string|undefined|null} sortType
 * @returns {Object}
 */
export function applySortType(base, sortType) {
  const params = { ...base };
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
 * 一次性把 UI 状态翻译成后端参数。供组件层调用。
 *
 * @param {Object} state
 * @param {Object} state.searchParams
 * @param {string} [state.filterType]
 * @param {string} [state.sortType]
 * @returns {Object}
 */
export function buildQueryParams({ searchParams, filterType, sortType }) {
  let params = buildBaseParams(searchParams);
  if (filterType) {
    params = applyFilterType(params, filterType);
  }
  if (sortType) {
    params = applySortType(params, sortType);
  }
  return params;
}

/**
 * 城市自动补全的纯过滤逻辑（与 App.vue 中 onCityInput 行为一致）。
 *
 * @param {string} keyword
 * @param {string[]} cities
 * @returns {string[]}
 */
export function suggestCities(keyword, cities) {
  if (!keyword) return [];
  return cities.filter((c) => c.includes(keyword));
}
