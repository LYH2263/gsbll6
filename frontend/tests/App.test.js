import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import axios from 'axios';
import App from '../src/App.vue';

vi.mock('axios');

describe('App Component', () => {
  const mockFlightsResponse = {
    data: {
      status: 'success',
      count: 2,
      data: [
        {
          id: 1,
          airline: '国泰航空',
          flight_number: 'CX123',
          aircraft: '波音777',
          departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
          arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
          departure_time: '2024-01-15 09:00',
          arrival_time: '2024-01-15 21:30',
          price: 8999.00,
          remaining_seats: 5,
          is_direct: true,
          is_shared: false
        },
        {
          id: 2,
          airline: '阿联酋航空',
          flight_number: 'EK456',
          aircraft: '空客A380',
          departure_airport: { name: '香港国际机场', code: 'HKG', city: '香港' },
          arrival_airport: { name: '伦敦希思罗机场', code: 'LHR', city: '伦敦' },
          departure_time: '2024-01-15 10:30',
          arrival_time: '2024-01-15 22:45',
          price: 7999.00,
          remaining_seats: 8,
          is_direct: false,
          is_shared: false
        }
      ]
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the app', () => {
    const wrapper = mount(App);
    expect(wrapper.find('.app').exists()).toBe(true);
    expect(wrapper.find('.header').exists()).toBe(true);
    expect(wrapper.find('.flight-searcher').exists()).toBe(true);
  });

  it('should have initial empty flights array', () => {
    const wrapper = mount(App);
    expect(wrapper.vm.flights).toEqual([]);
  });

  it('should initialize with default search params', () => {
    const wrapper = mount(App);
    expect(wrapper.vm.searchParams.tripType).toBe('oneway');
    expect(wrapper.vm.searchParams.personCount).toBe(1);
    expect(wrapper.vm.searchParams.cabin).toBe('经济舱');
  });

  it('should initialize with default filter and sort', () => {
    const wrapper = mount(App);
    expect(wrapper.vm.filterParams.type).toBe('all');
    expect(wrapper.vm.sortParam).toBe('price_asc');
  });

  it('should fetch flights and transform data on search', async () => {
    axios.get.mockResolvedValue(mockFlightsResponse);
    const wrapper = mount(App);

    await wrapper.vm.searchFlights();

    expect(axios.get).toHaveBeenCalled();
    expect(wrapper.vm.flights).toHaveLength(2);
    expect(wrapper.vm.flights[0].flightNumber).toBe('CX123');
    expect(wrapper.vm.flights[0].airline).toBe('国泰航空');
    expect(wrapper.vm.flights[0].departureAirport).toContain('香港国际机场');
    expect(wrapper.vm.flights[0].arrivalAirport).toContain('伦敦希思罗机场');
    expect(typeof wrapper.vm.flights[0].price).toBe('number');
    expect(wrapper.vm.flights[0].isDirect).toBe(true);
    expect(wrapper.vm.flights[1].isDirect).toBe(false);
  });

  it('should calculate duration for each flight', async () => {
    axios.get.mockResolvedValue(mockFlightsResponse);
    const wrapper = mount(App);

    await wrapper.vm.searchFlights();

    expect(wrapper.vm.flights[0].duration).toMatch(/^\d+h \d+m$/);
    expect(wrapper.vm.flights[0].route).toBe('直飞');
    expect(wrapper.vm.flights[1].route).toBe('中转');
  });

  it('should handle API error gracefully', async () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    axios.get.mockRejectedValue(new Error('Network error'));
    const wrapper = mount(App);

    await wrapper.vm.searchFlights();

    expect(alertSpy).toHaveBeenCalledWith('网络错误，请检查后端服务是否正常运行');
    alertSpy.mockRestore();
  });

  it('should show loading state during search', async () => {
    axios.get.mockResolvedValue(mockFlightsResponse);
    const wrapper = mount(App);

    const searchPromise = wrapper.vm.searchFlights();
    expect(wrapper.vm.isLoading).toBe(true);

    await searchPromise;
    expect(wrapper.vm.isLoading).toBe(false);
  });

  it('should filter flights with direct filter', async () => {
    axios.get.mockResolvedValue(mockFlightsResponse);
    const wrapper = mount(App);

    await wrapper.vm.filterFlights('direct');

    expect(axios.get).toHaveBeenCalled();
    const callArgs = axios.get.mock.calls[0];
    expect(callArgs[1].params.is_direct).toBe(true);
  });

  it('should filter flights with transfer filter', async () => {
    axios.get.mockResolvedValue(mockFlightsResponse);
    const wrapper = mount(App);

    await wrapper.vm.filterFlights('transfer');

    const callArgs = axios.get.mock.calls[0];
    expect(callArgs[1].params.is_direct).toBe(false);
  });

  it('should sort flights by price', async () => {
    axios.get.mockResolvedValue(mockFlightsResponse);
    const wrapper = mount(App);

    await wrapper.vm.sortFlights('price_asc');

    const callArgs = axios.get.mock.calls[0];
    expect(callArgs[1].params.ordering).toBe('price');
  });

  it('should sort flights by time', async () => {
    axios.get.mockResolvedValue(mockFlightsResponse);
    const wrapper = mount(App);

    await wrapper.vm.sortFlights('time');

    const callArgs = axios.get.mock.calls[0];
    expect(callArgs[1].params.ordering).toBe('departure_time');
  });

  it('should toggle flight detail expansion', () => {
    const wrapper = mount(App);
    wrapper.vm.flights = [{ id: 1 }, { id: 2 }];

    wrapper.vm.toggleFlightDetail(1);
    expect(wrapper.vm.expandedFlight).toBe(1);

    wrapper.vm.toggleFlightDetail(1);
    expect(wrapper.vm.expandedFlight).toBeNull();

    wrapper.vm.toggleFlightDetail(2);
    expect(wrapper.vm.expandedFlight).toBe(2);
  });

  it('should filter city suggestions on input', () => {
    const wrapper = mount(App);

    wrapper.vm.onCityInput('departure', { target: { value: '北' } });
    expect(wrapper.vm.autocomplete.departure.show).toBe(true);
    expect(wrapper.vm.autocomplete.departure.suggestions).toContain('北京');

    wrapper.vm.onCityInput('departure', { target: { value: '' } });
    expect(wrapper.vm.autocomplete.departure.show).toBe(false);
  });

  it('should select city from autocomplete', () => {
    const wrapper = mount(App);

    wrapper.vm.selectCity('departure', '香港');
    expect(wrapper.vm.searchParams.departureCity).toBe('香港');
    expect(wrapper.vm.autocomplete.departure.show).toBe(false);
  });

  it('should toggle date picker', () => {
    const wrapper = mount(App);
    expect(wrapper.vm.datePicker.show).toBe(false);

    wrapper.vm.toggleDatePicker();
    expect(wrapper.vm.datePicker.show).toBe(true);

    wrapper.vm.toggleDatePicker();
    expect(wrapper.vm.datePicker.show).toBe(false);
  });

  it('should select date', () => {
    const wrapper = mount(App);
    wrapper.vm.selectDate('2024-02-01');
    expect(wrapper.vm.searchParams.departureDate).toBe('2024-02-01');
    expect(wrapper.vm.datePicker.show).toBe(false);
  });

  it('should display result count', async () => {
    axios.get.mockResolvedValue(mockFlightsResponse);
    const wrapper = mount(App);
    await wrapper.vm.searchFlights();
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.result-count').text()).toBe('2');
  });
});
