export const AVAILABLE_CITIES = [
  '北京', '上海', '广州', '深圳', '香港', '澳门', '台北',
  '东京', '大阪', '首尔', '曼谷', '新加坡', '吉隆坡',
  '伦敦', '巴黎', '法兰克福', '罗马', '马德里',
  '纽约', '洛杉矶', '芝加哥', '迈阿密', '多伦多',
  '悉尼', '墨尔本', '奥克兰'
];

export function filterCitiesByInput(cities, inputValue) {
  if (!inputValue) {
    return [];
  }
  return cities.filter(city => city.includes(inputValue));
}

export function clientSortFlights(flights, sortType) {
  const sorted = [...flights];
  switch (sortType) {
    case 'price_asc':
      sorted.sort((a, b) => a.price - b.price);
      break;
    case 'time':
      sorted.sort((a, b) => {
        const timeA = a.departureTime || a.departure_time || '';
        const timeB = b.departureTime || b.departure_time || '';
        return timeA.localeCompare(timeB);
      });
      break;
    case 'airline':
      sorted.sort((a, b) => {
        const nameA = a.airline || '';
        const nameB = b.airline || '';
        return nameA.localeCompare(nameB, 'zh-CN');
      });
      break;
    default:
      break;
  }
  return sorted;
}

export function clientFilterFlights(flights, filterType) {
  switch (filterType) {
    case 'direct':
      return flights.filter(f => f.isDirect || f.is_direct);
    case 'transfer':
      return flights.filter(f => !(f.isDirect || f.is_direct));
    case 'shared':
      return flights.filter(f => f.isShared || f.is_shared);
    case 'all':
    default:
      return flights;
  }
}

export function generateDateItems(days = 30) {
  const items = [];
  for (let day = 1; day <= days; day++) {
    const date = new Date(Date.now() + day * 24 * 60 * 60 * 1000);
    items.push({
      date: date.toISOString().split('T')[0],
      label: date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    });
  }
  return items;
}
