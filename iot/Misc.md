# IoT 相关基础知识杂谈

前记：其实本来这个部分我准备放在最后再整理的，但是在学习各位大佬的博客时，发现 Iot 相关的知识面也是非常宽泛的，“冰冻三尺非一日之寒，滴水石穿非一日之功 。”我想这一部分的知识会进行不断的整理和更新。

## 一些杂谈

2025年7月22日:

距离上次学习 IoT 相关知识，已经过去一周了。这几天我和家人离开南京去了云南旅游。出发时南京地区的气温正达到峰值，而等我们回来时，正好赶上台风带来的降温，也算是碰巧躲过了最热的几天。回来之后，终于可以安心写代码了。

不过，由于系统环境的原因，我弃用了熟悉的 Ubuntu 22.04 和 KDE 桌面，转而使用了较新的 Ubuntu 24.04，桌面也换成了更简洁的 regolith。这种平铺式桌面带来了全新的体验，终于告别了之前窗口横七竖八的状态，让我个人非常喜欢。

而我一直在用的 IDA，它在 Linux 平台上的表现实在让我难以适应。感觉像是处于一种半残废状态，虽然基本功能还能凑合用，但总觉得缺了点什么核心的东西，让人用着不太顺手、效率打折。于是，我决定今后主要转向使用开源的 Ghidra 作为逆向分析工具。

目前来说，Cyberangel 师傅的博客对我有很大的参考、启发和指导作用，甚至可以说我目前为止的内容就是在照抄这位师傅的博客，在此特别感谢。指北：[ Cyberangle 公开知识库 ](https://www.yuque.com/cyberangel/rg9gdm)

2025年8月10日：

文件变多导致内容的管理更加复杂了，将“IoT 相关基础知识杂谈“部分改为“关于环境的配置“，同时整理系统的关键内容，毕竟没有人喜欢反复做无意义的劳动，对吧。

一键配置脚本会放在隔壁仓库。

## 网络环境的设置

为了避免每次开机或开启环境都需要重新配置网桥，我在deepseek的帮助下设置了一个脚本...

```bash
sudo vim /usr/local/bin/setup-bridge-tap.sh
```

```setup-bridge-tap.sh
#!/bin/bash
# 创建网桥
brctl addbr ms_br
ip link set ms_br up
ip addr add 192.168.10.1/24 dev ms_br

# 创建并连接TAP设备
ip tuntap add dev ms_tap mode tap
brctl addif ms_br ms_tap
ip link set ms_tap up
ip addr add 192.168.10.100/24 dev ms_tap
```

```bash
sudo chmod +x /usr/local/bin/setup-bridge-tap.sh
sudo vim /etc/systemd/system/bridge-tap.service 
```

```bridge-tap.service
[Unit]
Description=Setup Bridge and TAP for Custom Network
After=network.target
Requires=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/setup-bridge-tap.sh

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable bridge-tap.service 
```

完成配置后重启，查看 `ifconfig` 合乎预期就认为是配置成功啦。

## G502 侧键别浪费了

使用 `xbinkeys` 将侧键绑定为 `Alt`+`左右方向键` 帮助我在浏览器和Ghidra等应用中快速切换位置。
还有滚轮的左右健改为切换桌面。

```bash
sudo apt install xbindkeys xdotool
xbindkeys --defaults > ~/.xbindkeysrc
vim ~/.xbindkeysrc
killall xbindkeys && xbindkeys
```

```.xbinkeys
# 绑定鼠标按钮6 -> Alt + Super + 左方向键 (向左切换桌面)
"xdotool key --delay 50 alt+Super+Left"
  b:6 + Release

# 绑定鼠标按钮7 -> Alt + Super + 右方向键 (向右切换桌面)
"xdotool key --delay 50 alt+Super+Right"
  b:7 + Release

# 绑定鼠标按钮8 -> Alt + 左方向键 (浏览器后退)
"xdotool key --delay 50 alt+Left"
  b:8 + Release

# 绑定鼠标按钮9 -> Alt + 右方向键 (浏览器前进)
"xdotool key --delay 50 alt+Right"
  b:9 + Release
```