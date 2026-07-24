# 国际机票搜索结果页项目

## 项目简介
本项目是一个国际机票搜索结果页，基于Vue 3和Django开发，实现了航班搜索、筛选、排序等功能，提供了清晰、高效的用户界面。

## 技术栈
### 前端
- Vue 3
- Vite
- CSS3
- Vitest + @vue/test-utils (测试)

### 后端
- Django 5.0
- PostgreSQL
- Django CORS Headers
- Coverage.py (测试覆盖率)

### 部署
- Docker
- Docker Compose

## 如何运行

### 前提条件
- 安装Docker和Docker Compose
- 本地测试可选：Python 3.11+、Node.js 18+

### 启动步骤
1. 克隆项目到本地
2. 进入项目根目录
3. 执行以下命令启动服务：

```bash
docker compose up
```

4. 等待服务启动完成后，访问以下地址：
   - 前端页面：http://localhost:3000
   - 后端API：http://localhost:8000/api/flights/

## 服务说明

### 前端服务 (frontend)
- 端口：3000
- 功能：提供国际机票搜索结果页的用户界面
- 技术：Vue 3 + Vite

### 后端服务 (backend)
- 端口：8000
- 功能：提供航班数据API
- 技术：Django 5.0

### 数据库服务 (db)
- 端口：5432
- 功能：存储航班数据
- 技术：PostgreSQL 15

## 测试体系

### 测试目录结构

```
.
├── backend/
│   └── flights/
│       └── tests/
│           ├── __init__.py
│           ├── test_models.py        # 模型约束与关联测试
│           ├── test_views.py          # 视图边界、序列化字段、已知缺陷测试
│           └── test_integration.py    # 多条件查询、端到端集成测试
├── frontend/
│   ├── src/
│   │   └── utils/
│   │       ├── flightAdapter.js       # API适配纯函数
│   │       └── cityFilter.js          # 城市筛选/排序纯函数
│   └── tests/
│       ├── flightAdapter.test.js      # 适配层单测
│       ├── cityFilter.test.js         # 筛选/排序逻辑单测
│       └── App.test.js                # 组件交互测试（mock axios）
└── docker-compose.yml                 # 含 backend-test / frontend-test 服务
```

### 一条命令跑全部测试（Docker）

```bash
# 后端单元+集成测试
docker compose run --rm backend-test

# 后端测试 + 覆盖率报告
docker compose run --rm backend-test-cov

# 前端单元+组件测试
docker compose run --rm frontend-test
```

### 本地运行测试（需要本地环境）

#### 后端测试（SQLite）

```bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 使用 SQLite 运行测试（无需 PostgreSQL）
set DB_ENGINE=django.db.backends.sqlite3
python manage.py test flights.tests --verbosity=2
# 带覆盖率
coverage run --source='flights' manage.py test flights.tests --verbosity=2
coverage report --show-missing
```

#### 前端测试

```bash
cd frontend
npm install
npm test              # 运行一次
npm run test:watch    # 监听模式
npm run test:coverage # 覆盖率报告
```

### 测试覆盖范围

#### 后端单测（[test_models.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_models.py)）
| 测试类 | 覆盖范围 |
|--------|----------|
| `AirlineModelTest` | 创建/字符串表示/logo可空/字段长度约束 |
| `AirportModelTest` | 创建/字符串表示/城市国家字段长度 |
| `FlightModelTest` | 创建/字符串表示/外键级联删除(airline/dep/arr)/related_name/默认值/价格精度 |

#### 后端视图与边界测试（[test_views.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_views.py)）
| 测试类 | 覆盖范围 |
|--------|----------|
| `FlightListViewTest` | GET全量/POST/PUT/DELETE 405处理/城市精确+模糊匹配/双城市组合/合法日期/空结果/非法日期静默(当前行为)/空库/序列化字段完整性/price类型/时间格式/list不含country字段 |
| `FlightDetailViewTest` | 详情成功/404/country字段/全字段存在/id匹配/非法flight_id |
| `KnownDefectTest` | @expectedFailure 标注的已知缺陷 |

#### 后端集成测试（[test_integration.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_integration.py)）
- 夹具数据与 `init_data.py` 种子数据一致（5航司/6机场/6航班）
- HKG→LHR 3条航线价格断言（EK456:¥7999, CX123:¥8999, BA789:¥9499）
- PEK→LHR / PVG→LHR / HKG→SIN 单航线断言
- 城市模糊匹配（"北"→北京、"伦"→伦敦5条）
- 城市+日期组合过滤
- list端点与detail端点数据一致性
- EK456为中转/CX123为直飞断言
- 响应结构完整性（status/data/count）

#### 前端单测（[flightAdapter.test.js](file:///d:/Asolo4/众测723/gsbll6/frontend/tests/flightAdapter.test.js)）
- 飞行时长计算（整小时/含分钟/不足1小时）
- 时间格式化/机场名称格式化
- API数据→前端字段完整映射（snake_case→camelCase）
- route字段（直飞/中转）逻辑
- price字段保持number类型（含税价展示依赖）
- 搜索/筛选/排序参数构建

#### 前端筛选排序逻辑（[cityFilter.test.js](file:///d:/Asolo4/众测723/gsbll6/frontend/tests/cityFilter.test.js)）
- 城市列表完整性（26个城市）
- 城市模糊匹配/空输入/无匹配
- 客户端排序：价格升序/时间/航空公司/不修改原数组
- 客户端筛选：全部/直飞/中转/共享航班/snake_case兼容
- 日期选择器生成逻辑

#### 前端组件测试（[App.test.js](file:///d:/Asolo4/众测723/gsbll6/frontend/tests/App.test.js)）
- 组件渲染/初始状态/默认参数
- 搜索航班（axios mock）+ 数据转换验证
- 加载状态切换
- API错误处理
- 筛选参数传递（is_direct）
- 排序参数传递（ordering）
- 航班详情展开/收起
- 城市自动补全
- 日期选择器交互

### 覆盖率目标
- 后端核心视图（views.py）：≥80%
- 后端模型：100%
- 前端纯逻辑模块：≥90%

### 已知缺陷报告（故意暴露的失败用例）

以下缺陷通过 `@unittest.expectedFailure` 标注的测试用例暴露，运行测试时显示为 expected failures（不会导致 CI 失败）：

| 缺陷ID | 位置 | 描述 | 测试用例 |
|--------|------|------|----------|
| DEFECT-001 | [views.py:34-35](file:///d:/Asolo4/众测723/gsbll6/backend/flights/views.py#L34-L35) | **非法日期静默忽略**：`departure_date` 格式错误时 `except ValueError: pass`，直接返回全部航班而非错误或空结果 | `test_defect_invalid_date_should_return_error_or_empty` |
| DEFECT-002 | [views.py:10-67](file:///d:/Asolo4/众测723/gsbll6/backend/flights/views.py#L10-L67) | **排序参数未实现**：前端发送 `ordering=price/departure_time/airline`，后端完全忽略，无服务端排序 | `test_defect_ordering_param_not_implemented` |
| DEFECT-003 | [views.py:10-67](file:///d:/Asolo4/众测723/gsbll6/backend/flights/views.py#L10-L67) | **直飞筛选未实现**：前端发送 `is_direct=true/false`，后端忽略，不过滤直飞/中转 | `test_defect_is_direct_filter_not_implemented` |
| DEFECT-004 | [views.py:10-67](file:///d:/Asolo4/众测723/gsbll6/backend/flights/views.py#L10-L67) | **共享航班筛选未实现**：前端发送 `is_shared=true`，后端忽略 | `test_defect_is_shared_filter_not_implemented` |

> **说明**：以上测试标记为 `@expectedFailure`，表示当前实现下这些测试会失败（因为代码存在缺陷）。修复缺陷后，应移除 `@expectedFailure` 装饰器，测试应转为通过。

### 验证方法

#### 验证前端
1. 访问 http://localhost:3000
2. 检查页面是否正常加载
3. 测试搜索功能、筛选功能和排序功能
4. 检查页面响应式设计是否正常

#### 验证后端
1. 访问 http://localhost:8000/api/flights/
2. 检查是否返回航班数据
3. 测试API筛选参数，例如：
   - http://localhost:8000/api/flights/?departure_city=香港&arrival_city=伦敦

#### 验证数据库
1. 检查Docker日志中是否有数据库连接错误
2. 确认后端服务能够正常连接到数据库

## 项目结构

```
.
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── pages/
│   │   │   └── index.vue
│   │   ├── utils/         # 可测试的纯逻辑模块
│   │   │   ├── flightAdapter.js
│   │   │   └── cityFilter.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── tests/             # 前端测试
│   ├── Dockerfile
│   ├── vite.config.js     # 含 Vitest 配置
│   └── package.json
├── backend/               # 后端项目
│   ├── flights/
│   │   ├── tests/         # 后端测试包
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── flight_booking/    # 项目配置
│   ├── Dockerfile
│   ├── init_data.py       # 种子数据脚本
│   └── requirements.txt
├── docker-compose.yml     # 含 test 服务
└── README.md
```

## 功能特点

1. **机票搜索器**：支持单程/往返选择，出发/到达城市输入，日期选择等
2. **价格日历条**：展示临近几天的最低票价
3. **航班结果列表**：以卡片形式展示航班信息
4. **筛选与排序**：支持按直飞/中转、价格、时间等筛选排序
5. **航班详情**：点击查看航班详细信息
6. **响应式设计**：适配不同屏幕尺寸

## 注意事项

- 项目使用Docker容器化部署，确保Docker服务正常运行
- 首次启动时，数据库会自动迁移，种子数据需手动运行 `python init_data.py` 初始化
- 前端发送的 `is_direct`/`is_shared`/`ordering` 参数当前后端未处理（见已知缺陷）
- 本地运行后端测试时设置 `DB_ENGINE=django.db.backends.sqlite3` 使用 SQLite，无需 PostgreSQL
