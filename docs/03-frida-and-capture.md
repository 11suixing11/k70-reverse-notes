# Frida 和抓包

## 先统一版本和入口

手机 server、手机客户端和电脑客户端都锁定 **Frida 17.26.3**；`frida-tools` 为 **14.13.1**。Kali 客户端安装在 venv，避免覆盖 apt 管理的 Python。

server 按需启动，只监听手机 `127.0.0.1:27042`，没有设置开机自启。本机 Termux 的 `frida-ctl` helper 使用[服务控制源码](../examples/frida-control.sh)：

```bash
frida-ctl start
frida-ps -a
# 完成分析后
frida-ctl stop
```

这份控制源码依赖已放置的对应版本 server 和本机目录。换版本时要一起修改二进制路径与客户端，不能直接把源码当安装器。

电脑通过指定设备的 ADB 转发访问：

```powershell
$adb = 'C:\Android\platform-tools\adb.exe'
$serial = 'YOUR_K70_SERIAL'
& $adb -s "$serial" forward --list
# 先确认电脑 27070 没被其他程序/设备占用
& $adb -s "$serial" forward --no-rebind tcp:27070 tcp:27042
frida-ps -H 127.0.0.1:27070 -a
```

拔插 USB 或手机重启后，需要检查并恢复该设备的转发。若端口已被占用，应先确定归属，不能为了这台手机直接重启全局 ADB。

## Android 17 Java 注入踩坑

原生进程枚举、spawn、attach 和 Hook 已通过；Java 层测试则遇到时间点问题：立即在应用启动早期调用 Java bridge，曾使自制样本崩溃。

随后用两条路径验证：

- 先启动自制应用，再 attach：Java Hook 成功。
- 对自制应用延迟 **1800 ms** 调用 Java bridge：观察 6 秒，Hook 成功，进程仍运行。

因此本机日用优先 attach。1800 ms 是这个样本的测试参数，目标应用的 ART、初始化和进程行为各不相同，不能当成通用修复。

## Frida 17 的 Java bridge

脚本显式导入 `frida-java-bridge`，再编译打包。这次依赖锁定为 **7.0.13**。仓库只保存自己的脚本和 npm 锁文件，编译后包含上游库的 bundle 在本地生成。

```javascript
import Java from 'frida-java-bridge';
```

[attach 样本](../samples/frida/sample.js) Hook 自制应用 `dev.k70.reverselab.MainActivity.reverseCheck(int)`：输入 `4919`，原结果 `7`，替换为 `42`。[延迟样本](../samples/frida/sample-spawn.js)只增加调用时机，其他逻辑一致。

编译与复现步骤见[样本说明](../samples/README.md)。先打开自制应用，然后在电脑执行：

```powershell
frida -H 127.0.0.1:27070 -N dev.k70.reverselab -l .\samples\frida\build\sample-compiled.js
```

样本只分析我们自己的离线测试 Activity，没有网络或文件读取权限。实际 APK 的 native library、ClassLoader 和多进程行为仍需按题目处理。

## PCAPdroid 与 USB 网络共存

Gnirehtet 供网占用手机 VPN 槽位，PCAPdroid 的 VPN 抓包模式也要使用该槽位。这台已 Root 的手机改用 **PCAPdroid Root 模式**，与 USB 供网实际共存通过。

本次测试只筛选 Termux，发出一条新的 HTTPS 请求后导出 PCAP。记录确认文件为有效 PCAP，共 **35 包、10408 字节**；测试后抓包和 Root daemon 都已停止。

日用方式：选择自己的目标应用 → 启动 → 复现行为 → 停止 → 导出到 `CTF/captures`。不要把“抓包界面正在运行”当成成功，应检查文件格式、包数量和目标请求。

本次没有安装 CA，也没有启用 TLS 解密，因此 HTTPS 内容仍加密。抓包文件留在本地；仓库只保存结果摘要。
