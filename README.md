# 把 Redmi K70 调成一台顺手的 Reverse 测试机

这次折腾的目标，是让 K70 既能日常使用，也能拿起来做 reverse。最后采用 **LineageOS 24 / Android 17 + Magisk + Termux + Kali ARM64 chroot**，用 Frida 分析 Android 真机，用 Ghidra、GDB、LLDB 和 Python 工具处理题目，再配上稳定的 USB 供网和统一的桌面。

记录整理于 **2026-11-16**，依据 2026-11-14 至 2026-11-16 的这台真机测试。这里的版本是当时的快照，换 ROM、OTA 或升级工具以后，需要重新验证。

## 最后用了什么

| 部分 | 最终方案 | 已确认的范围 |
| --- | --- | --- |
| 系统 | Redmi K70 标准版，`vermeer`；LOS `24.0-20261114-NIGHTLY-vermeer` | Android 17 / SDK 37，ARM64-only |
| Root | Magisk 31.1，修补同构建的 `init_boot` | Root 成功，SELinux Enforcing，数据仍加密 |
| 逆向环境 | Termux + 官方 NetHunter ARM64 rootfs 的 Kali chroot | APK、ARM64 ELF、Windows PE 静态分析 |
| 动态分析 | Frida 17.26.3、GDB 18.1、LLDB 21 | 原生 Hook、Java attach、自制样本的延迟启动注入 |
| 跨架构 | QEMU user 11.1.2 | 自制静态 x86_64 Linux ELF 运行成功 |
| 抓包 | PCAPdroid 2.0.2 Root 模式 | 与 USB 供网共存，真实导出有效 PCAP |
| 网络 | Gnirehtet 2.5.1 + 本机 USB 通道自动恢复 | 拔插/通道恢复、短时息屏请求、重启后连接 |
| 外观 | Lawnchair 15 Beta 3 + Delta 2.21.0 + Painterly 2 | 两屏 4×6、统一图标、灰蓝系统配色、三种微件 |

这套 Kali 运行在 Android 原有内核上。没有安装完整 NetHunter 专用内核，也没有在这次配置中换掉已有 ROM。Windows PE 的动态调试仍放在电脑上做。

## 从哪里看

1. [系统选型和 Root](docs/01-system-and-root.md)：为什么保留 Android、为什么修补 `init_boot`、怎样核对槽位与回退条件。
2. [逆向工作台](docs/02-reverse-workbench.md)：Termux、Kali、共享目录、Ghidra、ELF 调试与跨架构边界。
3. [Frida 和抓包](docs/03-frida-and-capture.md)：Android 17 Java 注入踩坑、版本匹配、loopback 转发、Root 抓包。
4. [USB 联网与日用配置](docs/04-usb-and-daily.md)：电脑给手机供网、断线恢复、天气误判离线、均衡设置。
5. [主题配方与恢复](docs/05-theme-and-recovery.md)：从类 iOS 叠加方案换到 Delta，以及桌面和微件恢复的坑。
6. [验证结果与排障](docs/06-validation-and-lessons.md)：通过了什么、怎样判断通过、还有什么没解决。
7. [上游来源](docs/sources.md)：安装文档、下载入口和社区参考。

## 可以直接复用的部分

- [主题配方](configs/theme-recipe.json)：网格、布局、配色和微件提供者；按配方重建。
- [工具版本快照](records/tool-versions.json)、[验证摘要](records/verification-summary.json)：用来比较自己的环境。
- [自制样本源码](samples/README.md)：ARM64 ELF、x86_64 ELF、PE、Android Java Hook 和 Ghidra 反编译验证。
- [只读设备检查脚本](scripts/inspect_device.py)：明确指定 ADB 序列号，读取系统与 Root 状态，不会刷机或修改设置。

```powershell
# 使用你自己的 platform-tools 路径和设备序列号
$adb = 'C:\Android\platform-tools\adb.exe'
$serial = 'YOUR_K70_SERIAL'
python .\scripts\inspect_device.py --adb "$adb" --serial "$serial"
# 已授权 Root 的设备可额外读取 Root、SELinux、加密状态与工作台目录
python .\scripts\inspect_device.py --adb "$adb" --serial "$serial" --include-root
```

脚本必须显式指定设备，并检查 `vermeer`，不会自动挑选列表里的第一台手机。输出包含你指定的序列号；若要保存，使用已被忽略的 `local-device-report.json`。

## 这次最有用的经验

**先核对兼容性，再抄配置。** 同样是 K70，HyperOS 的主题和内核配置不能直接套进 LineageOS；同样是 ARM64 Linux，能静态反编译 x86 文件，也不代表能原生执行它。

**验证实际行为。** 安装了工具，要再做一次断点、Hook、反编译和文件导出；天气微件显示出来，要区分缓存和真实更新；桌面设置改完，要测试手势和重启。

**保留可回退的基线。** 原生桌面、旧配色、同构建启动镜像和声音设置先留存。只动需要动的部分，恢复前重新检查版本、槽位和微件归属。

本仓库保存整理后的经验、配置配方与源码。手机标识、个人应用数据、抓包文件、原始系统转储、启动镜像和签名私钥保留在本地。图标与壁纸通过上游获取，作者与来源见文档。
