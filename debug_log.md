# 调试日志

## 2026-02-03（更新）
- **任务**：初始化“猫咪读心机”MVP
- **状态**：MVP 已完成（含 Mock 降级方案）
- **API 问题排查**：
    - **现象**：`student-api.ai-builders.space` 解析到 `45.63.66.158`（Vultr/Choopa），但 ping 超时；`requests` 报 SSL 错误并连接到 `127.0.0.1`。
    - **分析**：
        - `nslookup` 显示公网 IP 为 `45.63.66.158`。
        - 然而 `requests` 日志提示“正在向主机 127.0.0.1 发起未验证的 HTTPS 请求”。
        - 强烈怀疑本地代理、VPN 或防火墙规则拦截流量并重定向到 localhost，或当前 Python 环境/网络栈存在 split-horizon DNS 问题。
        - 访问 `ai-builders.space` 返回 HTML（Circle.so 社区平台），而非后端 API。
    - **结论**：当前环境因网络/DNS 配置或服务器防火墙阻止该 IP 的 ICMP/HTTPS，导致无法访问给定 API 端点。
    - **临时方案**：继续采用 Mock 降级方案演示 MVP。

## 2026-02-03 (最终复盘)
- **任务**：API 调试与修复
- **状态**：**成功**（API 正常连通，Mock 方案作为备用）
- **问题与解决方案总结**：
    1.  **API 连通性**：
        -   初始域名 `student-api.ai-builders.space` 存在 DNS/代理问题，无法直接连接。
        -   **修复**：更换为正确的 Base URL `https://space.ai-builders.com/backend/v1`。
    2.  **301 重定向与 POST 降级**：
        -   旧域名或不完整的 URL 会触发 301 跳转，导致 `httpx` 自动将 POST 请求转为 GET，造成参数丢失。
        -   **修复**：在 `httpx.AsyncClient` 中开启 `follow_redirects=True`，并直接使用最终正确的 API 地址，避免不必要的跳转。
    3.  **404 Not Found**：
        -   Base URL 末尾自带 `/v1`，代码中拼接时又加了一层 `/v1`，导致路径错误。
        -   **修复**：修正路径拼接逻辑，确保 URL 结构正确 (`.../backend/v1/chat/completions`)。
    4.  **空响应内容**：
        -   调用 `gemini-2.5-pro` 时，虽然返回 200 OK，但 `content` 为空字符串。
        -   **修复**：
            -   将模型更换为能力更强的 **`supermind-agent-v1`**。
            -   将 `max_tokens` 从 100 增加到 1024。
            -   添加 `temperature` 参数以稳定输出。
    5.  **调试体验**：
        -   引入 `logging` 模块替换 `print`，实现了带时间戳和错误堆栈的详细日志，极大提升了排查效率。

## 运行方式
1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务：`uvicorn main:app --reload`
3. 浏览器访问：`http://localhost:8000`
