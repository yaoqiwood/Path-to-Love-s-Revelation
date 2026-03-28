---
trigger: model_decision
description: When developing backend requirements using Python
---

# backend.md - Backend 开发指南 (In Grace)

- 所有 Python 代码必须遵循 PEP 8 风格，使用 4 个空格缩进。
- 制作计划时，使用中文。
- 开发环境为 **Windows 系统**，Shell 命令使用 **PowerShell** 语法，禁止使用 Linux 专用命令（`cp`, `rm`, `ls` 等）。
- **⚠️ PowerShell 命令分隔符**：禁止使用 `&&`，必须使用 `;`（分号）。推荐通过 `run_command` 的 `Cwd` 参数指定工作目录。

## 项目概述

素材制作管理系统后端服务，基于 **Python 3.12+ / FastAPI / SQLAlchemy 2.0 / Celery** 构建。

---

## 技术栈

| 组件          | 技术                                  | 说明                                          |
| ------------- | ------------------------------------- | --------------------------------------------- |
| Web 框架      | FastAPI 0.128 + Uvicorn               | 异步高并发 RESTful API                        |
| ORM           | SQLAlchemy 2.0                        | 关系型数据库映射                              |
| MySQL 驱动    | `aiomysql`（异步）/ `pymysql`（同步） | FastAPI 用异步 Session；Celery 用同步 Session |
| 文档数据库    | MongoDB 7.0 + Motor                   | 操作日志与非结构化数据                        |
| 缓存 / Broker | Redis 8+                              | Celery 消息代理与结果后端                     |
| 任务队列      | Celery 5.6 + Celery Beat              | 视频渲染、定时归档                            |
| 对象存储      | MinIO                                 | S3 兼容分布式文件系统                         |

---

## 项目结构

```
backend/
├── alembic/                # 数据库迁移脚本
├── app/
│   ├── api/                # FastAPI 路由 (Endpoints)
│   │   ├── deps.py         # 依赖注入 (get_current_user 等)
│   │   └── endpoints/      # 各业务端点
│   ├── constants/          # 常量定义
│   ├── core/               # 核心配置
│   │   ├── config.py       # Pydantic Settings
│   │   ├── database.py     # AsyncSession + SyncSessionLocal
│   │   ├── celery_app.py   # Celery 应用实例
│   │   ├── security.py     # JWT 认证
│   │   ├── storage.py      # 混合存储服务
│   │   └── logging.py      # 日志配置
│   ├── enums/              # 枚举定义
│   ├── models/             # SQLAlchemy 模型
│   ├── schemas/            # Pydantic DTOs
│   ├── services/           # 业务逻辑服务层
│   ├── tasks/              # Celery 异步任务
│   └── utils/              # 工具函数
├── logs/                   # 日志目录
├── storage/                # 本地文件存储
├── main.py                 # 应用入口
└── requirements.txt
```

---

## ⚠️ 核心开发规范

### 1. Python 包结构

- 包含 `.py` 的代码目录必须有 `__init__.py`。
- 新增代码文件时，在同级 `__init__.py` 中导出。

### 2. 异步与同步分离

本项目存在两套 Session 和 Redis 客户端，严格区分使用场景：

| 组件         | 实例/方法                          | 驱动       | 使用场景         |
| ------------ | ---------------------------------- | ---------- | ---------------- |
| **Database** | `AsyncSession` (get_db)            | `aiomysql` | FastAPI 异步端点 |
| **Database** | `SyncSessionLocal()`               | `pymysql`  | Celery 同步任务  |
| **Redis**    | `RedisClient` (get_redis)          | `aioredis` | FastAPI 异步端点 |
| **Redis**    | `RedisSyncClient` (get_redis_sync) | `redis`    | Celery 同步任务  |

**❌ 禁止混用：**

```python
# FastAPI 端点 — 必须用 await + execute
result = await db.execute(select(Model).where(...))
obj = result.scalar_one_or_none()

# Celery 任务 — 必须用同步 query
db = SyncSessionLocal()
obj = db.query(Model).filter(...).first()
```

### 3. ORM 关系加载

- **默认 `lazy='raise'`**：防止 N+1 查询，必须主动预加载。
- **高频访问用 `lazy='selectin'`**：90% 场景需要的关联字段。

```python
# 异步预加载 — selectinload
stmt = select(Task).options(selectinload(Task.creator)).where(...)
result = await db.execute(stmt)

# 同步预加载 — joinedload
obj = db.query(Task).options(joinedload(Task.creator)).filter(...).first()
```

### 4. Celery 任务规范

- 使用 `SyncSessionLocal()`，手动 `commit()` / `rollback()` / `close()`
- 任务参数只传 ID，内部查库获取数据
- 禁止 `self.update_state(state="FAILURE")`（会导致 Worker 崩溃），用自定义状态名
- 查询 ORM 对象时 `joinedload` 所有需要访问的关系

### 5. API 端点规范

- 路由前缀统一 `/api`，RESTful 风格
- 请求/响应必须定义 Pydantic Schema
- 分页返回 `{ items, total, page, page_size }`
- 使用 `response_model` 声明返回类型

```python
@router.get("/items/", response_model=ItemListResponse)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    total = (await db.execute(select(func.count(Model.id)).where(...))).scalar_one()
    items = ...
    return ItemListResponse(items=items, total=total, page=page, page_size=page_size)
```

### 6. 数据模型规范

- SQLAlchemy 模型: `app/models/`，Pydantic Schema: `app/schemas/`
- **禁止**使用 MySQL 关键字（`name`, `type`, `order`, `key`, `desc`, `group` 等）作为列名
- **禁止**使用 `metadata` 作为列名（SQLAlchemy 保留字）
- 枚举用 `String` 存储，Schema 层用 Python `Enum`

### 7. 日志规范

```python
from app.core.logging import get_logger
logger = get_logger(__name__)
# 禁止使用 print()
```

### 8. 五层解耦架构

```
Client -> [Endpoint层] 路由定义、参数接收
       -> [Service层]  业务逻辑、校验、状态流转
       -> [Repo层]     数据库 CRUD（禁止抛 HTTPException）
       -> [Models层]   ORM 表结构
       -> [Schemas层]  序列化响应 -> Client
```

- **Endpoint** (`app/api/endpoints/`): Thin Controller，用 `Annotated[Service, Depends()]` 注入
- **Service** (`app/services/`): 核心逻辑，可抛 `HTTPException`
- **Repository** (`app/repository/`): 纯数据库操作，注入 `AsyncSession`
- **Models** (`app/models/`): ORM 定义，无业务逻辑
- **Schemas** (`app/schemas/`): Pydantic DTO，`ConfigDict(from_attributes=True)`

### 9. 认证规范

- JWT `sub` 字段必须是字符串: `str(user.id)`
- 认证依赖: `Depends(get_current_user)`

### 10. 数据库外键规范（无物理外键）

- **禁止物理外键约束**，关联由代码维护
- SQLAlchemy 可用 `relationship` + `primaryjoin` 做跨表查询
- Alembic 迁移文件中须删除自动生成的 `ForeignKeyConstraint`

### 11. 多进程部署注意

- 开发 `workers=1`，生产 `workers=4+`
- 全局变量在进程间不共享，配置变更须以 DB/Redis 为准
- 涉及「启动加载 + 运行时可改」的状态必须考虑多进程同步

---

## 运行命令

> 运行前必须激活虚拟环境: `conda activate creative;`
> 使用该命令以虚拟环境执行程序: `conda run -n creative python xxx.py;`

```bash
# API 服务
python main.py

# Celery Beat（定时调度，全局只运行一个）
celery -A app.core.celery_app beat -l info

# Celery Network Worker（网络请求队列 — 调用外部 API，可多并发）
celery -A app.core.celery_app worker -n network@%COMPUTERNAME% -Q network_queue -l info -P threads -c 4 -E
```

---

## 数据库迁移（手动 SQL）

> **⚠️ 本项目不使用 Alembic 进行数据库迁移变更。**

1. 修改 SQLAlchemy Model 定义
2. AI 提供对应的 `ALTER TABLE` / `CREATE TABLE` 等 SQL 语句
3. 开发者审核 SQL 后在 MySQL 中手动执行
4. 验证数据库结构与 ORM 模型一致

---

## 常见坑点

| 问题 | 解决方案 |
| --- | --- |
| `lazy='raise'` 报错 | 查询时加 `.options(joinedload/selectinload(Model.relation))` |
| `AsyncSession has no attribute 'query'` | 改为 `await db.execute(select(...))` |
| Celery Worker 崩溃 | 禁止 `state="FAILURE"`，用自定义状态名 |
| DuplicateNodenameWarning | 启动加 `-n worker@%COMPUTERNAME%` |
| `MultipleResultsFound` | 改用 `.scalars().first()` 代替 `.scalar_one_or_none()` |
| 多进程配置不一致 | 从 DB/Redis 加载而非依赖内存缓存 |

---

## 修改代码检查清单

1. ✅ FastAPI 端点中是否使用了 `await db.execute(select(...))` 而非 `db.query()`？
2. ✅ 新增 API 是否同步更新了前端 TypeScript 类型定义？
3. ✅ 是否使用 `get_logger` 而非 `print`？
