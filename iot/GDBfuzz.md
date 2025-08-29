# GDBfuzz: Fuzzing Embedded Systems using Debug Interfaces

前记：在对 DIR-816路由器 的漏洞 CVE-2025-5623 的复现过程中，发现这是一个典型的内存溢出漏洞，利用该漏洞可以控制路由器的内存，从而实现对路由器的控制。为了进一步研究该漏洞和学习相关fuzz工具，模拟漏洞发现过程，我们使用了 GDBfuzz 这个工具来对路由器进行 fuzzing 测试。 

相关论文在 `docs/Fuzzing Embedded Systems using Debug Interfaces.pdf`

## 环境安装

下载 `GDB` 源码、用于构建
https://ftp.gnu.org/gnu/gdb/



```bash
git clone https://github.com/boschresearch/gdbfuzz.git
cd gdbfuzz
```

```bash
python3 -m venv .venv # 创建新虚拟环境
source .venv/bin/activate  # 进入虚拟环境
make
```
