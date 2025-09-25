#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>

#define PORT 8080
#define BUFFER_SIZE 2048
#define MAX_CLIENTS 10

// 日志函数
void log_message(const char* message) {
    time_t now = time(NULL);
    char time_buf[100];
    strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M:%S", localtime(&now));
    printf("[%s] %s\n", time_buf, message);
    fflush(stdout);
}

// 发送HTTP响应
void send_response(int client_socket, int status_code, const char* status_text, const char* body) {
    char response[BUFFER_SIZE];
    int length = snprintf(response, BUFFER_SIZE, 
                         "HTTP/1.1 %d %s\r\n"
                         "Content-Type: text/plain\r\n"
                         "Connection: close\r\n"
                         "Content-Length: %zu\r\n"
                         "\r\n"
                         "%s", 
                         status_code, status_text, strlen(body), body);
    
    send(client_socket, response, length, 0);
}

// 处理HTTP请求
void handle_request(int client_socket, const char* request) {
    log_message(request);  // 记录请求用于调试
    
    // 简单的路由解析
    if (strstr(request, "GET / ") != NULL || strstr(request, "GET /index") != NULL) {
        send_response(client_socket, 200, "OK", "Welcome to GDBFuzz Test Server\nUse endpoints: /vuln, /buffer, /calc");
    }
    else if (strstr(request, "GET /vuln") != NULL) {
        // 模拟一个易受攻击的端点
        send_response(client_socket, 200, "OK", "Vulnerable endpoint - ready for fuzzing");
    }
    else if (strstr(request, "GET /buffer") != NULL) {
        // 模拟缓冲区溢出漏洞
        char* query = strstr(request, "?input=");
        if (query) {
            char input[64];  // 故意使用小缓冲区
            sscanf(query, "?input=%63s", input);
            char response[128];
            snprintf(response, sizeof(response), "You entered: %s", input);
            send_response(client_socket, 200, "OK", response);
        } else {
            send_response(client_socket, 200, "OK", "Buffer test endpoint - add ?input= parameter");
        }
    }
    else if (strstr(request, "GET /calc") != NULL) {
        // 模拟计算功能，可能有整数溢出等问题
        char* query = strstr(request, "?a=");
        if (query) {
            int a, b;
            sscanf(query, "?a=%d&b=%d", &a, &b);
            char response[128];
            snprintf(response, sizeof(response), "Result: %d + %d = %d", a, b, a + b);
            send_response(client_socket, 200, "OK", response);
        } else {
            send_response(client_socket, 200, "OK", "Calculation endpoint - add ?a=num&b=num parameters");
        }
    }
    else {
        send_response(client_socket, 404, "Not Found", "Endpoint not found");
    }
}

int main() {
    int server_socket, client_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);
    
    // 创建socket
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // 设置socket选项
    int opt = 1;
    if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("Setsockopt failed");
        exit(EXIT_FAILURE);
    }
    
    // 绑定地址和端口
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);
    
    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }
    
    // 开始监听
    if (listen(server_socket, MAX_CLIENTS) < 0) {
        perror("Listen failed");
        exit(EXIT_FAILURE);
    }
    
    printf("GDBFuzz test server running on port %d\n", PORT);
    log_message("Server started");
    
    // 主循环
    while (1) {
        client_socket = accept(server_socket, (struct sockaddr *)&client_addr, &client_len);
        if (client_socket < 0) {
            perror("Accept failed");
            continue;
        }
        
        char buffer[BUFFER_SIZE] = {0};
        ssize_t bytes_read = read(client_socket, buffer, BUFFER_SIZE - 1);
        
        if (bytes_read > 0) {
            handle_request(client_socket, buffer);
        }
        
        close(client_socket);
    }
    
    close(server_socket);
    return 0;
}