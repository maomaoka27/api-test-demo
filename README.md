# API Test Demo - 接口自动化测试框架

这是一个基于 Python 搭建的轻量级接口自动化测试框架，用于实战演练接口测试的完整流程。

## 🛠️ 技术栈
- **开发语言**: Python 3.11
- **测试框架**: Pytest
- **请求库**: Requests
- **数据驱动**: YAML
- **测试报告**: Allure Report
- **被测系统**: FastAPI (本地 Mock 服务)

## 📁 项目结构
```text
api-test-demo/
├── app.py                 # 被测系统源码 (FastAPI)
├── conftest.py            # Pytest 全局前置操作，自动登录获取 Token
├── test_api.py            # 测试用例层 (包含登录和用户模块)
├── data/                  # 测试数据文件夹
│   └── login_data.yaml    # 登录接口的数据驱动文件
├── utils/                 # 工具类文件夹
│   └── request_util.py    # 请求封装类 (自动带 Token、打印日志)
└── README.md              # 项目说明文档