# 记录说明

这些 JSON 从本地已完成的记录中选取并整理：

- `tool-versions.json`：当时 Kali、Termux 和 Frida 的工具包版本。
- `rom-download-manifest.json`：官方同构建 ROM/镜像下载来源、大小和 SHA256。
- `verification-summary.json`：Root、逆向样本、抓包、USB 息屏、桌面功能及重启检查的结果和边界。

设备序列号、电脑账户路径、热点名、微件 ID、个人音量值、原始抓包和完整系统转储未导出。原始验证记录保留在电脑，摘要不能替代在自己的设备上复测。

`source_record_names` 表示本地证据文件的文件名，并非本仓库的可下载原始转储。历史校验值针对当时文件；`current` 下载入口和工具仓库会更新，需要获取对应新版本的校验值。
