# VibeCoding 影响面分析工具

## 项目简介
基于 Python 和 SQLite 的代码调用图影响面分析与风险评级工具。

## 功能特性
- 解析 SQLite 调用图数据库（`edges` 与 `nodes` 表）
- 查询函数的上游调用方（Blast Radius）
- 结合 Git 变更行数进行风险评级
- 支持生成 HTML 可视化测试报告与影响面报告

## 运行环境
- Python 3.8+
- 依赖：pytest, pytest-html

## 运行命令
1. 安装依赖：
pip install pytest pytest-html
2. 运行影响面分析：
python impact_analyzer.py main
3. 运行测试并生成 HTML 报告：
pytest test_impact_analyzer.py --html=report.html --self-contained-html
## Git 提交规范
遵循 Conventional Commits 规范（如 `feat: 描述内容`）。

## AI 使用声明
- 代码初稿由 AI 辅助生成。
- 影响面分析逻辑、风险评级规则设定与最终调试由队员人工主导完成。
