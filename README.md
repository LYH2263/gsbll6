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
│   ├── public/       # 静态资源
│   ├── Dockerfile    # 前端Docker配置
│   └── package.json  # 前端依赖
├── backend/          # 后端项目
│   ├── flights/      # 航班应用
│   ├── flight_booking/ # 项目配置
│   ├── Dockerfile    # 后端Docker配置
│   └── requirements.txt # 后端依赖
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
