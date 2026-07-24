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

## 项目结构

```
.
├── frontend/         # 前端项目
│   ├── src/          # 前端源代码
│   │   ├── api/      # API 适配层（可单测）
│   │   ├── utils/    # 筛选/排序/映射纯逻辑（可单测）
│   │   └── App.vue   # 页面组件
│   ├── test/         # Vitest 测试
│   ├── Dockerfile    # 前端Docker配置
│   └── package.json  # 前端依赖
├── backend/          # 后端项目
│   ├── flights/      # 航班应用
│   │   └── tests/    # Django 测试包（models/views/serialization/integration/defects）
│   ├── flight_booking/ # 项目配置（含 test_settings.py）
│   ├── docs/DEFECTS.md # 缺陷报告
│   ├── .coveragerc   # 覆盖率配置
│   ├── Dockerfile    # 后端Docker配置
│   └── requirements.txt # 后端依赖
├── docker-compose.yml # Docker Compose配置（含 backend-test / frontend-test）
├── run-tests.ps1     # 一条命令跑全部测试（Windows）
├── run-tests.sh      # 一条命令跑全部测试（Linux/macOS/CI）
└── README.md         # 项目说明
```

## 测试

测试体系覆盖后端（Django 单测 + 集成测）与前端（Vitest 单测 + 组件测），
并以 `@expectedFailure` 标注了故意暴露现有实现缺陷的用例（详见
[backend/docs/DEFECTS.md](backend/docs/DEFECTS.md)）。

### 一条命令跑前后端

Windows（PowerShell）：

```powershell
./run-tests.ps1              # 前后端全部
./run-tests.ps1 -Backend     # 仅后端
./run-tests.ps1 -Frontend -Coverage
```

Linux / macOS / CI：

```bash
./run-tests.sh               # 前后端全部
./run-tests.sh backend       # 仅后端
COVERAGE=1 ./run-tests.sh frontend
```

### 后端测试（docker compose，无需本地 Python/Postgres）

后端测试使用 SQLite 内存库（`flight_booking/test_settings.py`），不依赖 db 服务：

```bash
docker compose run --rm backend-test
```

或在已构建镜像中直接运行：

```bash
docker compose run --rm backend python manage.py test flights --settings=flight_booking.test_settings
```

预期结果：`Ran 54 tests ... OK (expected failures=15)`，核心视图/模型覆盖率 **100%**（目标 ≥80%）。

### 前端测试（Vitest）

```bash
cd frontend
npm install
npm run test            # 运行全部用例
npm run test:coverage   # 附带覆盖率
```

或通过 docker：

```bash
docker compose run --rm frontend-test
```

预期结果：`Test Files 4 passed, Tests 34 passed`，`src/utils`、`src/api` 覆盖率 100%。

### 覆盖范围

| 层次 | 内容 |
|------|------|
| 后端单测 | `Airline`/`Airport`/`Flight` 约束与关联、级联删除、`__str__`；`flight_list`/`flight_detail` 的城市模糊匹配、日期筛选、空结果、404、请求方法；序列化字段完整性（含税价依赖的原始字段、机场嵌套字段、时间格式） |
| 后端集成测 | 多条件组合查询、与种子数据一致的端到端断言、排序语义现状 |
| 后端缺陷用例 | 非法日期静默忽略、排序/筛选参数未实现、输入校验缺失等 15 项（`@expectedFailure`） |
| 前端单测 | 筛选/排序参数构建、城市自动补全、航班数据映射纯逻辑；API 适配层（mock axios） |
| 前端组件测 | 搜索/筛选/排序交互、自动补全、详情展开、含税价展示（mock axios） |

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
