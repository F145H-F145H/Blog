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

我们本次实验的目标为 DIR-816路由器，根据先前的信息可以知道，通常是 **32位** 的 **`MIPS`** 小端序环境，通过cpuinfo我们得到更加详细的信息，可以帮助用于编译出适合于这个环境的程序。第一步，根据 cpuinfo 和我们的需要设置 `buildroot` 配置（注意，在 `toolchain` 中需要打开c++的支持和宽字符支持，否则可能无法编译新版本的`gdb`）。然后修改和运行自动脚本便可完成 `gdb` 依赖和本体的编译。

![image](.pictures/GDBfuzz-1-1.png)

```
cd buildroot-2025.05.1
make menuconfig
make

autobuild.sh
```
帮助快速修改和配置环境的小脚本 : P

```bash
#!/bin/bash

set -e

# 清除可能干扰的环境变量
unset LDFLAGS
unset CPPFLAGS
unset CFLAGS
unset CXXFLAGS

# 设置构建平台
BUILD="x86_64-pc-linux-gnu"

# 设置目标平台
TOOLCHAIN_PATH="/opt/cross-gdb/buildroot-2025.05.1/output/host"
TARGET="mipsel-buildroot-linux-uclibc"

# 将工具链添加到PATH
export PATH="$TOOLCHAIN_PATH/bin:$PATH"

# 设置工作路径
WORK_DIR="/opt/cross-gdb"
BACKUP_DIR="$WORK_DIR/backup"
OUTPUT_DIR="$WORK_DIR/output-$TARGET"

mkdir -p "$OUTPUT_DIR"

# 设置交叉编译环境
export CC="${TARGET}-gcc"
export CXX="${TARGET}-g++"
export CPP="${TARGET}-cpp"
export AR="${TARGET}-ar"
export AS="${TARGET}-as"
export LD="${TARGET}-ld"
export RANLIB="${TARGET}-ranlib"
export STRIP="${TARGET}-strip"

# 配置选项
CONFIGURE_OPTS="--prefix=$OUTPUT_DIR --build=$BUILD --host=$TARGET --target=$TARGET"
MAKE_OPTS="-j$(nproc)"

# 函数：清理并恢复源代码
clean_and_restore() {
    local lib_name=$1
    local lib_dir=$2
    local backup_file=$3

    echo "清理并恢复 $lib_name..."

    cd "$WORK_DIR"
    rm -rf "$lib_dir"
    tar -xf "$BACKUP_DIR/$backup_file"

    echo "$lib_name 恢复完成"
}

# 函数：编译和安装库
compile_and_install() {
    local lib_name=$1
    local lib_dir=$2
    local extra_opts=$3
    
    cd "$WORK_DIR/$lib_dir"
    make distclean 2>/dev/null || true
    rm -f config.cache 2>/dev/null || true
    ./configure $CONFIGURE_OPTS $extra_opts
    make $MAKE_OPTS
    make install
    
    echo "$lib_name 编译完成"
}

# 编译 GMP
clean_and_restore "GMP" "gmp-6.3.0" "gmp-6.3.0.tar.xz"
compile_and_install "GMP" "gmp-6.3.0" ""

# 设置环境变量以便后续编译能找到 GMP
export CPPFLAGS="-I$OUTPUT_DIR/include"
export LDFLAGS="-L$OUTPUT_DIR/lib"

# 编译 MPFR
clean_and_restore "MPFR" "mpfr-master" "mpfr-master.tar.gz"
cd $WORK_DIR/mpfr-master
autoreconf -if
compile_and_install "MPFR" "mpfr-master" "--with-gmp=$OUTPUT_DIR"

# 编译 GDB
clean_and_restore "GDB" "gdb-16.3" "gdb-16.3.tar.gz"
cd "$WORK_DIR/gdb-16.3"

make distclean 2>/dev/null || true

# 添加针对 MIPS uClibc 的特殊配置
export CXXFLAGS="-std=c++17 -march=24kc -mtune=24kc -mips16 -mdsp"
export CFLAGS="-march=24kc -mtune=24kc -mips16 -mdsp"
export LDFLAGS="-L$OUTPUT_DIR/lib -static"

./configure \
    --build=$BUILD \
    --host=$TARGET \
    --target=$TARGET \
    --prefix=$OUTPUT_DIR \
    --with-gmp="$OUTPUT_DIR" \
    --with-mpfr="$OUTPUT_DIR" \
    --enable-static \
    --disable-shared 

make $MAKE_OPTS
make install

# 剥离二进制文件以减小大小
if command -v "${TARGET}-strip" >/dev/null 2>&1; then
    "${TARGET}-strip" "$OUTPUT_DIR/bin/gdb"
    "${TARGET}-strip" "$OUTPUT_DIR/bin/gdbserver"
fi

echo "编译完成！$TARGET 的 GDB 和 GDBServer 位于: $OUTPUT_DIR/bin/"
```

这一部配置完成获得可执行文件后，我们将其放到 tftp 服务器中，使用 `minicom` 连接路由器，下载 `gdbserver` 并运行检测到正确回显和连接便说明我们已经完成了 `gdbserver` 的配置工作。

```bash
iptables -A INPUT -p all -j ACCEPT # 防火墙全开

tftp -g -r gdbserver -l /tmp/gdbserver 192.168.0.2 # 获取 gdbserver
chmod +x /tmp/gdbserver 
/tmp/gdbserver 0.0.0.0:1451 --attach 42 & # 后台运行（前台运行可能会卡死 minicom
```

```bash
gdb
target remote 192.168.0.1:1451 # 连接 gdbserver
```

![image](.pictures/GDBfuzz-1-2.png)