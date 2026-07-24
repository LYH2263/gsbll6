import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';

// mock axios，避免真实网络请求
vi.mock('axios');
import axios from 'axios';
import App from '../src/App.vue';

const rawFlight = (id, overrides = {}) => ({
  id,
  airline: '国泰航空',
  flight_number: `CX${id}`,
  aircraft: '波音777',
  departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
  arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
  departure_time: '2026-08-01 09:00',
  arrival_time: '2026-08-01 21:30',
  price: 8999.0,
  remaining_seats: 5,
  is_direct: true,
  is_shared: false,
  ...overrides
});

beforeEach(() => {
  vi.clearAllMocks();
});

describe('App.vue 关键交互', () => {
  it('点击搜索后渲染航班卡片', async () => {
    axios.get.mockResolvedValue({
      data: { status: 'success', data: [rawFlight(1), rawFlight(2)], count: 2 }
    });
    const wrapper = mount(App);
    await wrapper.find('.search-btn').trigger('click');
    await new Promise(r => setTimeout(r)); // 等待微任务
    await wrapper.vm.$nextTick();
    expect(wrapper.findAll('.flight-card')).toHaveLength(2);
    expect(wrapper.find('.result-count').text()).toBe('2');
  });

  it('城市输入触发自动补全建议', async () => {
    const wrapper = mount(App);
    const input = wrapper.findAll('.city-input')[0];
    await input.setValue('京');
    await wrapper.vm.$nextTick();
    const suggestions = wrapper.findAll('.suggestion-item');
    expect(suggestions.length).toBeGreaterThan(0);
    expect(suggestions.map(s => s.text())).toContain('北京');
  });

  it('点击直飞筛选会带 is_direct 参数请求', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: [rawFlight(1)], count: 1 } });
    const wrapper = mount(App);
    const directLink = wrapper.findAll('.filter a')[1]; // 直飞
    await directLink.trigger('click');
    await wrapper.vm.$nextTick();
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining('/flights/'),
      { params: expect.objectContaining({ is_direct: true }) }
    );
  });

  it('点击价格排序会带 ordering=price 参数请求', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: [rawFlight(1)], count: 1 } });
    const wrapper = mount(App);
    const sortLink = wrapper.findAll('.sort a')[0]; // 价格低到高
    await sortLink.trigger('click');
    await wrapper.vm.$nextTick();
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining('/flights/'),
      { params: expect.objectContaining({ ordering: 'price' }) }
    );
  });

  it('展开/收起航班详情', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: [rawFlight(1)], count: 1 } });
    const wrapper = mount(App);
    await wrapper.find('.search-btn').trigger('click');
    await new Promise(r => setTimeout(r));
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.flight-detail-content').exists()).toBe(false);
    await wrapper.find('.flight-detail a').trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.flight-detail-content').exists()).toBe(true);
  });

  it('含税价展示：卡片包含 ¥ 金额 与 含税 文案', async () => {
    axios.get.mockResolvedValue({ data: { status: 'success', data: [rawFlight(1)], count: 1 } });
    const wrapper = mount(App);
    await wrapper.find('.search-btn').trigger('click');
    await new Promise(r => setTimeout(r));
    await wrapper.vm.$nextTick();
    const priceInfo = wrapper.find('.price-info');
    expect(priceInfo.find('.currency').text()).toBe('¥');
    expect(priceInfo.find('.amount').text()).toBe('8999');
    expect(priceInfo.find('.tax').text()).toBe('含税');
  });
});
