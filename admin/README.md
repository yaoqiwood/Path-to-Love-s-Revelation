# In Grace — Admin

创意资产管理后台前端应用，基于 Vue 3 + TypeScript + Element Plus 构建。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript 5.x
- **构建工具**: Vite 7.x
- **UI 组件库**: Element Plus 2.x
- **状态管理**: Pinia 3.x
- **路由**: Vue Router 4.x
- **HTTP 客户端**: Axios
- **包管理**: pnpm

## 快速开始

### 1. 安装依赖

```bash
pnpm install
```

### 2. 配置环境变量

```bash
.env.development    # 开发环境 API 地址
.env.production     # 生产环境 API 地址
```

### 3. 启动开发服务器

```bash
pnpm run dev
```

访问: http://localhost:3000

> Vite 已配置 `/api` 代理到后端 `http://localhost:8011`

### 4. 构建生产版本

```bash
pnpm run build
```

## 项目结构

```
admin/
├── src/
│   ├── api/              # API 请求模块 (Axios 封装)
│   ├── assets/           # 静态资源 (图片、字体)
│   ├── components/       # 组件
│   │   ├── common/       # 通用组件 (Header, Sidebar)
│   │   └── business/     # 跨页面复用的业务组件
│   ├── composables/      # Vue 3 组合式函数
│   ├── config/           # 应用配置
│   ├── router/           # 路由配置 (含导航守卫)
│   ├── store/            # Pinia 状态管理
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数
│   ├── views/            # 页面视图
│   ├── App.vue           # 根组件
│   ├── main.ts           # 应用入口
│   └── style.css         # 全局样式
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 开发规范

- 使用 `<script setup lang="ts">` 语法
- 类型导入使用 `import type`
- 样式使用 `<style scoped>`
- API 请求统一通过 `src/api/request.ts` 封装
- 所有类型集中在 `src/types/` 目录
