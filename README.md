# 🚧 drf_resource：DRF资源化框架（开发中）

🌟 **从蓝鲸 `bk_resource` 剥离的核心能力** → 让DRF项目也能享受声明式API开发体验！

---

## 🌱 项目目标

将 `bk_resource` 的核心能力抽离成独立框架 → **彻底解除蓝鲸框架依赖**[3]



## 🚀 核心进展

● 已完成项目初始化与基础框架搭建[1]
● 正在优化 `resource` 模块自动发现机制 → 简化配置[4]
● 保留蓝鲸开发体验，但去掉所有蓝鲸专属依赖

---

## ⚙️ 快速使用（预览版）

```python
# resources.py
from drf_resource import Resource

class QuickResource(Resource):
    def perform_request(self, name="DRF"):
        return {"hello": name}
```

👉 自动映射到 `/api/quick/` (参数自动校验 ✨)

---

## 📌 贡献指引

本项目**早期阶段**，急需：

- 🐞 测试反馈 & Bug报告
- 🔍 自动发现机制优化[4]
- 🌐 更多DRF生态兼容性支持

---

> ✨ **设计原则**：**保持核心轻量** · 不做蓝鲸的第二个影子
> 🚧 **重要提示**：API可能变动，**不建议生产环境使用**

[正在活跃开发中] → ⭐ 欢迎试用 & 提PR！