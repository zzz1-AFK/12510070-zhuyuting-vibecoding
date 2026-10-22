import subprocess
import re
from tree_sitter import Language, Parser
import tree_sitter_python as tspython

# 初始化 tree-sitter
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def get_git_diff():
    """获取当前工作区与最后一次提交的差异 (无上下文)"""
    result = subprocess.run(
        ["git", "diff", "--no-color", "-U0"],
        capture_output=True, text=True
    )
    return result.stdout

def parse_hunk_ranges(diff_output):
    """解析 diff 文本，提取变更的行号范围 (基于新文件)"""
    ranges = []
    # 正则匹配 @@ -旧行,旧数 +新行,新数 @@
    pattern = r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@'
    for match in re.finditer(pattern, diff_output):
        start = int(match.group(1))
        count = int(match.group(2) or 1)
        ranges.append((start, start + count))
    return ranges

def get_function_ranges(source_code):
    """用 tree-sitter 解析代码，提取函数定义的行号范围"""
    tree = parser.parse(source_code)
    functions = []
    
    def walk(node):
        # Python 的函数定义节点类型为 function_definition
        if node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                func_name = source_code[name_node.start_byte:name_node.end_byte].decode('utf8')
                # tree-sitter 行号是 0-indexed，转换为 1-indexed
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                functions.append((start_line, end_line, func_name))
        for child in node.children:
            walk(child)
            
    walk(tree.root_node)
    return functions

def main():
    # 1. 获取 diff
    diff_text = get_git_diff()
    if not diff_text:
        print("✅ 没有检测到新的代码变更。请先修改一下 analyzer.py 然后保存（不要提交）！")
        return
        
    print("🔍 检测到代码变更，开始分析...")
    
    # 2. 解析变更行范围
    hunk_ranges = parse_hunk_ranges(diff_text)
    
    # 3. 读取当前文件源码 (这里以 analyzer.py 为例演示)
    # 实际比赛中可以遍历 git diff --name-only 的结果
    try:
        with open('analyzer.py', 'rb') as f:
            source_bytes = f.read()
    except FileNotFoundError:
        print("❌ 找不到 analyzer.py")
        return
        
    # 4. 获取函数范围
    function_ranges = get_function_ranges(source_bytes)
    
    # 5. 映射：变更行属于哪个函数？
    print("变更映射结果：")
    for hunk_start, hunk_end in hunk_ranges:
        touched_functions = []
        for fn_start, fn_end, fn_name in function_ranges:
            # 判断变更行是否与函数范围有重叠
            if max(hunk_start, fn_start) < min(hunk_end, fn_end):
                touched_functions.append(fn_name)
                
        if touched_functions:
            print(f"  - 变更行 [{hunk_start}-{hunk_end}] 位于函数: {', '.join(touched_functions)}")
        else:
            print(f"  - 变更行 [{hunk_start}-{hunk_end}] 位于全局作用域")

if __name__ == "__main__":
    main()