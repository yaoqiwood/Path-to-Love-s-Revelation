# 前端开发文档

## 项目定位

本项目已从 `uni-app` 小程序前端重构为标准 Web 技术栈：

- `Vue 3`
- `Vite`
- `Vue Router`
- `Axios`
- `Less`

当前默认以移动端访问为优先目标，桌面端会以手机壳容器的形式居中展示。

## 启动命令

```bash
npm install
npm run dev
npm run build
```

默认开发地址：

- `http://localhost:5173`

如果需要局域网手机访问，可使用开发机 IP：

- `http://你的局域网IP:5173`

## 目录结构

```text
frontend/
├─ public/
│  └─ static/                  静态资源，保留原 pages 依赖的图片路径
├─ src/
│  ├─ api/
│  │  ├─ http.js               Axios 实例
│  │  └─ modules/              业务 API 服务
│  ├─ components/
│  │  └─ compat/               兼容旧模板的轻量组件
│  ├─ data/                    本地 JSON 数据
│  ├─ pages/                   业务页面
│  │  ├─ index/
│  │  ├─ user/
│  │  ├─ feed/
│  │  └─ guide/
│  ├─ platform/                Web 端 bridge / uniCloud 兼容层
│  ├─ plugins/                 全局插件
│  ├─ router/                  路由
│  ├─ styles/                  全局 Less 样式
│  ├─ App.vue
│  └─ main.js
├─ index.html
├─ vite.config.js
└─ package.json
```

## 页面路由

为了尽量保留原页面语义，Web 路由路径继续沿用原 `uni-app` 页面地址：

- `/pages/index/index`
- `/pages/index/service`
- `/pages/user/helper`
- `/pages/feed/entry`
- `/pkg/guide/hub`
- `/pkg/guide/panel`
- `/pkg/guide/roster`
- `/pkg/guide/insight`
- `/pkg/guide/relay`
- `/pkg/guide/intent`
- `/pkg/guide/detail`

这样做的好处是：

- 旧页面内容迁移成本低
- 原有跳转逻辑大部分可以直接保留
- 后续如果要对照旧需求文档，路径也更容易对应

## 技术架构说明

### 1. 路由层

- 使用 `vue-router`
- 在 [`src/router/index.js`](/c:/Users/yaoqi/Documents/Path-to-Love-s-Revelation%20Project/frontend/src/router/index.js) 统一维护页面入口

### 2. 接口层

- 使用 `Axios`
- 在 [`src/api/http.js`](/c:/Users/yaoqi/Documents/Path-to-Love-s-Revelation%20Project/frontend/src/api/http.js) 创建统一请求实例
- 在 [`src/api/modules/personnel-user.js`](/c:/Users/yaoqi/Documents/Path-to-Love-s-Revelation%20Project/frontend/src/api/modules/personnel-user.js) 管理业务接口

### 3. 兼容层

为了保留原 `pages` 模板内容，项目提供了一层轻量兼容组件和 bridge：

- [`src/platform/uni-compat.js`](/c:/Users/yaoqi/Documents/Path-to-Love-s-Revelation%20Project/frontend/src/platform/uni-compat.js)
- [`src/platform/unicloud-compat.js`](/c:/Users/yaoqi/Documents/Path-to-Love-s-Revelation%20Project/frontend/src/platform/unicloud-compat.js)
- [`src/plugins/compat-components.js`](/c:/Users/yaoqi/Documents/Path-to-Love-s-Revelation%20Project/frontend/src/plugins/compat-components.js)

这不是继续使用 `uni-app`，而是为了在标准 Vue Web 环境里平滑承接原页面结构。

### 4. 样式层

- 全局样式入口：[`src/styles/base.less`](/c:/Users/yaoqi/Documents/Path-to-Love-s-Revelation%20Project/frontend/src/styles/base.less)
- 页面样式统一使用 `<style scoped lang="less">`
- `vite.config.js` 中已内置 `rpx -> vw` 转换，便于原页面移动端样式直接工作

## Axios 开发规范

### 基础原则

- 所有 HTTP 请求都走 `src/api/http.js`
- 业务模块按领域拆到 `src/api/modules/`
- 页面内不要直接拼散乱的 `axios.get/post`

### 推荐写法

```js
import { personnelUserService } from '@/api/modules/personnel-user'

const result = await personnelUserService.list({
  keyword: '',
  page: 1,
  pageSize: 10
})
```

### Mock 策略

当前项目支持两种模式：

- 无后端地址时：自动走本地 mock 数据
- 配置真实后端地址时：优先走真实接口，请求失败再回退 mock

这样做的目的：

- 前端开发不被后端阻塞
- 手机上能直接看到页面效果
- 管理页和测试流程有基础演示数据

## 环境变量

可在项目根目录新增 `.env.local`：

```bash
VITE_API_BASE_URL=https://your-api-domain.com
VITE_USE_MOCK=false
```

说明：

- `VITE_API_BASE_URL`：真实后端接口前缀
- `VITE_USE_MOCK`：是否强制启用 mock

## 移动端设计原则

- 页面内容默认以单栏布局为主
- 使用卡片化信息结构，减少横向挤压
- 管理表格场景保留横向滚动
- 通过 `rpx -> vw` 适配原移动端尺寸体系
- 桌面仅作为预览容器，不作为主设计断点

## 新增页面的建议流程

1. 在 `src/pages/` 下新增页面文件。
2. 使用 `<style scoped lang="less">`。
3. 在 `src/router/index.js` 注册对应路由。
4. 把接口收敛到 `src/api/modules/`。
5. 如果页面需要上传、存储、提示、弹窗，优先复用现有 bridge。

## 新增接口的建议流程

1. 在对应 `src/api/modules/*.js` 中添加服务方法。
2. 先定义真实接口请求。
3. 再补一个 mock fallback，保证前端独立可跑。
4. 页面只调用服务方法，不直接处理请求细节。

## 现阶段说明

- 旧 `pages` 内容已迁移到 `src/pages`
- 页面路由、静态资源、测试流程和后台页结构已保留
- 运行环境已切换为标准 `Vue 3 + Vite + Axios + Less`
- 兼容层仅用于承接旧页面结构，后续可逐步继续去兼容化
