# 自制验证样本

这些样本用于检查工具实际能否工作。目标函数都是简单的 `reverse_check` / `reverseCheck`，输入 `0x1337`（4919）时返回 7；Java Hook 演示改为 42。源码来自本次真机测试，不包含真实题目、个人文件或网络流量。

## 原生样本

- `native/reverse_sample.c`：在 Kali ARM64 编译 ELF，检查 GDB/LLDB 与反编译。
- `native/reverse_pe.c`：用 Windows 交叉编译工具构建 AMD64 PE，检查静态解析与反编译。
- `native/reverse_x64.S`：静态 x86_64 Linux ELF，检查 QEMU user。
- `ghidra/DecompileSample.java`：搜索 `reverse_check` 并输出反编译结果。

在 Kali ARM64 编译 C 样本：

```bash
mkdir -p build
gcc -g -O0 native/reverse_sample.c -o build/reverse-linux-arm64
gdb build/reverse-linux-arm64
```

编译和模拟 x86_64 汇编样本：

```bash
x86_64-linux-gnu-as native/reverse_x64.S -o build/reverse-x64.o
x86_64-linux-gnu-ld -static build/reverse-x64.o -o build/reverse-x86_64
qemu-x86_64 build/reverse-x86_64
```

预期输出 `K70 x86_64 emulation OK`。仓库只提供源码，构建出来的二进制放本地 `build`。

## Android 样本

`android/MainActivity.java` 和 `AndroidManifest.xml` 是当时测试 APK 的源码。单 Activity、target SDK 37、debuggable，没有网络或文件读取权限。

构建 APK 需要自己的 Android SDK / JDK / 签名配置。本仓库没有提交 APK、签名密钥或本机 SDK 路径，也不把源码目录包装成完整 Gradle 项目。可在自己的 Android 工程中使用该 Activity 与 manifest。

包名必须保持 `dev.k70.reverselab`，否则同时修改 Frida 脚本中的类名。先自行构建安装并打开应用，再测试 attach。

## Frida Java 脚本

`frida/package-lock.json` 锁定 Java bridge 7.0.13。电脑需安装 Node/npm 和匹配的 Frida Python 客户端：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install 'frida==17.26.3' 'frida-tools==14.13.1'
Set-Location .\samples\frida
npm ci
New-Item -ItemType Directory -Path build -Force
& '..\..\.venv\Scripts\frida-compile.exe' sample.js -o build\sample-compiled.js
& '..\..\.venv\Scripts\frida-compile.exe' sample-spawn.js -o build\sample-spawn-compiled.js
Set-Location ..\..
```

server 已启动、电脑 27070 转发到手机 27042、样本已打开时：

```powershell
.\.venv\Scripts\frida.exe -H 127.0.0.1:27070 -N dev.k70.reverselab -l .\samples\frida\build\sample-compiled.js
```

延迟脚本用于自制样本的 spawn 测试：

```powershell
.\.venv\Scripts\frida.exe -H 127.0.0.1:27070 -f dev.k70.reverselab -l .\samples\frida\build\sample-spawn-compiled.js
```

脚本延迟 1800 ms 只在这个样本上通过。Android 17 的即时启动 Java 注入曾崩溃，分析其他应用时优先 attach，参见[Frida 经验](../docs/03-frida-and-capture.md)。编译 bundle 包含 Java bridge，应遵循上游许可证；仓库未提交 bundle 或 node_modules。

## Python 逆向库

`python/verify_libraries.py` 检查 Capstone、Unicorn、Z3、pefile 与 pyelftools。运行前把本机编译的 `reverse-pe.exe` 和 `reverse-linux-arm64` 放到该脚本同一目录，并在 Kali 安装对应库。PE 需要自己的交叉编译环境，不在脚本中自动构建。

```bash
python3 python/verify_libraries.py
```

预期 Unicorn `X0=41`，Z3 解为 4919，PE 为 AMD64，ELF 为 AArch64。样本验证通过不代表所有输入文件或目标程序都兼容。
