## AI 协作笔记

### 表格版（推荐直接贴文档）

| 序号 | 任务环节 | AI工具及版本 | 使用场景与目的 | AI生成/贡献内容 | 人工判断与修改 | 留存证据 |
|:--|:--|:--|:--|:--|:--|:--|
| 1 | 环境初始化与Git配置 | DeepSeek V3.2 | 配置conda隔离环境、安装依赖、初始化仓库 | 给出 `conda create` / `pip install tree_sitter` / `git init` 指令序列；给出 `.gitignore` 内容 | 执行时发现 `git add` 报 `not a git repository`，补跑 `git init`；确认 `.venv`/`code_graph.db` 不提交 | commit：`chore: 初始化项目并配置gitignore` |
| 2 | 代码图谱骨架（analyzer.py） | DeepSeek V3.2 | 生成Tree-sitter建图+SQLite存储代码 | 生成 `analyzer.py` 骨架（函数定义提取、调用点提取、nodes/edges表） | 复制到项目文件、保存、终端运行验证；确认生成 `code_graph.db` | commit：`feat: 完成 analyzer.py 骨架代码并跑通` |
| 3 | 运行产物处理规范 | DeepSeek V3.2 | 明确哪些文件不进Git | 提示 `code_graph.db` 属运行产物、已被 `.gitignore` 忽略 | 不执行 `git add code_graph.db` | .gitignore 内容 |
| 4 | 行号映射（diff_analyzer.py） | DeepSeek V3.2 | 读取git diff并映射到函数 | 生成 `diff_analyzer.py`（`git diff -U0`解析、hunk行号、tree-sitter函数范围交集） | 修第75行漏写括号语法错；VS Code解释器切到 `codeguard` 消导入警告；在analyzer.py制造测试变更（不提交） | 终端输出 `变更行 [104-106] 位于全局作用域` |
| 5 | 协作过程留痕 | DeepSeek V3.2 | 整理AI协作说明 | 指导笔记结构、版本填写口径 | 人工汇总成表格，标注“人主导AI辅助” | 本笔记 |

---

### 文字版（可贴进《作品信息与原创性说明》）

**AI协作开发说明（节选）**

本项目开发过程中使用腾讯元宝（DeepSeek V3.2）作为辅助编程工具，仅用于生成代码初稿、给出环境配置指令、辅助排查基础报错；系统架构设计、核心算法逻辑（调用图构建、diff行号映射、影响面查询、风险评级规则）、最终代码组装与运行验证均由人工完成。

主要协作节点如下：
1. 环境配置：AI给出conda创建Python 3.10环境、安装tree-sitter依赖、配置.gitignore的指令；实际执行并补全git init。
2. analyzer.py：AI生成Tree-sitter解析Python函数定义与调用关系、存入SQLite的骨架代码；保存并运行验证。
3. diff_analyzer.py：AI生成git diff解析与行号→函数映射脚本；修复语法错误、切换VS Code解释器至codeguard环境、构造测试变更验证输出。
4. 运行产物code_graph.db不参与版本提交，避免污染仓库。


