---
trigger: model_decision
description: When using Vue + TypeScript to develop frontend requirements
---

# frontend.md - Frontend 开发指南 (In Grace)

## 项目概述

素材管理系统前端应用，基于 **Vue 3 + TypeScript + Element Plus + Pinia** 构建。

---

## 技术栈

| 组件       | 技术         | 版本 |
| ---------- | ------------ | ---- |
| 框架       | Vue 3        | 3.5+ |
| 语言       | TypeScript   | 5.x  |
| 构建工具   | Vite         | 7.x  |
| UI组件库   | Element Plus | 2.x  |
| 状态管理   | Pinia        | 3.x  |
| 路由       | Vue Router   | 4.x  |
| HTTP客户端 | Axios        | 1.x  |
| 包管理     | pnpm         | -    |

---

## 项目结构

```
admin/
├── src/
│   ├── api/              # API 请求 (Axios 封装 + 业务模块)
│   ├── assets/           # 静态资源
│   ├── components/
│   │   ├── common/       # 通用组件 (Header, Sidebar)
│   │   └── business/     # 跨页面复用的业务组件
│   ├── composables/      # 组合式函数
│   ├── config/           # 应用配置
│   ├── router/           # 路由 (含导航守卫)
│   ├── store/            # Pinia 状态管理
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数
│   ├── views/            # 页面视图
│   ├── App.vue
│   ├── main.ts
│   └── style.css
├── package.json
└── vite.config.ts
```

---

## 核心规范

### 1. TypeScript

- 类型集中在 `src/types/`
- **必须** `import type` 导入类型，否则 Vite 构建报错

```typescript
import type { User } from "@/types";
import type { FormInstance } from "element-plus";
```

### 2. 组件

- 使用 `<script setup lang="ts">`
- Props: `defineProps<T>()`，Emits: `defineEmits<T>()`
- 样式: `<style scoped>`

### 3. 公共组件

`src/components/business/` 存放跨页面复用组件，**禁止重复实现已有组件**。修改公共组件时新增属性必须设默认值，不可破坏现有契约。

### 4. 路由

- 配置在 `src/router/index.ts`
- 权限: `meta.requiresAuth`，访客: `meta.guest`

### 5. 状态管理

- Pinia Composition API 风格
- 命名: `store/<entityName>.ts`

### 6. API 请求

- 统一通过 `src/api/request.ts` 的 `http` 对象
- Token 自动附加 Bearer，401 自动登出

```typescript
import { http } from "@/api/request";
const data = await http.get<Item>("/items/1");
```

### 7. 路径别名

`@` → `src/`，配置在 `vite.config.ts` + `tsconfig.app.json`

---

## 运行命令

```bash
pnpm install     # 安装依赖
pnpm dev         # 开发模式
pnpm build       # 构建生产版本
```

---

## 常见坑点

| 问题 | 解决方案 |
| --- | --- |
| 类型导入报错 `does not provide an export named 'XXX'` | 使用 `import type` |
| `@keyframes` 在 scoped 中不生效 | 将 `@keyframes` 定义放在非 scoped 的 `<style>` 块 |
| `<component :is>` 图标渲染异常 | 用 `markRaw()` 包裹图标映射对象 |
| UI 不渲染但无报错 | **数据先行**：优先检查 API 响应字段是否匹配，而非组件逻辑 |
| `.vue` 文件编辑 replace 工具失败 | CRLF 问题，改用 Python `rb`/`wb` 二进制模式操作 |

---

## 调试原则

- **API 响应 > TypeScript 类型 > 数据库结构**：前端消费的是 API JSON，类型定义仅为参考
- **静默失败要警惕**：`v-if`/`v-show` 条件为 false 时不报错但不渲染，优先检查数据
