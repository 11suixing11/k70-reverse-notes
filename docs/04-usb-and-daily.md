# USB 联网与日用配置

## 电脑给手机供网

热点曾反复消失，影响安装和天气获取，随后改为 Gnirehtet 2.5.1：电脑作为 relay，通过 ADB 把网络交给手机 VPN。这是电脑给手机供网，与 Android 设置里“USB 网络共享”给电脑供网的方向相反。

上游提供 Windows 版本，第一次启动要在手机允许 VPN。基础用法是在工具所在目录打开两个终端：

```powershell
# 终端 1：保持 relay 运行
.\gnirehtet.exe relay
```

```powershell
# 终端 2：ADB 已识别目标手机，替换为自己的序列号
$serial = 'YOUR_K70_SERIAL'
.\gnirehtet.exe start "$serial"
# 需要结束时
.\gnirehtet.exe stop "$serial"
```

它转发 IPv4 TCP/UDP，使用电脑当前可用的网络。电脑的代理设置不会自动成为手机代理；VPN、IPv6 和网络策略应按实际环境另测。上游已说明项目不再积极维护，使用时应跟踪阻断性兼容问题。

## 自动恢复做了哪些约束

这次在 Windows 为本机增加了后台监视，5 秒检查一次。核心逻辑是检查目标设备与该设备的反向通道，必要时恢复通道并重新连接手机 VPN。

- 固定目标序列号，遇到 `unauthorized` 或设备离线就等待。
- relay 只监听电脑 loopback，不暴露到局域网。
- 先检查现有进程和通道，避免重复 relay。
- 手机切换到其他 VPN 时等待，不抢回 VPN 槽位。
- 手动 stop 同时关闭自动恢复。
- 没有安装 Windows 开机任务，电脑重启后需要再次启动。

故障注入只移除了这台手机的转发通道，观察到约 **18 秒**后自动恢复。随后 35 秒的 USB 连接息屏区间内，新 HTTPS 请求返回 200；最终手机重启后供网也已恢复。这些结果不覆盖数小时待机、深度 Doze 或所有 USB 硬件故障。

本仓库记录机制；原监视脚本绑定本机路径与序列号，保留在本地，不能直接作为通用脚本照搬。

## `unauthorized` 不是普通断线

如果 ADB 身份或授权重新建立，手机可能再次弹出 USB 调试授权。这时自动恢复只能等待用户在手机允许；不能把反复重启 ADB 当成修复。多设备环境中的全局 `adb kill-server` 还可能打断其他工作。

依次区分：数据线/USB 枚举 → ADB `device` 状态 → 本机 relay → 该设备反向通道 → 手机 VPN → 新的真实网络请求。

## 天气微件的假象

Breezy Weather 6.2.2 在仅有 Gnirehtet VPN、没有 Wi-Fi 或移动网络时，联网检测曾误判离线。核对源码后确认这是应用的网络判定限制：浏览器已经能联网，天气微件却仍显示之前获取的缓存。

当时的处理是保留固定城市和天气源设置，用[中国天气网](https://www.weather.com.cn/)网页入口作为 USB-only 联网时的补充。恢复 Wi-Fi/移动网络后，Breezy 按原设置更新。后续换桌面和重启只验证了微件保留，**没有将缓存显示写成 USB 天气刷新成功**。

因此天气验收要检查数据时间、真实更新结果和网络条件，不能只看主屏上是否有天气文字。

## 均衡日用设置

最终采用自动亮度、0.75 倍动画、60 秒息屏和插电不常亮，保留系统刷新率行为。下面是同类设置的示例，执行前指定自己的设备：

```powershell
$adb = 'C:\Android\platform-tools\adb.exe'
$serial = 'YOUR_K70_SERIAL'
& $adb -s "$serial" shell settings put system screen_brightness_mode 1
& $adb -s "$serial" shell settings put system screen_off_timeout 60000
& $adb -s "$serial" shell settings put global window_animation_scale 0.75
& $adb -s "$serial" shell settings put global transition_animation_scale 0.75
& $adb -s "$serial" shell settings put global animator_duration_scale 0.75
& $adb -s "$serial" shell settings put global stay_on_while_plugged_in 0
```

调试界面时曾临时关闭自动亮度，收尾和重启后已读回 `1`。所以要核对最终状态，而非仅记住曾经发过什么命令。

声音按原设置保留。本轮比较持久化 `volume_*`、铃声、通知声和闹钟声，差异为空；没有凭早期测试时的临时音量重新设置声音。

中文输入采用 Fcitx，终端增加 ESC、TAB、CTRL、ALT 和方向键。日历、时钟等参考 GKUI 组件；上游部分为 debug 构建且只做过 AndVM 验证，我们仅补了这台手机的基础操作验证。长期提醒、消息推送、支付、来电和续航仍需实际使用继续检验。
