# [OPEN] preview-connection-errors

## 问题描述
- 现象：浏览器报 `net::ERR_ABORTED http://10.255.75.13:8000/api/state`
- 现象：浏览器报 `net::ERR_CONNECTION_REFUSED http://10.255.75.13:7777/event`
- 目标：确认是服务未启动、地址不可达，还是页面残留了调试请求。

## 已知环境
- 项目目录：`/Users/bytedance/Desktop/design demo`
- 预览服务：`sync_server.py`
- 控制页：`index.html`
- 手机页：`mobile-preview.html`

## 初始假设
- H1：`8000` 端口上的 `sync_server.py` 已停止，所以 `/api/state` 被拒绝连接。
- H2：页面里还残留了调试埋点，继续请求 `7777/event`，但调试服务器未运行。
- H3：浏览器里开的还是旧页面脚本，脚本仍指向旧的调试地址。
- H4：局域网 IP `10.255.75.13` 已变化，导致请求打到了错误地址。
- H5：控制页或手机页加载被中断，触发了 `ERR_ABORTED` 连带报错。
