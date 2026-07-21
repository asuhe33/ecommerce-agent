"""测试 database/db_manager.py — 连接管理和只读查询。"""

import pytest
from unittest.mock import MagicMock, patch

from sqlalchemy import text


class TestDatabaseManager:
    """测试 DatabaseManager 类。"""

    def test_test_connection_success(self):
        """连接成功返回 True。"""
        with patch("database.db_manager.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine

            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            assert db.test_connection() is True

    def test_test_connection_failure(self):
        """连接失败返回 False。"""
        with patch("database.db_manager.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_engine.connect.side_effect = Exception("Connection refused")
            mock_create.return_value = mock_engine

            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            assert db.test_connection() is False

    def test_execute_query_select_allowed(self):
        """SELECT 查询正常执行。"""
        with patch("database.db_manager.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_result = MagicMock()

            # 模拟返回结果
            mock_result.mappings.return_value.all.return_value = [
                {"id": 1, "name": "test"}
            ]
            mock_conn.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__ = (
                lambda s: mock_conn
            )
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            result = db.execute_query("SELECT * FROM products")

            assert len(result) == 1
            assert result[0]["name"] == "test"

    def test_execute_query_rejects_insert(self):
        """INSERT 被拒绝，抛出 ValueError。"""
        with patch("database.db_manager.create_engine") as mock_create:
            mock_create.return_value = MagicMock()

            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            with pytest.raises(ValueError, match="仅允许只读查询"):
                db.execute_query("INSERT INTO products VALUES (1)")

    def test_execute_query_rejects_update(self):
        """UPDATE 被拒绝，抛出 ValueError。"""
        with patch("database.db_manager.create_engine") as mock_create:
            mock_create.return_value = MagicMock()

            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            with pytest.raises(ValueError, match="仅允许只读查询"):
                db.execute_query("UPDATE products SET price=100")

    def test_execute_query_rejects_delete(self):
        """DELETE 被拒绝，抛出 ValueError。"""
        with patch("database.db_manager.create_engine") as mock_create:
            mock_create.return_value = MagicMock()

            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            with pytest.raises(ValueError, match="仅允许只读查询"):
                db.execute_query("DELETE FROM products")

    def test_execute_query_show_allowed(self):
        """SHOW 查询正常执行。"""
        with patch("database.db_manager.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_result = MagicMock()

            mock_result.mappings.return_value.all.return_value = []
            mock_conn.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__ = (
                lambda s: mock_conn
            )
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            db.execute_query("SHOW TABLES")  # 不应抛出异常

    def test_execute_query_with_params(self):
        """带参数的查询正确传递参数。"""
        with patch("database.db_manager.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_result = MagicMock()

            mock_result.mappings.return_value.all.return_value = []
            mock_conn.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__ = (
                lambda s: mock_conn
            )
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            db.execute_query(
                "SELECT * FROM products WHERE name LIKE :kw",
                {"kw": "%手机%"},
            )

            # 验证 execute 被调用
            mock_conn.execute.assert_called_once()
