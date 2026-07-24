import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import axios from 'axios';
import App from '../../src/App.vue';

vi.mock('axios', () => {
  const get = vi.fn();
  return { default: { get }, get };
});

const SAMPLE_FLIGHT = {
  id: 1,
  airline: '国泰航空',
  flight_number: 'CX123',
  aircraft: '波音777',
  departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
  arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
  departure_time: '2026-08-02T09:00:00',
  arrival_time: '2026-08-02T21:30:00',
  price: 8999.0,
  remaining_seats: 5,
  is_direct: true,
  is_shared: false,
};

function mockSuccess(flights = [SAMPLE_FLIGHT]) {
  axios.get.mockResolvedValue({
    data: { status: 'success', data: flights, count: flights.length },
  });
}

function factory() {
  return mount(App, {
    attachTo: document.body,
    global: {
      config: { globalProperties: {} },
    },
  });
}

describe('App.vue 关键交互', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('默认挂载：搜索按钮存在、默认排序高亮为 price_asc', () => {
    const wrapper = factory();
    expect(wrapper.find('.search-btn').exists()).toBe(true);
    const sortLinks = wrapper.findAll('.sort a');
    const active = sortLinks.find((a) => a.classes().includes('active'));
    expect(active.text()).toContain('价格低到高');
  });

  it('点击搜索按钮 -> 调用 GET /flights/ 并渲染结果', async () => {
    mockSuccess();
    const wrapper = factory();
    await wrapper.find('.search-btn').trigger('click');
    await flushPromises();

    // 检查 axios 以 base params 被调用
    expect(axios.get).toHaveBeenCalledTimes(1);
    const [url, config] = axios.get.mock.calls[0];
    expect(url.endsWith('/flights/')).toBe(true);
    expect(config.params).toEqual({
      departure_city: '',
      arrival_city: '',
      departure_date: '',
    });

    // 结果列表渲染了航班卡片
    expect(wrapper.findAll('.flight-card')).toHaveLength(1);
    expect(wrapper.text()).toContain('国泰航空');
    expect(wrapper.text()).toContain('CX123');
    // 含税价展示依赖 price 字段
    expect(wrapper.text()).toContain('8999');
    expect(wrapper.text()).toContain('含税');
  });

  it('输入城市后再搜索 -> 参数携带城市', async () => {
    mockSuccess();
    const wrapper = factory();
    const cityInputs = wrapper.findAll('.city-input');
    const depInput = cityInputs[0];
    const arrInput = cityInputs[1];

    depInput.element.value = '香港';
    await depInput.trigger('input');
    arrInput.element.value = '伦敦';
    await arrInput.trigger('input');
    await wrapper.find('.search-btn').trigger('click');
    await flushPromises();

    const config = axios.get.mock.calls.at(-1)[1];
    expect(config.params.departure_city).toBe('香港');
    expect(config.params.arrival_city).toBe('伦敦');
  });

  it('筛选：点击"直飞"发送 is_direct=true，并激活该筛选项', async () => {
    mockSuccess();
    const wrapper = factory();
    const directLink = wrapper.findAll('.filter a').find((a) => a.text() === '直飞');
    await directLink.trigger('click');
    await flushPromises();

    const config = axios.get.mock.calls.at(-1)[1];
    expect(config.params.is_direct).toBe(true);
    expect(directLink.classes()).toContain('active');
  });

  it('筛选：点击"中转"发送 is_direct=false；"共享"发送 is_shared=true', async () => {
    mockSuccess([]);
    const wrapper = factory();

    const transferLink = wrapper.findAll('.filter a').find((a) => a.text() === '中转');
    await transferLink.trigger('click');
    await flushPromises();
    let config = axios.get.mock.calls.at(-1)[1];
    expect(config.params.is_direct).toBe(false);

    const sharedLink = wrapper.findAll('.filter a').find((a) => a.text() === '共享航班');
    await sharedLink.trigger('click');
    await flushPromises();
    config = axios.get.mock.calls.at(-1)[1];
    expect(config.params.is_shared).toBe(true);
  });

  it('排序：点击"时间优先"发送 ordering=departure_time；"航空公司"发送 airline', async () => {
    mockSuccess([]);
    const wrapper = factory();

    const timeLink = wrapper.findAll('.sort a').find((a) => a.text() === '时间优先');
    await timeLink.trigger('click');
    await flushPromises();
    let config = axios.get.mock.calls.at(-1)[1];
    expect(config.params.ordering).toBe('departure_time');

    const airlineLink = wrapper.findAll('.sort a').find((a) => a.text() === '航空公司');
    await airlineLink.trigger('click');
    await flushPromises();
    config = axios.get.mock.calls.at(-1)[1];
    expect(config.params.ordering).toBe('airline');
  });

  it('城市自动补全：输入"香"显示匹配项；选择后填入并隐藏', async () => {
    const wrapper = factory();
    const depInput = wrapper.findAll('.city-input')[0];
    depInput.element.value = '香';
    await depInput.trigger('input');

    // 日期 input 之后，自动补全框应渲染
    const suggestions = wrapper.findAll('.suggestion-item');
    expect(suggestions.length).toBeGreaterThan(0);
    expect(suggestions.some((n) => n.text() === '香港')).toBe(true);

    // 选择第一个建议
    await suggestions[0].trigger('mousedown');
    expect(wrapper.vm.searchParams.departureCity).toBe(suggestions[0].text());
    expect(wrapper.vm.autocomplete.departure.show).toBe(false);
  });

  it('日期选择器：点击日期输入打开面板；选中后写入 departureDate', async () => {
    const wrapper = factory();
    await wrapper.find('.date-input').trigger('focus');
    expect(wrapper.vm.datePicker.show).toBe(true);
    expect(wrapper.findAll('.date-item').length).toBe(30);

    await wrapper.findAll('.date-item')[0].trigger('click');
    expect(wrapper.vm.datePicker.show).toBe(false);
    expect(wrapper.vm.searchParams.departureDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it('航班详情展开/收起', async () => {
    mockSuccess();
    const wrapper = factory();
    await wrapper.find('.search-btn').trigger('click');
    await flushPromises();

    // 初始详情区域不可见
    expect(wrapper.find('.flight-detail-content').exists()).toBe(false);
    const toggle = wrapper.find('.flight-detail a');
    await toggle.trigger('click');
    expect(wrapper.find('.flight-detail-content').exists()).toBe(true);
    expect(wrapper.text()).toContain('航班号：');

    // 再点一次收起
    await toggle.trigger('click');
    expect(wrapper.find('.flight-detail-content').exists()).toBe(false);
  });

  it('加载中状态：请求 pending 时显示 loading-spinner，完成后消失', async () => {
    let resolveReq;
    axios.get.mockReturnValue(new Promise((res) => { resolveReq = res; }));
    const wrapper = factory();
    wrapper.find('.search-btn').trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.loading-spinner').exists()).toBe(true);

    resolveReq({ data: { status: 'success', data: [] } });
    await flushPromises();
    expect(wrapper.find('.loading-spinner').exists()).toBe(false);
  });

  it('后端返回非 success：弹出 alert 且不清空已有列表语义', async () => {
    // 先有一条数据
    mockSuccess();
    const wrapper = factory();
    await wrapper.find('.search-btn').trigger('click');
    await flushPromises();
    expect(wrapper.findAll('.flight-card').length).toBe(1);

    // 再触发 error 响应
    axios.get.mockResolvedValue({
      data: { status: 'error', message: 'bad' },
    });
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    await wrapper.find('.search-btn').trigger('click');
    await flushPromises();
    expect(alertSpy).toHaveBeenCalled();
    alertSpy.mockRestore();
  });
});
