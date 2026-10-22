import sqlite3
import sys
from pathlib import Path
from tree_sitter import Language, Parser, Query
from tree_sitter import QueryCursor
import tree_sitter_python as tspython

# 初始化 tree-sitter 解析器 (适配 0.26 新版 API)
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

# 定义查询规则：提取函数定义和调用点
DEFS_QUERY = Query(
    PY_LANGUAGE,
    "(function_definition name: (identifier) @def.name) @def.node"
)

CALLS_QUERY = Query(
    PY_LANGUAGE,
    """
    (call function: (identifier) @call.name) @call.node
    (call function: (attribute attribute: (identifier) @call.name)) @call.node
    """
)

def init_db(db_path='code_graph.db'):
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS edges")
    cursor.execute("DROP TABLE IF EXISTS nodes")
    cursor.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            file_path TEXT,
            line_start INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE edges (
            caller_id INTEGER,
            callee_id INTEGER
        )
    """)
    conn.commit()
    return conn

def analyze_file(file_path: Path, conn: sqlite3.Connection):
    """解析单个 Python 文件并提取函数关系"""
    cursor = conn.cursor()
    source_code = file_path.read_bytes() # tree-sitter 0.26 需要 bytes[4](@ref)
    
    # 解析为 AST
    tree = parser.parse(source_code)
    root_node = tree.root_node
    
    # 存储节点信息
    node_ids = {}
    
    # 提取函数定义
    def_captures = QueryCursor(DEFS_QUERY).captures(root_node)
    for node in def_captures.get('def.node', []):
        name_node = node.child_by_field_name('name')
        if name_node:
            func_name = source_code[name_node.start_byte:name_node.end_byte].decode('utf8')
            line_start = node.start_point[0] + 1
            
            cursor.execute(
                "INSERT INTO nodes (name, file_path, line_start) VALUES (?, ?, ?)",
                (func_name, str(file_path), line_start)
            )
            node_ids[func_name] = cursor.lastrowid
            
    # 提取函数调用
    call_captures = QueryCursor(CALLS_QUERY).captures(root_node)
    for node in call_captures.get('call.node', []):
        name_node = node.child_by_field_name('function')
        if name_node and name_node.type == 'identifier':
            call_name = source_code[name_node.start_byte:name_node.end_byte].decode('utf8')
            # 简单关联：如果调用了已定义的函数，则记录边
            if call_name in node_ids:
                # 这里简化为：谁调用了它（实际需结合外层函数作用域，此处仅作骨架演示）
                cursor.execute(
                    "INSERT INTO edges (caller_id, callee_id) VALUES (?, ?)",
                    (node_ids.get(call_name), node_ids[call_name]) 
                )
                
    conn.commit()

def main():
    # 1. 初始化数据库
    init_db()
    
    # 2. 查找当前目录下的 Python 文件并分析
    for py_file in Path('.').glob('*.py'):
        if py_file.name != 'analyzer.py': # 跳过自身
            print(f"正在分析: {py_file}")
            analyze_file(py_file, sqlite3.connect('code_graph.db'))
            
    print("✅ 扫描完成！已生成 code_graph.db")

if __name__ == "__main__":
    main()
# test change