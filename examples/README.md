# 本机 helper 实现参考

这里保存三个本次实际使用的入口源码，便于理解实现和重新适配：

| 文件 | 用途 | 运行前提 |
| --- | --- | --- |
| `kali-enter.sh` | 在私有 mount namespace 进入 Kali | Magisk BusyBox、已准备的 ARM64 rootfs、挂载目录与 samples 目录 |
| `frida-control.sh` | 按需启动/停止 loopback Frida server | Root、已放置的 Frida 17.26.3 server、本机目录 |
| `ghidra-headless.sh` | 设置 Java 与内存后调用 Ghidra | Kali Ghidra 与 Java 25 ARM64 已安装 |

它们使用 Android/Kali 内部路径，不包含电脑账户路径或设备序列号。这些是已完成本机配置的一部分，不是通用安装器；复制之前核对目录、版本和执行权限。`kali-enter.sh` 只隔离挂载，不隔离 PID/user/network。

Termux 的 `kali`、`frida-ctl` 等入口还需要本机 Root bridge 和 wrapper。README 中的命令面向已经完成该配置的手机；全新环境先按[工作台说明](../docs/02-reverse-workbench.md)准备。
