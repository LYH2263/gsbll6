<template>
  <div class="app">
    <!-- 顶部区域 -->
    <header class="header">
      <!-- 用户状态栏 -->
      <div class="user-status-bar">
        <div class="container">
          <div class="user-links">
            <a href="#">登录</a>
            <span>|</span>
            <a href="#">注册</a>
            <span>|</span>
            <a href="#">客户服务</a>
          </div>
        </div>
      </div>
      <!-- 主导航 -->
      <div class="main-nav">
        <div class="container">
          <div class="logo">
            <h1>同程旅行</h1>
          </div>
          <nav class="nav-links">
            <a href="#">首页</a>
            <a href="#" class="active">机票</a>
            <a href="#">酒店</a>
            <a href="#">旅游</a>
            <a href="#">更多</a>
          </nav>
          <!-- 二级导航 -->
          <div class="sub-nav">
            <a href="#">国内机票</a>
            <a href="#" class="active">国际·港澳机票</a>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <div class="container">
        <!-- 机票搜索器 -->
        <div class="flight-searcher">
          <div class="search-form">
            <div class="form-row">
              <div class="form-group">
                <label>行程类型</label>
                <div class="radio-group">
                  <label><input type="radio" name="tripType" value="oneway" v-model="searchParams.tripType"> 单程</label>
                  <label><input type="radio" name="tripType" value="roundtrip" v-model="searchParams.tripType"> 往返</label>
                </div>
              </div>
              <div class="form-group">
                <label>出发城市</label>
                <div class="city-input-wrapper">
                  <input 
                    type="text" 
                    placeholder="请输入出发城市" 
                    class="city-input" 
                    v-model="searchParams.departureCity"
                    @input="onCityInput('departure', $event)"
                    @blur="setTimeout(() => autocomplete.departure.show = false, 200)"
                  >
                  <!-- 城市自动补全建议 -->
                  <div v-if="autocomplete.departure.show && autocomplete.departure.suggestions.length > 0" class="autocomplete-suggestions">
                    <div 
                      v-for="city in autocomplete.departure.suggestions" 
                      :key="city"
                      class="suggestion-item"
                      @mousedown="selectCity('departure', city)"
                    >
                      {{ city }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label>到达城市</label>
                <div class="city-input-wrapper">
                  <input 
                    type="text" 
                    placeholder="请输入到达城市" 
                    class="city-input" 
                    v-model="searchParams.arrivalCity"
                    @input="onCityInput('arrival', $event)"
                    @blur="setTimeout(() => autocomplete.arrival.show = false, 200)"
                  >
                  <!-- 城市自动补全建议 -->
                  <div v-if="autocomplete.arrival.show && autocomplete.arrival.suggestions.length > 0" class="autocomplete-suggestions">
                    <div 
                      v-for="city in autocomplete.arrival.suggestions" 
                      :key="city"
                      class="suggestion-item"
                      @mousedown="selectCity('arrival', city)"
                    >
                      {{ city }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label>出发日期</label>
                <div class="date-input-wrapper">
                  <input 
                    type="text" 
                    placeholder="请选择出发日期" 
                    class="date-input" 
                    v-model="searchParams.departureDate"
                    @focus="toggleDatePicker()"
                    readonly
                  >
                  <!-- 日期选择器 -->
                  <div v-if="datePicker.show" class="date-picker">
                    <div class="date-picker-header">
                      <h4>选择日期</h4>
                      <button class="close-btn" @click="datePicker.show = false">×</button>
                    </div>
                    <div class="date-picker-body">
                      <div 
                        v-for="day in 30" 
                        :key="day"
                        class="date-item"
                        @click="selectDate(new Date(Date.now() + day * 24 * 60 * 60 * 1000).toISOString().split('T')[0])"
                      >
                        {{ new Date(Date.now() + day * 24 * 60 * 60 * 1000).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label>人数</label>
                <select class="person-select" v-model="searchParams.personCount">
                  <option value="1">1人</option>
                  <option value="2">2人</option>
                  <option value="3">3人</option>
                  <option value="4">4人</option>
                  <option value="5">5人</option>
                </select>
              </div>
              <div class="form-group">
                <label>舱位</label>
                <select class="cabin-select" v-model="searchParams.cabin">
                  <option value="经济舱">经济舱</option>
                  <option value="公务舱">公务舱</option>
                  <option value="头等舱">头等舱</option>
                </select>
              </div>
              <button class="search-btn" @click="searchFlights">搜索</button>
            </div>
          </div>
        </div>

        <!-- 价格日历条 -->
        <div class="price-calendar">
          <div class="calendar-header">
            <h3>价格日历</h3>
            <div class="calendar-nav">
              <button class="nav-btn">‹</button>
              <button class="nav-btn">›</button>
            </div>
          </div>
          <div class="calendar-scroll">
            <div class="calendar-item">
              <div class="date">今天</div>
              <div class="price">¥1299</div>
            </div>
            <div class="calendar-item">
              <div class="date">明天</div>
              <div class="price">¥1199</div>
            </div>
            <div class="calendar-item">
              <div class="date">后天</div>
              <div class="price">¥1099</div>
            </div>
            <div class="calendar-item">
              <div class="date">1月30日</div>
              <div class="price">¥999</div>
            </div>
            <div class="calendar-item">
              <div class="date">1月31日</div>
              <div class="price">¥1099</div>
            </div>
            <div class="calendar-item">
              <div class="date">2月1日</div>
              <div class="price">¥1199</div>
            </div>
            <div class="calendar-item">
              <div class="date">2月2日</div>
              <div class="price">¥1299</div>
            </div>
          </div>
        </div>

        <!-- 公告栏 -->
        <div class="announcement-bar">
          <div class="container">
            <p>【重要通知】国际航班出行请注意查看目的地国家的入境政策，提前做好准备。</p>
          </div>
        </div>

        <!-- 航班结果列表 -->
        <div class="flight-results">
          <!-- 结果摘要和筛选排序 -->
          <div class="results-header">
            <div class="results-summary">
              找到 <span class="result-count">{{ flights.length }}</span> 个航班
            </div>
            <div class="filter-sort">
              <div class="filter">
                <span>筛选：</span>
                <a href="#" :class="{ active: filterParams.type === 'all' }" @click.prevent="filterFlights('all')">全部</a>
                <a href="#" :class="{ active: filterParams.type === 'direct' }" @click.prevent="filterFlights('direct')">直飞</a>
                <a href="#" :class="{ active: filterParams.type === 'transfer' }" @click.prevent="filterFlights('transfer')">中转</a>
                <a href="#" :class="{ active: filterParams.type === 'shared' }" @click.prevent="filterFlights('shared')">共享航班</a>
              </div>
              <div class="sort">
                <span>排序：</span>
                <a href="#" :class="{ active: sortParam === 'price_asc' }" @click.prevent="sortFlights('price_asc')">价格低到高</a>
                <a href="#" :class="{ active: sortParam === 'time' }" @click.prevent="sortFlights('time')">时间优先</a>
                <a href="#" :class="{ active: sortParam === 'airline' }" @click.prevent="sortFlights('airline')">航空公司</a>
              </div>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="isLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载航班信息...</p>
          </div>

          <!-- 航班信息卡片列表 -->
          <div v-else class="flight-list">
            <!-- 航班卡片 -->
            <div v-for="flight in flights" :key="flight.id" class="flight-card">
              <div class="flight-info">
                <div class="airline">
                  <span class="airline-name">{{ flight.airline }}</span>
                  <span class="flight-number">{{ flight.flightNumber }}</span>
                  <span class="aircraft">{{ flight.aircraft }}</span>
                </div>
                <div class="schedule">
                  <div class="departure">
                    <div class="time">{{ flight.departureTime }}</div>
                    <div class="airport">{{ flight.departureAirport }}</div>
                  </div>
                  <div class="duration">
                    <div class="time">{{ flight.duration }}</div>
                    <div class="route">{{ flight.route }}</div>
                  </div>
                  <div class="arrival">
                    <div class="time">{{ flight.arrivalTime }}</div>
                    <div class="airport">{{ flight.arrivalAirport }}</div>
                  </div>
                </div>
                <div class="price-info">
                  <div class="price">
                    <span class="currency">¥</span>
                    <span class="amount">{{ flight.price }}</span>
                    <span class="tax">含税</span>
                  </div>
                  <div class="remaining-seats">
                    余票：<span>{{ flight.remainingSeats }}</span>张
                  </div>
                  <button class="select-btn" @click="selectFlight(flight.id)">选择</button>
                </div>
              </div>
              <div class="flight-detail">
                <a href="#" @click.prevent="toggleFlightDetail(flight.id)">
                  {{ expandedFlight === flight.id ? '收起详情' : '航班详情' }}
                </a>
              </div>
              <!-- 航班详情展开区域 -->
              <div v-if="expandedFlight === flight.id" class="flight-detail-content">
                <div class="detail-item">
                  <span>航班号：</span>
                  <span>{{ flight.flightNumber }}</span>
                </div>
                <div class="detail-item">
                  <span>机型：</span>
                  <span>{{ flight.aircraft }}</span>
                </div>
                <div class="detail-item">
                  <span>出发时间：</span>
                  <span>{{ flight.departureTime }}</span>
                </div>
                <div class="detail-item">
                  <span>到达时间：</span>
                  <span>{{ flight.arrivalTime }}</span>
                </div>
                <div class="detail-item">
                  <span>飞行时长：</span>
                  <span>{{ flight.duration }}</span>
                </div>
                <div class="detail-item">
                  <span>是否直飞：</span>
                  <span>{{ flight.isDirect ? '是' : '否' }}</span>
                </div>
                <div class="detail-item">
                  <span>是否共享航班：</span>
                  <span>{{ flight.isShared ? '是' : '否' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-content">
        <div class="service-box">
          <h3>在线客服</h3>
          <p>如有疑问，请随时咨询</p>
          <button class="service-btn">立即咨询</button>
        </div>
        <div class="back-to-top">
          <a href="#" class="top-btn">返回顶部</a>
        </div>
      </div>
    </aside>

    <!-- 底部区域 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-links">
          <div class="link-group">
            <h4>关于同程</h4>
            <ul>
              <li><a href="#">公司简介</a></li>
              <li><a href="#">招贤纳士</a></li>
              <li><a href="#">联系我们</a></li>
            </ul>
          </div>
          <div class="link-group">
            <h4>帮助中心</h4>
            <ul>
              <li><a href="#">常见问题</a></li>
              <li><a href="#">机票预订</a></li>
              <li><a href="#">退改政策</a></li>
            </ul>
          </div>
          <div class="link-group">
            <h4>商务合作</h4>
            <ul>
              <li><a href="#">企业合作</a></li>
              <li><a href="#">广告投放</a></li>
              <li><a href="#">分销合作</a></li>
            </ul>
          </div>
          <div class="link-group">
            <h4>APP下载</h4>
            <div class="qrcode">
              <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=QR%20code%20for%20travel%20app%20download&image_size=square" alt="APP下载二维码">
            </div>
          </div>
        </div>
        <div class="copyright">
          <p>© 2024 同程旅行 版权所有</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { fetchFlights } from './api/flights.js';
import { buildBaseParams, buildFilterParams, buildSortParams, filterCitySuggestions } from './utils/searchParams.js';

export default {
  name: 'App',
  data() {
    return {
      // 加载状态
      isLoading: false,
      // 搜索参数
      searchParams: {
        tripType: 'oneway',
        departureCity: '',
        arrivalCity: '',
        departureDate: '',
        personCount: 1,
        cabin: '经济舱'
      },
      // 筛选参数
      filterParams: {
        type: 'all' // all, direct, transfer, shared
      },
      // 排序参数
      sortParam: 'price_asc', // price_asc, time, airline
      // 航班数据
      flights: [],
      // 展开的航班详情
      expandedFlight: null,
      // 城市数据
      cities: [
        '北京', '上海', '广州', '深圳', '香港', '澳门', '台北',
        '东京', '大阪', '首尔', '曼谷', '新加坡', '吉隆坡',
        '伦敦', '巴黎', '法兰克福', '罗马', '马德里',
        '纽约', '洛杉矶', '芝加哥', '迈阿密', '多伦多',
        '悉尼', '墨尔本', '奥克兰'
      ],
      // 城市自动补全状态
      autocomplete: {
        departure: {
          show: false,
          suggestions: []
        },
        arrival: {
          show: false,
          suggestions: []
        }
      },
      // 日期选择器状态
      datePicker: {
        show: false,
        selectedDate: ''
      },
      // API基础URL
      apiBaseUrl: import.meta.env.VITE_API_URL || '/api'
    }
  },
  methods: {
    // 搜索航班
    async searchFlights() {
      this.isLoading = true;
      try {
        const params = buildBaseParams(this.searchParams);
        const result = await fetchFlights(params);
        if (result.success) {
          this.flights = result.data;
        } else {
          console.error('API返回错误:', result.message);
          // 显示错误提示
          alert('搜索失败，请稍后重试');
        }
      } catch (error) {
        console.error('API请求错误:', error);
        // 显示错误提示
        alert('网络错误，请检查后端服务是否正常运行');
      } finally {
        this.isLoading = false;
      }
    },
    // 筛选航班
    async filterFlights(type) {
      this.filterParams.type = type;
      this.isLoading = true;
      try {
        const params = buildFilterParams(this.searchParams, type);
        const result = await fetchFlights(params);
        if (result.success) {
          this.flights = result.data;
        }
      } catch (error) {
        console.error('筛选请求错误:', error);
        alert('筛选失败，请稍后重试');
      } finally {
        this.isLoading = false;
      }
    },
    // 排序航班
    async sortFlights(sortType) {
      this.sortParam = sortType;
      this.isLoading = true;
      try {
        const params = buildSortParams(this.searchParams, sortType);
        const result = await fetchFlights(params);
        if (result.success) {
          this.flights = result.data;
        }
      } catch (error) {
        console.error('排序请求错误:', error);
        alert('排序失败，请稍后重试');
      } finally {
        this.isLoading = false;
      }
    },
    // 切换航班详情展开/收起
    toggleFlightDetail(flightId) {
      if (this.expandedFlight === flightId) {
        this.expandedFlight = null;
      } else {
        this.expandedFlight = flightId;
      }
    },
    // 选择航班
    selectFlight(flightId) {
      // 跳转到订单填写页
      console.log('选择航班:', flightId);
      // 实际项目中可以使用路由跳转
      // this.$router.push(`/order/${flightId}`);
    },
    // 城市输入框输入事件
    onCityInput(type, event) {
      const value = event.target.value;
      if (type === 'departure') {
        this.searchParams.departureCity = value;
        if (value) {
          this.autocomplete.departure.suggestions = filterCitySuggestions(this.cities, value);
          this.autocomplete.departure.show = true;
        } else {
          this.autocomplete.departure.show = false;
        }
      } else if (type === 'arrival') {
        this.searchParams.arrivalCity = value;
        if (value) {
          this.autocomplete.arrival.suggestions = filterCitySuggestions(this.cities, value);
          this.autocomplete.arrival.show = true;
        } else {
          this.autocomplete.arrival.show = false;
        }
      }
    },
    // 选择城市
    selectCity(type, city) {
      if (type === 'departure') {
        this.searchParams.departureCity = city;
        this.autocomplete.departure.show = false;
      } else if (type === 'arrival') {
        this.searchParams.arrivalCity = city;
        this.autocomplete.arrival.show = false;
      }
    },
    // 切换日期选择器
    toggleDatePicker() {
      this.datePicker.show = !this.datePicker.show;
    },
    // 选择日期
    selectDate(date) {
      this.searchParams.departureDate = date;
      this.datePicker.show = false;
    }
  }
}
</script>

<style scoped>
/* 全局样式 */
.container {
  width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 顶部区域 */
.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-status-bar {
  background-color: #f5f5f5;
  padding: 8px 0;
}

.user-links {
  text-align: right;
}

.user-links a {
  color: #666;
  text-decoration: none;
  margin: 0 10px;
}

.user-links span {
  color: #ccc;
}

.main-nav {
  padding: 20px 0;
}

.logo h1 {
  font-size: 24px;
  color: #00b38a;
  margin: 0;
}

.nav-links {
  margin: 10px 0;
}

.nav-links a {
  color: #333;
  text-decoration: none;
  margin: 0 15px;
  font-size: 16px;
}

.nav-links a.active {
  color: #00b38a;
  font-weight: bold;
}

.sub-nav {
  margin-top: 10px;
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
}

.sub-nav a {
  color: #666;
  text-decoration: none;
  margin-right: 20px;
}

.sub-nav a.active {
  color: #00b38a;
  font-weight: bold;
}

/* 主内容区域 */
.main-content {
  padding: 20px 0;
  min-height: 600px;
}

/* 机票搜索器 */
.flight-searcher {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.search-form {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.form-row {
  display: flex;
  gap: 15px;
  align-items: center;
}

.form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 12px;
  color: #666;
}

.city-input, .date-input, .person-select, .cabin-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.radio-group {
  display: flex;
  gap: 15px;
}

.radio-group label {
  display: inline-block;
  margin-bottom: 0;
  cursor: pointer;
}

.search-btn {
  background-color: #00b38a;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  height: 40px;
  align-self: flex-end;
}

.search-btn:hover {
  background-color: #00a07a;
}

/* 价格日历条 */
.price-calendar {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.calendar-header h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.calendar-nav {
  display: flex;
  gap: 10px;
}

.nav-btn {
  width: 30px;
  height: 30px;
  border: 1px solid #ddd;
  background-color: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.calendar-scroll {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.calendar-item {
  flex: 0 0 100px;
  text-align: center;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.calendar-item:hover {
  border-color: #00b38a;
  box-shadow: 0 2px 4px rgba(0, 179, 138, 0.1);
}

.calendar-item .date {
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
}

.calendar-item .price {
  font-size: 16px;
  font-weight: bold;
  color: #ff6600;
}

/* 公告栏 */
.announcement-bar {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 20px;
}

.announcement-bar p {
  margin: 0;
  color: #856404;
  font-size: 14px;
}

/* 航班结果列表 */
.flight-results {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.results-summary {
  font-size: 14px;
  color: #666;
}

.result-count {
  font-weight: bold;
  color: #333;
}

.filter-sort {
  display: flex;
  gap: 30px;
}

.filter, .sort {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.filter span, .sort span {
  color: #666;
}

.filter a, .sort a {
  color: #333;
  text-decoration: none;
  padding: 4px 8px;
  border-radius: 4px;
}

.filter a:hover, .sort a:hover {
  background-color: #f5f5f5;
}

.filter a.active, .sort a.active {
  background-color: #00b38a;
  color: #fff;
}

/* 航班列表 */
.flight-list {
  padding: 20px;
}

.flight-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 15px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.flight-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.flight-info {
  display: flex;
  padding: 20px;
  gap: 30px;
}

.airline {
  flex: 0 0 150px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.airline-name {
  font-weight: bold;
  color: #333;
}

.flight-number, .aircraft {
  font-size: 12px;
  color: #666;
}

.schedule {
  flex: 1;
  display: flex;
  gap: 30px;
  align-items: center;
}

.departure, .arrival {
  flex: 1;
}

.departure .time, .arrival .time {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.departure .airport, .arrival .airport {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.duration {
  flex: 0 0 120px;
  text-align: center;
}

.duration .time {
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
}

.duration .route {
  font-size: 12px;
  color: #666;
}

.price-info {
  flex: 0 0 200px;
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.price {
  font-size: 24px;
  font-weight: bold;
  color: #ff6600;
}

.currency {
  font-size: 16px;
}

.tax {
  font-size: 12px;
  color: #666;
  margin-left: 5px;
}

.remaining-seats {
  font-size: 12px;
  color: #666;
}

.select-btn {
  background-color: #00b38a;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.select-btn:hover {
  background-color: #00a07a;
}

.flight-detail {
  padding: 10px 20px;
  border-top: 1px solid #f0f0f0;
  background-color: #f9f9f9;
}

.flight-detail a {
  color: #0066cc;
  text-decoration: none;
  font-size: 12px;
}

.flight-detail a:hover {
  text-decoration: underline;
}

/* 航班详情展开区域 */
.flight-detail-content {
  padding: 15px 20px;
  background-color: #f9f9f9;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 12px;
}

.detail-item span:first-child {
  width: 100px;
  color: #666;
}

.detail-item span:last-child {
  color: #333;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  background-color: #f9f9f9;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #00b38a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #666;
  font-size: 14px;
}

/* 城市输入框和自动补全 */
.city-input-wrapper {
  position: relative;
}

.autocomplete-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.suggestion-item {
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.suggestion-item:hover {
  background-color: #f5f5f5;
}

/* 日期输入框和选择器 */
.date-input-wrapper {
  position: relative;
}

.date-picker {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 15px;
  z-index: 1000;
  min-width: 300px;
}

.date-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.date-picker-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.date-picker-body {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.date-item {
  padding: 8px;
  text-align: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
}

.date-item:hover {
  background-color: #f5f5f5;
  border-color: #00b38a;
}

/* 侧边栏 */
.sidebar {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 100px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 15px;
}

.service-box {
  text-align: center;
  margin-bottom: 20px;
}

.service-box h3 {
  font-size: 14px;
  color: #333;
  margin-bottom: 10px;
}

.service-box p {
  font-size: 12px;
  color: #666;
  margin-bottom: 15px;
}

.service-btn {
  background-color: #00b38a;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  width: 100%;
}

.back-to-top {
  text-align: center;
}

.top-btn {
  display: inline-block;
  padding: 8px 16px;
  background-color: #f5f5f5;
  color: #333;
  text-decoration: none;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.3s ease;
}

.top-btn:hover {
  background-color: #e0e0e0;
}

/* 底部区域 */
.footer {
  background-color: #f5f5f5;
  padding: 40px 0;
  margin-top: 40px;
}

.footer-links {
  display: flex;
  gap: 60px;
  margin-bottom: 30px;
}

.link-group {
  flex: 1;
}

.link-group h4 {
  font-size: 14px;
  color: #333;
  margin-bottom: 15px;
}

.link-group ul {
  list-style: none;
}

.link-group ul li {
  margin-bottom: 10px;
}

.link-group ul li a {
  color: #666;
  text-decoration: none;
  font-size: 12px;
  transition: color 0.3s ease;
}

.link-group ul li a:hover {
  color: #00b38a;
}

.qrcode img {
  width: 80px;
  height: 80px;
}

.copyright {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
  font-size: 12px;
  color: #999;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .container {
    width: 90%;
  }
  
  .form-row {
    flex-wrap: wrap;
  }
  
  .form-group {
    flex: 1 1 150px;
  }
  
  .flight-info {
    flex-wrap: wrap;
  }
  
  .sidebar {
    display: none;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 0 15px;
  }
  
  .nav-links {
    display: none;
  }
  
  .sub-nav {
    flex-wrap: wrap;
  }
  
  .flight-info {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .schedule {
    width: 100%;
  }
  
  .price-info {
    width: 100%;
    text-align: left;
    align-items: flex-start;
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 30px;
  }
  
  .link-group {
    flex: 1 1 150px;
  }
}
</style>
