# GitHub + Render 部署说明

这个项目不是纯静态页面，电脑控制页和手机预览页之间依赖 `sync_server.py` 提供的 `/api/state` 接口，所以正式上线时需要把整个目录作为一个小型 Python 服务部署出去。

## 目录说明

- `index.html`：电脑控制页
- `mobile-preview.html`：手机实时预览页
- `assets/`：页面图片资源
- `sync_server.py`：静态文件 + 状态同步服务
- `.preview_state.json`：运行态默认状态
- `Dockerfile`：容器部署入口

## 推荐方式

推荐路径：

- 代码托管到 GitHub
- 网站部署到 Render

当前目录已经补齐了：

- `Dockerfile`
- `render.yaml`
- `.gitignore`
- `.dockerignore`

所以很适合直接走 GitHub + Render。

## 第一步：推到 GitHub

### 1. 在 GitHub 创建一个空仓库

例如仓库名：

```text
title-preview-demo
```

### 2. 在本地初始化并提交

```bash
git init
git add .
git commit -m "init title preview demo"
```

### 3. 绑定 GitHub 远端并推送

把下面的仓库地址替换成你自己的：

```bash
git remote add origin git@github.com:YOUR_NAME/title-preview-demo.git
git branch -M main
git push -u origin main
```

如果你用 HTTPS，也可以：

```bash
git remote add origin https://github.com/YOUR_NAME/title-preview-demo.git
git branch -M main
git push -u origin main
```

## 第二步：在 Render 部署

### 1. 登录 Render

- 打开 [https://render.com](https://render.com)
- 用 GitHub 账号登录

### 2. 创建 Web Service

- 选择 `New +`
- 选择 `Blueprint`
- 选择你刚刚推送的 GitHub 仓库

因为仓库里已经有 `render.yaml`，Render 会自动识别部署配置。

### 3. 配置环境变量

重点设置：

- `PUBLIC_BASE_URL`
  - 值填 Render 分配给你的公网地址
  - 例如：`https://title-preview-demo.onrender.com`

如果第一次创建时还不知道最终域名，可以先留空，等服务成功创建后再回填。

### 4. 等待部署完成

部署成功后，你会得到一个公网地址，例如：

```text
https://title-preview-demo.onrender.com
```

## 第三步：访问地址

- 电脑控制页：`https://your-domain.example.com/`
- 手机预览页：`https://your-domain.example.com/mobile-preview.html`

## 本地 Docker 部署

如果你以后想在别的平台手动部署，也可以继续使用 Docker：

```bash
docker build -t title-preview-demo .
docker run -d \
  --name title-preview-demo \
  -p 8000:8000 \
  -e PREVIEW_HOST=0.0.0.0 \
  -e PREVIEW_PORT=8000 \
  -e PUBLIC_BASE_URL=https://your-domain.example.com \
  title-preview-demo
```

## 环境变量

- `PREVIEW_HOST`
  - 默认值：`0.0.0.0`
- `PREVIEW_PORT`
  - 默认值：`8000`
- `PUBLIC_BASE_URL`
  - 正式公网部署时建议配置成站点公网地址
  - 示例：`https://your-domain.example.com`
  - 用途：控制页里的“手机预览”二维码会优先使用这个公网地址生成

## 健康检查

服务提供健康检查接口：

```text
/healthz
```

返回：

```text
ok
```

## 上线后访问地址

- 电脑控制页：`https://your-domain.example.com/`
- 手机预览页：`https://your-domain.example.com/mobile-preview.html`

## 注意事项

- 这是一个轻量状态服务，`.preview_state.json` 会保存最近一次编辑状态
- 如果部署平台的文件系统是临时的，服务重启后状态会回到镜像内默认值
- 如果希望多人同时使用且互不影响，后续需要把当前单状态文件改成“按会话隔离”的服务
- Render 免费实例可能会休眠，首次打开会有冷启动等待
