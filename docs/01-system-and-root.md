# 系统选型和 Root

## 先明确手机承担什么

这台设备以 reverse 为主，目标包括 Android APK、ARM64 原生库、Linux ELF 和 Windows PE。最终分工是：K70 负责 Android 真机行为、ARM64 动态分析和移动端静态分析；电脑负责更重的图形界面、x86 原生调试和 Windows 环境。

当时核查了专门用于 CTF 的系统，也查了 K70 原生 Linux 移植。没有找到能直接刷入 K70、同时成熟覆盖这些用途的专用 CTF 镜像。因此保留已经装好的 LineageOS，用 Root + Kali ARM64 补工具。

| 候选 | 适合什么 | 当时如何处理 |
| --- | --- | --- |
| Parrot HTB Edition | CTF / HTB、通用 ELF 工具 | HTB 下载项当时列 AMD64，作为电脑/VM 候选 |
| FLARE VM | Windows PE、.NET、x64dbg、dnSpyEx 等 | 是 Windows VM 配置，作为电脑端候选 |
| REMnux | 恶意软件、脚本、解包、取证 | 有 ARM64 VM，但通用 VM 镜像不能直接刷 K70 |
| Mobexler | 移动应用安全与逆向 | 电脑端工具 VM，可通过 USB 连接手机 |
| Athena OS | CTF 与按角色配置工具 | 当时官方 ISO 为 x86_64，未找到 K70 镜像 |
| Kali / NetHunter | 手机上的 Linux 工具环境 | 使用官方 ARM64 rootfs，自己验证 chroot 和工具 |
| K70 原生 Linux 移植 | 主线内核与桌面实验 | 有社区项目，但驱动、构建和镜像成熟度各不相同 |

查不到成熟镜像，不等于 K70 完全不能启动 Linux。Nura、vermeer-mainline 和社区 NetHunter Toolkit 都值得参考，但它们的状态与这台 LOS 24 / Android 17 设备不能混为一谈。具体入口见[来源](sources.md)。这些电脑 VM 和原生 Linux 候选未在本次配置中安装。

## 刷机基线

设备是 **Redmi K70 标准版，代号 `vermeer`，型号 `23113RKC6C`**。最终验证的构建为 `24.0-20261114-NIGHTLY-vermeer`，Android 17 / SDK 37，ARM64-only，内核版本记录为 5.15.223。

ROM、Recovery 和分区镜像取自同一构建，下载后按官方 SHA256 校验。[ROM 来源清单](../records/rom-download-manifest.json)保存文件名、官方 URL 和校验值，仓库不包含镜像。

2026-11-14 查阅的 K70 官方安装教程要求底层固件 `OS3.0.307.0.WNKCNXM`。这是当时文档要求的快照；以后安装应重新查对应机型的安装与固件更新页。不能用另一变体的流程，也不能把这条记录当成所有后续构建的固定要求。首次安装涉及清空内部存储，应按[官方安装教程](https://wiki.lineageos.org/devices/vermeer/install/variant2/)准备。

## 这次 Root 实际做了什么

使用 Magisk 31.1 修补 **当前 LOS 构建对应的 `init_boot.img`**。刷入前确认 product、解锁状态、当前槽位和分区大小；本次当前槽为 B，只写了 `init_boot_b`。

刷入后验证：

- `su -c id` 返回 `uid=0(root)`。
- Magisk 版本为 `31.1:MAGISK:R`。
- SELinux 为 `Enforcing`，数据加密仍为 `encrypted`。
- 真机 `init_boot_b` 的哈希与这次修补镜像一致。

不要从这条经验推导出所有手机都应刷 `boot` 或都应刷 `init_boot_b`。分区和槽位取决于设备与当前构建。

```powershell
$fastboot = 'C:\Android\platform-tools\fastboot.exe'
$serial = 'YOUR_K70_SERIAL'
# 手机已进入 fastboot；先阅读返回信息
& $fastboot -s "$serial" getvar product
& $fastboot -s "$serial" getvar current-slot
& $fastboot -s "$serial" getvar unlocked
```

只有确认还是这次构建、设备为 `vermeer`、槽位符合预期、Bootloader 已解锁，且修补文件来自该构建以后，才进入对应槽位的写入步骤。这份仓库不提供自动刷机脚本。

## 更新和回退

原 `init_boot` 和 Magisk 修补镜像都在电脑保留。本机回退资料对应这次 LOS 构建和当时 B 槽；OTA、换槽或重新刷 ROM 后，要用新的原镜像重新准备，不能沿用旧文件。

Root 后没有关闭 SELinux，也没有为了安装工具去清应用数据。镜像校验、Root 成功与日常应用兼容是不同的检查；银行/支付应用、长期待机和 OTA 后兼容没有被本次结果覆盖。

## Root 补不了内核缺项

原 LOS 启动镜像提取到的配置中：`CONFIG_SYSVIPC=n`、`CONFIG_USER_NS=n`、`CONFIG_PID_NS=n`，而 mount namespace 可以用于隔离 chroot 挂载。

因此采用私有 mount namespace 启动 Kali，并逐项验证工具。不能宣称它具备完整 NetHunter 的无线注入、外置网卡或 USB HID 功能。`CONFIG_USB_CONFIGFS_F_HID=y` 只说明内核配置存在，这次没有做实物功能验证。
