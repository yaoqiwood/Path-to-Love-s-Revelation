# In Grace — Backend

创意资产管理后台 API 服务，基于 FastAPI + SQLAlchemy 2.0 + Celery 构建。

## 技术栈

- **语言**: Python 3.11+
- **包管理**: [uv](https://docs.astral.sh/uv/)
- **Web 框架**: FastAPI + Uvicorn
- **数据库**: MySQL (aiomysql 异步 / pymysql 同步)
- **缓存**: Redis
- **任务队列**: Celery + Celery Beat
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (python-jose)
- **对象存储**: MinIO (可选)

## 快速开始

### 1. 安装依赖

```bash
# 安装 uv (如未安装)
pip install uv

# 同步依赖 (自动创建 .venv)
uv sync
```

### 2. 配置环境变量

环境变量文件按优先级加载：`.env` → `.env.{APP_ENV}`

```bash
.env                # 基础通用配置
.env.development    # 开发环境 (默认)
.env.production     # 生产环境
```

关键配置项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MYSQL_HOST` | MySQL 地址 | localhost |
| `MYSQL_DATABASE` | 数据库名 | creative_tools |
| `REDIS_HOST` | Redis 地址 | localhost |
| `SECRET_KEY` | JWT 密钥 | 需修改 |
| `CELERY_BROKER_URL` | Celery Broker | redis://localhost:6379/0 |

### 3. 前置服务

- **MySQL** (端口 3306)
- **Redis** (端口 6379)
- **MinIO** (端口 9000，可选)

### 4. 启动服务

```bash
# API 服务 (开发模式)
uv run python main.py

# Celery Worker (异步任务)
uv run celery -A app.core.celery_app worker -n network@%COMPUTERNAME% -Q network_queue -l info -P threads -c 2 -E

# Celery Beat (定时调度)
uv run celery -A app.core.celery_app beat -l info
```

生产环境可直接运行 `.bat` 脚本：

```
run_python.bat              # FastAPI 服务
run_celery_network.bat      # Celery Worker
run_celery_scheduler.bat    # Celery Beat
```

### 5. 验证

- API 文档: http://localhost:8011/docs
- 健康检查: http://localhost:8011/health

## 项目结构

```
backend/
├── app/
│   ├── api/            # FastAPI 路由 (Endpoints)
│   ├── core/           # 核心配置 (数据库、认证、日志)
│   ├── models/         # SQLAlchemy ORM 模型
│   ├── schemas/        # Pydantic DTO
│   ├── repository/     # 数据库交互层 (CRUD)
│   ├── services/       # 业务逻辑层
│   ├── tasks/          # Celery 异步任务
│   ├── enums/          # 枚举定义
│   ├── constants/      # 常量
│   └── utils/          # 工具函数
├── alembic/            # 数据库迁移脚本
├── storage/            # 本地文件存储
├── logs/               # 日志目录
├── main.py             # 应用入口
├── pyproject.toml      # 项目配置与依赖
└── requirements.txt    # 兼容 pip 的依赖列表
```

## 常用命令

```bash
# 添加新依赖
uv add <package>

# 数据库迁移
uv run alembic revision --autogenerate -m "描述"
uv run alembic upgrade head
```
