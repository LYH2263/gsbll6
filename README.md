# 国际机票搜索结果页项目

## 项目简介
本项目是一个国际机票搜索结果页，基于Vue 3和Django开发，实现了航班搜索、筛选、排序等功能，提供了清晰、高效的用户界面。

## 技术栈
### 前端
- Vue 3
- Vite
- CSS3

### 后端
- Django 5.0
- PostgreSQL
- Django REST Framework (API)

### 部署
- Docker
- Docker Compose

## 如何运行

### 前提条件
- 安装Docker和Docker Compose

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

## 验证方法

### 验证前端
1. 访问 http://localhost:3000
2. 检查页面是否正常加载
3. 测试搜索功能、筛选功能和排序功能
4. 检查页面响应式设计是否正常

### 验证后端
1. 访问 http://localhost:8000/api/flights/
2. 检查是否返回航班数据
3. 测试API筛选参数，例如：
   - http://localhost:8000/api/flights/?departure_city=香港&arrival_city=伦敦

### 验证数据库
1. 检查Docker日志中是否有数据库连接错误
2. 确认后端服务能够正常连接到数据库

## 自动化测试

本次补齐了**可自动执行**的前后端测试体系，**未改动任何业务功能**。所有命令均可在本地或 CI 环境一条命令跑通，默认通过 Docker 执行，无需在宿主机安装 Python / Node。

### 一条命令跑前后端

在项目根目录执行（PowerShell）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\test-all.ps1
```

Linux / macOS / Git Bash：

```bash
bash scripts/test-all.sh
```

常用参数：

| 参数 | 作用 |
| --- | --- |
| `-Coverage`（ps1）/ `--coverage`（sh） | 在跑单测的同时输出覆盖率，后端 fail_under=80，未达标将非零退出 |
| `-Postgres` / `--postgres` | 后端用 PostgreSQL（docker-compose 的 db 服务）跑测；默认用 SQLite 内存库，启动更快、无需 db 容器 |
| `-SkipBackend` / `--skip-backend` | 只跑前端 |
| `-SkipFrontend` / `--skip-frontend` | 只跑后端 |

示例：带覆盖率、SQLite 快速跑：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\test-all.ps1 -Coverage
```

### 后端测试（Django）

后端使用 Django 内置 `TestCase` + `Client`，配合 `coverage.py`。测试专用配置见 [test_settings.py](file:///d:/Asolo4/众测723/gsbll6/backend/flight_booking/test_settings.py)，默认使用 SQLite 内存库，可通过 `DB_ENGINE=postgres` 切回 docker-compose 的 PostgreSQL。

```powershell
# 跑全部后端单测 + 集成测（SQLite，最快）
docker compose run --rm --no-deps -e DB_ENGINE=sqlite3 backend python manage.py test --settings=flight_booking.test_settings -v 2

# 用 PostgreSQL（docker-compose 的 db 服务）跑
docker compose run --rm backend python manage.py test --settings=flight_booking.test_settings

# 覆盖率（.coveragerc 中 fail_under=80）
docker compose run --rm --no-deps -e DB_ENGINE=sqlite3 backend sh -c "coverage run --rcfile=.coveragerc manage.py test --settings=flight_booking.test_settings && coverage report -m"
```

当前结果：**82 个用例，67 通过 / 15 个 expected failure（主动暴露的缺陷，见下文缺陷报告）**。核心视图覆盖率 100%，远超 ≥80% 目标：

```
Name                 Stmts  Miss  Cover
--------------------------------------
flights/models.py       27     0   100%
flights/urls.py          4     0   100%
flights/views.py        36     0   100%
TOTAL                   67     0   100%
```

后端测试文件位于 [backend/flights/tests/](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests)：

| 文件 | 覆盖内容 |
| --- | --- |
| [factories.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/factories.py) | 固定基准日夹具，构造与 `init_data` 同构但日期固定的 6 条航班，供断言使用 |
| [test_models.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_models.py) | `Airline`/`Airport`/`Flight` 的 `__str__`、字段约束、FK 级联、`related_name`、默认值、Decimal 精度 |
| [test_serialization.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_serialization.py) | list/detail 序列化字段完整性（含税价依赖的 `price`/`remaining_seats`/时间字段/机场嵌套字段）、时间格式、价格类型 |
| [test_views_list.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_views_list.py) | `flight_list` 城市模糊匹配（精确/子串/双向）、日期有效/解析失败/空字符串、空结果、非 GET 方法 |
| [test_views_detail.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_views_detail.py) | `flight_detail` 成功、404、非 int 参数、含 country 字段、逐条种子航班 |
| [test_integration.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_integration.py) | 多条件组合查询（出发/到达/日期/中文）、排序语义、直接调用 `init_data.init_data()` 的端到端断言 |
| [test_defects.py](file:///d:/Asolo4/众测723/gsbll6/backend/flights/tests/test_defects.py) | **15 个 `@unittest.expectedFailure`**，把现有实现缺陷写成可执行的"待修复清单" |

### 前端测试（Vitest + @vue/test-utils）

前端使用 Vitest + jsdom，axios 被 `vi.mock` 拦截，纯逻辑抽到 [src/utils/](file:///d:/Asolo4/众测723/gsbll6/frontend/src/utils) 和 [src/api/](file:///d:/Asolo4/众测723/gsbll6/frontend/src/api) 便于单测。业务行为保持与原页面一致（`App.vue` 模板与样式未动，仅把 axios 调用与字段映射抽成模块）。

```powershell
# 在容器内跑全部前端单测 + 组件测
docker compose run --rm --no-deps frontend npx vitest run

# 覆盖率（v8）
docker compose run --rm --no-deps frontend npx vitest run --coverage

# watch 模式（本地开发，需宿主机 npm install）
cd frontend; npm install; npm run test:watch
```

当前结果：**4 个测试文件 / 43 个用例全部通过**：

```
✓ test/unit/searchParams.test.js  (16 tests)
✓ test/unit/flightMapper.test.js  (12 tests)
✓ test/unit/flightsApi.test.js    (4 tests)
✓ test/components/App.test.js     (11 tests)
```

覆盖率（v8）：

```
File                      | % Stmts | % Branch | % Funcs | % Lines
src/utils/flightMapper.js |   100   |   100    |   100   |   100
src/utils/searchParams.js |   100   |   100    |   100   |   100
src/api/flights.js        |   100   |    60    |   100   |   100
src/App.vue               |   99.2  |   90.7   |   60.7  |   99.2
All files                 |   99.3  |   92.1   |   71.1  |   99.3
```

> `api/flights.js` 未覆盖的分支是 baseUrl 的环境变量回退，`App.vue` 未覆盖的是极少触发的 catch 分支（筛选/排序网络错误）；组件测已覆盖搜索成功、参数携带、筛选直飞/中转/共享、排序时间/航司、城市自动补全、日期选择器、详情展开、loading 态、非 success alert。

前端测试文件位于 [frontend/test/](file:///d:/Asolo4/众测723/gsbll6/frontend/test)：

| 文件 | 覆盖内容 |
| --- | --- |
| [setup.js](file:///d:/Asolo4/众测723/gsbll6/frontend/test/setup.js) | jsdom 环境注入 `alert` / `matchMedia` |
| [unit/searchParams.test.js](file:///d:/Asolo4/众测723/gsbll6/frontend/test/unit/searchParams.test.js) | `buildBaseParams`/`applyFilterType`/`applySortType`/`buildQueryParams`/`suggestCities` 纯函数与不可变性 |
| [unit/flightMapper.test.js](file:///d:/Asolo4/众测723/gsbll6/frontend/test/unit/flightMapper.test.js) | 时长计算、snake_case→camelCase、机场/航司展示文案、直飞/中转、价格透传 |
| [unit/flightsApi.test.js](file:///d:/Asolo4/众测723/gsbll6/frontend/test/unit/flightsApi.test.js) | mock axios，验证 URL/参数透传、baseUrl 回退、异常上抛、detail URL |
| [components/App.test.js](file:///d:/Asolo4/众测723/gsbll6/frontend/test/components/App.test.js) | 挂载默认态、搜索渲染含税价、筛选/排序参数、城市补全、日期选择器、详情展开、loading、错误 alert |

### 缺陷报告（由 expectedFailure 用例主动暴露）

下列缺陷是**现有实现的真实问题**，被写成 `@unittest.expectedFailure`（在测试报告里显示为 `expected failures`，不会让 CI 变红）。一旦修复对应业务代码，这些用例应改为普通断言并把 `expectedFailure` 去掉。

| 编号 | 缺陷 | 现状 | 期望行为 | 相关用例（test_defects.py） |
| --- | --- | --- | --- | --- |
| DEFECT-001 | 非法日期静默忽略 | `flight_list` 里 `except ValueError: pass`，`departure_date=abc` / `2026/08/02` / `2026-13-40` 均返回全部航班 | 返回 400 并提示日期格式错误 | `InvalidDateDefectTests`（3 个 xfail） |
| DEFECT-002 | `ordering` 参数未生效 | 前端传 `ordering=price`/`departure_time`/`airline` 被视图忽略，结果不排序 | 按指定字段升序/降序返回 | `OrderingDefectTests`（3 个 xfail） |
| DEFECT-003 | `is_direct` / `is_shared` 参数未生效 | 前端"直飞/中转/共享"筛选按钮携带参数但后端不处理，返回全集 | 按标志位过滤 | `FilterFlagDefectTests`（3 个 xfail） |
| DEFECT-004 | 航司/机场代码无唯一约束 | `Airline.code`、`Airport.code` 允许重复插入 | 加 `unique=True` | `ModelConstraintDefectTests`（2 个 xfail） |
| DEFECT-005 | Flight 缺业务级校验 | 允许到达时间早于起飞、负价格、负余票、起飞机场=到达机场 | 模型/视图层拒绝非法数据 | `BusinessRuleDefectTests`（4 个 xfail） |

> 这些用例在测试输出里以 `expected failures=15` 呈现，是**有意保留**的回归保护：修缺陷时把对应装饰器去掉即可立即获得防止回退的断言。

## 项目结构

```
.
├── frontend/         # 前端项目
│   ├── src/          # 前端源代码
│   ├── test/         # 前端 Vitest 测试（unit + components）
│   ├── Dockerfile    # 前端Docker配置
│   └── package.json  # 前端依赖
├── backend/          # 后端项目
│   ├── flights/      # 航班应用
│   │   └── tests/    # 后端 Django 测试（models/views/integration/defects）
│   ├── flight_booking/ # 项目配置（含 test_settings.py）
│   ├── .coveragerc   # 覆盖率配置（fail_under=80）
│   ├── Dockerfile    # 后端Docker配置
│   └── requirements.txt # 后端依赖
├── scripts/          # 一条命令跑前后端的脚本（ps1 / sh）
├── docker-compose.yml # Docker Compose配置
└── README.md         # 项目说明
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
- 首次启动时，数据库会自动初始化，但需要手动创建超级用户以访问Django admin
- 前端页面默认展示模拟数据，实际使用时需要后端API返回真实数据
