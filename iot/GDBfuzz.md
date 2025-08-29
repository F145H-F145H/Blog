# GDBfuzz: Fuzzing Embedded Systems using Debug Interfaces

前记：在对 DIR-816路由器 的漏洞 CVE-2025-5623 的复现过程中，发现这是一个典型的内存溢出漏洞，利用该漏洞可以控制路由器的内存，从而实现对路由器的控制。为了进一步研究该漏洞和学习相关fuzz工具，模拟漏洞发现过程，我们使用了 GDBfuzz 这个工具来对路由器进行 fuzzing 测试。 

相关论文在 `docs/Fuzzing Embedded Systems using Debug Interfaces.pdf`

## 环境安装

下载 `GDB` `libgmp` `mpfr` 的源码和交叉编译工具以构建适用于当前设备架构的 `gdbserver` 程序。

- https://ftp.gnu.org/gnu/gdb/
- https://gmplib.org/
- https://gitlab.inria.fr/mpfr/mpfr

```bash
axel -n 4 https://sourceware.org/pub/gdb/releases/gdb-16.3.tar.gz
axel -n 4 https://gitlab.inria.fr/mpfr/mpfr/-/archive/master/mpfr-master.tar.gz
axel -n 4 https://gmplib.org/download/gmp/gmp-6.3.0.tar.xz
axel -n 4 https://buildroot.org/downloads/buildroot-2025.05.1.tar.gz

tar -xf ./gdb-16.3.tar.gz
tar -xf ./mpfr-master.tar.gz
tar -xf ./gmp-6.3.0.tar.xz
tar -xf ./buildroot-2025.05.1.tar.gz
```

我们本次实验的目标为 DIR-816路由器，根据先前的信息可以知道，通常是 **32位** 的 **`MIPS`** 小端序环境，通过cpuinfo我们得到更加详细的信息，并且我们的最终目的就是编译出适合于这个环境的程序。第一步，根据 cpuinfo 设置 `buildroot` 配置

![image](.pictures/GDBfuzz-1-1.png)

```
cd buildroot-2025.05.1
make menuconfig
make
```

```bash
tftp -g -r gdbserver -l /tmp/gdbserver 192.168.0.2
chmod +x /tmp/gdbserver
/tmp/gdbserver :1234 
```