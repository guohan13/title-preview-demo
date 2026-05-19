# [OPEN] mobile-sync-state

## 问题描述
- 现象：电脑端控制面板修改后，手机端标题文本超过 30 个字时，没有按预期切换到中字号。
- 目标：确认状态同步链路、手机端应用逻辑、以及本地编辑态是否导致字号未切换。

## 已知环境
- 项目目录：`/Users/bytedance/Desktop/design demo`
- 控制页：`index.html`
- 手机预览页：`mobile-preview.html`
- 本地服务：`python3 sync_server.py`

## 初始假设
- H1：电脑端虽然上报了状态，但上报的 `appliedPreset` 没有按最新阈值计算。
- H2：手机端成功拉到新状态，但没有把 `appliedPreset` 应用到标题样式。
- H3：手机端处于编辑态 `isEditingTitle = true`，导致新状态被跳过。
- H4：手机端本地输入只同步了 `titleText`，没有重新计算并同步新的字号结果。
- H5：服务端保存的是旧状态，电脑端新状态被后续手机端本地状态覆盖。

## 调试计划
1. 给控制页、手机页、服务端增加最小化取证日志。
2. 复现“手机端超过 30 字不切中字号”。
3. 比对控制页上报、服务端落盘、手机页拉取与应用四段证据。
4. 基于证据做最小修复。

## 证据分析
- H1 否定：控制页日志显示上报链路正常，问题复现期间电脑端并未参与手机输入后的本地字号计算。
- H2 否定：手机页 `applyState` 能持续收到状态并应用样式，但收到的 `appliedPreset` 本身就是 `34/48`。
- H3 否定：`isEditingTitle` 会阻止覆盖本地输入，但不是根因；即使失焦后重新应用，状态里的字号仍然是 `34/48`。
- H4 确认：日志中 `titleLength` 已达到 `31/35/43/52`，但 `mobile-post-state` 仍上报 `appliedPreset: 34/48`，说明手机页回写时没有重新计算字号。
- H5 否定：服务端只是持久化手机页发来的状态，没有证据表明它改写了字号结果。

## 关键日志
- 预修复证据：`.dbg/trae-debug-log-mobile-sync-state.ndjson`
- `mobile-post-state` 里 `titleLength: 43, appliedPreset: 34/48`
- `mobile-post-state` 里 `titleLength: 52, appliedPreset: 34/48`

## 修复方案
- 在 `mobile-preview.html` 内补齐与控制页一致的字体档位解析和字号计算逻辑。
- 手机端每次本地输入时，先根据 `mode / maxShrinkLevels / thresholds / fontSelections` 重新计算 `appliedPreset`，再同步到服务端。

## 修复进展
- 已在 `mobile-preview.html` 增加 `FONT_PRESETS / getFontPreset / getAppliedPresetFromState / measureLines`。
- 已在手机端输入回写前重新计算 `appliedPreset`，并先本地应用再上报。
- 已将手机页调试日志切换到 `post-fix`，等待用户复现后比对结果。
