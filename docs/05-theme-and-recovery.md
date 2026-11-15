# 主题配方与恢复

## 最终选了统一的 Android 主题

试过类 iOS 桌面、控制中心、锁屏和外观模块之后，最终撤下了叠加方案，换成 **Delta 低饱和图标 + Painterly 2 壁纸 + Lawnchair + Material You 灰蓝配色**。

旧启动器、控制中心和锁屏应用设为 `disabled-user`，两个旧外观 Magisk 模块关闭。原生 Trebuchet 保留。没有安装 QuickSwitch，也没有替换系统最近任务服务。

| 项目 | 最终配置 |
| --- | --- |
| 启动器 | Lawnchair 15 Beta 3 官方版本 |
| 图标 | Delta 2.21.0 官方包 |
| 壁纸 | Leif Niemczik 的 Painterly 2，桌面与锁屏同时应用 |
| 系统配色 | `9BA1B3`，`TONAL_SPOT` |
| 主屏 | 两屏，4 列 6 行，16 个应用入口、3 个微件 |
| Dock | 电话、浏览器、文件、设置 |
| 抽屉 | 5 列，保留搜索，关闭建议行与双行标签 |
| 主屏简化 | 关闭未配置资讯一览和底部搜索栏 |

[JSON 配方](../configs/theme-recipe.json)可用来重建；它不是启动器自带的可导入备份，不包含任何手机的微件 ID 或数据库。

## 两屏布局

坐标从 0 开始，`screen=0` 为首屏，`screen=1` 为第二屏。

| 屏幕 | 位置 | 内容 |
| --- | --- | --- |
| 首屏 | `(0,0)`，4×1 | 透明数字时钟 |
| 首屏 | `(0,2)`，4×3 | 固定城市天气预报 |
| 首屏 | 第 6 行 | 逆向工作台、Termux、PCAPdroid、Magisk |
| 第二屏 | `(0,1)`，4×1 | 音乐微件 |
| 第二屏 | 第 5 行 | 图库、时钟、日历、音乐 |
| 第二屏 | 第 6 行 | 天气、计算器、酷安、短信 |

逆向工作台补用 Delta `code_editor` 图标，日历补用动态 `calendar_`。图标覆盖要核对实际组件名，不能只按应用名称匹配。

## 三个兼容性判断

**HyperOS `.mtz` 依赖小米主题引擎。** 手机硬件是 K70，不代表 LineageOS 能导入 HyperOS 主题。

**本次 Trebuchet 不支持第三方图标包。** 曾判断可以直接套包，实测后纠正，改用 Lawnchair 普通 HOME。要逐个核对当前启动器功能，不能凭同属 Launcher3 就认为一致。

**第三方 HOME 和最近任务服务是两部分。** 本次保留原生最近任务，真实测试了系统上滑 HOME 和上滑停住的最近任务手势。没有为了套图标额外替换 Quickstep。

## 微件 ID 不能照搬

AppWidget ID 属于当前设备和当前 host。原 Trebuchet 的微件不能直接搬给 Lawnchair；网格迁移时也曾丢失旧绑定，最后重新申请并绑定三个 Lawnchair 微件。

重建时先设网格，再添加微件，并核对 `dumpsys appwidget` 中的 host、provider 与 callbacks。跨设备使用 JSON 的 provider 和几何信息重建，不能导入另一台手机的 ID。

## 改桌面数据前让 HOME 退到后台

在这次设备上，HOME 位于前台时直接 force-stop，Android 会很快重新启动它。此时离线修改数据库，界面可能仍展示内存中的旧布局。

本机恢复流程改为：先打开系统设置 → 停止 Lawnchair → 确认进程已退出 → 修改保存的偏好和数据库行 → 显式启动 Lawnchair 并设为 HOME。数据库行通过事务恢复，保留文件归属与其他表，随后做 integrity check。

Lawnchair 此版本同时用 XML、DataStore protobuf 和多个数据库保存偏好。只改某一份 XML，不能保证设置完整恢复。

这是针对本机恢复实现的经验。日常用户优先从启动器设置重建；原始数据库与二进制偏好未放进仓库。

## 系统颜色如何确认

本机 secure setting 的预设为：

```json
{
  "android.theme.customization.color_source": "preset",
  "android.theme.customization.system_palette": "9BA1B3",
  "android.theme.customization.theme_style": "TONAL_SPOT"
}
```

SystemUI 的 `mMainWallpaperColor` 曾仍显示旧壁纸主色，而实际 `mColorScheme` seed 已是 `#9BA1B3`。预设配色可以覆盖壁纸取色，因此检查最终 color scheme，不能只凭旧壁纸色字段判失败。

壁纸文件与官方 Painterly 2 原图的 SHA256 一致，桌面和锁屏都已应用。资产从[上游链接](sources.md)获取，本仓库不重新分发壁纸和图标。

## 回退和重启验证

原生桌面、原配色与原壁纸先保存，本机专用脚本完成了 **原生 → Delta** 的往返操作，随后重启验证两屏、图标、三种微件和颜色仍保留。

原生回退包括重新设置 Trebuchet HOME、恢复原配色和原壁纸。恢复本次 Delta 布局会覆盖后续桌面编辑，因此先保存新的修改。恢复脚本只适用于这台设备、该构建和仍有效的微件绑定；它保留在本地，仓库提供的是重建配方。

声音、Root 和逆向环境在这轮恢复与重启检查中保留。截图已在本地保存，功能验收依据真实 UI 节点、控件位置、数据库、系统颜色与图像像素；本轮工具未完成截图的人工视觉验收。
