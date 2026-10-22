import os
import sys
import sqlite3
import subprocess

# 数据库路径（确保在当前项目目录下）
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "code_graph.db"
)

def get_changed_lines():
    """获取变更行数（结合 git diff 统计）"""
    try:
        result = subprocess.run(
            ["git", "diff", "--numstat", "HEAD~1..HEAD"],
            capture_output=True, text=True
        )
        total_changed = 0
        for line in result.stdout.strip().splitlines():
            parts = line.split("	")
            if len(parts) == 3:
                added, removed, _ = parts
                if added.isdigit(): total_changed += int(added)
                if removed.isdigit(): total_changed += int(removed)
        return total_changed
    except Exception:
        return 0

def main():
    # 1. 获取函数名（支持命令行参数，没有则提示输入）
    if len(sys.argv) > 1:
        changed_func_name = sys.argv[1]
    else:
        changed_func_name = input("请输入变更的函数名: ").strip()
    
    if not changed_func_name:
        print("错误：未输入函数名")
        sys.exit(1)

    # 2. 读取 SQLite 调用关系 (适配 caller_id / callee_id + nodes 表结构)
    try:
        print(f"正在读取数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否存在
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_list = [t[0] for t in tables]
        if 'edges' not in table_list or 'nodes' not in table_list:
            print(f"错误：数据库中缺少 edges 或 nodes 表。现有表: {table_list}")
            sys.exit(1)

        # 查询谁调用了这个函数 
        # edges 表用 caller_id 和 callee_id 关联 nodes 表的 id
        cursor.execute("""
            SELECT DISTINCT caller.name, caller.file_path
            FROM edges e
            JOIN nodes caller ON caller.id = e.caller_id
            JOIN nodes callee ON callee.id = e.callee_id
            WHERE callee.name = ?
        """, (changed_func_name,))
        
        callers = cursor.fetchall()
        
        upstream_files = set()
        for _, file_path in callers:
            if file_path:
                upstream_files.add(file_path)
                
        conn.close()
    except sqlite3.Error as e:
        print(f"数据库读取失败: {e}")
        sys.exit(1)

    # 3. 输出受影响的上游信息
    print("【影响面分析】")
    if callers:
        print(f"变更函数 '{changed_func_name}' 的调用方（上游）：")
        for caller_name, file_path in callers:
            print(f"  - 函数: {caller_name} (文件: {file_path})")
        print(f"受影响的上游文件: {', '.join(upstream_files)}")
    else:
        print(f"变更函数 '{changed_func_name}' 暂无上游调用方（可能是入口函数、未被调用或数据库暂未解析到数据）")

    # 4. 简易风险评级
    changed_lines = get_changed_lines()
    caller_count = len(callers)
    
    if caller_count > 3 or changed_lines > 20:
        risk_level = "高风险 🔴"
    else:
        risk_level = "中低风险 🟢"
        
    print("【风险评级】")
    print(f"调用方数量: {caller_count}")
    print(f"变更行数: {changed_lines}")
    print(f"最终评级: {risk_level}")

if __name__ == "__main__":
    main()