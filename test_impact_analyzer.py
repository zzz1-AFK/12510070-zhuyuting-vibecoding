import sqlite3
import pytest
from impact_analyzer import get_changed_lines, DB_PATH

def test_get_changed_lines():
    """测试获取Git变更行数函数"""
    lines = get_changed_lines()
    assert isinstance(lines, int)
    assert lines >= 0

def test_db_structure():
    """测试数据库表结构是否符合预期"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        edges_cols = [col[1] for col in cursor.execute("PRAGMA table_info(edges)").fetchall()]
        nodes_cols = [col[1] for col in cursor.execute("PRAGMA table_info(nodes)").fetchall()]
        
        assert 'caller_id' in edges_cols
        assert 'callee_id' in edges_cols
        assert 'name' in nodes_cols
        conn.close()
    except sqlite3.Error:
        pytest.fail("数据库读取失败，请检查 code_graph.db 是否存在及结构是否正确")