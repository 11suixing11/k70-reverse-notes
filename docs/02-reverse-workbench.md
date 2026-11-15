# 逆向工作台

## 环境怎样组织

Termux 是手机上的终端入口。Kali 使用官方 NetHunter minimal ARM64 rootfs，解压到 Android 私有文件系统的 `/data/local/k70-ctf/kali-arm64`，通过 Root chroot 启动，沿用 Android 内核。

这台手机已安装的简明入口：

```bash
ctf-help    # 查看本机使用提示
ctf         # 进入 Termux 的 ~/ctf
kali        # 进入 Kali，exit 返回 Termux
```

这些命令是本次安装的本地 helper，普通 Termux 新装后不会自带。重建环境时需要先准备 rootfs 和入口脚本。

| 路径 | 用途 |
| --- | --- |
| `/sdcard/CTF/inbox` | 从电脑或手机下载导入题目 |
| `/sdcard/CTF/samples` | 样本与脚本 |
| `/sdcard/CTF/work` | 方便文件管理器访问的分析输出 |
| `/sdcard/CTF/captures` | 抓包导出 |
| Kali `/root/ctf/work` | 编译、执行 ELF、调试项目和 Ghidra 工程 |
| Termux `~/ctf/shared`、Kali `/root/ctf/shared` | 指向共享的 `/sdcard/CTF` |

共享存储用于导入和取回文件。需要执行权限的文件放内部 Linux 工作目录；`/root/ctf/work` 与 `/sdcard/CTF/work` 是两个不同的目录。

## chroot 挂载的处理

[本机使用的 Kali 入口源码](../examples/kali-enter.sh)记录了挂载方式：

1. 用 Magisk BusyBox 的 `unshare --mount --propagation private` 创建私有挂载空间。
2. 比较 namespace 标识，确认没有继续使用原宿主 mount namespace。
3. 将挂载传播设为 private，在 chroot 内准备 `/dev`、`/dev/pts`、`/proc`、`/sys` 和 `/dev/shm`。
4. 绑定共享目录与样本目录，清理 `LD_PRELOAD`、`LD_LIBRARY_PATH` 和 Termux `PREFIX` 后进入 chroot。

这份源码依赖已经准备好的 rootfs、目录和 Magisk BusyBox 路径，是本机实现的参考。它没有创建 PID、user 或网络 namespace，也不能用来隔离运行不可信程序。收尾时核对 Android 宿主没有残留 Kali 挂载。

Kali 系统包由 apt 管理，额外 Python 客户端放 venv。源切到官方 HTTPS `https://kali.download/kali` 后，`apt-get update` 已通过。rootfs 的 `current` URL 会变化，重建时要重新取当次校验值，不能强求它与历史快照一致。

## 工具实测

| 工具 | 本次验证 |
| --- | --- |
| JADX 1.5.6、apktool 2.7.0 | 自制 APK 的 Java 和 smali 恢复 |
| Ghidra 12.2 | ARM64 原生 headless，反编译 ARM64 ELF 和 AMD64 PE 的函数 |
| GDB 18.1、LLDB 21 | ARM64 ELF 断点、读取参数、继续运行 |
| radare2、Rizin | ELF/PE 架构、符号与反汇编 |
| QEMU user 11.1.2 | 自制静态 x86_64 ELF 运行 |
| Capstone、Unicorn、Z3 | ARM64 反汇编、模拟寄存器、求解约束 |
| pefile、pyelftools | AMD64 PE 导出与 AArch64 ELF 读取 |

完整版本在[快照](../records/tool-versions.json)。这些是样本验证的范围，不能据版本表推定任意题目都能直接运行。

## APK 静态分析

从 Termux 使用本机 `kali` helper：

```bash
kali jadx -d /sdcard/CTF/work/jadx-output /sdcard/CTF/inbox/challenge.apk
kali apktool d -f /sdcard/CTF/inbox/challenge.apk -o /sdcard/CTF/work/apktool-output
```

JADX 的发行版包装脚本会改变工作目录，输入输出都用绝对路径。桌面“逆向工作台”入口对应本次自制测试应用；它用于验证 Hook 和反编译，分析工具实际从 Termux/Kali 调用。

## ARM64 ELF 调试

把仓库的 `samples/native/reverse_sample.c` 放到 `/sdcard/CTF/samples`，进入 Kali：

```bash
mkdir -p /root/ctf/work
cd /root/ctf/work
gcc -g -O0 /sdcard/CTF/samples/reverse_sample.c -o lab-arm64
gdb ./lab-arm64
```

```gdb
break reverse_check
run
print value
continue
quit
```

样本参数应为 `4919`，函数结果为 `7`。LLDB 对同一样本的断点与继续执行也已通过。

## Ghidra headless

本机 wrapper 默认 Java 堆为 1 GB，限制分析 CPU 数可降低手机上的负担。[源码](../examples/ghidra-headless.sh)使用当时 Kali 的 Java 25 ARM64 路径，升级后应检查 `JAVA_HOME`。

```bash
mkdir -p /root/ctf/work/ghidra-projects
ghidra-headless /root/ctf/work/ghidra-projects my-project \
  -import /sdcard/CTF/inbox/challenge -max-cpu 2
```

自制 ELF 和 PE 的 `reverse_check` 已使用[验证脚本](../samples/ghidra/DecompileSample.java)正确反编译。图形桌面没有配置；headless 可用不能写成完整 GUI 体验已通过。

## 跨架构边界

手机 CPU 架构不要求与静态分析目标相同。K70 可以读取和反编译 x86_64 ELF / PE，但原生运行仍受 CPU 与操作系统约束。

QEMU 验证的是自制静态 x86_64 Linux ELF。动态 ELF 还需要匹配的加载器和库；Windows PE 还依赖 Windows API，本次未配置 Windows 执行环境。Windows 动态调试继续交给电脑上的 FLARE VM 等环境。

## Termux 的两个坑

GDB 曾遇到 libc++ 版本不匹配，curl 曾遇到 OpenSSL 版本冲突。修复后既检查包依赖，也在真实 Termux 应用进程内复测，而非只在 Root/ADB 环境中运行。

不要固定照抄本机的 Android 应用 UID，也不要手动覆盖一份未知版本的库来“解决”包冲突。按同一源更新相关依赖，随后运行 `dpkg --audit`、工具启动和实际功能检查。
