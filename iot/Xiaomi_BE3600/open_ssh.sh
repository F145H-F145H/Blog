#!/bin/bash

# 路由器配置脚本 for Ubuntu 24.04
# 用途：通过curl命令配置路由器开启SSH功能

# ===== 用户配置部分 =====
# 请替换以下变量为您的实际值
ip="192.168.31.1"                 # 路由器的IP地址
stok="570cd9729704886bbb2c924c18b4ead2"      # 认证令牌（在登录后的URL中可见）

# ===== 函数定义 =====
# 发送POST请求并检查结果的函数
send_post_request() {
    local data="$1"
    local description="$2"
    
    echo "正在执行: $description"
    
    # 使用curl发送POST请求
    response=$(curl -s -X POST "http://$ip/cgi-bin/luci/;stok=$stok/api/xqsystem/start_binding" -d "$data")
    
    # 检查curl命令是否成功执行
    if [ $? -ne 0 ]; then
        echo "错误: 请求执行失败 - $description" >&2
        return 1
    fi
    
    # 检查响应是否包含错误
    if echo "$response" | grep -q "error"; then
        echo "警告: 路由器可能返回错误 - $description" >&2
        echo "响应内容: $response" >&2
    fi
    
    # 添加短暂延迟，避免请求过于频繁
    sleep 1
}

# ===== 主脚本执行 =====
echo "开始配置路由器 SSH 设置..."
echo "目标路由器: $ip"

# 检查curl是否可用
if ! command -v curl &> /dev/null; then
    echo "错误: 系统未安装curl，请先运行 'sudo apt install curl' 安装" >&2
    exit 1
fi

# 执行配置命令序列
send_post_request "uid=1234&key=1234'%0Anvram%20set%20ssh_en%3D1'" "启用SSH功能"
send_post_request "uid=1234&key=1234'%0Anvram%20commit'" "提交NVRAM设置"
send_post_request "uid=1234&key=1234'%0Ased%20-i%20's%2Fchannel%3D.*%2Fchannel%3D%22debug%22%2Fg'%20%2Fetc%2Finit.d%2Fdropbear'" "修改Dropbear配置"
send_post_request "uid=1234&key=1234'%0A%2Fetc%2Finit.d%2Fdropbear%20start'" "启动Dropbear服务"

echo "路由器SSH配置序列执行完成。"
echo "请注意：实际效果取决于路由器型号和固件版本，请验证SSH服务是否已正常开启。"
